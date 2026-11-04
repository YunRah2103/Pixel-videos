#!/usr/bin/env python3
"""Hand-authored indexed pixel-art film: rainy neon street, 3 shots, 8.2 s, 30 fps, 720x720.

Built like real pixel art, not filtered vector art:
  * every pixel is a palette index on a 180x180 grid (4x nearest upscale) - nothing is ever blended or blurred;
  * shading = ordered dither patterns, glow = dithered halo rings, reflections = index remap tables;
  * props/characters are hand-placed sprite grids (see SPRITES) with 1px outlines and cluster shading;
  * motion = whole-pixel movement, sprite frame swaps and palette cycling (neon flicker, window twinkle).

  python3 scripts/pixel_neon.py still OUT_DIR T [T ...]
  python3 scripts/pixel_neon.py video OUT.mp4
  python3 scripts/pixel_neon.py sheet OUT.png        # sprite sheet for editing in Pixelorama/Aseprite
"""
import importlib.util, math, os, random, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw

VIEW = 180
BIG = 240
H = 180
UP = 4
FPS = 30
DUR = 8.2
CUTS = (2.5, 5.53)
START = (0, 30, 40)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]])


def hx(s):
    return [int(s[i:i + 2], 16) for i in (1, 3, 5)]


# ----------------------------------------------------------------- sprites (hand-placed pixels)
SPRITES = {
    "pine": ["...a...", "...a...", "..aab..", "..aab..", ".aaabb.", ".aaaab.", "aaaaabb", "..aab..", "...c..."],
    "ac": ["kkkkkkkkk", "kbbbbbbbk", "kbcbcbcbk", "kbbbbbbbk", "kbcbcbcbk", "kkkkkkkkk", ".k.....k."],
    "vending": ["kkkkkkkkk", "kcccccccк".replace("к", "k"), "kcdcdcdck", "kcccccccк".replace("к", "k"), "kcdcdcdck", "kcccccccк".replace("к", "k"),
                "kbbbbbbbk", "kbhhhhhbk", "kbbbbbbbk", "kbeeeeebk", "kbbbbbbbk", "kbbbbbbbk", "kbbbebbbk", "kkkkkkkkk"],
    "car": ["...........kkkkkkkkkkkk.........",
            "..........khbbbbbkbbbbbbk.......",
            ".........khbbbbbbkbbbbbbbk......",
            ".....kkkkkkkkkkkkkkkkkkkkkkkk...",
            "...kkhhhhhhhhhhhhhhhhhhhhhhhhkk.",
            "..kcccccccccccccccccccccccccccck",
            ".lcccccccccccckcccccccccccccccrk",
            "kccccssssccccckccccccccssssccccc",
            "kcccsddddsccccccccccccsddddsccck",
            ".kkksdeedskkkkkkkkkkkksdeedskkk.",
            "....sdeeds............sdeeds....",
            ".....sdds..............sdds....."],
    "wheel": ["..kkkkk..", ".kkkkkkk.", "kkkmmmkkk", "kkmmhmmkk", "kkkmmmkkk", ".kkkkkkk.", "..kkkkk.."],
    "bowl": ["kkkkkkkkkkkkkk", ".kkkkkkkkkkkk.", "..kkkkkkkkkk..", "...kkkkkkkk...", "....kkkkkk....", "...kkkkkkkk..."],
    "lantern": ["..kkkk..", ".rrrrrr.", "rrhrrrrr", "rhrrrrdr", "rrrrrrdr", "rhrrrrdr", "rrrrrrdr", "rrhrrrrr", ".rrrrrr.", "..kkkk..", "...kk...", "...k...."],
    "cook0": ["...kkkkkk...", "..kkkkkkkk..", "...kkkkkk...", "....kkkk....", "....kkkk....", "...kkkkkk...", "..kkkkkkkk..",
              ".kkkkkkkkkk.", "kkkkkkkkkkkk", "kkkkkkkkkkkk", "kkkkkkkkkkkk", "kkkkkkkkkkkk", "kkkkkkkkkkkk", "kkkkkkkkkkkk"],
    "cook1": ["...kkkkkk...", "..kkkkkkkk..", "...kkkkkk...", "....kkkk....", "....kkkk...k", "...kkkkkk.kk", "..kkkkkkkkk.",
              ".kkkkkkkkk..", "kkkkkkkkkkk.", "kkkkkkkkkkkk", "kkkkkkkkkkkk", "kkkkkkkkkkkk", "kkkkkkkkkkkk", "kkkkkkkkkkkk"],
    "walker0": ["....hhhhh....", "..uuuuuuuuu..", ".uuuuuuuuuuu.", "uuuuuuuuuuuuu", "s.s.s.k.s.s.s", "......k......", ".....kkk.....",
                ".....kkk.....", "....kkkkk....", "....kkkkk....", "....kkkkk....", "....kkkkk....", ".....k.k.....", "....k...k....", "....k...k...."],
    "walker1": ["....hhhhh....", "..uuuuuuuuu..", ".uuuuuuuuuuu.", "uuuuuuuuuuuuu", "s.s.s.k.s.s.s", "......k......", ".....kkk.....",
                ".....kkk.....", "....kkkkk....", "....kkkkk....", "....kkkkk....", "....kkkkk....", ".....kk......", ".....k.k.....", "......k......"],
    "splash0": [".a.", "..."], "splash1": ["a.a", ".a."], "splash2": ["a...a", "....."],
}

# original made-up glyphs (not a real script): 5x7 for big neon, 3x5 for small
G57 = [["#####", "..#..", "..#..", "#####", "..#.#", ".#..#", "#...#"], ["#...#", "#####", "#...#", "..#..", "#####", "#...#", "#####"],
       ["####.", "...#.", "#####", ".#...", ".####", "....#", "#####"], ["#.#.#", "#.#.#", "#####", "..#..", ".###.", "..#..", "#####"],
       ["..#..", "#####", "#...#", "#...#", "#####", "..#..", ".#.#."], ["#####", "#....", "####.", "#...#", "#...#", "####.", "#...."],
       [".###.", "#...#", "..##.", ".#...", "#####", "...#.", "..#.."], ["#..#.", "####.", "#..##", "#..#.", "####.", "...#.", "#####"]]
G35 = [["###", "..#", "###", "#..", "###"], ["#.#", "###", "..#", "#.#", "###"], ["##.", ".##", "#.#", "##.", ".##"], ["###", "#.#", "#.#", "###", "..#"],
       ["#..", "###", ".#.", "###", "#.."], [".#.", "###", "#.#", ".#.", "###"]]


class Pix:
    """Indexed-colour canvas. Values are palette indices; colour only exists at the very end."""

    def __init__(self, w, h, fill=0):
        self.w, self.h = w, h
        self.a = np.full((h, w), fill, np.uint8)

    def rect(self, x0, y0, x1, y1, c):
        x0, x1 = sorted((int(x0), int(x1))); y0, y1 = sorted((int(y0), int(y1)))
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, self.w - 1), min(y1, self.h - 1)
        if x1 >= x0 and y1 >= y0:
            self.a[y0:y1 + 1, x0:x1 + 1] = c

    def px(self, x, y, c):
        x, y = int(x), int(y)
        if 0 <= x < self.w and 0 <= y < self.h:
            self.a[y, x] = c

    def line(self, x0, y0, x1, y1, c):
        x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.px(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    def mask_poly(self, pts):
        m = Image.new("1", (self.w, self.h), 0)
        ImageDraw.Draw(m).polygon([(int(x), int(y)) for x, y in pts], fill=1)
        return np.asarray(m, bool)

    def poly(self, pts, c):
        self.a[self.mask_poly(pts)] = c

    def dmask(self, level):
        """level/16 coverage ordered-dither mask for the whole canvas."""
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        return BAYER[yy % 4, xx % 4] < level

    def dither(self, x0, y0, x1, y1, c, level=8, where=None):
        m = np.zeros_like(self.a, bool)
        x0, x1 = sorted((int(x0), int(x1))); y0, y1 = sorted((int(y0), int(y1)))
        m[max(0, y0):max(0, y1 + 1), max(0, x0):max(0, x1 + 1)] = True
        m &= self.dmask(level)
        if where is not None:
            m &= where
        self.a[m] = c

    def grad(self, y0, y1, idx):
        """Vertical banded gradient, ordered-dithered between neighbouring palette indices."""
        n = len(idx) - 1
        for y in range(y0, y1):
            u = (y - y0) / max(1, y1 - y0 - 1) * n
            lo = min(int(u), n - 1); f = u - lo
            row = np.where(BAYER[y % 4, np.arange(self.w) % 4] < f * 16, idx[lo + 1], idx[lo])
            self.a[y] = row

    def ellipse(self, cx, cy, rx, ry, c, outline=False, width=1):
        yy, xx = np.mgrid[0:self.h, 0:self.w]
        d = ((xx - cx) / (rx + .5)) ** 2 + ((yy - cy) / (ry + .5)) ** 2
        m = d <= 1
        if outline:
            m &= ((xx - cx) / max(.5, rx + .5 - width)) ** 2 + ((yy - cy) / max(.5, ry + .5 - width)) ** 2 > 1
        self.a[m] = c

    def sprite(self, x, y, name, key, flip=False):
        for j, row in enumerate(SPRITES[name]):
            row = row[::-1] if flip else row
            for i, ch in enumerate(row):
                if ch in key:
                    self.px(x + i, y + j, key[ch])

    def glyphs(self, x, y, seq, c, big=True, gap=1):
        font = G57 if big else G35
        for n, g in enumerate(seq):
            pat = font[g % len(font)]
            for j, row in enumerate(pat):
                for i, ch in enumerate(row):
                    if ch == "#":
                        self.px(x + n * (len(pat[0]) + gap) + i, y + j, c)

    def glow(self, src, ring1, ring2=None, l1=8, l2=4):
        """Pixel-art halo: dithered rings grown from pixels of the given indices (no blur)."""
        m = np.isin(self.a, src)
        def grow(k):
            g = k.copy()
            g[1:] |= k[:-1]; g[:-1] |= k[1:]; g[:, 1:] |= k[:, :-1]; g[:, :-1] |= k[:, 1:]
            return g
        r1 = grow(m) & ~m
        r2 = grow(grow(m | r1)) & ~(m | r1)
        self.a[r1 & self.dmask(l1)] = ring1
        if ring2 is not None:
            self.a[r2 & self.dmask(l2)] = ring2

    def reflect(self, water, t, remap, gaps=3, depth=999):
        """Wet-ground mirror: rows mirrored about the waterline, wobbled by whole pixels, indices remapped darker."""
        for y in range(water + 1, self.h):
            src = 2 * water - y
            if src < 0 or y - water > depth or (y - water) % gaps == gaps - 1:
                continue
            sh = int(round(math.sin(y * .8 + t * 3.0) * (1 if y - water < 12 else 2)))
            row = np.roll(self.a[src], sh)
            self.a[y] = remap[row]


def remap_table(pairs, default_down):
    tab = np.arange(256, dtype=np.uint8)
    for k, v in default_down.items():
        tab[k] = v
    for k, v in pairs.items():
        tab[k] = v
    return tab


def catenary(p, x0, y0, x1, y1, sag, c):
    for x in range(int(x0), int(x1) + 1):
        u = (x - x0) / max(1, x1 - x0)
        p.px(x, round(y0 + (y1 - y0) * u + math.sin(u * math.pi) * sag), c)


def rain(p, t, seed, n, c, ground, speed=95):
    r = random.Random(seed)
    for _ in range(n):
        x0, y0, v = r.uniform(0, BIG), r.uniform(0, H), r.uniform(.8, 1.2)
        y = int((y0 + t * speed * v) % (H + 6)) - 6
        x = int(x0 + y / 3) % BIG
        for k in range(3):
            p.px(x + (k + y % 3) // 3, y + k, c)
    for i in range(n // 4):
        x, y = r.randrange(BIG), r.randrange(ground + 4, H - 2)
        ph = int((t * 10 + r.random() * 9)) % 9
        if ph < 3:
            p.sprite(x - 2 + (ph < 2), y, f"splash{ph}", {"a": c})


def mist(p, y0, y1, c, t, level=2):
    sh = int(t * 4)
    m = np.zeros_like(p.a, bool)
    m[y0:y1] = True
    yy, xx = np.mgrid[0:p.h, 0:p.w]
    band = (np.sin((xx + sh) / 13.0) + np.sin((xx - sh) / 29.0 + yy / 7.0)) > .6
    p.a[m & band & p.dmask(level)] = c


# ----------------------------------------------------------------- shot 1: teal dusk roadside
P1 = ["#061c26", "#0a2c3a", "#0b3a4d", "#0e4a60", "#126078", "#1a7890", "#2a90a6", "#48aabb", "#7cc8d2", "#c8ecee",
      "#f2e3a1", "#c9953a", "#ff4a5a", "#8a1a30", "#e0b43c", "#5fd0e0", "#2a4e5e", "#7fa5b5", "#fff8e0", "#ff7a8a", "#e0b43c"]
R1 = remap_table({10: 11, 18: 10, 9: 7, 12: 13, 19: 13, 14: 11, 20: 11, 15: 6, 17: 5, 16: 2, 11: 2, 13: 1},
                 {0: 0, 1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 3, 7: 3, 8: 4, 9: 5})


def shot_roadside(t):
    G = 112
    p = Pix(BIG, H)
    p.grad(0, G, [3, 4, 5, 6, 7])
    for cx, cy, cw in ((10, 14, 50), (96, 30, 36), (170, 8, 46), (50, 50, 30)):            # stepped clouds
        x = cx + int(t * 3)
        p.rect(x + 4, cy, x + cw - 6, cy, 8); p.rect(x, cy + 1, x + cw, cy + 2, 7)
        p.rect(x + 2, cy + 3, x + cw - 3, cy + 3, 6); p.dither(x + 3, cy + 4, x + cw - 5, cy + 4, 6, 8)
    rr = random.Random(21); x = 150                                                           # far blocks
    while x < BIG:
        w, h = rr.randint(6, 11), rr.randint(10, 30)
        p.rect(x, G - 12 - h, x + w, G - 10, 4)
        for _ in range(2):
            p.px(x + rr.randint(1, w - 1), G - 12 - rr.randint(2, h), 14)
        x += w + rr.randint(1, 3)
    tower = [(100, G), (118, 30), (150, 9), (205, 26), (230, G)]                              # tower
    p.poly(tower, 1)
    lit = p.mask_poly([(165, 11), (205, 26), (230, G), (176, G)])
    term = p.mask_poly([(158, 11), (205, 26), (230, G), (168, G)]) & ~lit
    p.a[lit] = 2; p.a[term & p.dmask(8)] = 2
    for x in range(110, 176, 5):                                                              # ribs
        p.line(x, G - 1, 118 + (x - 110) * .55, 34 + (x - 110) * .1, 0)
    p.line(150, 9, 205, 26, 6); p.line(205, 26, 230, G, 5); p.line(118, 30, 150, 9, 3)
    for x in range(132, 225):                                                                 # red ring
        y = 62 - round(17 * math.sin((x - 132) / 93 * math.pi))
        if p.a[y, x] in (1, 2):
            p.px(x, y, 12); p.px(x, y + 1, 13)
    r = random.Random(4)
    for _ in range(40):
        x, y = r.randint(122, 222), r.randint(48, 104)
        if p.a[y, x] in (1, 2):
            p.px(x, y, 20 if r.random() < .3 else 14)
    p.glow([12], 13, None, 6)
    p.poly([(0, 98), (30, 85), (65, 92), (100, 88), (100, G), (0, G)], 2)                    # hills + pines
    p.line(0, 98, 30, 85, 3); p.line(30, 85, 65, 92, 3)
    r = random.Random(8)
    for x in range(-2, 100, 4):
        top = 98 - (x * 13 // 30 if x < 30 else (13 - (x - 30) * 7 // 35 if x < 65 else 6))
        p.sprite(x, top - 6 + r.randint(-2, 2), "pine", {"a": 1, "b": 3, "c": 0})
    for px_, hgt in ((35, 60), (131, 58), (212, 62)):                                         # poles
        p.line(px_, G - hgt, px_, G, 0)
        for dy, hw in ((4, 7), (10, 5)):
            p.line(px_ - hw, G - hgt + dy, px_ + hw, G - hgt + dy, 0)
            for ix in (-hw, hw):
                p.px(px_ + ix, G - hgt + dy - 1, 7)
    for k in (0, 6):
        for a, b in ((-10, 35), (35, 131), (131, 212), (212, 250)):
            catenary(p, a, 56 + k + (a % 7), b, 56 + k + (b % 7), 7, 0)
    # shop
    p.rect(65, 84, 131, G, 1); p.dither(65, 85, 131, G, 2, 4)
    p.rect(63, 80, 133, 83, 3); p.rect(63, 80, 133, 80, 7); p.rect(63, 84, 133, 84, 0)
    p.sprite(72, 73, "ac", {"k": 0, "b": 3, "c": 5})
    p.rect(88, 72, 120, 79, 0); p.glyphs(90, 73, [0, 3, 5, 1, 6], 19, big=False, gap=1)   # roof sign
    for i, wx in enumerate((69, 84, 99, 114)):
        p.rect(wx - 1, 90, wx + 11, 104, 0); p.rect(wx, 91, wx + 10, 103, 10)
        p.line(wx + 5, 91, wx + 5, 103, 11); p.line(wx, 97, wx + 10, 97, 11)
        p.rect(wx, 91, wx + 1, 103 - (i % 2) * 4, 11); p.px(wx + 8, 92, 18); p.px(wx + 9, 92, 18)
        p.rect(wx - 1, 105, wx + 11, 105, 7)
    for i in range(0, 66, 4):
        p.rect(65 + i, 86, 66 + i, 88, 6); p.px(65 + i, 89, 6)
    p.glow([10], 11, None, 4)
    p.rect(132, 92, 150, G, 2); p.rect(132, 92, 150, 92, 6)
    p.sprite(137, 98, "vending", {"k": 0, "c": 15, "d": 9, "b": 3, "h": 6, "e": 0})
    p.glow([15], 6, None, 8)
    p.rect(0, 103, 64, 103, 1)
    for x in range(2, 64, 6):
        p.line(x, 103, x, G, 1)
    p.sprite(8, 100, "car", {"k": 0, "b": 3, "h": 9, "c": 17, "l": 18, "r": 12, "s": 16, "d": 0, "e": 5})
    p.rect(0, G, BIG, H, 2)
    p.reflect(G, t, R1, depth=44)
    p.rect(0, G, BIG, G, 8); p.rect(0, G + 1, BIG, G + 1, 5)
    p.dither(0, G + 2, BIG, H, 3, 2)
    for x in range(0, BIG, 20):
        p.rect(x, 132, x + 9, 132, 6)
    for k in range(3):                                                                         # ripples
        rad = (t * 7 + k * 4) % 12
        if rad > 1:
            p.ellipse(84, 152, rad * 1.6, rad * .5, 6, outline=True)
    mist(p, 104, G + 2, 6, t, 1)
    rain(p, t, 1, 110, 8, G)
    return p


def pal_roadside(t):
    pal = [hx(c) for c in P1]
    if math.sin(t * 9 + .7) * math.sin(t * 2.3 + 1.4) < -.6:
        pal[19] = hx("#5a2a33")
    pal[20] = hx("#e0b43c") if int(t * 3) % 2 else hx("#0b3a4d")
    return pal


# ----------------------------------------------------------------- shot 2: neon noodle shop at night
P2 = ["#02040c", "#060b1a", "#0a0f1f", "#101830", "#1a2444", "#2a3a6a", "#3a1019", "#7a1020", "#c0141e", "#ff3a3a",
      "#ffd8c8", "#3b3414", "#8a7a10", "#d8c030", "#f4e11c", "#fff6a0", "#16130a", "#17bfd0", "#06323a", "#2c4066", "#e01420", "#ff3a3a"]
R2 = remap_table({14: 12, 15: 13, 13: 11, 12: 11, 9: 7, 21: 7, 10: 8, 20: 7, 8: 6, 7: 6, 17: 18, 18: 1, 16: 0, 11: 1, 6: 0, 19: 2},
                 {5: 3, 4: 2, 3: 1, 2: 1, 1: 0})


def shot_shop(t):
    G = 140
    p = Pix(BIG, H)
    p.grad(0, H, [2, 1, 1, 0])
    for x0, x1, sd in ((0, 39, 33), (205, BIG, 34)):                                          # side blocks
        rr = random.Random(sd); x = x0
        while x < x1:
            w, h = rr.randint(7, 13), rr.randint(45, 105)
            p.rect(x, G - h, x + w, G, 1); p.rect(x, G - h, x + w, G - h, 3)
            for _ in range(3):
                yy = G - rr.randint(6, h - 4); xx = x + rr.randint(1, max(1, w - 3))
                p.rect(xx, yy, xx + 1, yy + 2, 11 if rr.random() < .6 else 18)
            x += w + 1
    p.rect(40, 0, 204, G, 2)                                                                  # facade + brickwork
    for y in range(0, G, 4):
        p.rect(40, y, 204, y, 3)
        for x in range(40 + (y // 4 % 2) * 4, 205, 8):
            p.px(x, y + 1, 3); p.px(x, y + 2, 3)
    p.rect(40, 0, 40, G, 4); p.rect(204, 0, 204, G, 1)
    for row in range(2):                                                                      # upper windows
        for col in range(7):
            x, y = 50 + col * 22, 6 + row * 18
            p.rect(x - 1, y - 1, x + 12, y + 10, 1)
            lit = (col * 3 + row * 5) % 4 == 0
            p.rect(x, y, x + 11, y + 9, 12 if lit else 3)
            p.line(x + 6, y, x + 6, y + 9, 1)
            if lit:
                p.rect(x, y, x + 2, y + 9, 11); p.px(x + 9, y + 1, 13)
            p.rect(x - 1, y + 10, x + 12, y + 10, 4)
    p.poly([(26, 75), (122, 56), (218, 75), (218, 81), (26, 81)], 3)                          # tiled eave
    for y in range(59, 81, 3):
        p.line(26 + (75 - y) * 5 if y < 75 else 26, y, 218 - (75 - y) * 5 if y < 75 else 218, y, 2)
    p.line(26, 75, 122, 56, 5); p.line(122, 56, 218, 75, 5); p.rect(26, 81, 218, 82, 0)
    for x in range(28, 218, 6):
        p.px(x, 80, 4)
    # disc sign with bowl emblem
    p.ellipse(77, 53, 17, 17, 9); p.ellipse(77, 53, 15, 15, 10, outline=True); p.ellipse(77, 53, 18, 18, 7, outline=True)
    p.sprite(70, 55, "bowl", {"k": 6}); p.line(73, 46, 82, 53, 6); p.line(76, 45, 84, 52, 6)
    for i, sx in enumerate((72, 77, 82)):
        for k in range(5):
            p.px(sx + ((k + int(t * 6) + i) % 4 in (1, 2)), 50 - k, 10)
    m = Image.new("1", (BIG, H), 0)                                                            # pill sign
    ImageDraw.Draw(m).rounded_rectangle([96, 43, 162, 66], 10, outline=1, width=2)
    p.a[np.asarray(m, bool)] = 21
    p.glyphs(104, 47, [0, 1, 2, 3, 4, 5, 6], 10, big=True, gap=1)
    p.glyphs(103, 58, [0, 2, 1, 3, 5, 4, 2, 0, 1, 3], 10, big=False, gap=2)
    p.rect(173, 0, 189, 46, 20); p.rect(173, 0, 173, 46, 7); p.rect(189, 0, 189, 46, 7); p.rect(173, 46, 189, 46, 7)
    for k in range(4):
        p.glyphs(179, 4 + k * 10, [k + 2], 10, big=False)
    for i in range(6):
        p.rect(86 + i * 12, 86, 92 + i * 12, 90, 17); p.px(87 + i * 12, 87, 10)
    p.glow([9, 21, 20], 8, 6, 8, 4)
    p.glow([17], 18, None, 8)
    # clutter
    p.sprite(44, 86, "ac", {"k": 0, "b": 3, "c": 4}); p.sprite(192, 90, "ac", {"k": 0, "b": 3, "c": 4})
    p.line(43, 0, 43, 84, 4); p.line(200, 50, 200, 88, 4)
    for k in (0, 4):
        catenary(p, 0, 30 + k, 43, 44 + k, 5, 0); catenary(p, 204, 48 + k, BIG, 34 + k, 5, 0)
    for i, c in enumerate((7, 5, 12)):
        sw = int(math.sin(t * 2.2 + i) > .3)
        p.rect(140 + i * 5 + sw, 84, 143 + i * 5 + sw, 90, c)
    p.line(136, 84, 158, 84, 1)
    # shop front
    p.rect(50, 96, 168, 99, 11); p.rect(50, 96, 168, 96, 12)
    for i in range(0, 118, 6):
        p.rect(50 + i, 100, 52 + i, 105, 13); p.rect(53 + i, 100, 55 + i, 105, 16)
        p.px(51 + i, 106, 13)
    p.rect(54, 107, 164, 138, 11)
    p.rect(56, 108, 162, 136, 14)
    p.dither(56, 108, 162, 112, 15, 8)
    for x in range(56, 163, 13):
        p.line(x, 108, x, 136, 12)
    p.line(56, 120, 162, 120, 12)
    for i in range(8):
        p.rect(60 + i * 13, 113, 65 + i * 13, 115, 13); p.rect(61 + i * 13, 116, 64 + i * 13, 116, 12)
    p.rect(56, 129, 162, 131, 12); p.rect(56, 129, 162, 129, 13)
    p.sprite(100, 117, "cook0" if int(t * 3) % 2 else "cook1", {"k": 16})
    for k in range(6):
        sy = 127 - ((k * 3 + int(t * 12)) % 18)
        p.px(124 + (k + int(t * 4)) % 2, sy, 15)
    for lx, sd in ((44, 0), (192, 1)):
        sw = int(math.sin(t * 1.7 + sd * 2) > 0)
        p.line(lx + 4, 99, lx + 4 + sw, 103, 6)
        p.sprite(lx + sw, 103, "lantern", {"k": 16, "r": 9, "h": 10, "d": 7})
    p.glow([14, 15], 13, None, 4)
    p.rect(0, G, BIG, H, 0)
    p.reflect(G, t, R2)
    p.rect(0, G, BIG, G, 4); p.rect(0, G + 1, BIG, G + 1, 1)
    for x in range(0, BIG, 24):
        p.rect(x + 3, 160, x + 14, 160, 3)
    p.dither(60, G + 3, 160, G + 9, 12, 4); p.dither(80, G + 3, 140, G + 6, 13, 3)
    mist(p, G - 3, G + 6, 19, t, 1)
    rain(p, t, 2, 80, 19, G, 100)
    return p


def pal_shop(t):
    pal = [hx(c) for c in P2]
    if math.sin(t * 9 + 1.3) * math.sin(t * 2.3 + 2.6) < -.6:
        pal[9] = hx("#7a1020"); pal[21] = hx("#5a0c14")
    if math.sin(t * 7 + 4.1) * math.sin(t * 1.9 + 8.2) < -.55:
        pal[20] = hx("#5a0c14")
    return pal


# ----------------------------------------------------------------- shot 3: night gantry, tower, food stalls
P3 = ["#020814", "#050f2e", "#081c3a", "#0a2442", "#0c2a4e", "#12406a", "#1b5d90", "#2a6aa8", "#4aa0d8", "#9fd0ff",
      "#9cff2a", "#2a6a10", "#ff3a4a", "#cfd6df", "#7af0e0", "#0a3a40", "#ff6a3c", "#3f6fa8", "#fff0a0", "#0b2a52", "#1c4f86",
      "#ff3a4a", "#1b5d90", "#1b5d90"]
R3 = remap_table({10: 11, 14: 15, 13: 5, 18: 7, 16: 12, 12: 0, 21: 0, 9: 6, 8: 5, 7: 4, 22: 3, 23: 3, 20: 19, 17: 2, 11: 1, 15: 1},
                 {6: 4, 5: 3, 4: 2, 3: 1, 2: 1, 1: 0, 19: 1})


def shot_gantry(t):
    G = 124
    p = Pix(BIG, H)
    p.grad(0, G, [1, 1, 2, 3, 4])
    for x0, x1, sd, hmax in ((0, 140, 41, 40), (150, BIG, 42, 30)):                            # far skyline
        rr = random.Random(sd); x = x0
        while x < x1:
            w, h = rr.randint(6, 11), rr.randint(12, hmax + 14)
            p.rect(x, G - 10 - h, x + w, G - 10, 2); p.rect(x, G - 10 - h, x + w, G - 10 - h, 3)
            for _ in range(3):
                p.px(x + rr.randint(1, w - 1), G - 10 - rr.randint(3, h), 5)
            if rr.random() < .4:
                p.px(x + w // 2, G - 11 - h, 21)
            x += w + rr.randint(1, 2)
    p.rect(141, 7, 207, 118, 4); p.rect(150, 3, 198, 7, 5); p.rect(150, 3, 198, 3, 8)            # tower
    p.rect(141, 7, 141, 118, 7); p.dither(142, 7, 146, 118, 5, 8); p.dither(202, 7, 207, 118, 3, 8)
    p.line(174, 3, 174, 0, 6); p.px(174, 0, 21)
    rr = random.Random(5)
    for row in range(16):
        for col in range(12):
            x, y = 146 + col * 5, 24 + row * 6
            v = rr.random()
            p.rect(x, y, x + 2, y + 3, 22 if v < .15 else 23 if v < .27 else 3)
    p.rect(148, 11, 200, 21, 3); p.rect(148, 11, 200, 11, 7); p.rect(148, 21, 200, 21, 1)
    p.glyphs(156, 13, [6, 2, 7, 1], 8, big=True, gap=4)
    gant = [(20, 70), (130, 58), (204, 91), (204, 99), (130, 71), (20, 81)]                       # gantry
    p.poly(gant, 2)
    p.line(20, 70, 130, 58, 7); p.line(130, 58, 204, 91, 7); p.line(20, 81, 130, 71, 1); p.line(130, 71, 204, 99, 1)
    for k in range(0, 180, 9):
        x = 22 + k
        top = 70 - (k * 12 / 108) if x < 130 else 58 + (x - 130) * 33 / 74
        bot = 81 - (k * 10 / 108) if x < 130 else 71 + (x - 130) * 28 / 74
        p.line(x, top + 1, x + 5, bot - 1, 1); p.px(x, top + 1, 5)
    for x in (36, 66, 96, 170):
        b = 81 - ((x - 20) * 10 / 110) if x < 130 else 71 + (x - 130) * 28 / 74
        p.rect(x, b, x + 1, G, 1); p.rect(x, b, x, G, 3)
    for k in range(4):
        p.rect(28 + k * 14, 96, 36 + k * 14, 118, 2); p.rect(28 + k * 14, 96, 36 + k * 14, 96, 4)
    p.ellipse(142, 85, 8, 8, 10, outline=True, width=2); p.line(142, 80, 142, 90, 10)            # green sign
    p.glyphs(153, 81, [3, 0, 4], 10, big=True, gap=2)
    p.glow([10], 11, 2, 8, 4)
    p.rect(0, G, BIG, H, 1)
    p.rect(75, 104, 128, G - 3, 3); p.rect(75, 104, 128, 104, 7); p.rect(75, 104, 75, G - 3, 0)    # truck
    for x in range(81, 128, 6):
        p.line(x, 106, x, G - 5, 2)
    p.ellipse(100, 113, 7, 6, 6, outline=True); p.rect(76, 105, 128, 105, 5)
    p.rect(129, 108, 142, G - 3, 13); p.rect(131, 110, 139, 115, 6); p.px(132, 111, 9)
    p.rect(140, 117, 142, 119, 18); p.rect(75, 116, 76, 118, 12)
    p.dither(143, 114, 158, 122, 18, 2)
    for wx in (84, 116, 133):
        p.sprite(wx - 4, G - 6, "wheel", {"k": 0, "m": 4, "h": 7})
    p.rect(160, 106, 236, 110, 5)                                                                 # stalls
    for i in range(0, 78, 6):
        p.rect(160 + i, 106, 162 + i, 110, 7)
    for i in range(4):
        x = 162 + i * 18
        p.rect(x - 1, 112, x + 14, G - 1, 15); p.rect(x, 113, x + 13, G - 3, 14)
        p.glyphs(x + 2, 115, [i, i + 2], 15, big=False, gap=2)
    p.glow([14], 15, None, 8)
    for lx in (18, 60, 150):                                                                       # lamps
        p.line(lx, 86, lx, G, 2); p.rect(lx - 4, 84, lx + 4, 85, 20); p.rect(lx - 3, 84, lx + 3, 84, 9)
        p.dither(lx - 12, 86, lx + 12, G - 1, 19, 4, where=p.mask_poly([(lx - 3, 86), (lx + 3, 86), (lx + 12, G), (lx - 12, G)]) & (p.a < 3))
    wx = int(24 + t * 6)                                                                           # walker
    p.sprite(wx, G - 15, "walker0" if int(t * 4) % 2 else "walker1", {"h": 9, "u": 8, "s": 7, "k": 0})
    p.reflect(G, t, R3)
    p.rect(0, G, BIG, G, 5); p.rect(0, G + 1, BIG, G + 1, 2)
    p.dither(160, G + 3, 236, G + 8, 15, 4); p.dither(130, G + 2, 160, G + 6, 18, 2)
    mist(p, G - 4, G + 4, 19, t, 1)
    rain(p, t, 3, 90, 17, G, 95)
    return p


def pal_gantry(t):
    pal = [hx(c) for c in P3]
    if math.sin(t * 6 + 2.2) * math.sin(t * 2.3 + 4.4) < -.6:
        pal[10] = hx("#2a6a10")
    pal[21] = hx("#ff3a4a") if int(t * 1.6) % 2 == 0 else hx("#2a0a14")
    tw = int(t * 2.5) % 2
    pal[22], pal[23] = (hx("#4aa0d8"), hx("#0a2442")) if tw else (hx("#0a2442"), hx("#4aa0d8"))
    if int(t * 3) % 5 == 0:
        pal[14] = hx("#3ab8b0")
    return pal


SHOTS = ((shot_roadside, pal_roadside), (shot_shop, pal_shop), (shot_gantry, pal_gantry))


def frame_indices(t):
    s = 0 if t < CUTS[0] else 1 if t < CUTS[1] else 2
    t0 = (0, *CUTS)[s]
    p = SHOTS[s][0](t)
    off = min(START[s] + int((t - t0) * 4), BIG - VIEW)
    return p.a[:, off:off + VIEW], np.array(SHOTS[s][1](t), np.uint8)


def frame(t):
    idx, pal = frame_indices(t)
    rgb = pal[idx]
    return Image.fromarray(np.repeat(np.repeat(rgb, UP, 0), UP, 1))


def sprite_sheet(out):
    keys = {"k": (8, 8, 12), "a": (40, 90, 110), "b": (90, 160, 180), "c": (200, 210, 220), "d": (20, 20, 30), "e": (120, 140, 160),
            "h": (230, 240, 250), "l": (255, 248, 200), "r": (255, 60, 70), "s": (40, 70, 90), "m": (40, 60, 90), "u": (74, 160, 216)}
    names = list(SPRITES)
    cell = 36
    sheet = Image.new("RGBA", (cell * 6, cell * ((len(names) + 5) // 6)), (0, 0, 0, 0))
    for n, name in enumerate(names):
        for j, row in enumerate(SPRITES[name]):
            for i, ch in enumerate(row):
                if ch in keys:
                    sheet.putpixel(((n % 6) * cell + i, (n // 6) * cell + j), keys[ch] + (255,))
    sheet.save(out)


def video(out):
    here = os.path.dirname(os.path.abspath(__file__))
    sp = importlib.util.spec_from_file_location("neon_basic", os.path.join(here, "render_neon_offline.py"))
    basic = importlib.util.module_from_spec(sp); sp.loader.exec_module(basic)
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav"); basic.audio(wav)
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VIEW * UP}x{H * UP}", "-r", str(FPS),
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
            frame(float(s_)).save(os.path.join(sys.argv[2], f"p{float(s_):.2f}.png"))
    elif len(sys.argv) == 3 and sys.argv[1] == "video":
        video(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "sheet":
        sprite_sheet(sys.argv[2])
    else:
        sys.exit(__doc__)
