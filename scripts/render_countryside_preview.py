#!/usr/bin/env python3
"""2.5D pixel-art preview: a coupe driving through a golden-hour countryside (silent, ~8s).

True pseudo-3D: every screen row is projected from a world depth, so the road bends away,
fields tile in perspective, and roadside props (poles, fences, trees, farmhouses, hay bales)
scale and parallax by depth. Backlit sun, long pole shadows, haze, god rays, lens flare,
heat shimmer and tyre dust sell the light. Original procedural art only.

Native 270x480, upscaled 4x nearest-neighbour to 1080x1920.
Usage: python3 scripts/render_countryside_preview.py --out out/countryside-preview.mp4
       python3 scripts/render_countryside_preview.py --sheet out/countryside-sheet.png
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

W, H, SCALE, FPS = 270, 480, 4, 30
HY = 205                                    # horizon row
DUR = 8.0
SPEED = 20.0                                # world units per second
SUN = (176, 188)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
YY, XX = np.mgrid[0:H, 0:W]
BAY = BAYER[YY % 4, XX % 4]
HAZE = (255, 214, 150)


def hexc(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, k):
    return tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3))


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def glow(arr, cx, cy, r, color, k=1.0, levels=7, sy=1.0):
    ry = r / sy
    x0, x1 = int(max(cx - r, 0)), int(min(cx + r + 1, W))
    y0, y1 = int(max(cy - ry, 0)), int(min(cy + ry + 1, H))
    if x1 <= x0 or y1 <= y0 or k <= 0:
        return
    d = np.hypot(XX[y0:y1, x0:x1] - cx, (YY[y0:y1, x0:x1] - cy) * sy)
    a = np.clip(1 - d / r, 0, 1) ** 2 * k
    a = np.floor(a * levels + BAY[y0:y1, x0:x1]) / levels
    arr[y0:y1, x0:x1] += a[..., None] * np.array(hexc(color) if isinstance(color, str) else color, np.float32)


# ---------------------------------------------------------------- world model
def curv(zw):
    """Road curvature as a function of world distance: lazy S-bends after a straight start."""
    ramp = np.clip((zw - 14) / 34.0, 0, 1)
    return (0.95 * np.sin(zw / 52.0) + 0.3 * np.sin(zw / 25.0 + 1.0)) * ramp


ROWS = np.arange(HY + 1, H)
U = (ROWS - HY) / (H - HY)                  # 1 at the bottom, ->0 at the horizon
Z = 1.0 / U                                 # depth in "road units" (1 at the bottom of the frame)
ZS = Z[::-1]                                # ascending
DZ = np.diff(np.concatenate([[0.0], ZS]))
ROAD_HALF = 118.0                           # road half-width in px at u = 1


def road_offsets(dist):
    """World lateral offset of the road centre for every ground row (and an interpolator)."""
    c = curv(ZS + dist) * 0.027
    a = np.cumsum(c * DZ)
    b = np.cumsum(c * ZS * DZ)
    xw = ZS * a - b
    return xw[::-1], (lambda z: np.interp(z, ZS, xw))


def sprite_pos(zrel, lat, off_at):
    u = 1.0 / zrel
    return u, W / 2 + (off_at(zrel) + lat) * ROAD_HALF * u, HY + (H - HY) * u


# ---------------------------------------------------------------- sky, hills, clouds
SKY_STOPS = [(0.0, '#1c3672'), (0.32, '#4a78b4'), (0.58, '#d89aa0'), (0.82, '#ffb870'), (1.0, '#ffe2a8')]


def build_sky():
    arr = np.zeros((HY + 8, W, 3), np.float32)
    n = HY + 8
    p = np.array([s[0] for s in SKY_STOPS])
    cols = np.array([hexc(s[1]) for s in SKY_STOPS], np.float32)
    c = np.clip(np.arange(n)[:, None] / HY, 0, 1) * np.ones((1, W))
    idx = np.clip(np.searchsorted(p, c, side='right') - 1, 0, len(p) - 2)
    f = np.clip((c - p[idx]) / (p[idx + 1] - p[idx]), 0, 1)
    arr[:] = cols[idx + (f > BAY[:n])]
    return arr


SKY = build_sky()
_rng = random.Random(4)
CLOUDS = [(_rng.uniform(0, 2 * W), _rng.uniform(38, 150), _rng.uniform(46, 110), _rng.uniform(0.5, 1.2)) for _ in range(11)]
LAYERS = [(150, 24, 0.18, '#a9788e', 0.22, 0.25), (170, 30, 0.32, '#7f6482', 0.14, 0.45),
          (188, 22, 0.55, '#4e5a6a', 0.06, 0.75)]


def hills(arr, shift):
    for base, amp, par, col, hz, f0 in LAYERS:
        xs = (np.arange(W) + shift * par) * 0.022 * (1 + f0 * 0.6)
        top = base - amp * (0.55 * np.sin(xs * 1.0 + f0 * 9) + 0.3 * np.sin(xs * 2.3 + f0 * 4) + 0.18 * np.sin(xs * 5.1)
                            + 0.45)
        m = (YY[:HY + 8] >= np.round(top)[None, :]) & (YY[:HY + 8] < HY + 8)
        c = np.array(mix(hexc(col), HAZE, hz * 1.8), np.float32)
        arr[m] = c
        rim = (YY[:HY + 8] == np.round(top)[None, :])
        arr[rim] = np.array(mix(hexc(col), (255, 205, 130), 0.55), np.float32)


def clouds(img, t, shift):
    d = ImageDraw.Draw(img, 'RGBA')
    for x, y, w, sp in CLOUDS:
        cx = (x + t * 3 * sp + shift * 0.5) % (2 * W) - W * 0.4
        for k in range(5):
            ox = cx + k * w / 5
            rw, rh = w / 3, 3 + (k % 3) * 1.6
            d.ellipse((ox - rw, y - rh, ox + rw, y + rh), fill=(255, 170, 130, 120))
            d.ellipse((ox - rw * 0.9, y - rh * 0.3 - 2, ox + rw * 0.9, y + rh * 0.4 - 1), fill=(255, 226, 170, 170))
            d.ellipse((ox - rw * 0.9, y + rh * 0.35, ox + rw * 0.9, y + rh), fill=(150, 90, 130, 130))


def birds(img, t):
    d = ImageDraw.Draw(img)
    for i in range(5):
        bx = (40 + i * 38 + t * (9 + i)) % (W + 30) - 10
        by = 86 + i * 9 + 5 * math.sin(t * 1.6 + i)
        up = int(t * 7 + i) % 2
        for dx, dy in ((-3, 1 - up), (-2, 0 - up), (-1, 0), (0, 1), (1, 0), (2, 0 - up), (3, 1 - up)):
            d.point((bx + dx, by + dy), fill='#2a1a2e')


# ---------------------------------------------------------------- ground (road + fields)
FIELD = np.array([hexc(c) for c in ('#8cb046', '#b9b94c', '#dcb95a', '#6f9a3a', '#a8884a')], np.float32)
SHADOW_POLES = [n * 30.0 + 8.0 for n in range(0, 400)]


def ground(dist, off_rows):
    R = len(ROWS)
    cx = W / 2 + off_rows * ROAD_HALF * U
    half = ROAD_HALF * U
    lat = (XX[HY + 1:] - cx[:, None]) / half[:, None]
    zw = Z[:, None] + dist
    zw = np.broadcast_to(zw, (R, W))
    a = np.abs(lat)
    fx, fz = lat / 4.2, zw / 16.0
    ix, iz = np.floor(fx).astype(np.int64), np.floor(fz).astype(np.int64)
    idx = ((ix * 7349 + iz * 9157 + ix * iz * 31) % 5 + 5) % 5
    col = FIELD[idx].copy()
    furrow = ((lat * 6.0) % 1.0) < 0.5
    col *= np.where(furrow, 0.9, 1.06)[..., None]
    col *= (1 + 0.05 * ((np.floor(zw / 2.2) % 2) - 0.5))[..., None]
    hedge = (((fx % 1.0) < 0.035) | ((fz % 1.0) < 0.03)) & (a > 1.8)
    col[hedge] = np.array((34, 70, 32), np.float32)
    col[hedge & ((XX[HY + 1:] + YY[HY + 1:]) % 3 == 0)] = np.array((60, 102, 46), np.float32)
    verge = (a >= 1.18) & (a < 1.75)
    col[verge] = np.array((100, 138, 58), np.float32)
    col[(a >= 1.0) & (a < 1.18)] = np.array((146, 126, 96), np.float32)
    road = a < 1.0
    band = ((np.floor(zw / 3.5) % 2) * 5)[..., None]
    col[road] = (np.array((80, 76, 86), np.float32) + band)[road]
    spk = road & (((XX[HY + 1:] * 7 + YY[HY + 1:] * 13) % 11) == 0)
    col[spk] *= 0.86
    col[road & (a > 0.9) & (a < 0.96)] = np.array((228, 222, 204), np.float32)
    col[road & (a < 0.03) & ((zw % 6.0) < 3.0)] = np.array((232, 208, 112), np.float32)
    # long pole shadows streaking toward the camera (the sun is ahead, low)
    for pz in SHADOW_POLES:
        rel = pz - dist
        if rel < 1.5 or rel > 140:
            continue
        m = (zw > pz - 9) & (zw < pz) & (np.abs(lat - (-1.45 + (pz - zw) * 0.2)) < 0.07 + (pz - zw) * 0.004)
        col[m] *= 0.55
    # warm sheen on the asphalt toward the sun + haze with depth
    sheen = (1 - U[:, None]) ** 1.6 * 0.5 * np.clip(1 - a, 0, 1)
    col += sheen[..., None] * np.array((255, 170, 80), np.float32) * road[..., None]
    hf = np.clip(1 - U * 7.0, 0, 0.86) ** 1.25
    hq = np.floor(hf[:, None] * 5 + BAY[HY + 1:]) / 5
    col = col * (1 - hq[..., None]) + np.array(HAZE, np.float32) * hq[..., None]
    return col, cx


# ---------------------------------------------------------------- roadside props
def hazed(c, u):
    return mix(hexc(c) if isinstance(c, str) else c, HAZE, float(np.clip(1 - u * 7.0, 0, 0.86)) ** 1.25)


def tree(d, x, y, u, kind, seed):
    r = random.Random(seed)
    h = (215 if kind == 0 else (300 if kind == 1 else 250)) * u * (0.8 + r.random() * 0.4)
    if h < 2:
        return
    rim, dark, mid = hazed('#f0b45a', u), hazed('#16301a', u), hazed('#274d24', u)
    tw = max(1, round(h * 0.05))
    d.rectangle((x - tw, y - h * 0.34, x + tw, y), fill=hazed('#2a1c18', u))
    if kind == 0:
        blobs = [(0, -0.62, 0.30), (-0.20, -0.52, 0.22), (0.21, -0.54, 0.23), (0, -0.82, 0.22), (-0.13, -0.72, 0.18),
                 (0.14, -0.74, 0.19)]
    elif kind == 1:
        blobs = [(0, -0.30 - k * 0.11, 0.12 + 0.03 * math.sin(k)) for k in range(6)]
    else:
        blobs = [(0, -0.30 - k * 0.12, 0.26 - k * 0.035) for k in range(6)]
    for ox, oy, rr in blobs:
        cx, cy, rad = x + ox * h, y + oy * h, max(1.0, rr * h)
        d.ellipse((cx - rad - 1, cy - rad - 1.4, cx + rad + 1, cy + rad), fill=rim)
    for ox, oy, rr in blobs:
        cx, cy, rad = x + ox * h, y + oy * h, max(1.0, rr * h)
        d.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=dark)
        d.ellipse((cx - rad * 0.55, cy - rad * 0.2, cx + rad * 0.5, cy + rad * 0.8), fill=mid)


def farm(d, x, y, u, seed):
    w, h = 250 * u, 120 * u
    if w < 3:
        return
    d.rectangle((x - w / 2, y - h, x + w / 2, y), fill=hazed('#6a5648', u))
    d.polygon([(x - w / 2 - 2 * u * 10, y - h), (x + w / 2 + 2 * u * 10, y - h), (x, y - h - 70 * u)], fill=hazed('#6e2a2a', u))
    d.line((x - w / 2 - 2, y - h, x, y - h - 70 * u), fill=hazed('#f0b45a', u))
    for k in range(3):
        wx = x - w / 2 + w * (0.2 + 0.3 * k)
        d.rectangle((wx - 6 * u, y - h * 0.7, wx + 6 * u, y - h * 0.4), fill=hazed('#ffcf70', u))


def bale(d, x, y, u):
    r = 42 * u
    if r < 1:
        return
    d.ellipse((x - r, y - r * 1.5, x + r, y), fill=hazed('#c8a040', u))
    d.ellipse((x - r * 0.5, y - r * 1.1, x + r * 0.5, y - r * 0.4), fill=hazed('#e8c860', u))


def props(img, dist, off_at):
    d = ImageDraw.Draw(img)
    items = []
    for n in range(int(dist / 3.0) - 1, int((dist + 130) / 3.0) + 2):
        r = random.Random(n * 997)
        zw = n * 3.0
        if n % 10 == 3:
            items.append((zw, -1.45, 'pole', n))
        if n % 1 == 0:
            items.append((zw, -1.32, 'fp', n))
            items.append((zw, 1.32, 'fp', n))
        if r.random() < 0.55:
            side = r.choice((-1, 1))
            items.append((zw + r.random() * 3, side * r.uniform(1.9, 9.0), 'tree', n))
        if r.random() < 0.3:
            items.append((zw + r.random() * 3, r.choice((-1, 1)) * r.uniform(1.55, 2.5), 'bush', n))
        if r.random() < 0.035:
            items.append((zw, r.choice((-1, 1)) * r.uniform(6.5, 11.0), 'farm', n))
        if r.random() < 0.05:
            items.append((zw, r.choice((-1, 1)) * r.uniform(2.6, 7.0), 'bale', n))
    items.sort(key=lambda it: -it[0])
    poles = []
    for zw, lat, kind, n in items:
        zrel = zw - dist
        if zrel < 1.0 or zrel > 130:
            continue
        u, sx, sy = sprite_pos(zrel, lat, off_at)
        if kind == 'pole':
            hh = 215 * u
            poles.append((zrel, sx, sy - hh))
            c = hazed('#2a1c18', u)
            d.line((sx, sy, sx, sy - hh), fill=c, width=max(1, round(3 * u)))
            d.line((sx - 22 * u, sy - hh + 6 * u, sx + 22 * u, sy - hh + 6 * u), fill=c, width=max(1, round(2.4 * u)))
            d.point((sx - 22 * u, sy - hh + 5 * u), fill=hazed('#f0b45a', u))
        elif kind == 'fp':
            hh = 34 * u
            d.line((sx, sy, sx, sy - hh), fill=hazed('#463024', u), width=max(1, round(2.6 * u)))
            d.point((sx, sy - hh - 1), fill=hazed('#f0b45a', u))
        elif kind == 'tree':
            tree(d, sx, sy, u, n % 3, n * 31 + int(lat * 10))
        elif kind == 'bush':
            rr = max(1.0, 38 * u)
            for k in range(3):
                bx = sx + (k - 1) * rr * 0.9
                d.ellipse((bx - rr - 1, sy - rr * 1.5 - 1.2, bx + rr + 1, sy), fill=hazed('#f0b45a', u))
                d.ellipse((bx - rr, sy - rr * 1.5, bx + rr, sy), fill=hazed('#16301a', u))
                d.ellipse((bx - rr * 0.5, sy - rr * 0.9, bx + rr * 0.5, sy - rr * 0.1), fill=hazed('#274d24', u))
        elif kind == 'farm':
            farm(d, sx, sy, u, n)
        else:
            bale(d, sx, sy, u)
    poles.sort(key=lambda p: -p[0])                              # wires between neighbouring poles
    for (z1, x1, y1), (z2, x2, y2) in zip(poles, poles[1:]):
        for k in (0, 1):
            ya, yb = y1 + 5 * k * (1 / z1) * 14, y2 + 5 * k * (1 / z2) * 14
            mx, my = (x1 + x2) / 2, (ya + yb) / 2 + 7 * (1 / ((z1 + z2) / 2)) * 14
            d.line((x1, ya, mx, my, x2, yb), fill=hazed('#2a1c18', 1 / ((z1 + z2) / 2)))


# ---------------------------------------------------------------- the car (rear 3/4, leaning into the bend)
def gradient_fill(im, poly, box, stops):
    box = tuple(int(round(v)) for v in box)
    h = box[3] - box[1]
    g = Image.new('RGB', (box[2] - box[0], h))
    gd = ImageDraw.Draw(g)
    for y in range(h):
        k = y / max(h - 1, 1)
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            if p0 <= k <= p1:
                gd.line((0, y, g.width, y), fill=mix(hexc(c0), hexc(c1), (k - p0) / (p1 - p0)))
                break
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    layer = Image.new('RGB', im.size)
    layer.paste(g, (box[0], box[1]))
    im.paste(layer, (0, 0), mask)


def car(img, f, t, yaw, bump):
    """Rear 3/4 coupe: fastback glass, haunches, wrap tail lights; shows its flank when it leans into a bend."""
    cx, by = W // 2 + round(yaw * 5), 442 + bump
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((cx - 78, by - 6, cx + 78, by + 10), fill=(10, 6, 20, 130))
    img.paste(sh, (0, 0), sh)
    d = ImageDraw.Draw(img)
    sk = yaw * 9                                                         # roof leans into the turn
    paint = [(0, '#3478c8'), (0.3, '#1a4688'), (0.7, '#0e2552'), (1, '#070f28')]
    for sx in (-1, 1):                                                   # tyres tucked under the haunches
        x0 = cx + sx * 56
        d.rounded_rectangle((x0 - 10, by - 22, x0 + 10, by), 3, fill='#09090e')
        for k in range(4):
            d.line((x0 - 9, by - 18 + k * 5, x0 + 9, by - 18 + k * 5), fill='#181820')
    d.polygon([(cx - 56, by - 24), (cx + 56, by - 24), (cx + 52, by - 6), (cx - 52, by - 6)], fill='#0b0a12')   # diffuser
    for k in range(-5, 6):
        d.line((cx + k * 9, by - 21, cx + k * 9 - k, by - 8), fill='#26243a')
    for sx in (-1, 1):
        ex = cx + sx * 24
        d.ellipse((ex - 6, by - 20, ex + 6, by - 9), fill='#9aa6b4')
        d.ellipse((ex - 4, by - 18, ex + 4, by - 11), fill='#07070b')
    ws = abs(yaw) * 24
    if ws > 1.5:                                                         # flank facing the camera (turn right -> right side)
        s_ = 1 if yaw > 0 else -1
        x1, x2 = cx + s_ * 66, cx + s_ * (66 + ws)
        poly = [(x1, by - 28), (x1, by - 54), (x2, by - 52 - ws * 0.25), (x2, by - 30 - ws * 0.12)]
        gradient_fill(img, poly, (min(x1, x2) - 1, by - 58, max(x1, x2) + 1, by - 22), [(0, '#2a62aa'), (1, '#0a1a40')])
        d.line((x1, by - 54, x2, by - 52 - ws * 0.25), fill='#f4c070')
    for sx in (-1, 1):                                                   # round haunches
        hx = cx + sx * 56
        gradient_fill(img, [(hx - 17 + k * 0, by - 26) for k in range(1)] + [(hx - 17, by - 26), (hx + 17, by - 26),
                      (hx + 15, by - 44), (hx - 15, by - 44)], (hx - 18, by - 52, hx + 18, by - 24), paint)
        d.ellipse((hx - 16, by - 52, hx + 16, by - 34), fill='#1a4488')
        d.arc((hx - 16, by - 52, hx + 16, by - 34), 200, 340, fill='#f4c070')
    body = [(cx - 56, by - 26), (cx + 56, by - 26), (cx + 52 + sk * 0.3, by - 50), (cx - 52 + sk * 0.3, by - 50)]
    gradient_fill(img, body, (cx - 58, by - 52, cx + 58, by - 24), paint)
    d.line((cx - 52 + sk * 0.3, by - 50, cx + 52 + sk * 0.3, by - 50), fill='#f4c070')           # backlit deck edge
    d.rectangle((cx - 48 + sk * 0.3, by - 53, cx + 48 + sk * 0.3, by - 50), fill='#1c4a8e')    # ducktail lip
    d.line((cx - 48 + sk * 0.3, by - 53, cx + 48 + sk * 0.3, by - 53), fill='#f8d088')
    cab = [(cx - 44 + sk * 0.4, by - 53), (cx + 44 + sk * 0.4, by - 53), (cx + 30 + sk, by - 76), (cx - 30 + sk, by - 76)]
    gradient_fill(img, cab, (cx - 48, by - 78, cx + 48, by - 52), [(0, '#ffb064'), (0.25, '#5a68a0'), (1, '#0a1226')])
    for sx in (-1, 1):                                                   # C-pillars
        d.polygon([(cx + sx * 44 + sk * 0.4, by - 53), (cx + sx * 50 + sk * 0.4, by - 53), (cx + sx * 36 + sk, by - 76),
                   (cx + sx * 30 + sk, by - 76)], fill='#15397a')
    d.line((cx + sk * 0.7, by - 54, cx + sk * 0.9, by - 76), fill='#0a1226')
    d.polygon([(cx - 30 + sk, by - 76), (cx + 30 + sk, by - 76), (cx + 26 + sk, by - 80), (cx - 26 + sk, by - 80)], fill='#143468')
    d.line((cx - 26 + sk, by - 80, cx + 26 + sk, by - 80), fill='#f8d088')                      # roof rim light
    for sx in (-1, 1):                                                   # mirrors
        d.rectangle((cx + sx * 50 + sk * 0.5 - 4, by - 66, cx + sx * 56 + sk * 0.5 + 2, by - 60), fill='#123670')
    pulse = 0.85 + 0.15 * math.sin(f * 0.5)
    d.polygon([(cx - 50, by - 41), (cx + 50, by - 41), (cx + 49, by - 36), (cx - 49, by - 36)], fill=(int(255 * pulse), 40, 56))
    d.line((cx - 48, by - 39, cx + 48, by - 39), fill='#ffd8c8')
    for sx in (-1, 1):                                                   # wrap-around tail clusters
        d.polygon([(cx + sx * 40, by - 46), (cx + sx * 64, by - 43), (cx + sx * 64, by - 34), (cx + sx * 44, by - 34)],
                  fill='#d01a30')
        d.line((cx + sx * 42, by - 44, cx + sx * 62, by - 41), fill='#ff8a80')
    d.rectangle((cx - 14, by - 33, cx + 14, by - 25), fill='#e8e4d0')                           # plate
    for k in range(6):
        d.rectangle((cx - 11 + k * 4, by - 31, cx - 10 + k * 4, by - 27), fill='#2a2a34')
    d.rectangle((cx - 14, by - 33, cx - 12, by - 25), fill='#2a4ab0')


def dust(img, f, t, yaw):
    ov = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    r = random.Random(1)
    for i in range(46):
        side = -1 if i % 2 else 1
        age = ((t * 1.3 + r.random() * 3) % 1.0)
        x = W // 2 + round(yaw * 5) + side * (58 + age * (24 + r.random() * 26)) + r.uniform(-4, 4)
        y = 436 + age * 30 + r.uniform(-3, 3)
        rad = 2 + age * 11
        a = int(120 * (1 - age) ** 1.4)
        d.ellipse((x - rad, y - rad * 0.6, x + rad, y + rad * 0.6), fill=(214, 168, 112, a))
    img.paste(ov, (0, 0), ov)


# ---------------------------------------------------------------- frame
def post(arr, seed):
    a = np.clip(arr, 0, 255)
    bright = np.clip((a - 170) * 1.8, 0, 255).astype(np.uint8)
    a = a + np.asarray(Image.fromarray(bright).filter(ImageFilter.GaussianBlur(4.5)), np.float32) * 0.6
    vig = 1 - 0.34 * np.clip(np.hypot((XX - W / 2) / (W / 2), (YY - H / 2) / (H / 2)) - 0.6, 0, 1) ** 1.3
    a = a * vig[..., None] * np.array((1.02, 0.99, 0.94)) + np.random.RandomState(seed).randn(H, W, 1) * 2.2
    return np.clip(a, 0, 255).astype(np.uint8)


def frame(f):
    t = f / FPS
    dist = SPEED * t
    off_rows, off_at = road_offsets(dist)
    shift = dist * 1.4 + sum(curv(dist + k) for k in range(0, 1)) * 0
    sky = SKY.copy()
    hills(sky, shift)
    img = np.zeros((H, W, 3), np.float32)
    img[:HY + 8] = sky
    # sun, god rays
    glow(img, SUN[0], SUN[1], 120, '#ffb050', 0.62)
    sy_, sx_ = SUN[1], SUN[0]
    ang = np.arctan2(YY[:HY + 40] - sy_, XX[:HY + 40] - sx_)
    dd = np.hypot(YY[:HY + 40] - sy_, XX[:HY + 40] - sx_)
    rays = np.clip((0.5 + 0.5 * np.sin(ang * 15 + t * 0.35)) * np.exp(-dd / 190) - 0.2, 0, 1) * 0.55
    rq = np.floor(rays * 6 + BAY[:HY + 40]) / 6
    img[:HY + 40] += rq[..., None] * np.array((255, 190, 110), np.float32) * 0.28
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.ellipse((sx_ - 17, sy_ - 17, sx_ + 17, sy_ + 17), fill='#fff1b8')
    d.ellipse((sx_ - 11, sy_ - 11, sx_ + 11, sy_ + 11), fill='#ffffe8')
    img = np.asarray(im, np.float32).copy()
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    clouds(im, t, shift)
    birds(im, t)
    img = np.asarray(im, np.float32).copy()
    gr, _ = ground(dist, off_rows)
    # heat shimmer just under the horizon
    for k in range(0, 26):
        gr[k] = np.roll(gr[k], int(round(math.sin(t * 3.2 + k * 0.9) * (1.6 - k * 0.05))), axis=0)
    img[HY + 1:] = gr
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    props(im, dist, off_at)
    yaw = float(np.clip(curv(dist + 10) * 1.15, -1, 1))
    bump = round(1.2 * math.sin(t * 11) * 0.5 + 0.5 * math.sin(t * 17.3))
    dust(im, f, t, yaw)
    car(im, f, t, yaw, bump)
    arr = np.asarray(im, np.float32).copy()
    arr[HY + 20:] *= 1.0
    glow(arr, SUN[0], SUN[1], 90, '#ffb860', 0.28)
    ln = np.clip(1 - np.abs(np.arange(W) - SUN[0]) / 190.0, 0, 1) ** 2                # anamorphic streak
    for dy in (-1, 0, 1):
        arr[SUN[1] + dy] += ln[:, None] * np.array((255, 214, 150), np.float32) * (0.45 if dy == 0 else 0.2)
    for k, (fr, rad, col) in enumerate(((0.45, 9, '#ffa860'), (0.8, 5, '#ffd8a0'), (1.25, 13, '#ff8a70'))):   # lens ghosts
        gx, gy = SUN[0] + (W / 2 - SUN[0]) * fr * 1.6, SUN[1] + (H / 2 - SUN[1]) * fr * 1.6
        glow(arr, gx, gy, rad * 2.4, col, 0.22)
    out = post(arr, f)
    fade = min(1.0, (DUR - t) / 0.5, t / 0.3)
    if fade < 1:
        out = (out * fade).astype(np.uint8)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='out/countryside-preview.mp4')
    ap.add_argument('--sheet')
    args = ap.parse_args()
    total = int(DUR * FPS)
    if args.sheet:
        picks = [10, 50, 90, 130, 170, 215]
        tiles = [Image.fromarray(frame(p)) for p in picks]
        sheet = Image.new('RGB', (W * 3, H * 2))
        for i, tl in enumerate(tiles):
            sheet.paste(tl, ((i % 3) * W, (i // 3) * H))
        Path(args.sheet).parent.mkdir(parents=True, exist_ok=True)
        sheet.save(args.sheet)
        print('sheet', args.sheet)
        return
    if not shutil.which('ffmpeg'):
        raise SystemExit('FFmpeg not found. Install FFmpeg first.')
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-', '-an', '-vf', f'scale={W * SCALE}:{H * SCALE}:flags=neighbor,format=yuv420p',
           '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(dest)]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as p:
        try:
            assert p.stdin
            for f in range(total):
                p.stdin.write(np.ascontiguousarray(frame(f)).tobytes())
        finally:
            if p.stdin:
                p.stdin.close()
        if p.wait() != 0:
            raise SystemExit('FFmpeg failed')
    print(f'Created {dest} ({total} frames, {DUR:.1f}s, silent)')


if __name__ == '__main__':
    main()
