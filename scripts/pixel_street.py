#!/usr/bin/env python3
"""Living rainy neon street - hand-authored indexed pixel art with parallax and inhabitants.

240x240 indexed grid (x3 nearest = 720x720), 30 fps, 8.2 s, hard cuts at 2.5 s / 5.53 s.
Engine (indexed canvas, dither, halos, reflections, glyphs) is reused from scripts/pixel_neon.py.
Each shot = far / mid / near layers (parallax), static art cached, life drawn per frame:
  shot 1 dusk roadside: passing car + headlights, birds on wires, cat on fence, vending customer, TV glow, drips
  shot 2 noodle shop:   cook ladling, 3 customers eating, noren sway, lantern string, sleeping cat, passer-by
  shot 3 night gantry:  monorail with passengers, truck exhaust, stall vendor + steam, umbrella walkers
Usage: python3 scripts/pixel_street.py still OUT_DIR T [T ...] | video OUT.mp4
"""
import importlib.util, math, os, random, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw

_here = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("pixel_neon", os.path.join(_here, "pixel_neon.py"))
E = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(E)
Pix, hx, remap_table, catenary = E.Pix, E.hx, E.remap_table, E.catenary

V = 240           # view size (pixels)
UP = 3
FPS, DUR, CUTS = 30, 8.2, (2.5, 5.53)
T_ = 255          # transparent index for layers
LAYER_W = {"far": 310, "mid": 300, "near": 330}
SPEED = {"far": .35, "mid": 1.0, "near": 1.7}

SPR = {
    "cat_sit0": ["k...k..", "kk.kk..", "kkkkk..", "kekek..", "kkkkk..", ".kkk...", ".kkkk..", "kkkkkk.", "kkkkkkt", "kkkkkkt", ".k.k.tt"],
    "cat_sit1": ["k...k..", "kk.kk..", "kkkkk..", "kekek..", "kkkkk..", ".kkk...", ".kkkk..", "kkkkkk.", "kkkkkk.", "kkkkkkt", ".k.kttt"],
    "cat_sleep0": ["...kk......", "..kkkkkkk..", ".kkkkkkkkk.", "kkkkkkkkkkt", ".kkkkkkkktt"],
    "cat_sleep1": ["...kk......", "..kkkkkkk..", ".kkkkkkkkk.", "kkkkkkkkkk.", ".kkkkkkkkkt"],
    "bird0": [".kk.", "kkkk", ".k.."], "bird1": ["k..k", ".kk.", "...."],
    "bike": ["............kk...", "..kkk......k.....", "....k.....kkk....", "...kkkkkkkk..k...", "..k..k...k....k..",
             ".kkk..k.k....kkk.", "k.k.k..k....k.k.k", "kk.kk.......kk.kk", "k.k.k.......k.k.k", ".kkk.........kkk."],
    "stool": ["kkkkkk", ".k..k.", ".k..k.", ".kkkk.", ".k..k.", "k....k"],
    "plant": ["..l.l.l..", ".lglglgl.", "lggglgggl", ".ggggggg.", "..ppppp..", "..ppppp..", "...ppp..."],
    "fern": ["l...l...l", ".l.lgl.l.", "lgllgllgl", ".ggggggg.", "..ggggg..", "...ppp...", "...ppp..."],
    "cone": ["..o..", "..o..", ".ooo.", ".www.", ".ooo.", "ooooo", "kkkkk"],
    "crate": ["kkkkkkkk", "kbbbbbbk", "kbkbbkbk", "kbbbbbbk", "kbkbbkbk", "kkkkkkkk"],
    "bin": [".kkkkk.", "kbbbbbk", "kbhbbbk", "kbhbbbk", "kbbbbbk", "kbbbbbk", ".kkkkk."],
}
E.SPRITES.update(SPR)


def person(p, x, y, t, coat, skin, umb=None, umb_hi=None, walk=True, face=1, scale=1):
    """~24px pedestrian: umbrella canopy with ribs, head, coat, alternating legs (4-frame cycle)."""
    ph = int(t * 8) % 4 if walk else 0
    bob = 1 if ph in (1, 3) else 0
    y0 = y - bob
    if umb is not None:
        for k in range(7):                                          # dome canopy, stepped
            w = [3, 6, 8, 9, 10, 10, 10][k]
            p.rect(x - w, y0 - 22 + k, x + w, y0 - 22 + k, umb)
        if umb_hi is not None:
            p.rect(x - 4, y0 - 21, x + 2, y0 - 21, umb_hi); p.px(x - 6, y0 - 19, umb_hi)
        for rx in (-10, -5, 0, 5, 10):
            p.px(x + rx, y0 - 15, 0)
        p.line(x, y0 - 15, x, y0 - 11, 0)
    p.rect(x - 2, y0 - 13, x + 1, y0 - 10, skin); p.rect(x - 2, y0 - 14, x + 1, y0 - 13, 0)       # head + hair
    p.px(x + face, y0 - 12, 0)
    p.rect(x - 3, y0 - 9, x + 2, y0 - 2, coat); p.rect(x - 3, y0 - 9, x - 3, y0 - 2, 0)          # coat
    p.px(x + 3 * face if face > 0 else x - 4, y0 - 7, coat)
    legs = {0: (-1, 1), 1: (0, 0), 2: (1, -1), 3: (0, 0)}[ph]
    p.line(x - 1, y0 - 1, x - 1 + legs[0], y + 2, 0); p.line(x + 1, y0 - 1, x + 1 + legs[1], y + 2, 0)


def compose(dst, layer, off):
    src = layer[:, off:off + V]
    m = src != T_
    dst[m] = src[m]


def rain_layer(p, t, seed, n, c, speed, length, ground, splash=True, slant=3):
    r = random.Random(seed)
    for _ in range(n):
        x0, y0, v = r.uniform(0, V), r.uniform(0, V), r.uniform(.8, 1.2)
        y = int((y0 + t * speed * v) % (V + length)) - length
        x = int(x0 + y / slant) % V
        for k in range(length):
            p.px(x + (k + y % slant) // slant, y + k, c)
    if splash:
        for _ in range(n // 3):
            x, y = r.randrange(V), r.randrange(ground + 3, V - 2)
            ph = int((t * 12 + r.random() * 12)) % 12
            if ph < 3:
                p.sprite(x - 2 + (ph < 2), y, f"splash{ph}", {"a": c})


def windowpane(p, x, y, w, h, kind, c, rnd):
    """Detailed window: frame, glass, interior story (curtain, plant, lamp, blinds, tv glow, silhouette)."""
    fr, glass, warm, warm2, dark, curtain, plant, tv = c
    p.rect(x - 1, y - 1, x + w, y + h, fr)
    if kind == "dark":
        p.rect(x, y, x + w - 1, y + h - 1, dark)
        for k in range(min(w, h) // 2):
            p.px(x + w - 2 - k, y + 1 + k, glass)                                     # glint diagonal
        p.rect(x, y + h - 1, x + w - 1, y + h - 1, glass)
    else:
        p.rect(x, y, x + w - 1, y + h - 1, tv if kind == "tv" else warm)
        if kind != "tv":
            p.dither(x, y + h // 2, x + w - 1, y + h - 1, warm2, 6)                   # light falloff
        if kind == "blinds":
            for yy in range(y + 1, y + h, 2):
                p.rect(x, yy, x + w - 1, yy, warm2)
        if kind in ("curtain", "plant", "tv"):
            p.rect(x, y, x + 1, y + h - 1, curtain); p.rect(x + w - 2, y, x + w - 1, y + h - 1, curtain)
            p.px(x + 2, y + h - 1, curtain); p.px(x + w - 3, y + h - 1, curtain)
        if kind == "plant":
            p.sprite(x + w // 2 - 4, y + h - 7, "plant", {"l": plant, "g": fr, "p": fr})
        if kind == "tv":
            p.rect(x + 3, y + h - 4, x + w - 4, y + h - 1, fr)                         # sofa back silhouette
        if kind == "lamp":
            p.rect(x + 2, y + 2, x + 4, y + 3, warm2); p.line(x + 3, y + 4, x + 3, y + h - 2, fr)
        p.line(x + w // 2, y, x + w // 2, y + h - 1, fr)
    p.rect(x - 2, y + h, x + w + 1, y + h, glass)                                         # sill


# =================================================================== SHOT 1: dusk roadside
P1 = ["#04141c", "#082430", "#0b3240", "#0d3e50", "#114c62", "#165c74", "#1d6e86", "#278299", "#3a98ac", "#5cb2c0",
      "#8ccdd4", "#c4e8e8", "#f6f0d0", "#f2d98a", "#d9a54a", "#8a5a2a", "#ff5266", "#a01e3c", "#5a1430", "#ffd04a",
      "#5fe0ea", "#2a5a6a", "#9ab8c4", "#ff8a9a", "#ffd04a", "#7ad8ff", "#2e7a3a", "#5aa04a", "#1a2a20", "#e8743a",
      "#ffffff", "#0a1a22"]
R1 = remap_table({12: 13, 13: 14, 14: 15, 19: 14, 24: 14, 16: 17, 23: 17, 17: 18, 20: 7, 25: 6, 30: 12, 11: 8, 10: 7, 22: 6,
                  29: 15, 27: 2, 26: 2, 21: 2, 15: 2, 18: 1, 28: 0, 31: 0},
                 {0: 0, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5})
G1 = 150


def s1_far():
    p = Pix(LAYER_W["far"], V, T_)
    p.grad(0, G1, [4, 5, 6, 7, 8, 9])
    p.poly([(0, 118), (40, 96), (70, 104), (110, 88), (150, 100), (150, G1), (0, G1)], 5)          # mountains
    p.line(0, 118, 40, 96, 6); p.line(40, 96, 70, 104, 6); p.line(70, 104, 110, 88, 7); p.line(110, 88, 150, 100, 6)
    p.dither(0, 100, 150, G1, 4, 4, where=p.a == 5)
    rr = random.Random(21); x = 170                                                                  # distant blocks
    while x < LAYER_W["far"]:
        w, h = rr.randint(7, 13), rr.randint(14, 40)
        p.rect(x, G1 - 14 - h, x + w, G1, 5); p.rect(x, G1 - 14 - h, x + w, G1 - 14 - h, 6)
        for _ in range(4):
            p.px(x + rr.randint(1, w - 1), G1 - 14 - rr.randint(2, h), 19)
        x += w + rr.randint(1, 3)
    T = [(132, G1), (152, 42), (190, 14), (262, 36), (300, G1)]                                     # cooling tower
    p.poly(T, 2)
    lit = p.mask_poly([(212, 16), (262, 36), (300, G1), (226, G1)])
    term = p.mask_poly([(203, 16), (262, 36), (300, G1), (216, G1)]) & ~lit
    p.a[lit] = 3; p.a[term & p.dmask(8)] = 3; p.a[term & ~p.dmask(8) & p.dmask(12)] = 2
    for x in range(140, 226, 6):
        p.line(x, G1 - 2, 152 + (x - 140) * .5, 46 + (x - 140) * .08, 1)
    for y in range(52, G1, 14):                                                                      # rings of panels
        xl = 152 - (y - 42) * 20 / (G1 - 42) if y > 42 else 152
        p.line(xl + 2, y, 260, y, 1)
    p.line(190, 14, 262, 36, 8); p.line(262, 36, 300, G1, 7); p.line(152, 42, 190, 14, 4)
    p.rect(180, 8, 214, 13, 2); p.rect(180, 8, 214, 8, 7); p.line(198, 8, 198, 0, 3); p.line(186, 8, 176, 0, 3)  # crown + crane
    for band, (yc, amp) in enumerate(((78, 16), (84, 15))):
        for x in range(168, 296):
            y = yc - round(amp * math.sin((x - 168) / 128 * math.pi))
            if p.a[y, x] in (1, 2, 3):
                p.px(x, y, 16 if band == 0 else 17)
                if band == 0:
                    p.px(x, y + 1, 17)
    p.glow([16], 17, 18, 8, 4)
    r = random.Random(4)
    for _ in range(80):
        x, y = r.randint(150, 296), r.randint(50, 145)
        if p.a[y, x] in (1, 2, 3):
            p.px(x, y, 24 if r.random() < .3 else 19)
    return p


def s1_mid():
    p = Pix(LAYER_W["mid"], V, T_)
    p.poly([(0, 128), (36, 112), (80, 120), (128, 114), (128, G1), (0, G1)], 3)                    # hill + pines
    p.line(0, 128, 36, 112, 4); p.line(36, 112, 80, 120, 4); p.line(80, 120, 128, 114, 4)
    r = random.Random(8)
    for row, (base, cols) in enumerate(((0, (1, 4, 0)), (8, (2, 5, 1)))):
        for x in range(-3, 130, 4 + row):
            top = 128 - (x * 16 // 36 if x < 36 else (16 - (x - 36) * 8 // 44 if x < 80 else 8 - (x - 80) * 6 // 48))
            p.sprite(x, top - 7 + base + r.randint(-2, 2), "pine", {"a": cols[0], "b": cols[1], "c": cols[2]})
    # shop-house: two storeys
    X0, X1, Y0 = 92, 196, 96
    p.rect(X0, Y0, X1, G1, 2); p.dither(X0, Y0, X1, G1, 3, 3)
    for y in range(Y0 + 3, G1, 6):                                                                     # siding lines
        p.rect(X0, y, X1, y, 1)
    p.rect(X0 - 3, Y0 - 6, X1 + 3, Y0 - 1, 4)                                                         # roof with tiles
    for x in range(X0 - 3, X1 + 4, 3):
        p.px(x, Y0 - 5, 6); p.px(x + 1, Y0 - 3, 3)
    p.rect(X0 - 3, Y0 - 7, X1 + 3, Y0 - 7, 9); p.rect(X0 - 3, Y0, X1 + 3, Y0, 0)
    p.sprite(X0 + 8, Y0 - 14, "ac", {"k": 0, "b": 3, "c": 6})
    p.line(X1 - 10, Y0 - 7, X1 - 10, Y0 - 24, 1); p.line(X1 - 16, Y0 - 20, X1 - 4, Y0 - 20, 1); p.line(X1 - 14, Y0 - 16, X1 - 6, Y0 - 16, 1)
    WC = (0, 9, 13, 14, 1, 15, 27, 25)
    windowpane(p, 100, 102, 16, 12, "tv", WC, r)
    windowpane(p, 124, 102, 16, 12, "plant", WC, r)
    windowpane(p, 172, 102, 16, 12, "dark", WC, r)
    p.rect(146, 104, 166, 117, 1); p.rect(146, 104, 166, 104, 8)                                          # balcony
    for x in range(146, 167, 3):
        p.line(x, 105, x, 117, 4)
    p.line(146, 108, 166, 108, 9)
    p.sprite(148, 99, "plant", {"l": 27, "g": 26, "p": 15}); p.sprite(158, 99, "fern", {"l": 27, "g": 26, "p": 15})
    p.rect(X0 + 4, 124, X1 - 4, 127, 21); p.rect(X0 + 4, 124, X1 - 4, 124, 22)                       # sign board
    p.glyphs(X0 + 10, 125, [0, 3, 5, 1, 6, 2, 4, 0], 23, big=False, gap=2)
    for i in range(0, X1 - X0 - 4, 6):                                                                 # awning
        p.rect(X0 + 2 + i, 129, X0 + 4 + i, 133, 16); p.rect(X0 + 5 + i, 129, X0 + 7 + i, 133, 11)
        p.px(X0 + 3 + i, 134, 16); p.px(X0 + 6 + i, 134, 11)
    for i, wx in enumerate((97, 117, 137, 157)):                                                       # shop windows w/ shelves
        p.rect(wx - 1, 136, wx + 15, G1 - 2, 0); p.rect(wx, 137, wx + 14, G1 - 3, 12)
        for sy in (140, 145):
            p.rect(wx, sy, wx + 14, sy, 14)
            for k in range(0, 14, 2):
                p.px(wx + k, sy - 1, (16, 20, 27, 29, 19)[(k + i + sy) % 5])
        p.dither(wx, 146, wx + 14, G1 - 3, 13, 8)
        p.line(wx + 7, 137, wx + 7, G1 - 3, 14)
    p.rect(177, 134, 189, G1, 0); p.rect(178, 135, 188, G1, 13); p.line(183, 135, 183, G1, 14); p.px(186, 142, 14)  # door
    p.glow([12, 13], 14, 15, 6, 3)
    p.rect(200, 118, 230, G1, 2); p.rect(200, 118, 230, 118, 7)                                         # vending alcove
    p.sprite(203, 134, "vending", {"k": 0, "c": 20, "d": 11, "b": 3, "h": 6, "e": 0})
    p.sprite(213, 134, "vending", {"k": 0, "c": 16, "d": 12, "b": 3, "h": 6, "e": 0})
    p.glow([20], 7, None, 8); p.glow([16], 17, None, 6)
    p.rect(232, 126, 236, G1, 1); p.rect(232, 126, 236, 126, 7)                                         # utility box
    p.sprite(240, G1 - 10, "bike", {"k": 0})
    p.sprite(262, G1 - 7, "bin", {"k": 0, "b": 21, "h": 8}); p.sprite(270, G1 - 7, "bin", {"k": 0, "b": 26, "h": 27})
    p.rect(0, 140, 88, 140, 1)                                                                          # fence
    for x in range(1, 88, 5):
        p.rect(x, 140, x + 1, G1, 1); p.px(x, 139, 6)
    for k, x in enumerate(range(4, 86, 11)):
        p.sprite(x, 143 + k % 2, "fern", {"l": 27, "g": 26, "p": 28})
    for px_, h in ((60, 82), (220, 86)):                                                                # poles
        p.rect(px_, G1 - h, px_ + 1, G1, 0)
        for dy, hw in ((4, 9), (11, 6)):
            p.rect(px_ - hw, G1 - h + dy, px_ + hw + 1, G1 - h + dy, 0)
            for ix in (-hw, -hw // 2, hw // 2 + 1, hw + 1):
                p.px(px_ + ix, G1 - h + dy - 1, 9)
        p.rect(px_ + 2, G1 - h + 16, px_ + 7, G1 - h + 24, 1); p.rect(px_ + 2, G1 - h + 16, px_ + 7, G1 - h + 16, 7)
    p.line(78, 98, 78, G1, 0); p.rect(70, 96, 82, 97, 0); p.rect(71, 98, 81, 98, 12)                    # streetlight
    for k in (0, 5, 10):
        catenary(p, -10, 66 + k, 60, 68 + k, 6, 0); catenary(p, 60, 68 + k, 220, 64 + k, 14, 0)
        catenary(p, 220, 64 + k, 310, 70 + k, 7, 0)
    p.rect(0, G1, LAYER_W["mid"], V - 1, 2)
    return p


def s1_life(p, t):
    """Per-frame inhabitants drawn into a copy of the mid layer."""
    for bx, by, ph in ((96, 79, 0), (104, 80, 3), (150, 83, 5), (176, 81, 2)):                        # birds on wires
        fl = (int(t * 6) + ph) % 17 == 0
        p.sprite(bx, by - (2 if fl else 0), "bird1" if fl else "bird0", {"k": 0})
    p.sprite(30, 132, "cat_sit0" if int(t * 2) % 3 else "cat_sit1", {"k": 0, "e": 19, "t": 0})       # cat on fence
    person(p, 209, G1, t * 0, 29, 13, walk=False, face=1)                                              # vending customer
    if int(t * 3) % 4 == 0:
        p.px(213, G1 - 8, 29)                                                                          # reaching arm
    ix = 98 + int((math.sin(t * .9) + 1) * 5)                                                          # shopkeeper inside
    p.rect(ix + 18, 139, ix + 21, 146, 15); p.rect(ix + 18, 137, ix + 21, 138, 15)
    for k in range(4):                                                                                 # drips off awning
        dy = int((t * 40 + k * 9) % 16)
        p.px(100 + k * 26, 135 + dy, 10)


def s1_front(p, t):
    """Foreground in view space (after reflection): car with lights, puddles."""
    cx = int(-70 + (t / 2.5) * 360)
    for k in range(26):                                                                                # headlight cone
        p.dither(cx + 32 + k, 158 - k // 6, cx + 33 + k, 162 + k // 6, 12, 6 - k // 6)
    p.sprite(cx, 150, "car", {"k": 0, "b": 3, "h": 11, "c": 22, "l": 30, "r": 16, "s": 21, "d": 0, "e": 7})
    p.rect(cx + 1, 162, cx + 32, 163, 1)
    for k in range(3):
        rad = (t * 7 + k * 4) % 12
        if rad > 1:
            p.ellipse(110, 200, rad * 1.8, rad * .55, 8, outline=True)
    p.ellipse(190, 214, 9, 3, 3, outline=True); p.rect(186, 214, 194, 214, 3)                            # manhole


def s1_near():
    p = Pix(LAYER_W["near"], V, T_)
    p.rect(300, 0, 306, V - 1, 31); p.rect(300, 0, 300, V - 1, 3)                                     # foreground pole
    for k in (0, 4):
        catenary(p, 200, 0 + k, 300, 30 + k, 4, 31)
    r = random.Random(9)
    p.line(0, 4, 40, 14, 31); p.line(0, 5, 40, 15, 31); p.line(22, 9, 52, 6, 31); p.line(30, 12, 44, 26, 31)   # branch + twigs
    for _ in range(16):                                                                                # leaf clusters
        cx, cy = r.randint(2, 60), r.randint(2, 28)
        rx, ry = r.randint(3, 6), r.randint(2, 3)
        p.ellipse(cx, cy, rx, ry, 31)
        for k in range(rx):                                                                            # lit leaf edges
            if r.random() < .6:
                p.px(cx - rx // 2 + k, cy - ry, 28)
        p.px(cx + rx, cy + ry - 1, 31); p.px(cx - rx - 1, cy, 31)
    return p


def pal1(t):
    pal = [hx(c) for c in P1]
    if math.sin(t * 9 + .7) * math.sin(t * 2.3 + 1.4) < -.6:
        pal[23] = hx("#6a2a3a")
    pal[24] = hx("#ffd04a") if int(t * 3) % 2 else hx("#0d3e50")
    pal[25] = [hx("#7ad8ff"), hx("#4ab0e8"), hx("#a8e8ff"), hx("#6ac0f0")][int(t * 7) % 4]
    return pal


# =================================================================== SHOT 2: noodle shop
P2 = ["#02030a", "#05091a", "#080e22", "#0c142c", "#121c3a", "#1c2a52", "#2c3e70", "#3a1018", "#6a1020", "#b01424",
      "#ff3a3a", "#ffd8c8", "#33280e", "#6a5410", "#b8961c", "#f0d020", "#fff4a0", "#1a1408", "#15c0d0", "#063440",
      "#2c4066", "#e01420", "#ff3a3a", "#3a6a3a", "#6aa04a", "#e8743a", "#f4a0c0", "#4a2a6a", "#b46aff", "#ffffff",
      "#22304a", "#2a3a8a"]
R2 = remap_table({16: 14, 15: 13, 14: 13, 13: 12, 10: 8, 22: 8, 21: 8, 11: 9, 9: 7, 8: 7, 18: 19, 28: 27, 26: 7, 25: 12,
                  29: 11, 31: 4, 24: 3, 23: 2, 17: 0, 12: 1, 7: 1, 19: 1, 27: 1, 20: 2, 30: 2},
                 {6: 4, 5: 3, 4: 2, 3: 1, 2: 1, 1: 0})
G2 = 176


def s2_far():
    p = Pix(LAYER_W["far"], V, T_)
    p.grad(0, G2, [3, 2, 1, 1, 0])
    for x0, x1, sd in ((0, 80, 61), (190, 270, 62)):
        rr = random.Random(sd); x = x0
        while x < x1:
            w, h = rr.randint(10, 18), rr.randint(80, 170)
            p.rect(x, G2 - h, x + w, G2, 2); p.rect(x, G2 - h, x + w, G2 - h, 4)
            for yy in range(G2 - h + 4, G2 - 10, 5):
                for xx in range(x + 2, x + w - 1, 3):
                    if rr.random() < .18:
                        p.px(xx, yy, 13 if rr.random() < .7 else 18)
            x += w + 2
    return p


def s2_mid():
    p = Pix(LAYER_W["mid"], V, T_)
    X0, X1 = 40, 250
    p.rect(X0, 0, X1, G2, 2)                                                                          # facade brick
    for y in range(0, G2, 4):
        p.rect(X0, y, X1, y, 3)
        for x in range(X0 + (y // 4 % 2) * 4, X1 + 1, 8):
            p.px(x, y + 1, 3); p.px(x, y + 2, 3)
    p.rect(X0, 0, X0, G2, 5); p.rect(X1, 0, X1, G2, 1)
    r = random.Random(3)
    WC = (1, 6, 14, 13, 3, 8, 24, 31)
    kinds = ["curtain", "dark", "blinds", "tv", "dark", "plant", "lamp", "dark", "curtain"]
    for row in range(2):                                                                               # upper floors
        for col in range(8):
            x, y = 50 + col * 25, 6 + row * 26
            windowpane(p, x, y, 15, 14, kinds[(col * 2 + row * 3) % len(kinds)], WC, r)
            if (col + row) % 3 == 0:                                                                  # balcony rail + laundry
                p.rect(x - 3, y + 16, x + 17, y + 16, 5)
                for xx in range(x - 3, x + 18, 3):
                    p.line(xx, y + 16, xx, y + 20, 4)
                p.rect(x - 3, y + 20, x + 17, y + 20, 5)
    p.sprite(53, 1, "ac", {"k": 0, "b": 3, "c": 5}); p.sprite(203, 27, "ac", {"k": 0, "b": 3, "c": 5})
    p.line(46, 0, 46, 92, 5); p.line(244, 0, 244, 92, 5)
    for x in (47, 245):
        for y in range(10, 92, 18):
            p.rect(x - 2, y, x + 1, y + 1, 4)
    p.poly([(24, 78), (145, 58), (266, 78), (266, 85), (24, 85)], 4)                                  # tiled eave
    for y in range(61, 85, 3):
        xl = 24 + max(0, (78 - y)) * 6; xr = 266 - max(0, (78 - y)) * 6
        p.line(xl, y, xr, y, 3)
        for x in range(int(xl) + (y % 2) * 3, int(xr), 6):
            p.px(x, y + 1, 5)
    p.line(24, 78, 145, 58, 6); p.line(145, 58, 266, 78, 6); p.rect(24, 85, 266, 86, 0)
    p.rect(24, 76, 28, 78, 6); p.rect(262, 76, 266, 78, 6)
    # big disc sign + pill sign
    p.ellipse(84, 52, 21, 21, 10); p.ellipse(84, 52, 18, 18, 11, outline=True); p.ellipse(84, 52, 22, 22, 8, outline=True)
    p.sprite(77, 55, "bowl", {"k": 7}); p.line(78, 43, 90, 53, 7); p.line(82, 42, 93, 52, 7)
    m = Image.new("1", (LAYER_W["mid"], V), 0)
    ImageDraw.Draw(m).rounded_rectangle([108, 40, 196, 66], 12, outline=1, width=2)
    p.a[np.asarray(m, bool)] = 22
    p.glyphs(118, 45, [0, 1, 2, 3, 4, 5, 6, 7], 11, big=True, gap=2)
    p.glyphs(117, 57, [0, 2, 1, 3, 5, 4, 2, 0, 1, 3, 5, 2], 11, big=False, gap=3)
    p.rect(214, 0, 232, 54, 21); p.rect(214, 0, 214, 54, 8); p.rect(232, 0, 232, 54, 8); p.rect(214, 54, 232, 54, 8)
    for k in range(5):
        p.glyphs(221, 4 + k * 10, [k + 1], 11, big=False)
    p.rect(10, 96, 34, 104, 1); p.rect(11, 97, 33, 103, 27); p.glyphs(13, 98, [2, 4, 1, 5], 28, big=False, gap=2)  # purple bar sign
    for i in range(8):
        p.rect(96 + i * 13, 92, 104 + i * 13, 97, 18); p.px(98 + i * 13, 94, 11); p.px(101 + i * 13, 94, 11)
    p.glow([10, 22, 21], 9, 7, 8, 4); p.glow([18], 19, None, 8); p.glow([28], 27, None, 8)
    for k in (0, 4):
        catenary(p, 0, 34 + k, 46, 50 + k, 6, 0); catenary(p, 244, 50 + k, 300, 30 + k, 6, 0)
    # shop front
    SX0, SX1 = 60, 224
    p.rect(SX0 - 4, 104, SX1 + 4, 109, 12); p.rect(SX0 - 4, 104, SX1 + 4, 104, 14)
    for i in range(SX1 - SX0 + 8):                                                                    # lantern string
        y = 103 + round(math.sin(i / (SX1 - SX0 + 8) * math.pi) * 4)
        p.px(SX0 - 4 + i, y, 0)
    for i in range(0, SX1 - SX0 + 8, 6):                                                              # striped awning
        p.rect(SX0 - 4 + i, 110, SX0 - 2 + i, 116, 15); p.rect(SX0 - 1 + i, 110, SX0 + 1 + i, 116, 17)
        p.px(SX0 - 3 + i, 117, 15)
    p.rect(SX0, 118, SX1, G2 - 1, 12)
    p.rect(SX0 + 2, 119, SX1 - 2, G2 - 3, 15)                                                         # warm interior
    p.dither(SX0 + 2, 119, SX1 - 2, 124, 16, 8)
    p.rect(SX0 + 2, 126, SX1 - 2, 126, 14)                                                            # shelf with bowls & bottles
    for i in range(0, SX1 - SX0 - 4, 7):
        p.rect(SX0 + 4 + i, 122, SX0 + 8 + i, 125, (14, 25, 26, 24, 13)[i % 5]); p.px(SX0 + 5 + i, 122, 16)
    for i, mx in enumerate(range(SX0 + 10, SX1 - 10, 30)):                                            # menu plaques
        p.rect(mx, 128, mx + 18, 136, 13); p.rect(mx, 128, mx + 18, 128, 16)
        p.glyphs(mx + 2, 130, [i, i + 1, i + 3], 17, big=False, gap=1)
    p.rect(SX0 + 2, 156, SX1 - 2, 160, 13); p.rect(SX0 + 2, 156, SX1 - 2, 156, 16)                    # counter
    p.rect(SX0 + 2, 161, SX1 - 2, G2 - 3, 12)
    for x in range(SX0 + 6, SX1 - 4, 8):
        p.line(x, 161, x, G2 - 3, 17)
    p.sprite(70, 158, "plant", {"l": 24, "g": 23, "p": 25})
    for x in (SX0, SX1):
        p.rect(x - 1, 118, x + 1, G2, 17)
    p.glow([15, 16], 14, 13, 6, 3)
    p.sprite(14, G2 - 10, "bike", {"k": 0}); p.sprite(234, G2 - 6, "crate", {"k": 0, "b": 12})
    p.sprite(242, G2 - 6, "crate", {"k": 0, "b": 12}); p.sprite(238, G2 - 12, "crate", {"k": 0, "b": 13})
    p.sprite(260, G2 - 7, "fern", {"l": 24, "g": 23, "p": 8}); p.sprite(270, G2 - 7, "plant", {"l": 24, "g": 23, "p": 8})
    p.rect(0, G2, LAYER_W["mid"], V - 1, 1)
    return p


def s2_life(p, t):
    cx = 140                                                                                          # cook + ladle + steam
    lad = int(math.sin(t * 5) * 3)
    p.rect(cx - 4, 140, cx + 4, 155, 0); p.rect(cx - 3, 133, cx + 2, 139, 0); p.rect(cx - 4, 130, cx + 3, 132, 11)
    p.line(cx + 4, 144, cx + 10, 146 + lad, 0); p.line(cx + 10, 146 + lad, cx + 10, 152, 0)
    p.rect(cx + 6, 151, cx + 20, 155, 0)                                                              # pot
    for k in range(9):
        sy = 150 - ((k * 4 + int(t * 14)) % 26)
        p.px(cx + 10 + int(math.sin(t * 3 + k) * 2), sy, 16)
        p.px(cx + 14 + int(math.cos(t * 2 + k) * 2), sy - 2, 16)
    for i, (sx, coat) in enumerate(((84, 31), (112, 25), (186, 30))):                                 # customers (back view)
        eat = (int(t * 2 + i * .7) % 3 == 0)
        dy = 1 if eat else 0
        p.sprite(sx - 3, G2 - 6, "stool", {"k": 0})
        p.rect(sx - 4, 146, sx + 4, G2 - 7, coat); p.rect(sx - 4, 146, sx - 4, G2 - 7, 0)
        p.rect(sx - 2, 139 + dy, sx + 2, 144 + dy, 0); p.rect(sx - 3, 140 + dy, sx + 3, 143 + dy, 0)
        if eat:
            p.rect(sx + 3, 147, sx + 7, 149, 13)                                                     # lifted bowl
    for i in range(5):                                                                                 # noren curtains sway
        nx = 196 + i * 0
    for k, nx in enumerate(range(SX := 64, 224, 32)):
        sway = int(math.sin(t * 2 + k) * 1.5)
        for yy in range(118, 132):
            shift = sway if yy > 124 else 0
            p.rect(nx + shift, yy, nx + 10 + shift, yy, 31)
        p.glyphs(nx + 4, 121, [k], 29, big=False)
    for k, lx in enumerate(range(62, 228, 22)):                                                       # lantern string bulbs
        y = 103 + round(math.sin((lx - 56) / 176 * math.pi) * 4)
        on = int(t * 4 + k) % 7 != 0
        p.rect(lx, y + 1, lx + 2, y + 4, 10 if on else 8); p.px(lx + 1, y + 2, 11 if on else 9)
    p.sprite(30, G2 - 5, "cat_sleep0" if int(t * 1.5) % 3 else "cat_sleep1", {"k": 0, "t": 0})
    for k in range(3):
        dy = int((t * 45 + k * 7) % 22)
        p.px(56 + k * 3, 87 + dy, 20)                                                                   # AC drip


def s2_front(p, t):
    p.ellipse(180, 214, 11, 3, 2, outline=True); p.rect(175, 214, 185, 214, 2)
    for x in range(0, V, 16):
        p.rect(x, G2 + 22, x + 1, G2 + 22, 2)
    for k in range(3):
        rad = (t * 6 + k * 4) % 12
        if rad > 1:
            p.ellipse(70, 210, rad * 1.8, rad * .5, 6, outline=True)


def s2_near(t):
    p = Pix(LAYER_W["near"], V, T_)
    px_ = int(330 - (t - CUTS[0]) / (CUTS[1] - CUTS[0]) * 380)                                       # passer-by, red umbrella
    person(p, px_, 232, t, 30, 25, umb=10, umb_hi=11, walk=True, face=-1, scale=1)
    p.rect(0, 0, 330, 2, 0)
    for k in (0, 3):
        catenary(p, 0, 6 + k, 330, 10 + k, 8, 0)
    p.rect(286, 0, 330, 14, 0); p.rect(288, 2, 328, 12, 9); p.glyphs(292, 4, [3, 1, 6, 0, 2], 11, big=False, gap=2)
    return p


def pal2(t):
    pal = [hx(c) for c in P2]
    if math.sin(t * 9 + 1.3) * math.sin(t * 2.3 + 2.6) < -.6:
        pal[10] = hx("#7a1020"); pal[22] = hx("#5a0c14")
    if math.sin(t * 7 + 4.1) * math.sin(t * 1.9 + 8.2) < -.55:
        pal[21] = hx("#5a0c14")
    if math.sin(t * 11 + 2) > .93:
        pal[28] = hx("#4a2a6a")
    return pal


# =================================================================== SHOT 3: night gantry + stalls
P3 = ["#020610", "#040c24", "#071834", "#0a2040", "#0c284c", "#12385e", "#1a4c7a", "#2a66a0", "#4a96d0", "#a0d4ff",
      "#9cff2a", "#2a6a10", "#ff3a4a", "#d4dae2", "#7af0e0", "#0a3a40", "#ff7a3c", "#3f6fa8", "#fff0a0", "#0b2a52",
      "#1c4f86", "#ff3a4a", "#1b5d90", "#1b5d90", "#ffb04a", "#6a3a1a", "#c060ff", "#3a1a5a", "#ffffff", "#e0e8f0",
      "#1a2a3a", "#f04a8a"]
R3 = remap_table({10: 11, 14: 15, 13: 5, 29: 5, 18: 24, 24: 25, 16: 25, 12: 0, 21: 0, 9: 6, 8: 5, 7: 4, 22: 3, 23: 3, 20: 19,
                  17: 2, 11: 1, 15: 1, 26: 27, 31: 27, 28: 9, 25: 1, 27: 1, 30: 1},
                 {6: 4, 5: 3, 4: 2, 3: 1, 2: 1, 1: 0, 19: 1})
G3 = 168


def s3_far():
    p = Pix(LAYER_W["far"], V, T_)
    p.grad(0, G3, [1, 1, 2, 3, 4, 5])
    for x0, x1, sd, hmax, col, top in ((0, 270, 71, 50, 4, 5), (0, 270, 72, 80, 2, 3)):             # two skyline depths
        rr = random.Random(sd); x = x0
        while x < x1:
            w, h = rr.randint(8, 16), rr.randint(16, hmax)
            p.rect(x, G3 - 14 - h, x + w, G3, col); p.rect(x, G3 - 14 - h, x + w, G3 - 14 - h, top)
            for _ in range(5):
                p.px(x + rr.randint(1, w - 1), G3 - 14 - rr.randint(3, h), 6 if col == 4 else 8)
            if rr.random() < .3:
                p.px(x + w // 2, G3 - 15 - h, 21)
            x += w + rr.randint(1, 3)
    X0, X1 = 150, 236                                                                                 # tower
    p.rect(X0, 14, X1, G3, 4); p.rect(X0 + 10, 4, X1 - 10, 14, 5); p.rect(X0 + 10, 4, X1 - 10, 4, 8)
    p.rect(X0, 14, X0, G3, 7); p.dither(X0 + 1, 14, X0 + 6, G3, 5, 8); p.dither(X1 - 6, 14, X1, G3, 3, 8)
    p.line(193, 4, 193, 0, 6); p.px(193, 0, 21)
    rr = random.Random(5)
    for row in range(22):
        for col in range(15):
            x, y = X0 + 6 + col * 5, 36 + row * 6
            v = rr.random()
            p.rect(x, y, x + 2, y + 3, 22 if v < .16 else 23 if v < .3 else 24 if v < .33 else 3)
    p.rect(X0 + 6, 18, X1 - 6, 30, 3); p.rect(X0 + 6, 18, X1 - 6, 18, 7); p.rect(X0 + 6, 30, X1 - 6, 30, 1)
    p.glyphs(X0 + 18, 21, [6, 2, 7, 1, 3], 8, big=True, gap=3)
    p.glow([8], 6, None, 6)
    return p


def s3_mid():
    p = Pix(LAYER_W["mid"], V, T_)
    p.rect(0, 52, 300, 55, 3); p.rect(0, 52, 300, 52, 7); p.rect(0, 56, 300, 56, 0)                    # monorail track
    for x in range(10, 300, 40):
        p.rect(x, 57, x + 3, 92, 2); p.rect(x, 57, x, 92, 5)
    gant = [(14, 96), (160, 78), (270, 124), (270, 134), (160, 92), (14, 110)]                         # gantry
    p.poly(gant, 2)
    p.line(14, 96, 160, 78, 7); p.line(160, 78, 270, 124, 7); p.line(14, 110, 160, 92, 1); p.line(160, 92, 270, 134, 1)
    for x in range(18, 268, 10):
        top = 96 - (x - 14) * 18 / 146 if x < 160 else 78 + (x - 160) * 46 / 110
        bot = 110 - (x - 14) * 18 / 146 if x < 160 else 92 + (x - 160) * 42 / 110
        p.line(x, top + 1, x + 5, bot - 1, 1); p.px(x, top + 1, 6); p.px(x + 2, top + 2, 6)
    for x in (40, 84, 128, 220):
        b = 110 - (x - 14) * 18 / 146 if x < 160 else 92 + (x - 160) * 42 / 110
        p.rect(x, b, x + 2, G3, 1); p.rect(x, b, x, G3, 4)
        p.line(x - 6, G3, x, b + 20, 1)
    p.ellipse(186, 116, 10, 10, 10, outline=True, width=2); p.line(186, 109, 186, 123, 10)            # green neon
    p.glyphs(200, 112, [3, 0, 4, 6], 10, big=True, gap=2)
    p.glow([10], 11, 2, 8, 4)
    for k in range(5):                                                                                 # warehouse doors
        p.rect(20 + k * 22, 128, 36 + k * 22, G3 - 1, 2); p.rect(20 + k * 22, 128, 36 + k * 22, 128, 5)
        for yy in range(130, G3, 3):
            p.rect(20 + k * 22, yy, 36 + k * 22, yy, 1)
    SX = 176                                                                                           # food stalls
    p.rect(SX, 136, 292, 141, 5)
    for i in range(0, 117, 6):
        p.rect(SX + i, 136, SX + 2 + i, 141, 26 if (i // 6) % 4 == 0 else 7); p.px(SX + 1 + i, 142, 7)
    for i in range(4):
        x = SX + 4 + i * 28
        p.rect(x - 1, 144, x + 22, 157, 15); p.rect(x, 145, x + 21, 156, 14)
        p.glyphs(x + 3, 147, [i, i + 2, i + 4], 15, big=False, gap=2)
        p.dither(x, 152, x + 21, 156, 9, 4)
        p.rect(x - 1, 158, x + 22, G3 - 1, 30); p.rect(x - 1, 158, x + 22, 158, 13)
    p.glow([14], 15, None, 8); p.glow([26], 27, None, 6)
    p.sprite(SX + 10, G3 - 6, "stool", {"k": 0}); p.sprite(SX + 66, G3 - 6, "stool", {"k": 0})
    for lx in (8, 70, 150):                                                                            # lamps
        p.rect(lx, 110, lx + 1, G3, 2); p.rect(lx - 5, 108, lx + 6, 109, 20); p.rect(lx - 4, 108, lx + 5, 108, 9)
        cone = p.mask_poly([(lx - 3, 110), (lx + 4, 110), (lx + 16, G3), (lx - 15, G3)]) & np.isin(p.a, [T_, 1, 2])
        p.a[cone & p.dmask(3)] = 19
    p.sprite(135, G3 - 7, "cone", {"o": 16, "w": 29, "k": 0}); p.sprite(143, G3 - 7, "cone", {"o": 16, "w": 29, "k": 0})
    p.rect(0, G3, 300, V - 1, 1)
    return p


def s3_life(p, t):
    tt = t - CUTS[1]
    mx = int(320 - tt * 150)                                                                           # monorail passing
    for car in range(3):
        x = mx + car * 46
        p.rect(x, 38, x + 42, 51, 6); p.rect(x, 38, x + 42, 38, 8); p.rect(x + 1, 51, x + 41, 51, 3)
        p.rect(x + 2, 41, x + 40, 46, 24)
        for wx in range(x + 2, x + 41, 6):
            p.px(wx, 41, 6); p.line(wx, 41, wx, 46, 6)
        for k, sx in enumerate(range(x + 4, x + 38, 9)):
            if (k + car) % 3:
                p.rect(sx, 43, sx + 2, 46, 25); p.rect(sx, 42, sx + 1, 42, 25)                          # passengers
        p.rect(x + 2, 48, x + 40, 48, 26)
    if mx < 300:
        p.rect(mx - 2, 42, mx - 1, 44, 18)
    tx = 96                                                                                             # truck + driver + exhaust
    p.rect(tx, 140, tx + 52, G3 - 5, 3); p.rect(tx, 140, tx + 52, 140, 7); p.rect(tx, 140, tx, G3 - 5, 0)
    for x in range(tx + 6, tx + 52, 6):
        p.line(x, 142, x, G3 - 7, 2)
    p.ellipse(tx + 26, 152, 8, 6, 6, outline=True)
    p.rect(tx + 53, 146, tx + 68, G3 - 5, 13); p.rect(tx + 55, 148, tx + 64, 154, 6); p.rect(tx + 53, 146, tx + 68, 146, 28)
    p.rect(tx + 58, 150, tx + 60, 154, 0); p.px(tx + 59, 149, 0)
    p.rect(tx + 66, 157, tx + 68, 159, 18); p.rect(tx, 156, tx + 1, 158, 12)
    for wx in (tx + 10, tx + 40, tx + 60):
        p.sprite(wx - 4, G3 - 7, "wheel", {"k": 0, "m": 4, "h": 7})
    for k in range(5):
        ex = tx - 3 - ((k * 3 + int(t * 10)) % 14)
        p.px(ex, G3 - 6 - k % 2 - (k * 3 + int(t * 10)) % 14 // 4, 5)
    vx = 210                                                                                           # vendor + steam
    p.rect(vx - 3, 147, vx + 3, 157, 0); p.rect(vx - 2, 142, vx + 2, 146, 0); p.rect(vx - 3, 141, vx + 3, 141, 29)
    p.line(vx + 3, 150, vx + 8, 152 + int(math.sin(t * 6) * 2), 0)
    for k in range(8):
        sy = 156 - ((k * 3 + int(t * 12)) % 20)
        p.px(vx + 12 + int(math.sin(t * 3 + k) * 2), sy, 29)
    person(p, 250, G3, t, 31, 24, umb=17, umb_hi=9, walk=False, face=-1)                              # waiting customer
    wx = int(20 + tt * 14)
    person(p, wx, G3, t, 30, 24, umb=8, umb_hi=9, walk=True, face=1)                                   # walker
    p.sprite(162, G3 - 11, "cat_sit0" if int(t * 2) % 3 else "cat_sit1", {"k": 0, "e": 10, "t": 0})


def s3_front(p, t):
    p.ellipse(120, 210, 10, 3, 2, outline=True)
    for x in range(0, V, 22):
        p.rect(x, 196, x + 10, 196, 4)


def s3_near(t):
    p = Pix(LAYER_W["near"], V, T_)
    p.rect(0, 226, 330, 228, 30); p.rect(0, 226, 330, 226, 6)                                         # foreground railing
    for x in range(0, 330, 12):
        p.rect(x, 226, x + 1, V - 1, 30)
    p.rect(0, 0, 6, V - 1, 30); p.rect(6, 0, 6, V - 1, 5)
    for k in (0, 4):
        catenary(p, 6, 20 + k, 330, 4 + k, 10, 0)
    return p


def pal3(t):
    pal = [hx(c) for c in P3]
    if math.sin(t * 6 + 2.2) * math.sin(t * 2.3 + 4.4) < -.6:
        pal[10] = hx("#2a6a10")
    pal[21] = hx("#ff3a4a") if int(t * 1.6) % 2 == 0 else hx("#2a0a14")
    tw = int(t * 2.5) % 2
    pal[22], pal[23] = (hx("#4aa0d8"), hx("#0a2440")) if tw else (hx("#0a2440"), hx("#4aa0d8"))
    if int(t * 3) % 5 == 0:
        pal[14] = hx("#3ab8b0")
    return pal


# =================================================================== assembly
SHOTS = [
    dict(far=s1_far, mid=s1_mid, near=lambda t: _cache("s1n", s1_near), life=s1_life, front=s1_front, pal=pal1, G=G1,
         remap=R1, rain=(8, 9), mist=(9, 126, G1 + 2)),
    dict(far=s2_far, mid=s2_mid, near=s2_near, life=s2_life, front=s2_front, pal=pal2, G=G2,
         remap=R2, rain=(20, 6), mist=(20, G2 - 6, G2 + 4)),
    dict(far=s3_far, mid=s3_mid, near=s3_near, life=s3_life, front=s3_front, pal=pal3, G=G3,
         remap=R3, rain=(17, 8), mist=(19, G3 - 10, G3 + 3)),
]
_C = {}


def _cache(k, fn):
    if k not in _C:
        _C[k] = fn()
    return _C[k]


def frame_indices(t):
    s = 0 if t < CUTS[0] else 1 if t < CUTS[1] else 2
    t0 = (0, *CUTS)[s]
    S = SHOTS[s]
    drift = (t - t0) * 6
    view = Pix(V, V, 0)
    far = _cache(f"f{s}", S["far"])
    compose(view.a, far.a, int(drift * SPEED["far"]))
    mid = _cache(f"m{s}", S["mid"])
    live = Pix(mid.w, mid.h, T_); live.a = mid.a.copy()
    S["life"](live, t)
    compose(view.a, live.a, int(drift * SPEED["mid"]))
    view.reflect(S["G"], t, S["remap"], depth=48)
    G = S["G"]
    view.rect(0, G, V, G, {0: 9, 1: 5, 2: 6}[s]); view.rect(0, G + 1, V, G + 1, {0: 5, 1: 2, 2: 2}[s])
    view.dither(0, G + 2, V, V, {0: 3, 1: 2, 2: 2}[s], 2, where=view.a < 4)
    S["front"](view, t)
    mc, y0, y1 = S["mist"]
    E.mist(view, y0, y1, mc, t, 1)
    rc, _ = S["rain"]
    rain_layer(view, t, 10 + s, 60, {0: 6, 1: 4, 2: 5}[s], 60, 2, G, splash=False)                     # far rain (dim, slow)
    near = S["near"](t)
    compose(view.a, near.a, int(drift * SPEED["near"]))
    rain_layer(view, t, 20 + s, 75, rc, 140, 4, G)                                                     # near rain (bright, fast)
    return view.a, np.array(S["pal"](t), np.uint8)


def frame(t):
    idx, pal = frame_indices(t)
    return Image.fromarray(np.repeat(np.repeat(pal[idx], UP, 0), UP, 1))


def video(out):
    sp = importlib.util.spec_from_file_location("neon_basic", os.path.join(_here, "render_neon_offline.py"))
    basic = importlib.util.module_from_spec(sp); sp.loader.exec_module(basic)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav"); basic.audio(wav)
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{V * UP}x{V * UP}", "-r", str(FPS),
               "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-tune", "animation", "-crf", "12",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", str(DUR), "-movflags", "+faststart", out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(int(round(DUR * FPS))):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close()
        if p.wait():
            sys.exit("ffmpeg failed")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "still":
        os.makedirs(sys.argv[2], exist_ok=True)
        for s_ in sys.argv[3:]:
            frame(float(s_)).save(os.path.join(sys.argv[2], f"s{float(s_):.2f}.png"))
    elif len(sys.argv) == 3 and sys.argv[1] == "video":
        video(sys.argv[2])
    else:
        sys.exit(__doc__)
