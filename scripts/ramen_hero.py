#!/usr/bin/env python3
"""Ramen shop in the rain - one continuous 8.2 s shot, hand-authored indexed pixel art.

Rules this renderer enforces:
  * one 180x180 grid for EVERY layer (sky, shop, car, reflections, rain, signs), x4 nearest -> 720x720;
    4x4 blocks line up with H.264 4:2:0 chroma, so edges stay crisp after encoding;
  * one fixed 32-colour palette for the whole clip (flicker = switching between palette entries, never new colours);
  * glow = blocky (2x2-cell) dithered halos; rain = solid undithered streaks;
  * camera push ~6% across parallax layers (far 3%, mid 6%, near 9%) via nearest sampling of index buffers.
Timeline: 0-4 s hero car crosses in the foreground, headlight beam sweeping the wet street;
          4-7 s shop life + passer-by; 6.9 s 'OPEN' sign and lantern string power on; 7.6-8.2 s payoff hold.
  python3 scripts/ramen_hero.py still OUT_DIR T [T ...] | video OUT.mp4 [AUDIO_SRC] | gif OUT.gif
"""
import importlib.util, math, os, random, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw

_here = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("pixel_neon", os.path.join(_here, "pixel_neon.py"))
E = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(E)
Pix, catenary = E.Pix, E.catenary
_ss = importlib.util.spec_from_file_location("pixel_street", os.path.join(_here, "pixel_street.py"))
_PS = importlib.util.module_from_spec(_ss); _ss.loader.exec_module(_PS)
E.SPRITES.update(_PS.SPR)                     # reuse bike, stool, crate, plant, cat sprites

N, UP, FPS, DUR = 180, 4, 30, 8.2
T_ = 255
G = 134                     # pavement line (world coords of the mid layer)
ROAD = 166                  # car wheel line
BAYER = E.BAYER

PALETTE = ["#02030a", "#060b1c", "#0a1228", "#0f1a36", "#172548", "#22345e", "#30487a",   # 0-6 navy ramp
           "#1a6a78", "#2aa0a8", "#6ad8d0", "#c8f4ee",                                    # 7-10 teal ramp
           "#2a0a10", "#6a1020", "#b8142a", "#ff3a3a", "#ff9a8a", "#fff0e4",              # 11-16 red neon ramp
           "#2e220c", "#6a4a10", "#b8901c", "#f0c828", "#fff4a8", "#e8743a",              # 17-22 warm ramp
           "#4a2a6a", "#b46aff", "#2e5a3a", "#6aa04a", "#d4dae2", "#8a9ab0", "#4a5670",   # 23-29 accents / car
           "#ffffff", "#f4a0c0"]                                                          # 30-31
PAL = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in PALETTE], np.uint8)

# reflection: every index -> a darker index of the same hue family (fixed palette, no blending)
REMAP = np.arange(256, dtype=np.uint8)
for k, v in {1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 4, 7: 3, 8: 7, 9: 8, 10: 8, 11: 0, 12: 11, 13: 12, 14: 13, 15: 13, 16: 14,
             17: 0, 18: 17, 19: 18, 20: 19, 21: 19, 22: 18, 23: 1, 24: 23, 25: 1, 26: 25, 27: 5, 28: 4, 29: 3, 30: 9, 31: 12}.items():
    REMAP[k] = v

FONT = {  # original 5x7 pixel font for readable signage
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
}
KANJI = [["###.###", "..#.#..", "#######", "...#...", ".#####.", "...#...", "#######"],   # clean ambient pseudo-kanji
         [".#...#.", "#######", ".#...#.", ".#####.", ".#...#.", ".#####.", "#.....#"],
         ["...#...", "#######", "#.....#", "..###..", "...#...", "#######", "...#..."]]


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def bmask(p, level, block=2, phase=0):
    """Blocky ordered-dither mask: thresholds per 2x2 cell -> chunky pixel-art glow."""
    yy, xx = np.mgrid[0:p.h, 0:p.w]
    return BAYER[((yy // block) + phase) % 4, ((xx // block) + phase) % 4] < level


def grow(m):
    g = m.copy()
    g[1:] |= m[:-1]; g[:-1] |= m[1:]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]
    return g


def neon_glow(p, src, rings, phase=0):
    """Halo rings around pixels of `src` indices: rings = [(index, level), ...] from inside out."""
    core = np.isin(p.a, src)
    done = core.copy()
    for idx, lvl in rings:
        ring = grow(done) & ~done
        if lvl >= 16:
            p.a[ring] = idx
        else:
            p.a[ring & bmask(p, lvl, 2, phase)] = idx
        done |= ring


def text(p, x, y, s, c):
    for n, ch in enumerate(s):
        for j, row in enumerate(FONT[ch]):
            for i, v in enumerate(row):
                if v == "#":
                    p.px(x + n * 7 + i, y + j, c)


def kanji(p, x, y, k, c):
    for j, row in enumerate(KANJI[k]):
        for i, v in enumerate(row):
            if v == "#":
                p.px(x + i, y + j, c)


# ------------------------------------------------------------------ layers (world coords)
def far_layer():
    p = Pix(200, N, T_)
    p.grad(0, G, [4, 3, 2, 1, 1])
    for x0, x1, sd in ((0, 40, 61), (150, 200, 62)):
        rr = random.Random(sd); x = x0
        while x < x1:
            w, h = rr.randint(8, 14), rr.randint(60, 130)
            p.rect(x, G - h, x + w, G, 2); p.rect(x, G - h, x + w, G - h, 5)
            for yy in range(G - h + 4, G - 6, 4):
                for xx in range(x + 2, x + w - 1, 3):
                    if rr.random() < .16:
                        p.px(xx, yy, 19 if rr.random() < .6 else 8)
            x += w + 2
    return p


def mid_layer():
    p = Pix(230, N, T_)
    X0, X1 = 22, 208
    p.rect(X0, 0, X1, G, 2)
    for y in range(0, G, 4):                                                      # brick courses
        p.rect(X0, y, X1, y, 3)
        for x in range(X0 + (y // 4 % 2) * 4, X1 + 1, 8):
            p.px(x, y + 1, 3)
    p.rect(X0, 0, X0, G, 5); p.rect(X1, 0, X1, G, 1)
    kinds = ["warm", "dark", "tv", "warm", "dark", "plant", "dark"]
    for row in range(2):                                                          # upper windows
        for col in range(7):
            x, y = 30 + col * 25, 4 + row * 18
            k = kinds[(col * 2 + row * 3) % 7]
            p.rect(x - 1, y - 1, x + 11, y + 10, 1)
            if k == "dark":
                p.rect(x, y, x + 10, y + 9, 3)
                for d in range(4):
                    p.px(x + 8 - d, y + 1 + d, 5)
            else:
                p.rect(x, y, x + 10, y + 9, 9 if k == "tv" else 20)
                p.rect(x, y + 5, x + 10, y + 9, 8 if k == "tv" else 19)
                p.rect(x, y, x + 1, y + 9, 12 if k != "tv" else 7); p.rect(x + 9, y, x + 10, y + 9, 12 if k != "tv" else 7)
                if k == "plant":
                    p.rect(x + 4, y + 6, x + 6, y + 9, 25); p.px(x + 3, y + 5, 26); p.px(x + 7, y + 5, 26); p.px(x + 5, y + 4, 26)
            p.line(x + 5, y, x + 5, y + 9, 1)
            p.rect(x - 2, y + 10, x + 12, y + 10, 5)
    for x in (52, 127):                                                           # balcony + laundry
        p.rect(x - 3, 33, x + 14, 33, 6)
        for xx in range(x - 3, x + 15, 3):
            p.line(xx, 33, xx, 37, 4)
    p.sprite(26, 40, "ac", {"k": 0, "b": 3, "c": 5}); p.sprite(196, 18, "ac", {"k": 0, "b": 3, "c": 5})
    p.line(25, 0, 25, 60, 5); p.line(205, 0, 205, 60, 5)
    p.poly([(10, 60), (115, 46), (220, 60), (220, 66), (10, 66)], 4)              # tiled eave
    for y in range(48, 66, 3):
        xl = 10 + max(0, 60 - y) * 7.5; xr = 220 - max(0, 60 - y) * 7.5
        p.line(xl, y, xr, y, 3)
        for x in range(int(xl) + (y % 2) * 3, int(xr), 6):
            p.px(x, y + 1, 5)
    p.line(10, 60, 115, 46, 6); p.line(115, 46, 220, 60, 6); p.rect(10, 66, 220, 67, 0)
    # shop front
    SX0, SX1 = 44, 186
    p.rect(SX0 - 2, 70, SX1 + 2, 75, 17); p.rect(SX0 - 2, 70, SX1 + 2, 70, 19)
    for i in range(0, SX1 - SX0 + 4, 6):                                          # awning stripes
        p.rect(SX0 - 2 + i, 76, SX0 + i, 81, 13); p.rect(SX0 + 1 + i, 76, SX0 + 3 + i, 81, 16)
        p.px(SX0 - 1 + i, 82, 13)
    p.rect(SX0, 83, SX1, G - 1, 17)
    p.rect(SX0 + 2, 84, SX1 - 2, G - 2, 20)                                       # warm interior
    p.rect(SX0 + 2, 84, SX1 - 2, 87, 21)
    p.rect(SX0 + 2, 92, SX1 - 2, 92, 19)                                          # shelf + bowls
    for i in range(0, SX1 - SX0 - 4, 6):
        p.rect(SX0 + 4 + i, 89, SX0 + 7 + i, 91, (19, 22, 13, 26)[i // 6 % 4])
    for i, mx in enumerate(range(SX0 + 8, SX1 - 30, 34)):                         # menu plaques: clean bars
        p.rect(mx, 95, mx + 16, 101, 18); p.rect(mx, 95, mx + 16, 95, 21)
        p.rect(mx + 2, 97, mx + 9, 97, 21); p.rect(mx + 2, 99, mx + 6, 99, 21); p.rect(mx + 12, 99, mx + 14, 99, 14)
    p.rect(SX0 + 2, 118, SX1 - 2, 121, 19); p.rect(SX0 + 2, 118, SX1 - 2, 118, 21)   # counter
    p.rect(SX0 + 2, 122, SX1 - 2, G - 2, 18)
    for x in range(SX0 + 6, SX1 - 4, 7):
        p.line(x, 122, x, G - 2, 17)
    for x in (SX0, SX1):
        p.rect(x - 1, 83, x + 1, G, 17)
    p.rect(0, 74, 20, 80, 1); p.rect(1, 75, 19, 79, 23)                           # purple bar sign: glass icon
    p.line(6, 76, 14, 76, 24); p.line(7, 76, 10, 78, 24); p.line(13, 76, 10, 78, 24); p.px(10, 78, 24)
    p.sprite(1, G - 10, "bike", {"k": 0})
    p.sprite(210, G - 14, "vending", {"k": 0, "c": 9, "d": 10, "b": 3, "h": 6, "e": 0})
    p.sprite(196, G - 6, "crate", {"k": 0, "b": 18}); p.sprite(218, G - 7, "plant", {"l": 26, "g": 25, "p": 12})
    p.rect(0, G, 230, N - 1, 1)                                                    # pavement + road
    return p


def life(p, t):
    """Per-frame: neon (with flicker), lanterns, cook, diners, noren, steam, passer-by, payoff."""
    dip = any(abs(t - c) < .05 for c in (1.35, 1.45, 3.9, 5.2, 5.28))             # brief neon dips
    buzz = int(t * 10) % 2
    tube, core = (13, 15) if dip else (14, 16)
    # disc sign with bowl emblem
    p.ellipse(62, 40, 14, 14, tube); p.ellipse(62, 40, 12, 12, core, outline=True)
    p.rect(55, 42, 69, 43, 11); p.rect(56, 44, 68, 45, 11); p.rect(58, 46, 66, 47, 11)
    p.line(57, 33, 66, 41, 16); p.line(60, 32, 69, 40, 16)
    for k, sx in enumerate((58, 62, 66)):
        for j in range(4):
            p.px(sx + ((j + int(t * 5) + k) % 4 in (1, 2)), 40 - j, 16)
    # RAMEN pill sign - readable
    m = Image.new("1", (p.w, p.h), 0)
    ImageDraw.Draw(m).rounded_rectangle([84, 30, 146, 48], 8, outline=1, width=1)
    p.a[np.asarray(m, bool)] = tube
    p.rect(86, 32, 144, 46, 11)
    text(p, 98, 36, "RAMEN", core)
    # vertical banner with 3 clean pseudo-kanji
    surge = t > 6.9
    p.rect(158, 0, 172, 44, 13 if not surge else 14); p.rect(158, 0, 158, 44, 12); p.rect(172, 0, 172, 44, 12)
    for k in range(3):
        kanji(p, 162, 4 + k * 14, k, 16 if surge or not dip else 15)
    # OPEN sign powers on at 6.9 s (stutter) -> payoff
    on = t > 7.25 or (t > 6.9 and int(t * 30) % 3 != 0)
    p.rect(160, 102, 182, 112, 1); text(p, 162, 104, "OPEN", 10 if on else 7)
    # lantern string + bulbs
    for i in range(140):
        p.px(46 + i, 69 + round(math.sin(i / 140 * math.pi) * 3), 0)
    for k, lx in enumerate(range(48, 186, 14)):
        y = 69 + round(math.sin((lx - 46) / 140 * math.pi) * 3)
        lit = t > 6.9 or (int(t * 4 + k) % 6 != 0)
        p.rect(lx, y + 1, lx + 1, y + 3, 14 if lit else 12); p.px(lx, y + 1, 16 if lit else 13)
    for lx, sd in ((32, 0), (190, 1)):                                            # red lanterns, gentle sway
        sw = 1 if math.sin(t * 1.7 + sd * 2) > 0 else 0
        p.line(lx + 3, 67, lx + 3 + sw, 71, 11)
        p.sprite(lx + sw, 71, "lantern", {"k": 17, "r": 14, "h": 16, "d": 13})
    neon_glow(p, [14, 15, 16], [(13, 16), (12, 10), (11, 5)], buzz)
    neon_glow(p, [10], [(8, 12), (7, 6)], buzz)
    neon_glow(p, [24], [(23, 10)], buzz)
    neon_glow(p, [9], [(7, 6)], buzz)
    # noren curtains (sway) with simple ring marks
    for k, nx in enumerate(range(54, 180, 30)):
        sw = int(round(math.sin(t * 2 + k) * 1.2))
        for yy in range(83, 95):
            s = sw if yy > 88 else 0
            p.rect(nx + s, yy, nx + 9 + s, yy, 6)
        p.ellipse(nx + 4, 87, 2, 2, 10, outline=True)
    # cook ladling + steam
    cx = 115; lad = int(round(math.sin(t * 5) * 2))
    p.rect(cx - 3, 104, cx + 3, 117, 0); p.rect(cx - 2, 98, cx + 2, 103, 0); p.rect(cx - 3, 96, cx + 3, 97, 30)
    p.line(cx + 3, 107, cx + 8, 109 + lad, 0); p.line(cx + 8, 109 + lad, cx + 8, 114, 0)
    p.rect(cx + 5, 113, cx + 16, 117, 0)
    for k in range(10):
        sy = 112 - ((k * 3 + int(t * 12)) % 24)
        p.px(cx + 9 + int(round(math.sin(t * 3 + k) * 2)), sy, 21)
        p.px(cx + 13 + int(round(math.cos(t * 2 + k) * 2)), sy - 2, 21)
    for i, (sx, coat) in enumerate(((64, 5), (86, 22), (150, 29))):              # diners
        eat = int(t * 2 + i * .7) % 3 == 0
        dy = 1 if eat else 0
        p.sprite(sx - 3, G - 6, "stool", {"k": 0})
        p.rect(sx - 3, 109, sx + 3, G - 7, coat); p.rect(sx - 3, 109, sx - 3, G - 7, 0)
        p.rect(sx - 2, 103 + dy, sx + 2, 108 + dy, 0)
        if eat:
            p.rect(sx + 3, 110, sx + 6, 112, 19)
    p.sprite(6, G - 5, "cat_sleep0" if int(t * 1.5) % 3 else "cat_sleep1", {"k": 0, "t": 0})
    # passer-by with red umbrella: enters right at 3.6 s, stops under the sign for the payoff
    if t > 3.6:
        u = ease((t - 3.6) / 3.6)
        px_ = int(round(240 - u * 130))
        E_person(p, px_, G + 6, t, walking=u < 1)


def E_person(p, x, y, t, walking=True):
    ph = int(t * 8) % 4 if walking else 0
    bob = 1 if ph in (1, 3) else 0
    y0 = y - bob
    for k, w in enumerate((3, 5, 7, 8, 8)):                                        # stepped umbrella dome
        p.rect(x - w, y0 - 20 + k, x + w, y0 - 20 + k, 14)
    p.rect(x - 3, y0 - 19, x + 1, y0 - 19, 15); p.px(x - 5, y0 - 17, 15)
    for rx in (-8, -4, 0, 4, 8):
        p.px(x + rx, y0 - 15, 12)
    p.line(x, y0 - 15, x, y0 - 11, 0)
    p.rect(x - 1, y0 - 12, x + 1, y0 - 9, 22); p.rect(x - 1, y0 - 13, x + 1, y0 - 12, 0)
    p.px(x - 1, y0 - 11 if walking else y0 - 12, 0)                                 # looks up when stopped
    p.rect(x - 2, y0 - 8, x + 2, y0 - 2, 29); p.rect(x + 2, y0 - 8, x + 2, y0 - 2, 0)
    legs = {0: (-1, 1), 1: (0, 0), 2: (1, -1), 3: (0, 0)}[ph]
    p.line(x - 1, y0 - 1, x - 1 + legs[0], y + 2, 0); p.line(x + 1, y0 - 1, x + 1 + legs[1], y + 2, 0)


def car_layer(t):
    """Hero car (world coords) + its wet reflection + headlight beam. Returns layer and beam mask."""
    p = Pix(230, N, T_)
    x = int(round(18 + 46 * t))
    y = ROAD
    if x > 260:
        return p, np.zeros_like(p.a, bool)
    beam = p.mask_poly([(x + 70, y - 12), (x + 150, y - 30), (x + 160, y + 10), (x + 70, y - 8)])    # headlight beam
    road = np.zeros_like(beam); road[G + 8:, :] = True
    p.a[beam & road & bmask(p, 4, 2)] = 21
    near = p.mask_poly([(x + 70, y - 12), (x + 105, y - 20), (x + 108, y), (x + 70, y - 8)])
    p.a[near & road & bmask(p, 8, 2)] = 21
    # body
    p.rect(x + 2, y - 13, x + 68, y - 5, 28)
    p.rect(x, y - 11, x + 70, y - 5, 28)
    p.poly([(x + 14, y - 13), (x + 22, y - 22), (x + 48, y - 22), (x + 58, y - 13)], 28)
    p.rect(x + 2, y - 13, x + 68, y - 13, 27); p.line(x + 22, y - 22, x + 48, y - 22, 27); p.line(x + 14, y - 13, x + 22, y - 22, 27)
    p.rect(x, y - 6, x + 70, y - 5, 29)                                             # lower shadow band
    p.rect(x + 2, y - 9, x + 68, y - 9, 10)                                         # chrome strip
    p.poly([(x + 17, y - 14), (x + 23, y - 20), (x + 34, y - 20), (x + 34, y - 14)], 3)   # windows
    p.poly([(x + 37, y - 14), (x + 37, y - 20), (x + 47, y - 20), (x + 54, y - 14)], 3)
    p.line(x + 35, y - 21, x + 35, y - 13, 29)
    p.rect(x + 40, y - 18, x + 42, y - 15, 0); p.rect(x + 41, y - 19, x + 42, y - 19, 0)  # driver
    for k in range(3):                                                              # neon reflections in glass
        p.px(x + 26 + k, y - 18 + k, 31); p.px(x + 44 + k, y - 19 + k, 9)
    wx = 140 - x                                                                    # shop light sliding along the body
    for k in range(0, 70, 1):
        if abs((x + k) - 115) < 30 and (x + k + int(t * 0)) % 3 == 0:
            p.px(x + k, y - 12, 20)
    p.line(x + 35, y - 12, x + 35, y - 6, 29); p.rect(x + 28, y - 11, x + 31, y - 11, 29); p.rect(x + 50, y - 11, x + 53, y - 11, 29)
    p.rect(x + 66, y - 12, x + 70, y - 10, 30); p.rect(x + 67, y - 11, x + 69, y - 11, 21)   # headlight
    p.rect(x, y - 12, x + 1, y - 10, 14)                                            # tail light
    p.rect(x + 56, y - 15, x + 58, y - 14, 29)                                       # mirror
    for k, wcx in enumerate((x + 14, x + 56)):                                      # wheels (spoke frames)
        p.ellipse(wcx, y - 3, 5, 5, 0); p.ellipse(wcx, y - 3, 3, 3, 29); p.px(wcx, y - 3, 27)
        if int(t * 12) % 2:
            p.px(wcx - 2, y - 3, 27); p.px(wcx + 2, y - 3, 27)
        else:
            p.px(wcx, y - 5, 27); p.px(wcx, y - 1, 27)
    neon_glow(p, [30], [(21, 16), (21, 8)])                                         # headlight halo (blocky)
    neon_glow(p, [14], [(13, 10)])
    # wet reflection: mirror the car rows below the wheel line, darker indices, gaps every 3rd row
    for dy in range(1, 20):
        src = y + 2 - dy
        if dy % 3 == 0 or src < 0:
            continue
        row = p.a[src].copy()
        m = row != T_
        sh = 1 if math.sin(dy * .9 + t * 3) > .3 else 0
        row = np.roll(row, sh); m = np.roll(m, sh)
        tgt = y + 2 + dy
        if tgt < N:
            p.a[tgt][m] = REMAP[row[m]]
    return p, beam


def near_layer():
    p = Pix(250, N, T_)
    for k in (0, 3):
        catenary(p, 0, 4 + k, 250, 10 + k, 7, 0)
    p.rect(238, 0, 243, N - 1, 0); p.rect(238, 0, 238, N - 1, 4)
    p.rect(226, 58, 243, 66, 0); p.rect(228, 60, 241, 64, 13)                      # hanging signal arm
    return p


# ------------------------------------------------------------------ camera + compositing
_CACHE = {}


def sample(a, cx, cy, z):
    u = np.arange(N)
    sx = np.clip(np.floor(cx + (u - N / 2 + .5) / z).astype(int), 0, a.shape[1] - 1)
    sy = np.clip(np.floor(cy + (u - N / 2 + .5) / z).astype(int), 0, a.shape[0] - 1)
    return a[np.ix_(sy, sx)]


def put(dst, src):
    m = src != T_
    dst[m] = src[m]


def rain(view, t, seed, n, c, speed, length, hilite=None, ground=None):
    r = random.Random(seed)
    for _ in range(n):
        x0, y0, v = r.uniform(0, N), r.uniform(0, N), r.uniform(.85, 1.15)
        y = int((y0 + t * speed * v) % (N + length)) - length
        x = int(x0 + y / 4) % N
        col = c
        if hilite is not None and 0 <= y < N and hilite[min(N - 1, max(0, y)), x]:
            col = 30                                                                # drops lit by the headlights
        for k in range(length):
            yy, xx = y + k, x + (k + y % 4) // 4
            if 0 <= yy < N and 0 <= xx < N:
                view[yy, xx] = col
    if ground is not None:
        for _ in range(n // 3):
            x, y = r.randrange(N), r.randrange(ground + 3, N - 2)
            ph = int(t * 12 + r.random() * 12) % 12
            if ph == 0:
                view[y, x] = c
            elif ph == 1:
                view[y - 1, max(0, x - 1)] = c; view[y - 1, min(N - 1, x + 1)] = c
            elif ph == 2:
                view[y, max(0, x - 2)] = c; view[y, min(N - 1, x + 2)] = c


def frame_indices(t):
    if "far" not in _CACHE:
        _CACHE.update(far=far_layer(), mid=mid_layer(), near=near_layer())
    e = ease(t / DUR)
    cx, cy = 115 + 3 * e, 92 - 4 * e                                                # slow push toward the sign
    z = {"far": 1 + .03 * e, "mid": 1 + .06 * e, "near": 1 + .09 * e}
    view = np.zeros((N, N), np.uint8)
    put(view, sample(_CACHE["far"].a, cx * 200 / 230 + 0, cy, z["far"]))
    live = Pix(230, N, T_); live.a = _CACHE["mid"].a.copy()
    life(live, t)
    put(view, sample(live.a, cx, cy, z["mid"]))
    vp = Pix(N, N, 0); vp.a = view
    gv = int(round(N / 2 + (G - cy) * z["mid"]))                                     # waterline in view
    vp.reflect(gv, t, REMAP, gaps=3, depth=40)
    vp.rect(0, gv, N, gv, 6); vp.rect(0, gv + 1, N, gv + 1, 3)
    curb = int(round(N / 2 + (G + 8 - cy) * z["mid"]))
    vp.rect(0, curb, N, curb, 5)
    for x in range(0, N, 12):
        vp.px(x, gv + 4, 3)
    def pool(wx, wy, rx, ry, c, lvl):                                                # blocky light spill on the wet street
        vx, vy = N / 2 + (wx - cx) * z["mid"], N / 2 + (wy - cy) * z["mid"]
        yy, xx = np.mgrid[0:N, 0:N]
        m = ((xx - vx) / (rx * z["mid"])) ** 2 + ((yy - vy) / (ry * z["mid"])) ** 2 <= 1
        m &= (yy > gv + 1) & np.isin(vp.a, [0, 1, 2, 3, 4, 5])
        vp.a[m & bmask(vp, lvl, 2)] = c
    pool(115, G + 12, 72, 7, 18, 6); pool(115, G + 10, 50, 4, 19, 5)
    pool(105, G + 22, 44, 5, 12, 6); pool(62, G + 16, 20, 4, 13, 5)
    if t > 6.9:
        pool(171, G + 12, 14, 3, 7, 8)
    E.mist(vp, gv - 6, gv + 4, 5, t, 1)
    rain(view, t, 11, 50, 4, 55, 2)                                                  # far rain (dim, behind car)
    car, beam = car_layer(t)
    put(view, sample(car.a, cx, cy, z["mid"]))
    beam_v = sample(np.where(beam, 1, 0).astype(np.uint8), cx, cy, z["mid"]).astype(bool)
    put(view, sample(_CACHE["near"].a, cx + 10, cy, z["near"]))
    rain(view, t, 21, 70, 9, 130, 4, hilite=beam_v, ground=gv)                      # front rain, solid streaks
    return view


def frame(t):
    return Image.fromarray(np.repeat(np.repeat(PAL[frame_indices(t)], UP, 0), UP, 1))


def video(out, audio_src=None):
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        if audio_src:
            ainput = ["-i", audio_src]; amap = ["-map", "0:v", "-map", "1:a", "-c:a", "copy"]
        else:
            sp = importlib.util.spec_from_file_location("nb", os.path.join(_here, "render_neon_offline.py"))
            nb = importlib.util.module_from_spec(sp); sp.loader.exec_module(nb)
            wav = os.path.join(tmp, "a.wav"); nb.audio(wav)
            ainput = ["-i", wav]; amap = ["-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "160k"]
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{N * UP}x{N * UP}", "-r", str(FPS),
               "-i", "-", *ainput, *amap, "-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", "10",
               "-pix_fmt", "yuv420p", "-t", str(DUR), "-movflags", "+faststart", out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(int(round(DUR * FPS))):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close()
        if p.wait():
            sys.exit("ffmpeg failed")


def gif(out, t0=0.0, t1=4.0, fps=15, scale=2):
    """Exact-palette preview GIF (32 colours, no dithering added by the encoder)."""
    pal = PAL.flatten().tolist() + [0] * (768 - PAL.size)
    frames = []
    for i in range(int((t1 - t0) * fps)):
        idx = frame_indices(t0 + i / fps)
        im = Image.fromarray(np.repeat(np.repeat(idx, scale, 0), scale, 1), "P"); im.putpalette(pal)
        frames.append(im)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=int(1000 / fps), loop=0, optimize=False)


if __name__ == "__main__":
    a = sys.argv
    if len(a) >= 4 and a[1] == "still":
        os.makedirs(a[2], exist_ok=True)
        for s in a[3:]:
            frame(float(s)).save(os.path.join(a[2], f"r{float(s):.2f}.png"))
    elif len(a) in (3, 4) and a[1] == "video":
        video(a[2], a[3] if len(a) == 4 else None)
    elif len(a) == 3 and a[1] == "gif":
        gif(a[2])
    else:
        sys.exit(__doc__)
