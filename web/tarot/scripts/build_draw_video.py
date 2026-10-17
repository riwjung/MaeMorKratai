"""Bake the home scene's shuffle-and-raise (master timeline 0 to 6.3 s) into public/scene/draw-shuffle.mp4.
Phones and Safari keep the filtered scene still (live, it runs at ~3 fps there); they play this video for the
draw instead, then the reveal dialog flips the card. Frames are rendered by seeking the GSAP timeline, so the
video is exact and smooth. The card back is shown; the flip to the face (6.35 s) is left to the dialog.
Run with the static site served: MMKT_TEST_URL=http://127.0.0.1:3010 ../.venv/bin/python scripts/build_draw_video.py
Needs ffmpeg.
"""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = os.getenv('MMKT_TEST_URL', 'http://127.0.0.1:3010').rstrip('/')
OUT = ROOT / 'public' / 'scene' / 'draw-shuffle.mp4'
FPS, END = 30, 6.3          # stop before card-flip (6.35 s)
CROP = (1080, 1500)         # the part of the 1080x1920 composition the home window shows
WIDTH = 720                 # encoded width; height follows the crop

def main():
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        sys.exit('ffmpeg not found')
    frames = Path(tempfile.mkdtemp(prefix='mmkt-draw-'))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1080, 'height': 1920}, device_scale_factor=1)
        page.goto(URL + '/scene/index.html?motion=still')
        page.wait_for_function("window.__timelines && window.__timelines['maemorkratai-halloween'] && document.fonts.status === 'loaded'")
        page.evaluate("Promise.all([...document.images].map(i => i.decode().catch(() => {})))")
        page.wait_for_timeout(800)
        count = int(END * FPS) + 1
        for i in range(count):
            # Seek without firing the bridge callbacks, then let the browser paint the new pose.
            page.evaluate("""(t) => new Promise(r => {window.__timelines['maemorkratai-halloween'].pause(t, true);
              requestAnimationFrame(() => requestAnimationFrame(r));})""", i / FPS)
            page.screenshot(path=str(frames / f'f{i:04d}.png'), clip={'x': 0, 'y': 0, 'width': CROP[0], 'height': CROP[1]})
        browser.close()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([ffmpeg, '-v', 'error', '-y', '-framerate', str(FPS), '-i', str(frames / 'f%04d.png'),
                    '-vf', f'scale={WIDTH}:-2:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-profile:v', 'main',
                    '-preset', 'slow', '-crf', '22', '-movflags', '+faststart', '-an', str(OUT)], check=True)
    shutil.rmtree(frames)
    print(f'{OUT.relative_to(ROOT)}: {count} frames, {OUT.stat().st_size // 1024} KB')

if __name__ == '__main__':
    main()
