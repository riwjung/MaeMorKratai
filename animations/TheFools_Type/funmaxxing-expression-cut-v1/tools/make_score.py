"""Procedural music + SFX bed for The Fool at work (no samples, no licences, no credits).

Synth voices are the ones from the EP02 Claude Cut score.  A bright C-major office groove (112 bpm) that
grows in the colosseum, drops out for the still meeting-room beat (S10) and resolves for the end credit.
Cue times are global seconds; shot cuts come from timing/timeline.json.  Writes audio/score-sfx-bed.wav.
  /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -I tools/make_score.py
"""
import json, wave
from pathlib import Path
import numpy as np

P = Path(__file__).resolve().parent.parent
SR = 48000
DUR = 61.0
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)
BEAT = 60 / 112


def hz(note):
    names = {'C': -9, 'C#': -8, 'D': -7, 'D#': -6, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'G#': -1, 'A': 0, 'A#': 1, 'B': 2}
    n, o = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[n] + (o - 4) * 12) / 12)


def add(sig, t0, pan=0.5, gain=1.0):
    s = int(t0 * SR)
    if s >= N or s < 0:
        return
    e = min(N, s + len(sig))
    sig = sig[:e - s] * gain
    L[s:e] += sig * np.cos(pan * np.pi / 2)
    R[s:e] += sig * np.sin(pan * np.pi / 2)


def env_ar(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def noise(n):
    return rng.standard_normal(n)


def pad(notes, t0, t1, gain=0.05, fade=1.5, bright=0.25):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    e = env_ar(n, min(fade, (t1 - t0) / 2), min(fade, (t1 - t0) / 2))
    for i, nt in enumerate(notes):
        f = hz(nt)
        ph = 2 * np.pi * f * np.cumsum(1 + 0.003 * np.sin(2 * np.pi * (0.13 + i * 0.07) * t)) / SR
        v = np.sin(ph) + bright * np.sin(2 * ph + 0.3) + bright * 0.4 * np.sin(3 * ph + 1.1)
        add((v + 0.6 * np.sin(ph * 1.004 + 0.5)) * e, t0, 0.5 + 0.15 * ((i % 2) * 2 - 1), gain)


def pluck(note, t0, gain=0.08, decay=1.2, pan=0.5):
    f = hz(note); n = int(decay * 2.2 * SR); t = np.arange(n) / SR
    v = sum((1 / k ** 1.3) * np.sin(2 * np.pi * f * k * t) * np.exp(-t * (1.2 + k * 0.9) / decay * 2) for k in range(1, 7))
    add(v * np.minimum(1, t / 0.004), t0, pan, gain)


def bell(note, t0, gain=0.06, decay=2.0, pan=0.5):
    f = hz(note); n = int(decay * 2 * SR); t = np.arange(n) / SR
    v = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 2)
         + 0.3 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 4)) * np.exp(-t / decay * 2.5) * np.minimum(1, t / 0.002)
    add(v, t0, pan, gain)


def kick(t0, gain=0.22):
    n = int(.35 * SR); t = np.arange(n) / SR
    f = 120 * (45 / 120) ** (t / .35)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11), t0, .5, gain)


def hat(t0, gain=0.03, pan=.6):
    n = int(.06 * SR)
    add(filt(noise(n), 6000, None) * np.exp(-np.arange(n) / SR * 70), t0, pan, gain)


def boom(t0, gain=0.3, f0=90, f1=32, dur=1.4):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.2) * np.minimum(1, t / 0.005), t0, 0.5, gain)


def whoosh(t0, dur=0.35, gain=0.07, lo=500, hi=6000, pan_from=0.3, pan_to=0.7):
    n = int(dur * SR)
    v = filt(noise(n), lo, hi) * np.sin(np.linspace(0, np.pi, n)) ** 2
    h = n // 2
    add(v[:h], t0 - dur * .6, pan_from, gain); add(v[h:], t0 - dur * .6 + h / SR, pan_to, gain)


def pop(t0, gain=0.07, f=900):
    n = int(.12 * SR); t = np.arange(n) / SR
    add(np.sin(2 * np.pi * (f + 1400 * np.exp(-t * 40)) * t) * np.exp(-t * 30), t0, .5, gain)


def boing(t0, gain=0.12):
    n = int(.7 * SR); t = np.arange(n) / SR
    f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4)
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5), t0, .5, gain)


def roar(t0, dur=1.3, gain=0.22):
    n = int(dur * SR); t = np.arange(n) / SR
    body = filt(noise(n), 70, 900) * (1 + .6 * np.sin(2 * np.pi * 23 * t))
    tone = np.sin(2 * np.pi * np.cumsum(110 - 40 * t / dur) / SR) * .6
    add((body + tone) * env_ar(n, .08, .5), t0, .5, gain)


def purr(t0, t1, gain=0.08):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR
    add(filt(noise(n), 40, 300) * (.5 + .5 * np.sin(2 * np.pi * 26 * t)) * env_ar(n, .2, .4), t0, .5, gain)


def paper(t0, dur=1.0, gain=0.08, pan=.5):
    n = int(dur * SR); v = np.zeros(n)
    for p in rng.integers(0, n - 3000, 26):
        ln = int(rng.integers(300, 2500)); v[p:p + ln] += noise(ln) * np.exp(-np.arange(ln) / (ln / 4))
    add(filt(v, 1200, 9000) * env_ar(n, .02, .4), t0, pan, gain)


def steps(t0, t1, rate, gain=0.05, pan=.5):
    t = t0
    while t < t1:
        n = int(.08 * SR); add(filt(noise(n), 150, 1200) * np.exp(-np.arange(n) / SR * 45), t, pan, gain); t += rate


def groove(t0, t1, chords, gain=1.0, drums=True, bass=True, bright=True):
    """Two beats per chord: bass pluck on 1, chord stabs on the offbeats, kick/hat if drums."""
    t, k = t0, 0
    while t < t1 - .05:
        ch = chords[k % len(chords)]
        if bass:
            pluck(ch[0], t, .07 * gain, 1.0, .5)
        for j, nt in enumerate(ch[1:]):
            pluck(nt, t + BEAT * .5, .03 * gain, .7, .35 + .15 * j)
            if bright:
                pluck(nt, t + BEAT * 1.5, .022 * gain, .6, .65 - .15 * j)
        if drums:
            kick(t, .16 * gain); hat(t + BEAT * .5, .025 * gain); hat(t + BEAT * 1.5, .025 * gain, .4)
        t += 2 * BEAT; k += 1



I, VI, IV, V = ['C3','E4','G4'], ['A2','C4','E4'], ['F2','A3','C4'], ['G2','B3','D4']
groove(0,16,[I,VI,IV,V],.4,drums=False)
groove(16,24.969,[VI,IV],.3,drums=False)
groove(24.969,38.111,[I,VI,IV,V],.5,drums=True)
pad(['C4','G4'],38.111,43.067,.012,.5,.1)
groove(43.067,50.98,[IV,I],.4,drums=False)
pad(['C4','E4','G4'],50.98,61,.02,1,.15)
for t in [8.806,27.547,32.688,43.067]:pop(t,.025)
paper(20.2,.7,.02);steps(25,27,.42,.018)
for i,note in enumerate(['C5','E5','G5']):bell(note,44.8+i*.18,.025)
for i,note in enumerate(['C5','E5','G5','C6']):bell(note,54.4+i*.5,.025)
fade=np.minimum(1,np.maximum(0,(61-np.arange(N)/SR)/1.2));out=np.stack([L,R],axis=1)*fade[:,None]
with wave.open(str(P/'audio/music-sfx.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(out,-.95,.95)*32767).astype('<i2').tobytes())
print('score ready')
