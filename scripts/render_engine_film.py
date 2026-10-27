#!/usr/bin/env python3
"""Cinematic pixel-art short: how a 4-stroke engine works (silent, voiceover-ready).

Shots: rainy neon night drive with the hook -> x-ray scan of the car -> dive into a lit
engine cutaway (intake, compression, power, exhaust) -> rev up -> the car speeds off and
the last frames dissolve back to frame 0 so the clip loops.

Original procedural art only. Native 180x320, upscaled 6x nearest-neighbour to 1080x1920.
Usage: python3 scripts/render_engine_film.py --out out/engine-film.mp4
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
from PIL import Image, ImageDraw, ImageFilter

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


def glow(arr, cx, cy, r, color, k=1.0, levels=6):
    """Additive light with quantised, dithered falloff so it stays pixel-art."""
    x0, x1 = int(max(cx - r, 0)), int(min(cx + r + 1, W))
    y0, y1 = int(max(cy - r, 0)), int(min(cy + r + 1, H))
    if x1 <= x0 or y1 <= y0 or k <= 0:
        return
    d = np.hypot(XX[y0:y1, x0:x1] - cx, YY[y0:y1, x0:x1] - cy)
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


# ---------------------------------------------------------------- street: rainy neon night
X0, GY = 42, 282                     # car rear x, ground contact y
SKY = np.zeros((H, W, 3), np.float32)
grad_box(SKY, 0, 0, W, 241, [(0, '#06051a'), (0.45, '#150e38'), (0.8, '#2e1656'), (1, '#4e1e62')])
glow(SKY, 40, 236, 130, '#7a1e6a', 0.35)
glow(SKY, 150, 230, 110, '#14607a', 0.3)
NEON = ['#ff3ea5', '#3ef0ff', '#ffd23e', '#9a5bff', '#ff6a3e']
_r = random.Random(9)
RAIN = [(_r.uniform(0, W), _r.uniform(0, H), _r.uniform(5, 8)) for _ in range(70)]

CAR = [(1, -7), (0, -12), (2, -17), (12, -19), (30, -20), (42, -28), (60, -28), (72, -20), (88, -17), (95, -14),
       (96, -9), (94, -6), (86, -5), (10, -5)]
WIN_R = [(31, -19), (42, -27), (50, -27), (50, -19)]
WIN_F = [(52, -27), (59, -27), (70, -19), (52, -19)]
WHEELS = (20, 76)


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


def draw_car(d, x0, gy, dist):
    d.polygon(cp(x0, gy, CAR), fill='#c81e34')
    d.polygon(cp(x0, gy, [(1, -8), (96, -8), (94, -6), (86, -5), (10, -5), (1, -7)]), fill='#6e0c1e')
    d.line(cp(x0, gy, [(2, -17), (12, -19), (30, -20)]), fill='#ff7078')
    d.line(cp(x0, gy, [(72, -20), (88, -17), (95, -14)]), fill='#ff7078')
    d.line(cp(x0, gy, [(42, -28), (60, -28)]), fill='#ffa0a0')
    d.line(cp(x0, gy, [(3, -12), (94, -11)]), fill='#e8404e')
    d.polygon(cp(x0, gy, WIN_R), fill='#121828')
    d.polygon(cp(x0, gy, WIN_F), fill='#121828')
    d.line(cp(x0, gy, [(36, -19), (43, -26)]), fill='#4a5c8c')
    d.line(cp(x0, gy, [(56, -19), (60, -25)]), fill='#4a5c8c')
    d.line(cp(x0, gy, [(51, -18), (51, -6)]), fill='#7a1222')
    d.line(cp(x0, gy, [(44, -15), (46, -15)]), fill='#ffa0a0')
    d.rectangle((x0 + 69, gy - 21, x0 + 71, gy - 19), fill='#a01628')
    d.polygon(cp(x0, gy, [(89, -15), (95, -14), (95, -12), (90, -12)]), fill='#fff4c8')
    d.rectangle((x0, gy - 15, x0 + 2, gy - 12), fill='#ff2a4a')
    for wx in WHEELS:
        cx, cy = x0 + wx, gy - 7
        d.pieslice((cx - 9, cy - 9, cx + 9, cy + 9), 180, 360, fill='#07050c')
        d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill='#0c0c12')
        d.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill='#6c7888')
        d.rectangle((cx + 2, cy - 4, cx + 3, cy - 1), fill='#d02030')
        for j in range(5):
            a = dist / 7 + j * 2 * math.pi / 5
            d.line((cx, cy, cx + math.cos(a) * 4.5, cy + math.sin(a) * 4.5), fill='#d4dce6')
        d.ellipse((cx - 1, cy - 1, cx + 1, cy + 1), fill='#2a3038')


def draw_xray(d, x0, gy, dist, f):
    d.polygon(cp(x0, gy, CAR), fill=(8, 32, 58, 235), outline='#6ef0ff')
    d.polygon(cp(x0, gy, WIN_R), outline='#3aa8d0')
    d.polygon(cp(x0, gy, WIN_F), outline='#3aa8d0')
    d.line((x0 + 66, gy - 8, x0 + 20, gy - 8), fill='#2a7aa0')          # drive shaft
    for wx in WHEELS:
        cx, cy = x0 + wx, gy - 7
        d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(4, 16, 30, 255), outline='#6ef0ff')
        for j in range(5):
            a = dist / 7 + j * 2 * math.pi / 5
            d.line((cx, cy, cx + math.cos(a) * 5, cy + math.sin(a) * 5), fill='#3aa8d0')
    ex, ey = x0 + 66, gy - 17                                            # glowing inline-4
    d.rectangle((ex, ey, ex + 20, ey + 10), fill='#0e3a5c', outline='#a0f6ff')
    for i in range(4):
        s = math.sin(f * 1.4 + (0, math.pi, math.pi, 0)[i])
        px0, off = ex + 2 + i * 5, round(2 * s)
        if s < -0.7 and (f // 4 + i) % 2 == 0:
            d.rectangle((px0, ey + 1, px0 + 2, ey + 3), fill='#ffb040')
        d.rectangle((px0, ey + 5 + off, px0 + 2, ey + 7 + off), fill='#d8faff')


def street_scene(f, dist, scan=None, speed=1.0):
    t = f / FPS
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
    im = to_im(arr)
    d = ImageDraw.Draw(im)
    for i in range(6):
        x = round((i * 40 - dist) % (W + 40) - 20)
        d.line((x, 304, x + 16, 304), fill='#8a7a4a')
    if speed > 1.2:
        rr = random.Random(f // 2)
        for _ in range(int(8 * (speed - 1))):
            y, x = rr.randint(150, 318), rr.uniform(0, W)
            d.line((x, y, x + rr.randint(8, 24), y), fill='#3a3466')
    by = GY + round(math.sin(f * 0.6) * 0.6)
    car = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    draw_car(ImageDraw.Draw(car), X0, by, dist)
    if scan is not None and scan > 0:
        xr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        draw_xray(ImageDraw.Draw(xr), X0, by, dist, f)
        car.paste(xr.crop((0, 0, int(scan), H)), (0, 0))
    refl = car.transpose(Image.FLIP_TOP_BOTTOM)
    refl.putalpha(refl.getchannel('A').point(lambda v: int(v * 0.33)))
    im.paste(refl, (0, 2 * by - (H - 1)), refl)
    im.paste(car, (0, 0), car)
    if scan is not None and 0 < scan < W:
        d.line((scan, 244, scan, 292), fill='#c8fbff')
        d.line((scan - 2, 244, scan - 2, 292), fill='#2a8ab0')
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
    hx, hy = X0 + 95, by - 13                                              # headlight, beam, tail light
    glow(arr, hx, hy, 18, '#fff0c0', 0.8)
    dx, dy = XX[:, hx:] - hx, YY[:, hx:] - hy
    a = np.clip(0.3 * (1 - dx / 90), 0, 1) * (np.abs(dy) < dx * 0.22 + 1)
    arr[:, hx:] += (np.floor(a * 6 + BAY[:, hx:]) / 6)[..., None] * np.array(hexc('#ffe6a8'), np.float32)
    glow(arr, X0 + 1, by - 13, 14, '#ff2040', 0.7)
    if scan is not None and scan > X0 + 70:
        glow(arr, X0 + 76, by - 12, 18, '#ff8a2a', 0.35 + 0.35 * (f % 4 < 2))
        glow(arr, X0 + 50, by - 14, 50, '#1a9ad0', 0.18)
    if speed > 1.2:
        ln = int(36 * (speed - 1))
        x0 = max(0, X0 - ln)
        if X0 > x0:
            ramp = np.linspace(0, 1, X0 - x0)[None, :, None] * np.array(hexc('#ff2a4a'), np.float32)
            arr[by - 14:by - 12, x0:X0] += ramp * 0.8
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
STROKES = [('INTAKE', '#7aeaff', 'AIR + FUEL RUSH IN'),
           ('COMPRESSION', '#ffd24a', 'THE MIX GETS SQUEEZED'),
           ('POWER', '#ff7a3a', 'SPARK. BOOM. PUSH.'),
           ('EXHAUST', '#c8b8ff', 'BURNT GAS GETS PUSHED OUT')]


def build_engine_bg():
    arr = np.zeros((H, W, 3), np.float32)
    grad_box(arr, 0, 0, W, 246, [(0, '#070b12'), (0.6, '#0d1822'), (1, '#132430')])
    for x in range(15, W, 30):
        arr[0:246, x] *= 0.72
    glow(arr, 90, 130, 120, '#1a4a5a', 0.6)
    glow(arr, 0, 0, 150, '#6a3a14', 0.35)
    grad_box(arr, 0, 246, W, H, [(0, '#0f161d'), (1, '#04070a')])
    arr[246] = hexc('#24323e')
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


def engine_scene(ci, theta, phase):
    th = theta % 720
    py = pin_y(theta)
    crown = int(round(py - 11))
    li, a_in = lift(th, 95)
    le, a_ex = lift(th, 625)
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
    if li > 0.05 and (th < 215 or th > 700):
        for i in range(10):
            p = (flow + i / 10) % 1
            x, y = (2 + p / 0.75 * 74, 91 + math.sin(i * 2.1) * 3) if p < 0.75 else (IN_X + math.sin(i) * 3, 91 + (p - 0.75) / 0.25 * 16)
            d.point((x, y), fill='#9ff0ff')
    if le > 0.05 and 515 < th:
        for i in range(10):
            p = (flow + i / 10) % 1
            x, y = (EX_X + math.sin(i) * 3, 107 - p / 0.25 * 16) if p < 0.25 else (EX_X + (p - 0.25) / 0.75 * 76, 91 + math.sin(i * 2.1) * 3)
            d.point((x, y), fill='#a8a0a4' if i % 2 else '#7a7276')
    if th < 180:                                                       # charge inside the chamber
        n, col = int(len(DOTS) * min(1, th / 150)), hexc('#8ff0ff')
    elif th < 360:
        n, col = len(DOTS), lerp_c('#8ff0ff', '#ffb070', (th - 180) / 180)
    elif th < 540:
        n, col = 0, None
    else:
        n, col = int(len(DOTS) * max(0, 1 - (th - 540) / 165)), hexc('#9a96a0')
    for i in range(n):
        u, v, ph = DOTS[i]
        x = BX0 + 2 + u * (BX1 - BX0 - 4) + math.sin(ci * 0.9 + ph * 20)
        y = CEIL + 2 + v * max(1, crown - CEIL - 4) + math.cos(ci * 0.7 + ph * 17) * 0.8
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
    if 356 <= th < 372:                                                # spark
        r = random.Random(ci)
        x, y = CX, 106
        for _ in range(3):
            nx2 = x + r.randint(-3, 3)
            d.line((x, y, nx2, y + 2), fill='#ffffff')
            x, y = nx2, y + 2
    arr = to_arr(im)
    if li > 0:
        glow(arr, 60, 92, 46, '#1ac8ff', 0.3 * li)
    if 180 <= th < 360:
        glow(arr, CX, (CEIL + crown) / 2, 26, '#ff8a3a', 0.3 * (th - 180) / 180)
    if 356 <= th < 372:
        glow(arr, CX, 106, 34, '#e8f4ff', 1.0)
    if burning:
        k = (1 - (th - 360) / 185) ** 1.5
        glow(arr, CX, CEIL + 10, 170, '#ff6a20', 0.5 * k)
        glow(arr, CX, (CEIL + crown) / 2, 40, '#ffd27a', 0.7 * k)
    hm = min(1.0, (th - 540) / 40) if th >= 540 else max(0.0, 1 - th / 120)
    glow(arr, 150, 92, 40, '#ff5a1a', 0.5 * hm)                        # header glows after exhaust
    n = H - 246                                                        # floor reflection
    arr[246:] += arr[246 - n:246][::-1] * (0.24 * (1 - np.arange(n) / n))[:, None, None]
    if 360 <= th < 376 and phase == 'slow':
        arr = np.roll(arr, (ci % 2) * 2 - 1, axis=1)
    elif phase == 'rev':
        arr = np.roll(arr, ci % 2, axis=0)
    return arr


def engine_ui(im, ci, theta, phase):
    t = ci / FPS
    d = ImageDraw.Draw(im)
    if phase == 'intro':
        text(im, 'HOW IT WORKS', 8, 2, '#ffd24a')
        labels = [(0.1, 'SPARK PLUG', 100, 30, 94, 42, '#ffd24a'),
                  (0.4, 'VALVES', 4, 62, 72, 90, '#7aeaff'),
                  (0.7, 'PISTON', 4, 126, 66, 120, '#e8eef4'),
                  (1.0, 'CRANKSHAFT', 118, 200, 100, 192, '#e0a040')]
        for t0, s, x, y, lx, ly, c in labels:
            if t >= t0:
                ax = x + len(s) * 6 if x < CX else x - 2
                d.line((ax, y + 3, lx, ly), fill=c)
                text(im, s, y, 1, c, x=x)
    elif phase == 'slow':
        s = int((theta % 720) // 180)
        name, col, sub = STROKES[s]
        text(im, name, 8, 2, col)
        text(im, sub, 26, 1, '#e6ecf4')
        if 360 <= theta < 420:
            text(im, 'BANG!', 38, 2, '#ffd24a', x=120 + (ci % 2))
    else:
        text(im, '3000 RPM', 8, 2, '#ff7a3a')
        text(im, 'X 4 CYLINDERS = 100 BANGS/S', 26, 1, '#e6ecf4')
    for i in range(4):
        x0, col = 14 + i * 39, STROKES[i][1]
        d.rectangle((x0, 304, x0 + 34, 306), fill='#141c26')
        if phase == 'slow':
            cur = int((theta % 720) // 180)
            fill = 1.0 if i < cur else ((theta % 180) / 180 if i == cur else 0)
        else:
            fill = 0.0 if phase == 'intro' else 1.0
        if fill > 0:
            d.rectangle((x0, 304, x0 + 34 * fill, 306), fill=col)


# ---------------------------------------------------------------- timeline
T_HOOK, SCAN_T, T_ZOOM, T_B = 2.8, (2.9, 4.0), 4.4, 5.0
N_B = int(T_B * FPS)
DIS_F = 9                                    # pixel dissolve: street zoom -> engine
C_INTRO, SLOW_W = 1.6, 50.0                  # labels, then 3.6s per stroke
N_E, LOOP_F = int(4.3 * FPS), 12             # outro drive, dissolve back to frame 0


def engine_timeline():
    thetas, phases = [], []
    th, f, rs = 0.0, 0, None
    while True:
        t = f / FPS
        if rs is None:
            w = SLOW_W * smooth((t - C_INTRO) / 0.3) if t >= C_INTRO else 0.0
            ph = 'intro' if t < C_INTRO else 'slow'
            if th >= 720:
                rs = t
        if rs is not None:
            u = t - rs
            if u >= 2.4:
                break
            w, ph = SLOW_W + (1100 - SLOW_W) * smooth(u / 1.6), 'rev'
        thetas.append(th)
        phases.append(ph)
        th += w / FPS
        f += 1
    return thetas, phases


THETAS, PHASES = engine_timeline()
N_C = len(THETAS)
TOTAL = N_B + N_C + N_E
DIST = [1.8 * f for f in range(N_B)]
_d, OUT_DIST, OUT_SPEED = DIST[-1], [], []
for _e in range(N_E):
    _v = 1.8 + 5.0 * smooth(_e / FPS / 1.8)
    _d += _v
    OUT_DIST.append(_d)
    OUT_SPEED.append(_v / 1.8)


def zoom(img, u):
    z = 1 + 4 * u * u
    bw, bh = W / z, H / z
    x0 = min(max(X0 + 76 - bw / 2, 0), W - bw)
    y0 = min(max(GY - 12 - bh / 2, 0), H - bh)
    crop = Image.fromarray(img).crop((round(x0), round(y0), round(x0 + bw), round(y0 + bh)))
    return np.asarray(crop.resize((W, H), Image.NEAREST))


def street_frame(f):
    t = f / FPS
    scan = W * smooth((t - SCAN_T[0]) / (SCAN_T[1] - SCAN_T[0])) if t >= SCAN_T[0] else None
    img = post(street_scene(f, DIST[f], scan), f)
    if t >= T_ZOOM:
        return zoom(img, smooth((t - T_ZOOM) / (T_B - T_ZOOM)))
    im = Image.fromarray(img)
    if t < T_HOOK:
        text(im, '100 EXPLOSIONS', 12, 2, '#ff8a3a')
        text(im, 'EVERY SECOND', 30, 2, '#ffe07a')
        text(im, 'INSIDE YOUR ENGINE', 50, 1, '#f0f0ff')
        text(im, '4 CYLINDERS AT 3000 RPM', 60, 1, '#8a8ab8')
    else:
        text(im, 'LOOK INSIDE', 12, 2, '#7aeaff')
        d = ImageDraw.Draw(im)
        for (x, y, sx, sy) in ((32, 246, 1, 1), (148, 246, -1, 1), (32, 290, 1, -1), (148, 290, -1, -1)):
            d.line((x, y, x + 7 * sx, y), fill='#6ef0ff')
            d.line((x, y, x, y + 7 * sy), fill='#6ef0ff')
        if (f // 8) % 2 == 0:
            text(im, 'X-RAY', 236, 1, '#6ef0ff', x=34)
    return np.asarray(im)


def frame(fi, cache):
    if fi < N_B:
        return street_frame(fi)
    ci = fi - N_B
    if ci < N_C:
        img = post(engine_scene(ci, THETAS[ci], PHASES[ci]), fi)
        im = Image.fromarray(img)
        engine_ui(im, ci, THETAS[ci], PHASES[ci])
        img = np.asarray(im)
        if ci < DIS_F:
            if 'zoom' not in cache:
                cache['zoom'] = street_frame(N_B - 1)
            img = dissolve(cache['zoom'], img, (ci + 1) / (DIS_F + 1))
        return img
    ei = ci - N_C
    img = post(street_scene(N_B + ei, OUT_DIST[ei], None, OUT_SPEED[ei]), fi)
    im = Image.fromarray(img)
    text(im, 'SUCK. SQUEEZE.', 12, 2, '#7aeaff')
    text(im, 'BANG. BLOW.', 30, 2, '#ff8a3a')
    text(im, 'FOLLOW FOR PART 2', 50, 1, '#ffe07a')
    img = np.asarray(im)
    if ei >= N_E - LOOP_F:                                             # loop back to the hook
        if 'first' not in cache:
            cache['first'] = street_frame(0)
        img = dissolve(img, cache['first'], (ei - (N_E - LOOP_F) + 1) / (LOOP_F + 1))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out/engine-film.mp4')
    ap.add_argument('--poster', default='out/engine-film-poster.png')
    ap.add_argument('--sheet', help='write a QA contact sheet and exit')
    args = ap.parse_args()
    cache = {}
    if args.sheet:
        picks = [int(s * FPS) for s in (0, 1.5, 3.3, 3.8, 4.7, 5.1, 6.0, 8.5, 12.0, 15.6, 16.0, 19.5, 22.0, 24.5)]
        picks = [p for p in picks if p < TOTAL] + [TOTAL - 5]
        tiles = [Image.fromarray(frame(p, cache)) for p in picks]
        cols = 8
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * W, rows * H))
        for i, tl in enumerate(tiles):
            sheet.paste(tl, ((i % cols) * W, (i // cols) * H))
        Path(args.sheet).parent.mkdir(parents=True, exist_ok=True)
        sheet.resize((cols * W * 2, rows * H * 2), Image.NEAREST).save(args.sheet)
        print('sheet', args.sheet, 'frames', TOTAL, 'duration %.1fs' % (TOTAL / FPS), 'picks', picks)
        return
    if not shutil.which('ffmpeg'):
        raise SystemExit('FFmpeg not found. Install FFmpeg first.')
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(frame(int(3.6 * FPS), cache)).resize((W * SCALE, H * SCALE), Image.NEAREST).save(args.poster)
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an',
           '-vf', f'scale={W * SCALE}:{H * SCALE}:flags=neighbor,format=yuv420p', '-c:v', 'libx264',
           '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(dest)]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as p:
        try:
            assert p.stdin
            for fi in range(TOTAL):
                p.stdin.write(np.ascontiguousarray(frame(fi, cache)).tobytes())
        finally:
            if p.stdin:
                p.stdin.close()
        if p.wait() != 0:
            raise SystemExit('FFmpeg failed')
    print(f'Created {dest} ({TOTAL} frames, {TOTAL / FPS:.1f}s, silent) / {args.poster}')


if __name__ == '__main__':
    main()
