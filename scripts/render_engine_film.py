#!/usr/bin/env python3
"""Cinematic pixel-art short: how a 4-stroke engine works, timed to a voiceover.

Shots: rainy neon night drive with the hook -> x-ray scan of the car -> dive into a lit
engine cutaway (intake, compression, power, exhaust) -> four-cylinder rev -> the car launches
and the last frames dissolve back to frame 0 so the clip loops. Word-synced captions are
burned in (TikTok is watched muted).

Timing (CLAUSES, KEYS and the T_* cues below) was measured from the supplied voiceover; if you
change the voiceover, re-measure those cues. Audio is mixed separately by make_engine_sfx.py.

Original procedural art only. Native 180x320, upscaled 6x nearest-neighbour to 1080x1920.
Usage: python3 scripts/render_engine_film.py --out out/engine-film-silent.mp4
       python3 scripts/render_engine_film.py --sheet out/engine-film-sheet.png   # QA contact sheet
"""
from __future__ import annotations
import argparse
import math
import random
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

W, H, SCALE, FPS = 180, 320, 6, 30
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
YY, XX = np.mgrid[0:H, 0:W]
BAY = BAYER[YY % 4, XX % 4]


def hexc(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def lerp_c(a, b, k):
    a, b = hexc(a), hexc(b)
    return tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def grad_box(arr, x0, y0, x1, y1, stops, axis='y'):
    """Bayer-dithered gradient into arr[y0:y1, x0:x1]; stops are (0..1, hex) along the axis."""
    x0, y0, x1, y1 = int(max(x0, 0)), int(max(y0, 0)), int(min(x1, W)), int(min(y1, H))
    if x1 <= x0 or y1 <= y0:
        return
    h, w = y1 - y0, x1 - x0
    p = np.array([s[0] for s in stops])
    cols = np.array([hexc(s[1]) for s in stops], np.float32)
    c = (np.arange(h)[:, None] + 0.5) / h if axis == 'y' else (np.arange(w)[None, :] + 0.5) / w
    c = np.broadcast_to(c, (h, w))
    idx = np.clip(np.searchsorted(p, c, side='right') - 1, 0, len(p) - 2)
    f = np.clip((c - p[idx]) / (p[idx + 1] - p[idx]), 0, 1)
    arr[y0:y1, x0:x1] = cols[idx + (f > BAY[y0:y1, x0:x1])]


def glow(arr, cx, cy, r, color, k=1.0, levels=6, sy=1.0):
    """Additive light with quantised, dithered falloff so it stays pixel-art (sy>1 flattens it)."""
    ry = r / sy
    x0, x1 = int(max(cx - r, 0)), int(min(cx + r + 1, W))
    y0, y1 = int(max(cy - ry, 0)), int(min(cy + ry + 1, H))
    if x1 <= x0 or y1 <= y0 or k <= 0:
        return
    d = np.hypot(XX[y0:y1, x0:x1] - cx, (YY[y0:y1, x0:x1] - cy) * sy)
    a = np.clip(1 - d / r, 0, 1) ** 2 * k
    a = np.floor(a * levels + BAY[y0:y1, x0:x1]) / levels
    arr[y0:y1, x0:x1] += a[..., None] * np.array(hexc(color), np.float32)


def to_im(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def to_arr(im):
    return np.asarray(im, np.float32).copy()


def post(arr, seed):
    a = np.clip(arr, 0, 255)
    bright = np.clip((a - 165) * 1.7, 0, 255).astype(np.uint8)
    a = a + np.asarray(Image.fromarray(bright).filter(ImageFilter.GaussianBlur(3)), np.float32) * 0.55
    vig = 1 - 0.38 * np.clip(np.hypot((XX - W / 2) / (W / 2), (YY - H / 2) / (H / 2)) - 0.55, 0, 1) ** 1.3
    a = a * vig[..., None] + np.random.RandomState(seed).randn(H, W, 1) * 2.5
    return np.clip(a, 0, 255).astype(np.uint8)


def dissolve(a, b, k):
    return np.where((BAY < k)[..., None], b, a)


# ---------------------------------------------------------------- 5x7 pixel font, outlined
_G = {
    'A': '.###./#...#/#...#/#####/#...#/#...#/#...#', 'B': '####./#...#/#...#/####./#...#/#...#/####.',
    'C': '.####/#..../#..../#..../#..../#..../.####', 'D': '####./#...#/#...#/#...#/#...#/#...#/####.',
    'E': '#####/#..../#..../####./#..../#..../#####', 'F': '#####/#..../#..../####./#..../#..../#....',
    'G': '.####/#..../#..../#..##/#...#/#...#/.####', 'H': '#...#/#...#/#...#/#####/#...#/#...#/#...#',
    'I': '.###./..#../..#../..#../..#../..#../.###.', 'J': '..###/...#./...#./...#./...#./#..#./.##..',
    'K': '#...#/#..#./#.#../##.../#.#../#..#./#...#', 'L': '#..../#..../#..../#..../#..../#..../#####',
    'M': '#...#/##.##/#.#.#/#.#.#/#...#/#...#/#...#', 'N': '#...#/##..#/#.#.#/#..##/#...#/#...#/#...#',
    'O': '.###./#...#/#...#/#...#/#...#/#...#/.###.', 'P': '####./#...#/#...#/####./#..../#..../#....',
    'Q': '.###./#...#/#...#/#...#/#.#.#/#..#./.##.#', 'R': '####./#...#/#...#/####./#.#../#..#./#...#',
    'S': '.####/#..../#..../.###./....#/....#/####.', 'T': '#####/..#../..#../..#../..#../..#../..#..',
    'U': '#...#/#...#/#...#/#...#/#...#/#...#/.###.', 'V': '#...#/#...#/#...#/#...#/#...#/.#.#./..#..',
    'W': '#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#', 'X': '#...#/#...#/.#.#./..#../.#.#./#...#/#...#',
    'Y': '#...#/#...#/.#.#./..#../..#../..#../..#..', 'Z': '#####/....#/...#./..#../.#.../#..../#####',
    '0': '.###./#...#/#..##/#.#.#/##..#/#...#/.###.', '1': '..#../.##../..#../..#../..#../..#../.###.',
    '2': '.###./#...#/....#/...#./..#../.#.../#####', '3': '####./....#/....#/.###./....#/....#/####.',
    '4': '#...#/#...#/#...#/#####/....#/....#/....#', '5': '#####/#..../####./....#/....#/#...#/.###.',
    '6': '.###./#..../#..../####./#...#/#...#/.###.', '7': '#####/....#/...#./..#../.#.../.#.../.#...',
    '8': '.###./#...#/#...#/.###./#...#/#...#/.###.', '9': '.###./#...#/#...#/.####/....#/....#/.###.',
    ' ': '...../...../...../...../...../...../.....', '.': '...../...../...../...../...../.##../.##..',
    ',': '...../...../...../...../.##../..#../.#...', '-': '...../...../...../#####/...../...../.....',
    '+': '...../..#../..#../#####/..#../..#../.....', '=': '...../...../#####/...../#####/...../.....',
    '/': '....#/....#/...#./..#../.#.../#..../#....', '!': '..#../..#../..#../..#../..#../...../..#..',
    "'": '..#../..#../...../...../...../...../.....',
}
FONT = {k: v.split('/') for k, v in _G.items()}


def text(im, s, y, scale=1, color='#ffffff', x=None, outline='#07060d'):
    d = ImageDraw.Draw(im)
    if x is None:
        x = (W - (len(s) * 6 * scale - scale)) // 2
    pts = []
    for i, ch in enumerate(s):
        for ry, row in enumerate(FONT.get(ch, FONT[' '])):
            for rx, c in enumerate(row):
                if c == '#':
                    pts.append((x + i * 6 * scale + rx * scale, y + ry * scale))
    for px, py in pts:
        d.rectangle((px - 1, py - 1, px + scale, py + scale), fill=outline)
    for px, py in pts:
        d.rectangle((px, py, px + scale - 1, py + scale - 1), fill=color)


# ---------------------------------------------------------------- voiceover timing (seconds)
T_HOOK_END = 4.65                           # hook text off, "LOOK INSIDE" on
T_SCAN = (4.7, 6.2)                         # x-ray sweep across the car
T_PUNCH = (6.0, 6.25)                       # two integer punch-ins on the x-ray engine
T_IRIS = (6.45, 7.05)                       # cyan iris opens onto the engine cutaway
T_ENG = 7.05
T_REV, T_BANK, T_OUT = 32.5, 34.45, 37.5    # rev-up begins, four-cylinder bank, outro street
T_SPARK, T_BOOM = (23.25, 23.55), 24.25     # spark flicker; flame bursts out of its hold
T_BANG = 39.36                              # "bang": the car launches
TOTAL_S = 40.8
LABELS = [('SPARK PLUG', 7.95), ('VALVES', 8.9), ('PISTON', 9.75), ('CRANKSHAFT', 10.45)]
KEYS = [(T_ENG, -90.0), (11.3, 0.0), (16.4, 180.0), (23.25, 360.0), (24.25, 363.5), (24.5, 380.0),
        (27.7, 540.0), (32.5, 720.0)]       # (time, crank angle): TDC/BDC land on the spoken beats
CLAUSES = [
    (0.17, 4.30, "Okay, so your engine is blasting about a hundred explosions every second."),
    (4.73, 6.31, "Let's see how that actually works."),
    (7.10, 8.64, "Inside, you've got a spark plug,"),
    (8.87, 9.48, "two valves,"),
    (9.72, 11.14, "a piston, and a crankshaft."),
    (11.40, 12.44, "First up is intake."),
    (12.95, 16.12, "The piston drops down, and air and fuel get sucked right in."),
    (16.56, 17.39, "Then compression."),
    (17.75, 18.89, "Both valves close,"),
    (19.16, 21.04, "and the piston squeezes that mix tight."),
    (21.43, 22.24, "Now the good part."),
    (22.62, 23.83, "The spark plug fires,"),
    (24.07, 25.06, "the mix explodes,"),
    (25.36, 27.41, "and that blast slams the piston back down."),
    (27.74, 28.77, "Last is exhaust."),
    (29.06, 30.71, "The piston pushes the burnt gas out,"),
    (31.06, 32.61, "and then the whole cycle starts again."),
    (33.18, 35.47, "At three thousand RPM with four cylinders,"),
    (35.83, 37.58, "that's a hundred bangs a second."),
    (37.91, 38.32, "Suck,"),
    (38.51, 39.11, "squeeze,"),
    (39.36, 40.20, "bang, blow."),
]
FIRST_CLAUSE_WORDS = [0.17, 0.65, 0.82, 1.0, 1.42, 1.54, 2.09, 2.30, 2.42, 2.83, 3.62, 3.89]


def build_captions():
    caps = []
    for ci, (c0, c1, s) in enumerate(CLAUSES):
        words = s.replace(',', '').replace('.', '').upper().split()
        if ci == 0:
            times = FIRST_CLAUSE_WORDS
        elif ci == len(CLAUSES) - 1:
            times = [39.36, 39.76]
        else:
            wt = [len(w) + 1.5 for w in words]
            acc, times = 0.0, []
            for w in wt:
                times.append(c0 + (c1 - c0) * acc / sum(wt))
                acc += w
        chunks, cur, n = [], [], 0
        for w, tw in zip(words, times):
            add = len(w) + (1 if cur else 0)
            if cur and n + add > 15:
                chunks.append(cur)
                cur, n = [], 0
                add = len(w)
            cur.append((w, tw))
            n += add
        chunks.append(cur)
        for i, ch in enumerate(chunks):
            end = chunks[i + 1][0][1] if i + 1 < len(chunks) else c1 + 0.18
            caps.append((ch[0][1], end, ch))
    return caps


CAPS = build_captions()


def captions(im, t, y):
    for a, b, ch in CAPS:
        if a <= t < b:
            active = max([i for i, (_, tw) in enumerate(ch) if tw <= t + 0.02] or [0])
            x = (W - (len(' '.join(w for w, _ in ch)) * 12 - 2)) // 2
            for i, (w, _) in enumerate(ch):
                text(im, w, y, 2, '#ffe35a' if i == active else '#ffffff', x=x)
                x += (len(w) + 1) * 12
            return


# ---------------------------------------------------------------- street: rainy neon night
X0, GY = 20, 284                     # car rear x, ground contact y
SKY = np.zeros((H, W, 3), np.float32)
grad_box(SKY, 0, 0, W, 241, [(0, '#06051a'), (0.45, '#150e38'), (0.8, '#2e1656'), (1, '#4e1e62')])
glow(SKY, 40, 236, 130, '#7a1e6a', 0.35)
glow(SKY, 150, 230, 110, '#14607a', 0.3)
NEON = ['#ff3ea5', '#3ef0ff', '#ffd23e', '#9a5bff', '#ff6a3e']
_r = random.Random(9)
RAIN = [(_r.uniform(0, W), _r.uniform(0, H), _r.uniform(5, 8)) for _ in range(70)]

def spline(pts, n=7):
    """Catmull-Rom through pts (clamped ends): smooth supercar curves without anti-aliasing."""
    p = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            u = k / n
            out.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * u + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * u * u
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * u ** 3) for j in (0, 1)))
    out.append(pts[-1])
    return out


# low, long, mid-engine wedge (x forward, y up is negative, ground at 0)
TOP = spline([(0, -9), (1, -14), (7, -18), (22, -21), (38, -23), (50, -27), (62, -29), (74, -29), (84, -27),
              (98, -21), (110, -17), (121, -13), (127, -10), (128, -7)])
BODY = TOP + [(127, -5), (118, -4), (108, -4), (14, -4), (5, -5), (1, -7)]
CANOPY = spline([(54, -21), (54, -24), (62, -27), (74, -27), (83, -25), (96, -20)], 5) + [(96, -20), (54, -20)]
WHEELS = (26, 100)
WHEEL_R = 8


def cp(x0, gy, pts):
    return [(x0 + x, gy + y) for x, y in pts]


def skyline(d, scroll, cell, hmin, hmax, body, rim, wins, lit, seed, signs=None):
    """Endless buildings keyed by absolute index, so scrolling never reshuffles them."""
    for n in range(int(scroll // cell) - 1, int((scroll + W) // cell) + 2):
        r = random.Random(seed * 7919 + n)
        bw, bh = cell - r.randint(0, 3), r.randint(hmin, hmax)
        x, top = round(n * cell - scroll), 236 - bh
        d.rectangle((x, top, x + bw - 1, 236), fill=body)
        d.line((x, top, x, 236), fill=rim)
        if r.random() < 0.4:
            d.line((x + bw // 2, top - r.randint(3, 9), x + bw // 2, top), fill=body)
        for wy in range(top + 3, 233, 4):
            for wx in range(2, bw - 2, 3):
                h = (n * 7919 + wy * 31 + wx * 17) % 100
                if h < lit * 100:
                    d.point((x + wx, wy), fill=wins[h % len(wins)])
        if signs is not None and r.random() < 0.5:
            sx, sy, sh = x + r.randint(1, max(1, bw - 7)), top + r.randint(6, 18), r.randint(12, 24)
            col = NEON[r.randrange(len(NEON))]
            d.rectangle((sx, sy, sx + 5, sy + sh), fill='#0c0814', outline=col)
            for k in range(sy + 3, sy + sh - 2, 4):
                d.line((sx + 2, k, sx + 3, k), fill=col)
            signs.append((sx + 3, sy + sh / 2, col, n))


def lamps(d, scroll, heads, cell=96):
    for n in range(int(scroll // cell) - 1, int((scroll + W) // cell) + 2):
        x = round(n * cell + 40 - scroll)
        d.rectangle((x, 170, x + 1, 236), fill='#0a0814')
        d.line((x, 170, x + 9, 170), fill='#0a0814')
        d.rectangle((x + 7, 171, x + 11, 172), fill='#fff1c8')
        heads.append((x + 9, 173))


def render_car(f, dist, x0, gy):
    """Candy-red wedge supercar: gradient body, cyan beltline, wing, vents, glass, spinning rims."""
    mask = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mask).polygon(cp(x0, gy, BODY), fill=255)
    g = np.zeros((H, W, 3), np.float32)
    grad_box(g, 0, gy - 30, W, gy - 3, [(0, '#ff6c78'), (0.18, '#f02844'), (0.5, '#b60e2e'), (0.8, '#640a24'),
                                         (1, '#2a0414')])
    body = to_im(g)
    gx = x0 + ((f * 2.6) % 330) - 80                                   # paint glint sweeping along the car
    band = Image.new('L', (W, H), 0)
    ImageDraw.Draw(band).polygon([(gx, gy - 32), (gx + 8, gy - 32), (gx - 3, gy), (gx - 11, gy)], fill=255)
    glint = ImageChops.multiply(mask, band).point(lambda v: int(v * 0.42))
    body = Image.composite(Image.new('RGB', (W, H), (255, 255, 255)), body, glint)
    car = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    car.paste(body, mask=mask)
    d = ImageDraw.Draw(car)
    P = lambda pts: cp(x0, gy, pts)
    # wheel arches: dark cut-outs clipped to the body
    arch = Image.new('L', (W, H), 0)
    ad = ImageDraw.Draw(arch)
    for wx in WHEELS:
        ad.ellipse((x0 + wx - 10, gy - 8 - 10, x0 + wx + 10, gy - 8 + 10), fill=255)
    arch = ImageChops.multiply(arch, mask)
    car.paste(Image.new('RGB', (W, H), (14, 2, 8)), mask=arch)
    d.polygon(P([(10, -8), (118, -8), (126, -5), (118, -4), (14, -4)]), fill='#2a0410')        # sill / skirt
    d.polygon(P([(0, -9), (9, -8), (9, -4), (3, -5), (1, -7)]), fill='#1a0208')                 # diffuser
    for k in range(3):
        d.line(P([(2 + k * 2, -8), (3 + k * 2, -5)]), fill='#4a1020')
    d.line(P(spline([(7, -18), (22, -21), (38, -23), (50, -27), (62, -29), (74, -29), (84, -27)], 5)), fill='#ffc0c8')
    d.line(P(spline([(84, -27), (98, -21), (110, -17), (121, -13), (127, -10)], 5)), fill='#ff98a4')   # edge light
    d.line(P(spline([(10, -16), (24, -19), (42, -21)], 5)), fill='#ff8794')                      # haunch highlight
    d.polygon(P(CANOPY), fill='#0a1224')                                                         # glass canopy
    d.line(P([(60, -26), (68, -22)]), fill='#5a7ac0')
    d.line(P([(73, -26), (82, -22)]), fill='#5a7ac0')
    d.line(P([(54, -20), (96, -20)]), fill='#ff98a4')                                            # beltline
    d.line(P([(55, -20), (53, -7)]), fill='#6a0a1e')                                             # door cut
    d.line(P([(94, -20), (98, -8)]), fill='#6a0a1e')
    d.line(P([(53, -7), (98, -8)]), fill='#6a0a1e')
    d.line(P([(84, -15), (88, -15)]), fill='#ffc0c8')                                            # handle
    d.polygon(P([(33, -20), (51, -21), (51, -9), (39, -9)]), fill='#16030a')                    # mid-engine intake
    for k in range(4):
        d.line(P([(36 + k * 4, -19), (40 + k * 4, -10)]), fill='#5a1226')
    d.rectangle(P([(101, -19), (109, -17)])[0] + P([(101, -19), (109, -17)])[1], fill='#2a0410')  # hood vent
    d.line(P([(102, -18), (108, -18)]), fill='#8a1a34')
    d.line(P([(8, -7), (121, -7)]), fill='#3ef0ff')                                              # neon sill line
    d.polygon(P([(-5, -29), (24, -26), (24, -24), (-4, -27)]), fill='#240812')                   # wing
    d.line(P([(-5, -29), (24, -26)]), fill='#ff98a4')
    d.polygon(P([(19, -29), (25, -28), (25, -22), (19, -22)]), fill='#c8142e')                   # end plate
    d.rectangle((x0 + 7, gy - 25, x0 + 8, gy - 19), fill='#1a0a14')                              # wing posts
    d.rectangle((x0 + 14, gy - 25, x0 + 15, gy - 19), fill='#1a0a14')
    d.polygon(P([(111, -17), (126, -12), (127, -10), (113, -13)]), fill='#fff8de')               # headlight
    d.line(P([(100, -18), (111, -17)]), fill='#9af4ff')
    d.polygon(P([(110, -4), (130, -5), (129, -7), (116, -6)]), fill='#12040a')                   # splitter
    d.line(P([(0, -13), (6, -17)]), fill='#ff2a4a', width=2)                                     # LED tail bar
    d.line(P([(0, -11), (3, -13)]), fill='#ff2a4a')
    d.rectangle((x0 - 2, gy - 8, x0, gy - 7), fill='#9aa6b2')                                    # twin exhaust tips
    d.rectangle((x0 - 2, gy - 6, x0, gy - 5), fill='#9aa6b2')
    for wx in WHEELS:
        cx, cy = x0 + wx, gy - 8
        d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill='#07070b')                              # tyre
        d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill='#2c3644')
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill='#c2ccd8')                              # rim
        d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill='#161c24')
        d.arc((cx - 6, cy - 6, cx + 6, cy + 6), 200, 330, fill='#3ef0ff')                        # glowing rim ring
        d.rectangle((cx + 2, cy - 4, cx + 3, cy - 1), fill='#ff2a4a')                            # brake caliper
        for j in range(5):
            a = dist / 6 + j * 2 * math.pi / 5
            d.line((cx, cy, cx + math.cos(a) * 4.6, cy + math.sin(a) * 4.6), fill='#eef4fa')
        d.ellipse((cx - 1, cy - 1, cx + 1, cy + 1), fill='#3ef0ff')
    return car


def draw_xray(d, x0, gy, dist, f):
    d.polygon(cp(x0, gy, BODY), fill=(8, 32, 58, 235), outline='#6ef0ff')
    d.polygon(cp(x0, gy, CANOPY), outline='#3aa8d0')
    d.line((x0 + 8, gy - 6, x0 + 120, gy - 6), fill='#1e6a90')                                  # chassis rail
    d.line((x0 + 56, gy - 6, x0 + 56, gy - 20), fill='#1e6a90')
    d.line((x0 + 96, gy - 6, x0 + 96, gy - 20), fill='#1e6a90')
    d.rectangle((x0 + 62, gy - 20, x0 + 70, gy - 11), outline='#2a7aa0')                       # seat
    d.line((x0 + 78, gy - 22, x0 + 82, gy - 17), fill='#2a7aa0')                                # steering wheel
    d.line((x0 + 48, gy - 12, x0 + 28, gy - 9), fill='#2a7aa0')                                 # drivetrain
    for wx in WHEELS:
        cx, cy = x0 + wx, gy - 8
        d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(4, 16, 30, 255), outline='#6ef0ff')
        for j in range(5):
            a = dist / 6 + j * 2 * math.pi / 5
            d.line((cx, cy, cx + math.cos(a) * 6, cy + math.sin(a) * 6), fill='#3aa8d0')
    ex, ey = x0 + 34, gy - 20                                                                    # glowing inline-4
    d.rectangle((ex, ey, ex + 20, ey + 11), fill='#0e3a5c', outline='#a0f6ff')
    for i in range(4):
        s = math.sin(f * 1.5 + (0, math.pi, math.pi, 0)[i])
        px0, off = ex + 2 + i * 5, round(2 * s)
        if s < -0.7 and (f // 4 + i) % 2 == 0:
            d.rectangle((px0 - 1, ey + 1, px0 + 3, ey + 3), fill='#ffb040')
        d.rectangle((px0, ey + 5 + off, px0 + 2, ey + 7 + off), fill='#d8faff')


def street_scene(f, dist, scan=None, speed=1.0, x0=X0, nitro=0.0, backfire=0.0):
    t = f / FPS
    x0 = int(round(x0))
    im = to_im(SKY)
    d = ImageDraw.Draw(im)
    signs, heads = [], []
    skyline(d, dist * 0.12, 18, 100, 200, '#171232', '#241c48', ['#4a3c86', '#6a54b0'], 0.08, 1)
    skyline(d, dist * 0.35, 26, 50, 150, '#0e0a20', '#221a44', ['#ffcf7a', '#ff9ad8', '#7ae8ff'], 0.16, 2, signs)
    lamps(d, dist, heads)
    d.rectangle((0, 236, W, 240), fill='#1a1630')
    d.line((0, 236, W, 236), fill='#3c3460')
    arr = to_arr(im)
    for sx, sy, col, n in signs:
        glow(arr, sx, sy, 18, col, 0.55 * (0.25 if (n * 13 + f // 3) % 23 == 0 else 1.0))
    for hx, hy in heads:
        glow(arr, hx, hy, 22, '#ffd890', 0.6)
        glow(arr, hx, 238, 26, '#ffd890', 0.18)
    grad_box(arr, 0, 241, W, H, [(0, '#120e26'), (1, '#05040c')])          # wet road + rippled reflections
    n = H - 241
    src = arr[241 - n:241][::-1]
    for k in range(n):
        sh = int(round(1.6 * math.sin(t * 5 + k * 0.8)))
        arr[241 + k] += np.roll(src[k], sh, axis=0) * 0.36 * (1 - k / n)
    by = GY + round(math.sin(f * 0.6) * 0.6)
    glow(arr, x0 + 64, by + 1, 70, '#20e0ff', 0.7, sy=4.2)                    # underglow on the asphalt
    glow(arr, x0 + 64, by + 1, 40, '#ff3ea5', 0.25, sy=4.2)
    im = to_im(arr)
    d = ImageDraw.Draw(im)
    for i in range(6):
        x = round((i * 40 - dist) % (W + 40) - 20)
        d.line((x, 306, x + 16, 306), fill='#8a7a4a')
    if speed > 1.2:
        rr = random.Random(f // 2)
        for _ in range(int(8 * (speed - 1))):
            y, x = rr.randint(150, 318), rr.uniform(0, W)
            d.line((x, y, x + rr.randint(8, 24), y), fill='#3a3466')
    car = render_car(f, dist, x0, by)
    if scan is not None and scan > 0:
        xr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw_xray(ImageDraw.Draw(xr), x0, by, dist, f)
        car.paste(xr.crop((0, 0, int(scan), H)), (0, 0))
    refl = car.transpose(Image.FLIP_TOP_BOTTOM)
    refl.putalpha(refl.getchannel('A').point(lambda v: int(v * 0.33)))
    im.paste(refl, (0, 2 * by - (H - 1)), refl)
    im.paste(car, (0, 0), car)
    d = ImageDraw.Draw(im)
    fl = max(backfire, 0.0)
    if fl > 0 or nitro > 0:                                                    # exhaust flame
        ln = max(22 * fl, nitro)
        ex, ey = x0 - 2, by - 6
        d.polygon([(ex, ey - 2), (ex - ln, ey - 4 * fl - 2), (ex - ln * 0.55, ey), (ex - ln, ey + 4 * fl + 1),
                   (ex, ey + 2)], fill='#ff8a2a')
        d.polygon([(ex, ey - 1), (ex - ln * 0.6, ey), (ex, ey + 1)], fill='#fff4b0')
    for i in range(3):                                                         # foreground poles flash past
        px = round(i * 420 + 150 - dist * 2.4) % (3 * 420) - 40
        if -4 < px < W + 4:
            d.rectangle((px, 0, px + 2, H - 1), fill='#04030a')
            d.line((px + 2, 0, px + 2, H - 1), fill='#1c1540')
    for rx, ry, v in RAIN:
        y = (ry + v * f * speed ** 0.5) % (H + 8) - 8
        x = (rx - y * 0.25 * speed) % W
        d.line((x, y, x - speed, y + 3), fill='#5e6aa4')
    rr = random.Random(f)
    for _ in range(7):
        x, y = rr.uniform(0, W), rr.uniform(246, 318)
        d.point((x, y), fill='#9aa6dc')
        d.point((x - 1, y - 1), fill='#6a76b0')
        d.point((x + 1, y - 1), fill='#6a76b0')
    arr = to_arr(im)
    hx, hy = x0 + 125, by - 12                                                 # headlight + beam + lens flare
    glow(arr, hx, hy, 20, '#fff0c0', 0.85)
    dx, dy = XX[:, hx:] - hx, YY[:, hx:] - hy
    a = np.clip(0.3 * (1 - dx / 90), 0, 1) * (np.abs(dy) < dx * 0.22 + 1)
    arr[:, hx:] += (np.floor(a * 6 + BAY[:, hx:]) / 6)[..., None] * np.array(hexc('#ffe6a8'), np.float32)
    if 0 <= hy < H:
        lo, hi = max(hx - 26, 0), min(hx + 27, W)
        if hi > lo:
            ramp = np.clip(1 - np.abs(np.arange(lo, hi) - hx) / 26, 0, 1) ** 2
            arr[hy, lo:hi] += ramp[:, None] * np.array(hexc('#bff8ff'), np.float32) * 0.9
    glow(arr, x0 + 2, by - 14, 16, '#ff2040', 0.75)
    glow(arr, x0 + 64, by - 8, 40, '#20e0ff', 0.14, sy=2.0)                  # sill neon spill on the paint
    if fl > 0 or nitro > 0:
        glow(arr, x0 - 8, by - 6, 26 + nitro * 0.5, '#ff8a2a', 0.8)
    if scan is not None and scan > x0 + 56:
        glow(arr, x0 + 44, by - 15, 20, '#ff8a2a', 0.35 + 0.35 * (f % 4 < 2))
        glow(arr, x0 + 52, by - 12, 54, '#1a9ad0', 0.2)
    if scan is not None and 0 < scan < W:                                      # scan beam with trailing glow
        xs = int(scan)
        lo = max(xs - 14, 0)
        arr[:, lo:xs] += (np.linspace(0, 1, xs - lo)[None, :, None] ** 2) * np.array(hexc('#20c8ff'), np.float32) * 0.28
        arr[:, max(xs - 1, 0):xs + 1] += np.array(hexc('#c8fbff'), np.float32) * 0.9
    if speed > 1.2:
        ln = int(36 * (speed - 1))
        xa = max(0, x0 - ln)
        if 0 < x0 <= W and x0 > xa:
            ramp = np.linspace(0, 1, x0 - xa)[None, :, None] * np.array(hexc('#ff2a4a'), np.float32)
            arr[by - 14:by - 12, xa:x0] += ramp * 0.8
    return arr


# ---------------------------------------------------------------- engine cutaway
CX, CEIL = 90, 104
BX0, BX1 = 67, 113
R, L, CY = 20, 46, 189
IN_X, EX_X = 76, 104
FIRE = np.array([hexc(c) for c in ('#2a0a14', '#7a1a16', '#d0401c', '#ff8a2a', '#ffc848', '#fff2b8')], np.float32)
PISTON = [(0, '#4e5864'), (0.3, '#e8eef4'), (0.55, '#aab4c0'), (1, '#424a54')]
_dr = random.Random(7)
DOTS = [(_dr.random(), _dr.random(), _dr.random()) for _ in range(50)]
STROKES = [('INTAKE', '#7aeaff'), ('COMPRESSION', '#ffd24a'), ('POWER', '#ff7a3a'), ('EXHAUST', '#c8b8ff')]


def workshop_bg():
    arr = np.zeros((H, W, 3), np.float32)
    grad_box(arr, 0, 0, W, 246, [(0, '#070b12'), (0.6, '#0d1822'), (1, '#132430')])
    for x in range(15, W, 30):
        arr[0:246, x] *= 0.72
    glow(arr, 90, 130, 120, '#1a4a5a', 0.6)
    glow(arr, 0, 0, 150, '#6a3a14', 0.35)
    grad_box(arr, 0, 246, W, H, [(0, '#0f161d'), (1, '#04070a')])
    arr[246] = hexc('#24323e')
    return arr


def build_engine_bg():
    arr = workshop_bg()
    grad_box(arr, 0, 82, 47, 102, [(0, '#9aacbe'), (0.45, '#556678'), (1, '#1e2630')])          # intake runner
    grad_box(arr, 133, 82, W, 102, [(0, '#8a786c'), (0.45, '#4e403a'), (1, '#1c1412')])         # exhaust header
    grad_box(arr, 46, 66, 135, 105, [(0, '#262e38'), (0.2, '#9aacbe'), (0.45, '#6a7e92'), (0.8, '#3e4c5c'),
                                     (1, '#1e252e')], 'x')                                          # head
    grad_box(arr, 52, 54, 129, 69, [(0, '#4a0a12'), (0.25, '#e8404e'), (0.55, '#a01c2a'), (1, '#3a0810')], 'x')
    grad_box(arr, 50, 105, 131, 220, [(0, '#1c2430'), (0.18, '#5c7084'), (0.4, '#3c4c5e'), (0.8, '#2a3644'),
                                      (1, '#141a22')], 'x')                                         # block
    grad_box(arr, 66, 104, 115, 175, [(0, '#05080c'), (0.35, '#1c2834'), (0.7, '#0e141c'), (1, '#04060a')], 'x')
    grad_box(arr, 58, 175, 123, 219, [(0, '#030507'), (1, '#0a0f14')])
    grad_box(arr, 54, 219, 127, 233, [(0, '#465466'), (1, '#141a22')])                            # oil pan
    im = to_im(arr)
    d = ImageDraw.Draw(im)
    for y in range(110, 172, 5):                                       # cooling fins
        for x0, x1 in ((50, 59), (121, 130)):
            d.line((x0, y, x1, y), fill='#10151c')
            d.line((x0, y + 1, x1, y + 1), fill='#53667a')
    d.line((53, 54, 127, 54), fill='#ff8a90')
    for bx in (56, 124):
        d.rectangle((bx, 58, bx + 1, 59), fill='#d8dde4')
    d.rectangle((62, 68, 118, 81), fill='#05080c')                     # cam chamber
    d.rectangle((0, 86, 82, 97), fill='#04070a')                       # intake port
    d.rectangle((70, 86, 82, 103), fill='#04070a')
    d.rectangle((98, 86, W, 97), fill='#04070a')                       # exhaust port
    d.rectangle((98, 86, 110, 103), fill='#04070a')
    d.line((65, 104, 65, 174), fill='#6a7c90')
    d.line((115, 104, 115, 174), fill='#6a7c90')
    d.rectangle((62, 233, 65, 246), fill='#1a222c')
    d.rectangle((115, 233, 118, 246), fill='#1a222c')
    d.rectangle((87, 38, 93, 48), fill='#b81e2c')                      # spark plug
    d.line((88, 38, 88, 48), fill='#e8505a')
    d.rectangle((88, 48, 92, 55), fill='#e6eaee')
    d.rectangle((87, 56, 93, 59), fill='#8c96a2')
    d.rectangle((89, 60, 91, 103), fill='#6c7884')
    d.line((89, 60, 89, 103), fill='#a8b4c0')
    d.rectangle((89, 104, 91, 105), fill='#c0c8d0')
    return to_arr(im)


ENGINE_BG = build_engine_bg()


def lift(th, mid):
    a = math.radians(((th - mid + 360) % 720) - 360) / 2                 # cam turns at half crank speed
    return max(0.0, min(1.0, (math.cos(a) - 0.6) / 0.4)), a


def pin_y(th):
    a = math.radians(th)
    return CY - (R * math.cos(a) + math.sqrt(L * L - (R * math.sin(a)) ** 2))


def draw_cam(d, cx, a, color):
    cy = 75
    d.ellipse((cx - 4, cy - 4, cx + 4, cy + 4), fill='#c8d2dc')
    pts = [(cx, cy)] + [(cx + math.cos(math.pi / 2 + a + math.radians(k * 8)) * 7,
                         cy + math.sin(math.pi / 2 + a + math.radians(k * 8)) * 7) for k in range(-4, 5)]
    d.polygon(pts, fill=color)
    d.point((cx, cy), fill='#05080c')


def engine_scene(fi, t, theta, phase):
    th = theta % 720
    py = pin_y(theta)
    crown = int(round(py - 11))
    li, a_in = lift(th, 95)
    le, a_ex = lift(th, 625)
    gas = phase != 'intro'
    arr = ENGINE_BG.copy()
    burning = 360 <= th < 545
    if burning:                                                        # flame front from the plug
        s = (th - 360) / 180
        front = 70 * min(1.0, max(0.0, (th - 361) / 16))
        ys, xs = slice(CEIL, crown), slice(BX0, BX1 + 1)
        dd = np.hypot(XX[ys, xs] - CX, YY[ys, xs] - CEIL)
        heat = max(0.0, 1 - s ** 0.8 * 0.92) * (1.15 - np.clip(dd / 60, 0, 1) * 0.8)
        idx = np.clip(np.floor(heat * 5 + BAY[ys, xs]), 0, 5).astype(int)
        region = arr[ys, xs]
        inside = dd < front
        region[inside] = FIRE[idx[inside]]
    im = to_im(arr)
    d = ImageDraw.Draw(im)
    a = math.radians(th)                                               # crankshaft
    cpx, cpy = CX + R * math.sin(a), CY - R * math.cos(a)
    wx, wy = -math.sin(a), math.cos(a)
    d.polygon([(CX - wy * 3, CY + wx * 3), (CX + wy * 3, CY - wx * 3),
               (cpx + wy * 3, cpy - wx * 3), (cpx - wy * 3, cpy + wx * 3)], fill='#3a4654')
    cwx, cwy = CX + wx * 9, CY + wy * 9
    d.ellipse((cwx - 9, cwy - 9, cwx + 9, cwy + 9), fill='#4a5868')
    d.ellipse((cwx - 7, cwy - 7, cwx + 2, cwy + 2), fill='#6a7c90')
    d.ellipse((CX - 5, CY - 5, CX + 5, CY + 5), fill='#c4ced8')
    d.point((CX, CY), fill='#1e262e')
    flow = theta / 180                                                 # gas moving through the ports
    if gas and li > 0.05 and (th < 215 or th > 700):
        for i in range(10):
            p = (flow + i / 10) % 1
            x, y = (2 + p / 0.75 * 74, 91 + math.sin(i * 2.1) * 3) if p < 0.75 else (IN_X + math.sin(i) * 3, 91 + (p - 0.75) / 0.25 * 16)
            d.point((x, y), fill='#9ff0ff')
    if gas and le > 0.05 and 515 < th:
        for i in range(10):
            p = (flow + i / 10) % 1
            x, y = (EX_X + math.sin(i) * 3, 107 - p / 0.25 * 16) if p < 0.25 else (EX_X + (p - 0.25) / 0.75 * 76, 91 + math.sin(i * 2.1) * 3)
            d.point((x, y), fill='#a8a0a4' if i % 2 else '#7a7276')
    if not gas:
        n, col = 0, None
    elif th < 180:
        n, col = int(len(DOTS) * min(1, th / 150)), hexc('#8ff0ff')
    elif th < 360:
        n, col = len(DOTS), lerp_c('#8ff0ff', '#ffb070', (th - 180) / 180)
    elif th < 540:
        n, col = 0, None
    else:
        n, col = int(len(DOTS) * max(0, 1 - (th - 540) / 165)), hexc('#9a96a0')
    for i in range(n):
        u, v, ph = DOTS[i]
        x = BX0 + 2 + u * (BX1 - BX0 - 4) + math.sin(fi * 0.9 + ph * 20)
        y = CEIL + 2 + v * max(1, crown - CEIL - 4) + math.cos(fi * 0.7 + ph * 17) * 0.8
        if y < crown - 1:
            d.point((x, y), fill=col)
    for vx, l, ca, col in ((IN_X, li, a_in, '#7aeaff'), (EX_X, le, a_ex, '#e0a070')):
        hy = CEIL + 4 * l
        d.rectangle((vx, 79 + 4 * l, vx + 1, hy), fill='#cfd8e0')
        d.rectangle((vx - 6, hy, vx + 7, hy + 1), fill='#d8e0e8' if vx == IN_X else '#c89870')
        draw_cam(d, vx, ca, col)
    arr = to_arr(im)
    grad_box(arr, BX0, crown, BX1 + 1, crown + 22, PISTON, 'x')        # piston
    arr[crown, BX0:BX1 + 1] = hexc('#f4f8fb')
    for ry in (crown + 3, crown + 5):
        arr[ry, BX0:BX1 + 1] *= 0.45
    arr[crown + 12:crown + 22, BX0:BX1 + 1] *= 0.85
    im = to_im(arr)
    d = ImageDraw.Draw(im)
    dx, dy = cpx - CX, cpy - py                                        # connecting rod
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln * 3, dx / ln * 3
    d.polygon([(CX + nx, py + ny), (CX - nx, py - ny), (cpx - nx, cpy - ny), (cpx + nx, cpy + ny)], fill='#8c98a6')
    d.line((CX, py, cpx, cpy), fill='#d4dde6')
    d.ellipse((CX - 3, py - 3, CX + 3, py + 3), fill='#1e262e')
    d.ellipse((cpx - 5, cpy - 5, cpx + 5, cpy + 5), fill='#9aa6b4')
    d.ellipse((cpx - 3, cpy - 3, cpx + 3, cpy + 3), fill='#e0a040')
    spark = T_SPARK[0] <= t < T_SPARK[1]
    if spark:
        r = random.Random(fi)
        x, y = CX, 106
        for _ in range(3):
            nx2 = x + r.randint(-3, 3)
            d.line((x, y, nx2, y + 2), fill='#ffffff')
            x, y = nx2, y + 2
    if phase == 'intro':                                               # pulse rings on each named part
        for (nm, t0), (cxr, cyr, rx, ry, col) in zip(
                LABELS, ((90, 50, 10, 10, '#ffd24a'), (90, 80, 30, 12, '#7aeaff'), (90, 128, 24, 20, '#e8eef4'),
                         (90, 189, 26, 26, '#e0a040'))):
            age = t - t0
            if 0 <= age < 0.7:
                g = 1 + age * 0.9
                d.ellipse((cxr - rx * g, cyr - ry * g, cxr + rx * g, cyr + ry * g), outline=lerp_c(col, '#000000', age / 0.7))
    arr = to_arr(im)
    if gas and li > 0:
        glow(arr, 60, 92, 46, '#1ac8ff', 0.3 * li)
    if gas and 180 <= th < 360:
        glow(arr, CX, (CEIL + crown) / 2, 26, '#ff8a3a', 0.3 * (th - 180) / 180)
    if 21.4 <= t < T_BOOM:                                             # the held breath before the bang
        k = smooth((t - 21.4) / 2.8)
        glow(arr, CX, CEIL + 6, 52, '#ff5a20', 0.08 + 0.2 * k * (0.6 + 0.4 * math.sin(t * 16)))
    if spark:
        glow(arr, CX, 106, 34, '#e8f4ff', 1.0)
    if burning:
        k = (1 - (th - 360) / 185) ** 1.5
        glow(arr, CX, CEIL + 10, 170, '#ff6a20', 0.5 * k)
        glow(arr, CX, (CEIL + crown) / 2, 40, '#ffd27a', 0.7 * k)
    hm = min(1.0, (th - 540) / 40) if th >= 540 else max(0.0, 1 - th / 120)
    glow(arr, 150, 92, 40, '#ff5a1a', 0.5 * hm)                        # header glows after exhaust
    n = H - 246                                                        # floor reflection
    arr[246:] += arr[246 - n:246][::-1] * (0.24 * (1 - np.arange(n) / n))[:, None, None]
    return arr


# ---------------------------------------------------------------- four-cylinder bank
BCX = [33, 71, 109, 147]
BR, BL, BCY = 12, 30, 168
BANK_BG = workshop_bg()
grad_box(BANK_BG, 8, 82, 172, 96, [(0, '#8a9cae'), (0.5, '#4a5a6c'), (1, '#1c242e')])               # manifold
grad_box(BANK_BG, 8, 200, 172, 214, [(0, '#465466'), (1, '#141a22')])                                  # oil pan


def bank_scene(fi, theta):
    im = to_im(BANK_BG)
    arr = to_arr(im)
    for cx in BCX:
        grad_box(arr, cx - 17, 96, cx + 18, 200, [(0, '#1c2430'), (0.2, '#6a7e92'), (0.5, '#3c4c5e'), (1, '#141a22')], 'x')
        grad_box(arr, cx - 12, 100, cx + 13, 176, [(0, '#05080c'), (0.4, '#1c2834'), (1, '#04060a')], 'x')
        grad_box(arr, cx - 17, 84, cx + 18, 97, [(0, '#4a0a12'), (0.25, '#e8404e'), (0.6, '#a01c2a'), (1, '#3a0810')], 'x')
    glows = []
    ims = to_im(arr)
    for i, cx in enumerate(BCX):
        th = (theta + (0, 540, 180, 360)[i]) % 720
        a = math.radians(th)
        py = BCY - (BR * math.cos(a) + math.sqrt(BL * BL - (BR * math.sin(a)) ** 2))
        crown = int(round(py - 8))
        if 360 <= th < 545:
            s = (th - 360) / 180
            ar = to_arr(ims)
            dd = np.hypot(XX[101:crown, cx - 12:cx + 13] - cx, YY[101:crown, cx - 12:cx + 13] - 101)
            heat = max(0.0, 1 - s ** 0.8 * 0.92) * (1.15 - np.clip(dd / 40, 0, 1) * 0.8)
            idx = np.clip(np.floor(heat * 5 + BAY[101:crown, cx - 12:cx + 13]), 0, 5).astype(int)
            ar[101:crown, cx - 12:cx + 13] = FIRE[idx]
            ims = to_im(ar)
            glows.append((cx, 110, 0.9 * max(0.0, 1 - s) ** 1.3))
        d = ImageDraw.Draw(ims)
        d.rectangle((cx - 11, crown, cx + 12, crown + 14), fill='#aab4c0')
        d.line((cx - 11, crown, cx + 12, crown), fill='#f4f8fb')
        d.line((cx - 11, crown + 3, cx + 12, crown + 3), fill='#4e5864')
        cpx, cpy = cx + BR * math.sin(a), BCY - BR * math.cos(a)
        d.line((cx, py, cpx, cpy), fill='#8c98a6', width=3)
        d.ellipse((cx - 8, BCY - 8, cx + 8, BCY + 8), fill='#4a5868')
        wx, wy = -math.sin(a), math.cos(a)
        d.ellipse((cx + wx * 6 - 6, BCY + wy * 6 - 6, cx + wx * 6 + 6, BCY + wy * 6 + 6), fill='#6a7c90')
        d.ellipse((cpx - 3, cpy - 3, cpx + 3, cpy + 3), fill='#e0a040')
        d.ellipse((cx - 2, BCY - 2, cx + 2, BCY + 2), fill='#c4ced8')
    arr = to_arr(ims)
    for cx, cy, k in glows:
        glow(arr, cx, cy, 60, '#ff6a20', 0.55 * k)
        glow(arr, cx, cy + 4, 26, '#ffd27a', 0.7 * k)
    n = H - 246
    arr[246:] += arr[246 - n:246][::-1] * (0.24 * (1 - np.arange(n) / n))[:, None, None]
    return arr


# ---------------------------------------------------------------- timeline / frames
def theta_at(t):
    if t <= KEYS[0][0]:
        return KEYS[0][1]
    for (t0, a0), (t1, a1) in zip(KEYS, KEYS[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            return a0 + (a1 - a0) * (0.3 * smooth(u) + 0.7 * u)
    u, w0, w1, rt = t - KEYS[-1][0], (720 - 540) / (32.5 - 27.7), 1400.0, 1.6
    x = min(u / rt, 1.0)
    return 720 + w0 * u + (w1 - w0) * (rt * (x ** 3 - x ** 4 / 2) + max(0.0, u - rt))


def phase_at(t):
    return 'intro' if t < 11.3 else ('slow' if t < T_REV else 'rev')


def punch(img, z, x0=X0):
    """Integer punch-in on the x-ray engine (crisp 2x/4x pixels, no resampling smear)."""
    bw, bh = W // z, H // z
    tx, ty = x0 + 45, GY - 14
    x1 = int(min(max(tx - bw / 2, 0), W - bw))
    y1 = int(min(max(ty - bh / 2, 0), H - bh))
    return np.repeat(np.repeat(img[y1:y1 + bh, x1:x1 + bw], z, axis=0), z, axis=1)


def iris_mix(a, b, r, cx, cy):
    """b inside a circle of radius r, a outside, with a glowing cyan rim."""
    d = np.hypot(XX - cx, YY - cy)
    out = np.where((d < r + (BAY - 0.5) * 3)[..., None], b, a).astype(np.float32)
    out[np.abs(d - r) <= 2.2] = (170, 250, 255)
    halo = (d > r + 2.2) & (d < r + 9)
    out[halo] = out[halo] * 0.62 + np.array([14, 80, 110], np.float32) * (1 - (d[halo] - r - 2.2) / 7)[:, None]
    return np.clip(out, 0, 255).astype(np.uint8)


def street_frame(t):
    f = int(round(t * FPS))
    scan = W * smooth((t - T_SCAN[0]) / (T_SCAN[1] - T_SCAN[0])) if t >= T_SCAN[0] else None
    bf = (1 - (f % 27) / 5) if (f % 27) < 5 and t < T_SCAN[0] else 0.0          # backfire pops
    img = post(street_scene(f, 1.8 * f, scan, 1.0, X0, backfire=bf), f)
    if t >= T_PUNCH[0]:
        img = punch(img, 4 if t >= T_PUNCH[1] else 2)
        for t0 in T_PUNCH:                                             # white-cyan flash on each cut
            if t0 <= t < t0 + 0.12:
                img = np.clip(img.astype(np.float32) + np.array([110, 150, 160]) * (1 - (t - t0) / 0.12), 0, 255).astype(np.uint8)
        return img
    im = Image.fromarray(img)
    if t < T_HOOK_END:
        text(im, '100 EXPLOSIONS', 14, 2, '#ffffff' if 2.4 <= t < 2.6 else '#ff8a3a')
        text(im, 'EVERY SECOND', 32, 2, '#ffe07a')
        text(im, 'INSIDE YOUR ENGINE', 52, 1, '#f0f0ff')
    else:
        text(im, 'LOOK INSIDE', 14, 2, '#7aeaff')
        d = ImageDraw.Draw(im)
        for (x, y, sx, sy) in ((18, 238, 1, 1), (162, 238, -1, 1), (18, 290, 1, -1), (162, 290, -1, -1)):
            d.line((x, y, x + 8 * sx, y), fill='#6ef0ff')
            d.line((x, y, x, y + 8 * sy), fill='#6ef0ff')
        if (f // 8) % 2 == 0:
            text(im, 'X-RAY', 228, 1, '#6ef0ff', x=22)
    return np.asarray(im)


def engine_frame(t):
    fi = int(round(t * FPS))
    theta, phase = theta_at(t), phase_at(t)
    arr = engine_scene(fi, t, theta, phase)
    if t >= T_BANK:
        bank = bank_scene(fi, theta)
        arr = bank if t >= T_BANK + 0.3 else dissolve(arr, bank, (t - T_BANK) / 0.3)
    img = post(arr, fi)
    if phase == 'rev':
        img = np.roll(img, fi % 2, axis=0)
    if T_BOOM <= t < T_BOOM + 0.7:                                    # the bang
        k = 1 - (t - T_BOOM) / 0.7
        img = np.roll(img, ((fi % 2) * 2 - 1) * round(4 * k), axis=1)
        img = np.clip(img.astype(np.float32) + 170 * max(0.0, 1 - (t - T_BOOM) / 0.18), 0, 255).astype(np.uint8)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    if phase == 'intro':
        text(im, 'HOW IT WORKS', 8, 2, '#ffd24a')
        for (s, t0), (x, y, lx, ly, c) in zip(LABELS, ((100, 30, 94, 42, '#ffd24a'), (4, 62, 72, 90, '#7aeaff'),
                                                       (4, 126, 66, 120, '#e8eef4'), (118, 200, 100, 192, '#e0a040'))):
            if t >= t0:
                ax = x + len(s) * 6 if x < CX else x - 2
                d.line((ax, y + 3, lx, ly), fill=c)
                text(im, s, y, 1, c, x=x)
    elif phase == 'slow':
        name, col = STROKES[int((theta % 720) // 180)]
        text(im, name, 8, 2, col)
        if T_BOOM <= t < T_BOOM + 0.9:
            text(im, 'BANG!', 128, 2, '#ffd24a', x=118 + (fi % 2))
        for i in range(4):
            x0 = 14 + i * 39
            d.rectangle((x0, 292, x0 + 34, 294), fill='#141c26')
            cur = int((theta % 720) // 180)
            fill = 1.0 if i < cur else ((theta % 180) / 180 if i == cur else 0)
            if fill > 0:
                d.rectangle((x0, 292, x0 + 34 * fill, 294), fill=STROKES[i][1])
    else:
        if t < 33.18:
            text(im, 'AGAIN + AGAIN', 8, 2, '#ffd24a')
        elif t < 35.83:
            text(im, '3000 RPM', 8, 2, '#ff7a3a')
        else:
            text(im, '100 BANGS/SEC', 8, 2, '#ffe07a')
        if t >= T_BANK + 0.3:
            for i, cx in enumerate(BCX):
                text(im, str(i + 1), 220, 1, '#9fb4c8', x=cx - 2)
    return np.asarray(im)


def outro_frame(t):
    fi = int(round(t * FPS))
    u = max(0.0, t - T_BANG)
    x0 = X0 + 95 * u * u
    dist = 2.4 * fi + 60 * u * u
    speed = 1.0 + 0.6 * smooth((t - 38.9) / 0.5) + 3.0 * smooth(u / 0.5)
    nitro = 44 * smooth(u / 0.2) if u > 0 else 0.0
    bf = (1 - (fi % 9) / 3) if (fi % 9) < 3 and 38.5 <= t < T_BANG else 0.0
    img = post(street_scene(fi, dist, None, speed, x0, nitro=nitro, backfire=bf), fi)
    if u > 0:
        img = np.roll(img, ((fi % 2) * 2 - 1) * round(4 * max(0.0, 1 - u / 0.5)), axis=0)
        img = np.clip(img.astype(np.float32) + 190 * max(0.0, 1 - u / 0.15), 0, 255).astype(np.uint8)
    im = Image.fromarray(img)
    for (a, b, word, col) in ((37.91, 38.51, 'SUCK', '#7aeaff'), (38.51, 39.36, 'SQUEEZE', '#ffd24a'),
                              (39.36, 39.76, 'BANG', '#ff7a3a'), (39.76, 41.0, 'BLOW', '#c8b8ff')):
        if a <= t < b:
            jit = 1 if (word == 'BANG' and fi % 2) else 0
            text(im, word, 70 + jit, 4, col)
    if t >= 40.05:
        text(im, 'FOLLOW FOR PART 2', 120, 1, '#ffe07a')
    return np.asarray(im)


def frame(fi, cache):
    t = fi / FPS
    if t < T_IRIS[0]:
        img = street_frame(t)
    elif t < T_ENG:                                                    # iris opens from the x-ray engine
        k = smooth((t - T_IRIS[0]) / (T_ENG - T_IRIS[0]))
        img = iris_mix(street_frame(t), engine_frame(t), 270 * k, 92, 160)
    elif t < T_OUT:
        img = engine_frame(t)
    elif t < T_OUT + 0.45:                                             # iris closes on the engine, opens on the street
        u = (t - T_OUT) / 0.45
        black = np.zeros((H, W, 3), np.uint8)
        if u < 0.45:
            img = iris_mix(black, engine_frame(t), 270 * (1 - smooth(u / 0.45)), 90, 160)
        else:
            img = iris_mix(black, outro_frame(t), 270 * smooth((u - 0.45) / 0.55), 90, 160)
    else:
        img = outro_frame(t)
        if t >= TOTAL_S - 0.4:                                         # loop back to the hook
            if 'first' not in cache:
                cache['first'] = street_frame(0)
            img = dissolve(img, cache['first'], (t - (TOTAL_S - 0.4)) / 0.4)
    im = Image.fromarray(np.ascontiguousarray(img))
    if t < T_OUT + 0.1:                                                # captions sit clear of the hero car
        captions(im, t, 70 if t < T_ENG else 256)
    return np.asarray(im)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out/engine-film-silent.mp4')
    ap.add_argument('--poster', default='out/engine-film-poster.png')
    ap.add_argument('--sheet', help='write a QA contact sheet and exit')
    args = ap.parse_args()
    total = int(TOTAL_S * FPS)
    cache = {}
    if args.sheet:
        picks = [int(s * FPS) for s in (0.4, 2.5, 4.4, 5.4, 6.7, 7.1, 8.6, 10.6, 14.5, 20.5, 23.4, 24.35, 24.8, 26.5,
                                        29.6, 34.0, 36.5, 38.2, 39.5, 40.4)]
        tiles = [Image.fromarray(frame(p, cache)) for p in picks]
        cols = 10
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * W, rows * H))
        for i, tl in enumerate(tiles):
            sheet.paste(tl, ((i % cols) * W, (i // cols) * H))
        Path(args.sheet).parent.mkdir(parents=True, exist_ok=True)
        sheet.resize((cols * W, rows * H), Image.NEAREST).save(args.sheet)
        print('sheet', args.sheet, 'frames', total, 'duration %.1fs' % (total / FPS))
        return
    if not shutil.which('ffmpeg'):
        raise SystemExit('FFmpeg not found. Install FFmpeg first.')
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(frame(int(24.7 * FPS), cache)).resize((W * SCALE, H * SCALE), Image.NEAREST).save(args.poster)
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an',
           '-vf', f'scale={W * SCALE}:{H * SCALE}:flags=neighbor,format=yuv420p', '-c:v', 'libx264',
           '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(dest)]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as p:
        try:
            assert p.stdin
            for fi in range(total):
                p.stdin.write(np.ascontiguousarray(frame(fi, cache)).tobytes())
        finally:
            if p.stdin:
                p.stdin.close()
        if p.wait() != 0:
            raise SystemExit('FFmpeg failed')
    print(f'Created {dest} ({total} frames, {total / FPS:.1f}s, silent) / {args.poster}')


if __name__ == '__main__':
    main()
