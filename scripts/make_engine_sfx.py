#!/usr/bin/env python3
"""Mix a voiceover with synthesized sound design for render_engine_film.py.

All effects are generated here (numpy only, no samples) and placed on the same cue times the
film is built on: x-ray sweep, dive, part labels, stroke thumps, the compression riser and
heartbeat, spark crackle, the BANG, exhaust puffs, the 3000 rpm engine, and the launch.
Effects under the voice are ducked by the voice's own loudness; the big hits are not.

Usage: python3 scripts/make_engine_sfx.py VOICE.mp3 out/engine-mix.wav [--voice-only]
"""
from __future__ import annotations
import argparse
import subprocess
import wave

import numpy as np

SR = 44100
DUR = 40.8
N = int(SR * DUR)
rng = np.random.RandomState(11)


def tarr(a, b):
    return np.arange(int(SR * (b - a))) / SR


def put(buf, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i < 0:
        return
    sig = sig[:len(buf) - i]
    buf[i:i + len(sig)] += sig * gain


def fft_band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    m = 1.0 / (1 + (f / hi) ** 4) * (1 - 1.0 / (1 + (f / max(lo, 1)) ** 4))
    return np.fft.irfft(X * m, len(x))


def noise(dur, lo=200, hi=8000):
    return fft_band(rng.randn(int(SR * dur)), lo, hi)


def env_bell(n, peak=0.5):
    x = np.linspace(0, 1, n)
    return np.sin(np.pi * x ** (1 / (2 * peak + 1e-9) * 0.5 + 0.5)) ** 2


def whoosh(dur, lo0, lo1, hi0, hi1, peak=0.55):
    """Noise whose band sweeps over time (block-wise FFT filtering with crossfade)."""
    n = int(SR * dur)
    out = np.zeros(n)
    blocks = 12
    bl = n // blocks
    for b in range(blocks):
        u = b / max(blocks - 1, 1)
        lo, hi = lo0 + (lo1 - lo0) * u, hi0 + (hi1 - hi0) * u
        seg = fft_band(rng.randn(bl * 2), lo, hi)[:bl * 2] * np.hanning(bl * 2)
        i = b * bl // 1
        out[i:i + bl * 2] += seg[:max(0, min(bl * 2, n - i))] if i + bl * 2 <= n else seg[:n - i]
    return out * env_bell(n, peak)


def thump(freq0=90, freq1=34, dur=0.9, decay=5.0):
    t = np.arange(int(SR * dur)) / SR
    ph = 2 * np.pi * np.cumsum(freq1 + (freq0 - freq1) * np.exp(-t * 18)) / SR
    return np.sin(ph) * np.exp(-t * decay) * np.minimum(1, t * 600)


def pop(freq=1200, dur=0.06):
    t = np.arange(int(SR * dur)) / SR
    return np.sin(2 * np.pi * freq * t) * np.exp(-t * 60)


def engine_tone(dur, f0, f1, level=1.0):
    t = np.arange(int(SR * dur)) / SR
    f = f0 + (f1 - f0) * np.clip(t / dur, 0, 1)
    ph = np.cumsum(f) / SR * 2 * np.pi
    s = sum(np.sin(k * ph) / k for k in range(1, 9))
    s = np.tanh(2.2 * s) * (0.7 + 0.3 * np.sin(2 * np.pi * 6 * t))
    return fft_band(s, 30, 2600) * level


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('voice')
    ap.add_argument('out')
    ap.add_argument('--voice-only', action='store_true')
    args = ap.parse_args()
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', args.voice, '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    vo = np.frombuffer(raw, np.float32).astype(np.float64)
    voice = np.zeros(N)
    voice[:min(N, len(vo))] = vo[:N]
    bed, hits = np.zeros(N), np.zeros(N)

    # shot 1: scan + dive
    put(bed, whoosh(1.6, 400, 1800, 2500, 9000), 4.65, 0.55)
    for t0, g in ((6.0, 0.7), (6.25, 0.9)):                               # punch-in cuts
        put(hits, thump(140, 50, 0.4, 9), t0, g)
        put(hits, pop(900, 0.05), t0, 0.35)
    put(bed, whoosh(0.6, 200, 3000, 2000, 9000, 0.7), 6.45, 0.6)         # iris opens
    put(hits, thump(120, 40, 0.8, 6), 7.05, 0.8)
    for t0 in (7.95, 8.9, 9.75, 10.45):                                   # part labels
        put(hits, pop(1500 if t0 < 9 else 1100), t0, 0.28)
    # strokes
    for t0, g in ((11.3, 0.5), (16.4, 0.5), (27.7, 0.5)):
        put(hits, thump(160, 60, 0.35, 12), t0, g)
    put(bed, noise(2.2, 300, 5000) * env_bell(int(SR * 2.2), 0.35), 11.4, 0.16)               # intake rush
    # compression riser, heartbeat, spark, hold, BANG
    n = int(SR * (23.25 - 16.5))
    tt = np.arange(n) / SR
    f = 110 + 520 * (tt / tt[-1]) ** 2.2
    riser = np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / tt[-1]) ** 2 + 0.6 * noise(n / SR, 800, 6000)[:n] * (tt / tt[-1]) ** 3
    put(bed, riser, 16.5, 0.32)
    for t0 in (21.45, 21.95, 22.4, 22.78, 23.08):
        put(hits, thump(80, 52, 0.3, 14), t0, 0.5)
    crack = np.zeros(int(SR * 0.4))
    crack[rng.randint(0, len(crack), 40)] = rng.randn(40)
    put(hits, fft_band(crack, 2500, 12000) * 4.0, 23.25, 0.45)
    th = tarr(23.3, 24.25)
    hold = np.sin(2 * np.pi * 55 * th) * np.linspace(0.2, 0.8, len(th))
    put(bed, hold, 23.3, 0.28)
    put(hits, thump(95, 26, 1.6, 3.2), 24.25, 1.1)
    put(hits, noise(0.9, 80, 2500) * np.exp(-tarr(0, 0.9) * 5), 24.25, 0.9)
    put(bed, noise(3.0, 60, 900) * np.exp(-tarr(0, 3.0) * 1.1), 24.4, 0.45)                    # rumble tail
    # exhaust puffs
    put(hits, noise(0.7, 200, 4000) * np.exp(-tarr(0, 0.7) * 4), 27.8, 0.45)
    put(bed, noise(1.4, 200, 3500) * env_bell(int(SR * 1.4), 0.4), 29.2, 0.25)
    put(bed, noise(1.2, 200, 3500) * env_bell(int(SR * 1.2), 0.4), 31.2, 0.22)
    # rev-up to 3000 rpm (~100 firing pulses a second) and hold
    put(bed, engine_tone(2.0, 32.0, 100.0, 0.4) * np.linspace(0, 1, int(SR * 2.0)), 32.5, 0.7)
    put(bed, engine_tone(3.0, 100.0, 112.0, 0.4) * np.minimum(1, np.linspace(1, 0, int(SR * 3.0)) * 8), 34.5, 0.7)
    put(bed, whoosh(0.22, 3000, 300, 9000, 2000, 0.5), 37.5, 0.5)         # iris closes, then opens
    put(bed, whoosh(0.26, 300, 3000, 2000, 9000, 0.5), 37.72, 0.55)
    # outro words, launch
    for t0, fr in ((37.91, 520), (38.51, 660)):
        put(hits, pop(fr, 0.09), t0, 0.5)
    put(bed, noise(1.4, 400, 5000) * np.linspace(0, 1, int(SR * 1.4)) ** 2, 38.0, 0.28)       # turbo spool
    put(hits, thump(110, 30, 1.2, 4), 39.36, 1.2)
    put(hits, noise(0.5, 100, 9000) * np.exp(-tarr(0, 0.5) * 9), 39.36, 0.8)
    put(bed, engine_tone(1.4, 120, 380, 0.5) * np.linspace(1, 0, int(SR * 1.4)), 39.36, 0.7)
    put(bed, whoosh(1.0, 300, 900, 3000, 9000, 0.3), 39.76, 0.45)

    env = np.abs(voice)
    k = int(SR * 0.08)
    env = np.convolve(env, np.ones(k) / k, 'same')
    env = np.clip(env / (np.percentile(env, 95) + 1e-9), 0, 1)
    duck = 1 - 0.55 * env
    sfx = bed * duck + hits * (1 - 0.18 * env)
    mix = voice * 1.0 + (0 if args.voice_only else sfx)
    mix = np.tanh(mix * 0.95) / np.tanh(0.95)
    mix *= 0.89 / max(np.max(np.abs(mix)), 1e-9)
    fade = np.clip((N - np.arange(N)) / (0.3 * SR), 0, 1)
    st = np.stack([mix * fade, mix * fade], 1)
    with wave.open(args.out, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype('<i2').tobytes())
    print('wrote', args.out, '%.1fs' % (N / SR), 'voice-only' if args.voice_only else 'voice + sound design')


if __name__ == '__main__':
    main()
