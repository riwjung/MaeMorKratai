"""Bake the home scene's motion into videos for phones and Safari, where the filtered scene animates at a few fps.
  idle  -> public/scene/idle-loop.mp4     one seamless loop of her idle motion (breathing, ghosts, candles, blink)
  draw  -> public/scene/draw-shuffle.mp4  shuffle and raise (master timeline 0 to 6.3 s, card back; the reveal
                                          dialog flips the face, so one video serves every card)
Frames come from seeking the GSAP timelines, so the videos are exact and smooth.
Run with the static site served:
  MMKT_TEST_URL=http://127.0.0.1:3010 ../.venv/bin/python scripts/build_scene_videos.py [idle] [draw]
Needs ffmpeg. The draw video takes about 5 minutes.
"""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = os.getenv('MMKT_TEST_URL', 'http://127.0.0.1:3010').rstrip('/')
FPS = 30
CROP = (1080, 1500)   # the part of the 1080x1920 composition the home window shows
WIDTH = 720           # encoded width; height follows the crop
DRAW_END = 6.3        # stop before card-flip (6.35 s)

def render(page, frames, seek_js, times):
    for i, t in enumerate(times):
        # Seek without firing the bridge callbacks, then let the browser paint the new pose.
        page.evaluate("(t) => new Promise(r => {(" + seek_js + ")(t); requestAnimationFrame(() => requestAnimationFrame(r));})", t)
        page.screenshot(path=str(frames / f'f{i:04d}.png'), clip={'x': 0, 'y': 0, 'width': CROP[0], 'height': CROP[1]})

def frame_diff(ffmpeg, a, b):
    # Mean absolute luma difference between two PNG frames (0 = identical).
    import re
    log = subprocess.run([ffmpeg, '-i', str(a), '-i', str(b), '-filter_complex',
                          '[0][1]blend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'YAVG=([\d.]+)', log)[-1])

def encode(ffmpeg, frames, out, crf):
    subprocess.run([ffmpeg, '-v', 'error', '-y', '-framerate', str(FPS), '-i', str(frames / 'f%04d.png'),
                    '-vf', f'scale={WIDTH}:-2:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-profile:v', 'main',
                    '-preset', 'slow', '-crf', str(crf), '-movflags', '+faststart', '-an', str(out)], check=True)
    print(f'{out.relative_to(ROOT)}: {out.stat().st_size // 1024} KB', flush=True)

def main():
    wanted = set(sys.argv[1:]) or {'idle', 'draw'}
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        sys.exit('ffmpeg not found')
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1)
        if 'idle' in wanted:
            # Live motion so the scene builds its idle timeline (exposed as window.__mmktIdle).
            page.goto(URL + '/scene/index.html?motion=live')
            page.wait_for_function("window.__mmktIdle && document.fonts.status === 'loaded'")
            page.wait_for_timeout(800)
            length = page.evaluate("window.__mmktIdle.pause(0).duration()")
            frames = Path(tempfile.mkdtemp(prefix='mmkt-idle-'))
            count = round(length * FPS)
            # One extra frame at t = length must equal frame 0, so the loop has no seam. Checked on the source frames:
            # after encoding, the wrap differs only by codec grain (invisible; a lower CRF barely changes it).
            render(page, frames, "t => window.__mmktIdle.pause(t, true)", [i / FPS for i in range(count + 1)])
            wrap = frames / f'f{count:04d}.png'
            seam, step = frame_diff(ffmpeg, frames / f'f{count - 1:04d}.png', frames / 'f0000.png'), frame_diff(ffmpeg, frames / 'f0030.png', frames / 'f0031.png')
            print(f'idle loop check: t=length vs t=0 {frame_diff(ffmpeg, wrap, frames / "f0000.png"):.3f}, seam step {seam:.3f}, fastest step {step:.3f}', flush=True)
            wrap.unlink()
            encode(ffmpeg, frames, ROOT / 'public' / 'scene' / 'idle-loop.mp4', 24)
            shutil.rmtree(frames)
        if 'draw' in wanted:
            page.goto(URL + '/scene/index.html?motion=still')
            page.wait_for_function("window.__timelines && window.__timelines['maemorkratai-halloween'] && document.fonts.status === 'loaded'")
            page.wait_for_timeout(800)
            frames = Path(tempfile.mkdtemp(prefix='mmkt-draw-'))
            render(page, frames, "t => window.__timelines['maemorkratai-halloween'].pause(t, true)", [i / FPS for i in range(int(DRAW_END * FPS) + 1)])
            encode(ffmpeg, frames, ROOT / 'public' / 'scene' / 'draw-shuffle.mp4', 22)
            shutil.rmtree(frames)
        browser.close()

if __name__ == '__main__':
    main()
