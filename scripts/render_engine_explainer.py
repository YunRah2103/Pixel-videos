#!/usr/bin/env python3
"""Four-stroke engine explainer in pixel art (silent, voiceover-ready).

Original procedural art: Pillow draws 360x640 frames, FFmpeg upscales them 3x with
nearest-neighbour to 1080x1920. Everything is driven by the crank angle (theta) so
pistons, valves, cams, gas, spark and wheels stay mechanically in sync. No audio track
is written on purpose; add your voiceover afterwards.

Usage: python3 scripts/render_engine_explainer.py --out out/engine-explainer.mp4
       python3 scripts/render_engine_explainer.py --sheet out/engine-sheet.png   # QA contact sheet
"""
from __future__ import annotations
import argparse
import math
import random
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

W, H, FPS = 360, 640, 30
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

# ---------------------------------------------------------------- geometry
CX, CY = 180, 292            # crankshaft centre
R, L = 28, 60                # crank radius, rod length (stroke = 2R)
BORE_X0, BORE_X1 = 151, 208  # piston / chamber inner x range
CEIL = 173                   # combustion chamber ceiling
INTAKE_X, EXHAUST_X = 158, 202

STEEL = ['#1c2c3d', '#2c4560', '#3d5f80', '#6a8fae']
DARK = '#0a131d'
STAGES = [
    ('INTAKE', '#6fe0ff', ['PISTON MOVES DOWN', 'INTAKE VALVE OPENS', 'AIR + FUEL FLOW IN']),
    ('COMPRESSION', '#ffd35a', ['BOTH VALVES CLOSE', 'PISTON SQUEEZES MIX', 'TIGHT + HOT = POWER']),
    ('POWER', '#ff7a45', ['SPARK PLUG FIRES', 'BLAST PUSHES PISTON', 'THIS MAKES THE POWER']),
    ('EXHAUST', '#b9a8e8', ['EXHAUST VALVE OPENS', 'PISTON PUSHES GAS OUT', 'THEN IT ALL REPEATS']),
]
PIPS = ['INTAKE', 'SQUEEZE', 'POWER', 'EXHAUST']
FIRE = ['#3a0f1c', '#8c2418', '#d8461f', '#ff8a2e', '#ffc94a', '#fff0b0']

# ---------------------------------------------------------------- 5x7 pixel font
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
    '/': '....#/....#/...#./..#../.#.../#..../#....', ':': '...../.##../.##../...../.##../.##../.....',
    '>': '#..../.#.../..#../...#./..#../.#.../#....', '!': '..#../..#../..#../..#../..#../...../..#..',
    '?': '.###./#...#/....#/...#./..#../...../..#..', '%': '##..#/##..#/...#./..#../.#.../#..##/#..##',
    '°': '.#.../#.#../.#.../...../...../...../.....',
}
FONT = {k: [row for row in v.split('/')] for k, v in _G.items()}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def text(d, s, x, y, scale=1, color='#ffffff', center=False, shadow=True):
    if center:
        x = (W - text_w(s, scale)) // 2
    for layer in ((scale, '#050b12'), (0, color)) if shadow else ((0, color),):
        off, col = layer
        cx = x + off
        for ch in s:
            for ry, row in enumerate(FONT.get(ch, FONT[' '])):
                for rx, c in enumerate(row):
                    if c == '#':
                        d.rectangle((cx + rx * scale, y + off + ry * scale,
                                     cx + rx * scale + scale - 1, y + off + ry * scale + scale - 1), fill=col)
            cx += 6 * scale


def rect(d, x0, y0, x1, y1, c):
    d.rectangle((round(x0), round(y0), round(x1), round(y1)), fill=c)


def lerp_c(a, b, k):
    a = tuple(int(a[i:i + 2], 16) for i in (1, 3, 5)); b = tuple(int(b[i:i + 2], 16) for i in (1, 3, 5))
    return tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))


def hexrgb(c):
    return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def bevel(d, x0, y0, x1, y1, base=1):
    rect(d, x0, y0, x1, y1, STEEL[base])
    rect(d, x0, y0, x1, y0, STEEL[3]); rect(d, x0, y0, x0, y1, STEEL[2])
    rect(d, x0, y1, x1, y1, STEEL[0]); rect(d, x1, y0, x1, y1, STEEL[0])


# ---------------------------------------------------------------- static layers
def build_static() -> Image.Image:
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    stops = [(0, '#09111f'), (260, '#112a43'), (520, '#16384f'), (H, '#0c1a2a')]
    px = img.load()
    for y in range(H):
        for i in range(len(stops) - 1):
            if stops[i][0] <= y <= stops[i + 1][0]:
                (y0, c0), (y1, c1) = stops[i], stops[i + 1]
                f = (y - y0) / (y1 - y0)
                a, b = hexrgb(c0), hexrgb(c1)
                for x in range(W):
                    k = f * 4 + 0 * x
                    t = BAYER[y % 4][x % 4] / 16
                    px[x, y] = b if f > t else a
                break
    for x in range(0, W, 24):                      # blueprint grid
        for y in range(0, 392):
            if (x // 24 + y) % 2 == 0:
                px[x, y] = (22, 52, 78)
    for y in range(0, 392, 24):
        for x in range(0, W):
            if (x // 24 + y) % 2 == 0:
                px[x, y] = (22, 52, 78)
    # intake (cool) + exhaust (warm) manifolds
    for (x0, x1, tint) in ((0, 112, 0), (248, 359, 1)):
        bevel(d, x0, 134, x1, 166, 1)
        rect(d, x0, 140, x1, 160, DARK)
        if tint:
            rect(d, x0, 134, x1, 134, '#7a5a54'); rect(d, x0, 166, x1, 166, '#3a2420')
    # head, cam housing
    bevel(d, 110, 96, 250, 172, 1)
    rect(d, 130, 90, 230, 96, STEEL[2]); rect(d, 130, 90, 230, 90, STEEL[3])
    rect(d, 140, 102, 220, 127, DARK)
    for x in range(114, 248, 6):
        rect(d, x, 98, x, 100, STEEL[0])
    # block with cooling fins
    bevel(d, 120, 172, 240, 352, 1)
    for y in range(184, 262, 7):
        rect(d, 120, y, 131, y, STEEL[0]); rect(d, 229, y, 240, y, STEEL[0])
        rect(d, 120, y + 1, 131, y + 1, STEEL[2]); rect(d, 229, y + 1, 240, y + 1, STEEL[2])
    rect(d, BORE_X0 - 1, CEIL, BORE_X1 + 1, 268, DARK)         # bore
    rect(d, 134, 268, 226, 350, DARK)                           # crankcase cavity
    rect(d, 116, 350, 244, 368, STEEL[0]); rect(d, 116, 350, 244, 350, STEEL[2])
    for x in range(124, 240, 12):
        rect(d, x, 358, x + 2, 358, STEEL[1])
    # ports: intake channel + valve columns re-carved dark
    rect(d, 0, 140, 168, 160, DARK)
    rect(d, 192, 140, 359, 160, DARK)
    rect(d, 148, 140, 168, CEIL - 1, DARK)
    rect(d, 192, 140, 212, CEIL - 1, DARK)
    return img


STATIC = build_static()


# ---------------------------------------------------------------- engine dynamics
def lift(theta, mid):
    a = math.radians(((theta - mid + 360) % 720) - 360) / 2          # cam angle, half crank speed
    return max(0.0, min(1.0, (math.cos(a) - 0.6) / 0.4)), a


def piston_pin_y(theta):
    t = math.radians(theta)
    return CY - (R * math.cos(t) + math.sqrt(L * L - (R * math.sin(t)) ** 2))


_rng = random.Random(7)
DOTS = [(_rng.random(), _rng.random(), _rng.random()) for _ in range(46)]


def draw_cam(d, cx, a, color):
    cy = 114
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=hexrgb('#c8d3dc'))
    pts = [(cx, cy)]
    for k in range(-5, 6):
        ang = math.pi / 2 + a + math.radians(k * 6)
        pts.append((cx + math.cos(ang) * 12, cy + math.sin(ang) * 12))
    d.polygon(pts, fill=hexrgb(color))
    d.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=hexrgb('#0a131d'))


def draw_engine(img, f, theta):
    d = ImageDraw.Draw(img)
    px = img.load()
    th = theta % 720
    pin_y = piston_pin_y(theta)
    crown = int(round(pin_y - 14))
    li, a_in = lift(th, 95)
    le, a_ex = lift(th, 625)
    stage = int(th // 180)

    # ---- gas
    if th < 180:
        n = int(len(DOTS) * min(1, th / 150)); col = '#7fe8ff'
    elif th < 360:
        n = len(DOTS); col = lerp_c('#7fe8ff', '#ffb070', (th - 180) / 180)
    elif th < 540:
        n = len(DOTS); col = '#ff9a3a'
    else:
        n = int(len(DOTS) * max(0, 1 - (th - 540) / 165)); col = '#9aa6b2'
    col = col if isinstance(col, tuple) else hexrgb(col)
    top, bottom = CEIL + 2, crown - 1
    if 360 <= th < 540 or (th >= 540 and th < 556):
        s = (th - 360) / 180
        front = 110 * min(1.0, max(0.0, (th - 362) / 22))
        for y in range(CEIL, max(CEIL, crown)):
            for x in range(BORE_X0, BORE_X1 + 1):
                dd = math.hypot(x - 180, y - CEIL)
                if dd < front:
                    heat = max(0.0, (1 - s ** 0.8 * 0.95)) * (1.15 - min(1, dd / 90) * 0.85)
                    v = heat * 5
                    i = int(v + BAYER[y % 4][x % 4] / 16)
                    px[x, y] = hexrgb(FIRE[max(0, min(5, i))])
    if not (360 <= th < 520):
        for i in range(n):
            u, v, ph = DOTS[i]
            jx = math.sin(f * 0.9 + ph * 20) * (0.8 + (th % 360 > 200) * 0.7)
            jy = math.cos(f * 0.7 + ph * 17) * 0.8
            x = BORE_X0 + 2 + u * (BORE_X1 - BORE_X0 - 5) + jx
            y = top + v * max(2, bottom - top - 2) + jy
            if y < bottom - 1:
                rect(d, x, y, x + 1, y + 1, col)

    # ---- gas in ports
    flow = theta / 180
    if li > 0.05 and (th < 215 or th > 700):
        for i in range(8):
            p = (flow * 1.0 + i / 8) % 1
            if p < 0.72:
                x, y = 4 + p / 0.72 * 150, 150 + math.sin(i * 2.1) * 3
            else:
                x, y = 158 + math.sin(i) * 3, 150 + (p - 0.72) / 0.28 * 28
            rect(d, x, y, x + 1, y + 1, '#7fe8ff')
    if le > 0.05 and 515 < th <= 720:
        for i in range(8):
            p = (flow * 1.0 + i / 8) % 1
            if p < 0.3:
                x, y = 202 + math.sin(i) * 3, 176 - p / 0.3 * 26
            else:
                x, y = 202 + (p - 0.3) / 0.7 * 154, 150 + math.sin(i * 2.1) * 3
            rect(d, x, y, x + 1, y + 1, '#aab4c4' if i % 2 else '#7c8696')

    # ---- valves + cams
    for cx, l, a, color in ((INTAKE_X, li, a_in, '#6fe0ff'), (EXHAUST_X, le, a_ex, '#d0a070')):
        hy = CEIL + 5 * l
        rect(d, cx - 1, 121 + 5 * l, cx, hy, '#d4dde4')
        rect(d, cx - 9, hy, cx + 9, hy + 2, '#c9d3da'); rect(d, cx - 6, hy - 1, cx + 6, hy - 1, '#c9d3da')
        draw_cam(d, cx, a, color)

    # ---- spark plug + spark
    rect(d, 177, 84, 183, 92, '#dfe8ee'); rect(d, 178, 79, 182, 83, '#8aa0b0')
    rect(d, 178, 93, 182, 172, '#b8c6d0'); rect(d, 178, 93, 178, 172, '#e6eef3')
    rect(d, 179, 172, 181, 175, '#3a4652')
    if 358 <= th < 374:
        r = random.Random(f)
        x, y = 180, 175
        for _ in range(4):
            nx, ny = x + r.randint(-6, 6), y + 4
            d.line((x, y, nx, ny), fill=hexrgb('#ffffff')); x, y = nx, ny
        d.ellipse((176, 171, 184, 179), outline=hexrgb('#fff0a0'))

    # ---- piston
    rect(d, BORE_X0, crown, BORE_X1, crown + 24, '#aebcc8')
    rect(d, BORE_X0, crown, BORE_X1, crown + 2, '#e8eff4')
    rect(d, BORE_X0, crown + 14, BORE_X1, crown + 24, '#93a4b2')
    for ry in (crown + 5, crown + 8):
        rect(d, BORE_X0, ry, BORE_X1, ry, '#5b6c7a')
    rect(d, BORE_X1 - 2, crown, BORE_X1, crown + 24, '#7a8c9a')
    d.ellipse((CX - 4, pin_y - 4, CX + 4, pin_y + 4), fill=hexrgb('#27323d'))
    if 360 <= th < 470 or (th >= 360 and th < 520 and f % 6 < 3 and th < 500):   # pressure chevrons
        for k in range(3):
            cxk = 164 + k * 16
            d.polygon([(cxk - 3, crown + 3 + 0), (cxk + 3, crown + 3), (cxk, crown + 7)], fill=hexrgb('#fff0a0'))

    # ---- crank + rod
    t = math.radians(th)
    pinx, piny = CX + R * math.sin(t), CY - R * math.cos(t)
    dx, dy = pinx - CX, piny - pin_y
    ln = math.hypot(dx, dy); nx, ny = -dy / ln * 3, dx / ln * 3
    d.polygon([(CX + nx, pin_y + ny), (CX - nx, pin_y - ny), (pinx - nx, piny - ny), (pinx + nx, piny + ny)],
              fill=hexrgb('#8fa4b3'))
    d.line((CX, pin_y, pinx, piny), fill=hexrgb('#c4d2dc'))
    wx, wy = -math.sin(t), math.cos(t)
    d.polygon([(CX - wy * 4, CY + wx * 4), (CX + wy * 4, CY - wx * 4),
               (pinx + wy * 4, piny - wx * 4), (pinx - wy * 4, piny + wx * 4)], fill=hexrgb('#3d5f80'))
    cwx, cwy = CX + wx * 12, CY + wy * 12
    d.ellipse((cwx - 10, cwy - 10, cwx + 10, cwy + 10), fill=hexrgb('#4c7497'))
    d.ellipse((cwx - 7, cwy - 7, cwx + 3, cwy + 3), fill=hexrgb('#6a96b8'))
    d.ellipse((CX - 8, CY - 8, CX + 8, CY + 8), fill=hexrgb('#c2d0da'))
    d.ellipse((CX - 3, CY - 3, CX + 3, CY + 3), fill=hexrgb('#27323d'))
    d.ellipse((pinx - 7, piny - 7, pinx + 7, piny + 7), fill=hexrgb('#f0a040'))
    d.ellipse((pinx - 3, piny - 3, pinx + 3, piny + 3), fill=hexrgb('#7a4a10'))

    # ---- direction arrow beside block
    return stage


def draw_arrow(d, up, color):
    x, y = 96, 232
    pts = [(x, y - 14), (x - 8, y), (x - 3, y), (x - 3, y + 14), (x + 3, y + 14), (x + 3, y), (x + 8, y)] if up else \
          [(x, y + 14), (x - 8, y), (x - 3, y), (x - 3, y - 14), (x + 3, y - 14), (x + 3, y), (x + 8, y)]
    d.polygon(pts, fill=hexrgb(color))


# ---------------------------------------------------------------- car + road
def draw_car(img, f, theta, speed):
    d = ImageDraw.Draw(img)
    rect(d, 0, 604, W, 640, '#0d141d'); rect(d, 0, 604, W, 605, '#27384a')
    off = int(theta * 0.18) % 48
    for x in range(-48, W + 48, 48):
        rect(d, x - off, 624, x - off + 24, 625, '#46627e')
    cx, cy = 110, 604
    body, shade = '#d6453d', '#9e2f2f'
    rect(d, cx, cy - 22, cx + 118, cy - 6, body)
    d.polygon([(cx + 22, cy - 22), (cx + 36, cy - 38), (cx + 82, cy - 38), (cx + 100, cy - 22)], fill=hexrgb(body))
    d.polygon([(cx + 38, cy - 34), (cx + 58, cy - 34), (cx + 58, cy - 24), (cx + 28, cy - 24)], fill=hexrgb('#9fdcff'))
    d.polygon([(cx + 62, cy - 34), (cx + 80, cy - 34), (cx + 92, cy - 24), (cx + 62, cy - 24)], fill=hexrgb('#7cc4ee'))
    rect(d, cx, cy - 10, cx + 118, cy - 6, shade)
    rect(d, cx + 112, cy - 18, cx + 118, cy - 14, '#ffe27a'); rect(d, cx, cy - 18, cx + 3, cy - 14, '#ff5a5a')
    rect(d, cx - 5, cy - 9, cx - 1, cy - 7, '#3a4652')                       # exhaust pipe
    for wx in (cx + 24, cx + 94):
        d.ellipse((wx - 11, cy - 20, wx + 11, cy + 2), fill=hexrgb('#0d141d'))
        d.ellipse((wx - 8, cy - 17, wx + 8, cy - 1), fill=hexrgb('#26323f'))
        a = math.radians(theta * 0.6)
        for k in range(4):
            ang = a + k * math.pi / 2
            d.line((wx, cy - 9, wx + math.cos(ang) * 7, cy - 9 + math.sin(ang) * 7), fill=hexrgb('#b7c4d0'))
        d.ellipse((wx - 2, cy - 11, wx + 2, cy - 7), fill=hexrgb('#b7c4d0'))
    if speed > 0.25:                                                          # speed lines + puffs
        r = random.Random(f // 2)
        for _ in range(int(6 * speed)):
            y = r.randint(560, 600); x = r.randint(250, 355)
            rect(d, x, y, x + r.randint(10, 26), y, '#4a7090')
        for k in range(4):
            p = ((f * 0.05 * (0.5 + speed)) + k / 4) % 1
            rect(d, cx - 8 - p * 40, cy - 9 - p * 10, cx - 6 - p * 40 + k % 2, cy - 7 - p * 10, lerp_c('#98a4b0', '#1a2430', p))


# ---------------------------------------------------------------- UI
def draw_labels(d, t):
    items = [(1.1, 'SPARK PLUG', 226, 86, 184, 90, '#ffd35a'),
             (1.5, 'VALVES', 14, 106, 152, 142, '#6fe0ff'),
             (1.9, 'PISTON', 16, 214, 152, 222, '#e8eff4'),
             (2.3, 'CYLINDER', 262, 196, 240, 200, '#6a8fae'),
             (2.7, 'CRANKSHAFT', 252, 308, 214, 294, '#f0a040')]
    for t0, s, x, y, lx, ly, c in items:
        if t > t0:
            tx = x if x < 180 else x
            ax = x + (text_w(s, 1) if x < 180 else 0)
            d.line((ax if x < 180 else x - 2, y + 3, lx, ly), fill=hexrgb(c))
            d.rectangle((lx - 1, ly - 1, lx + 1, ly + 1), fill=hexrgb(c))
            text(d, s, tx, y, 1, c)


def draw_ui(img, f, t, th, ph, rs):
    d = ImageDraw.Draw(img)
    # title
    if t < 3.2:
        text(d, 'HOW AN ENGINE', 0, 14, 3, '#ffd35a', center=True)
        text(d, 'WORKS', 0, 40, 3, '#ffd35a', center=True)
        text(d, '4-STROKE CYCLE', 0, 66, 1, '#6fe0ff', center=True)
        draw_labels(d, t)
    else:
        text(d, 'HOW AN ENGINE WORKS', 0, 12, 2, '#ffd35a', center=True)
        text(d, 'THE 4-STROKE CYCLE', 0, 34, 1, '#6fe0ff', center=True)
    slow = ph == 'slow'
    if slow:
        text(d, 'CRANK ANGLE %03d%s' % (int(th), '°'), 0, 52, 1, '#8fb0cc', center=True)
        s = int(th // 180)
        name, col, lines = STAGES[s]
        draw_arrow(d, s in (1, 3), col)
    elif ph == 'ramp':
        draw_arrow(d, int(th // 180) % 2 == 1, '#ffffff')
    # bottom panel
    if ph == 'intro':
        text(d, 'ENGINE OFF', 0, 404, 3, '#8fb0cc', center=True)
        for i, ln in enumerate(['A CYLINDER, A PISTON,', 'TWO VALVES, A SPARK PLUG', 'AND A CRANKSHAFT']):
            text(d, ln, 0, 440 + i * 18, 2, '#cfe3f3', center=True)
    elif slow:
        text(d, name, 0, 404, 3, col, center=True)
        for i, ln in enumerate(lines):
            text(d, ln, 0, 440 + i * 18, 2, '#e8f2fb', center=True)
    elif ph == 'ramp1':
        text(d, 'SPEED IT UP', 0, 404, 3, '#ffd35a', center=True)
        for i, ln in enumerate(['SAME 4 STROKES', 'AGAIN AND AGAIN', 'FASTER AND FASTER']):
            text(d, ln, 0, 440 + i * 18, 2, '#e8f2fb', center=True)
    elif ph == 'ramp2':
        text(d, 'EVERY MINUTE', 0, 404, 3, '#ff7a45', center=True)
        for i, ln in enumerate(['THE CRANKSHAFT SPINS', '1,000 TO 6,000 TIMES', 'FROM TINY BLASTS']):
            text(d, ln, 0, 440 + i * 18, 2, '#e8f2fb', center=True)
    else:
        text(d, 'SUCK SQUEEZE', 0, 398, 3, '#6fe0ff', center=True)
        text(d, 'BANG BLOW', 0, 424, 3, '#ff7a45', center=True)
        text(d, 'ONE POWER BURST', 0, 456, 2, '#e8f2fb', center=True)
        text(d, 'EVERY 4 STROKES', 0, 474, 2, '#e8f2fb', center=True)
    # progress pips
    for i in range(4):
        x0 = 30 + i * 75
        col = STAGES[i][1]
        rect(d, x0, 504, x0 + 68, 511, '#15283b')
        rect(d, x0, 504, x0 + 68, 504, '#27425c')
        if slow:
            cur = int(th // 180)
            fill = 1.0 if i < cur else (((th % 180) / 180) if i == cur else 0)
        elif ph == 'intro':
            fill = 0
        else:
            fill = 1.0
        if fill > 0:
            rect(d, x0, 504, x0 + 68 * fill, 511, col)
        on = (slow and i == int(th // 180)) or ph not in ('slow', 'intro')
        text(d, PIPS[i], x0 + (68 - text_w(PIPS[i], 1)) // 2, 516, 1, col if on else '#4f6a84')


# ---------------------------------------------------------------- timeline
def build_timeline():
    thetas, phases = [], []
    th, f, rs = 0.0, 0, None
    while True:
        t = f / FPS
        if rs is None:
            w = 36 * smooth((t - 3.2) / 0.5) if t >= 3.2 else 0.0
            ph = 'intro' if t < 3.2 else 'slow'
            if th >= 720:
                rs = t
        if rs is not None:
            u = t - rs
            if u < 6.5:
                w = 36 + (900 - 36) * smooth(u / 4.0)
                ph = 'ramp1' if u < 3.2 else 'ramp2'
            else:
                w = 900 - 750 * smooth((u - 6.5) / 2.5)
                ph = 'end'
            if u > 10.2:
                break
        thetas.append(th); phases.append(ph)
        th += w / FPS; f += 1
    return thetas, phases, rs


def render(f, thetas, phases, rs):
    th, ph = thetas[f], phases[f]
    t = f / FPS
    img = STATIC.copy()
    draw_engine(img, f, th)
    speed = 0 if ph in ('intro', 'slow') else min(1.0, (th - thetas[max(0, f - 1)]) * FPS / 700)
    draw_car(img, f, th, speed)
    d = ImageDraw.Draw(img)
    # engine vibration while running fast, one-frame punch at ignition
    if ph in ('ramp1', 'ramp2', 'end'):
        k = min(1.0, (th - thetas[max(0, f - 1)]) * FPS / 700)
        dx, dy = (1 if f % 2 else 0), (1 if (f // 2) % 2 else 0)
        if k > 0.35:
            region = img.crop((0, 60, W, 380))
            img.paste(region, (dx, 60 + dy))
    elif ph == 'slow' and 361 <= th % 720 < 369:
        region = img.crop((0, 60, W, 380)); img.paste(region, (0, 61))
    draw_ui(img, f, t, th, ph, rs)
    fade = min(1.0, t / 0.4)
    if fade < 1:
        img = Image.eval(img, lambda v: int(v * fade))
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out/engine-explainer.mp4')
    ap.add_argument('--poster', default='out/engine-explainer-poster.png')
    ap.add_argument('--sheet', help='write a QA contact sheet and exit')
    args = ap.parse_args()
    thetas, phases, rs = build_timeline()
    total = len(thetas)
    if args.sheet:
        picks = [30, 75, 120, 200, 270, 330, 390, 450, 520, 600, 700, 850, int(rs * FPS) + 60, int(rs * FPS) + 150,
                 total - 80, total - 15]
        picks = [p for p in picks if p < total]
        tiles = [render(p, thetas, phases, rs) for p in picks]
        cols = 8
        rows = (len(tiles) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * W // 2, rows * H // 2))
        for i, tl in enumerate(tiles):
            sheet.paste(tl.resize((W // 2, H // 2), Image.NEAREST), ((i % cols) * W // 2, (i // cols) * H // 2))
        Path(args.sheet).parent.mkdir(parents=True, exist_ok=True)
        sheet.save(args.sheet)
        print('sheet', args.sheet, 'frames', total, 'duration %.1fs' % (total / FPS), 'picks', picks)
        return
    if not shutil.which('ffmpeg'):
        raise SystemExit('FFmpeg not found. Install FFmpeg first.')
    dest = Path(args.out); dest.parent.mkdir(parents=True, exist_ok=True)
    render(int(2.6 * FPS), thetas, phases, rs).save(args.poster)
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-vcodec', 'rawvideo',
           '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an',
           '-vf', 'scale=1080:1920:flags=neighbor,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium',
           '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(dest)]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as p:
        try:
            assert p.stdin
            for f in range(total):
                p.stdin.write(render(f, thetas, phases, rs).tobytes())
        finally:
            if p.stdin:
                p.stdin.close()
        if p.wait() != 0:
            raise SystemExit('FFmpeg failed')
    print(f'Created {dest} ({total} frames, {total / FPS:.1f}s, silent) / {args.poster}')


if __name__ == '__main__':
    main()
