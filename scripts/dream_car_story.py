#!/usr/bin/env python3
"""THE BLUE COUPE - a ~4-5 minute narrated pixel-art short (vertical 1080x1920 for TikTok).

One 180x320 indexed grid for every layer, x6 nearest (6x6 blocks align with H.264 4:2:0 chroma).
One global 64-colour palette; reflections/lightning are index remaps, glow is blocky dither, rain is solid.
Narration: out/story/vo/<id>.wav + timings.json from scripts/story_tts.py (scene lengths follow the voice).
Captions: original 5x7 pixel font, sentence-timed from the pauses in each narration clip.
Score + SFX are synthesized here (no samples, no licensing).

  python3 scripts/dream_car_story.py still OUT_DIR T [T ...]
  python3 scripts/dream_car_story.py video OUT.mp4
"""
import importlib.util, json, math, multiprocessing as mp, os, random, re, subprocess, sys, tempfile, wave
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
_sp = importlib.util.spec_from_file_location("pixel_neon", os.path.join(HERE, "pixel_neon.py"))
E = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(E)
Pix, BAYER = E.Pix, E.BAYER

W, H, UP, FPS = 180, 320, 6, 30
T_ = 255
SCRIPT = os.path.join(ROOT, "stories/dream-car/script.json")
VO_DIR = os.path.join(ROOT, "out/story/vo")

PALETTE = [
    "#02030a", "#060b1c", "#0a1228", "#0f1a36", "#172548", "#22345e", "#30487a", "#4a6aa0",   # 0-7 night navy
    "#0f3a44", "#1a6a78", "#2aa0a8", "#6ad8d0", "#c8f4ee", "#ffffff",                         # 8-13 teal / white
    "#2a0a10", "#6a1020", "#b8142a", "#ff3a3a", "#ff9a8a",                                    # 14-18 red neon
    "#2e220c", "#6a4a10", "#b8901c", "#f0c828", "#fff4a8", "#e8743a",                         # 19-24 warm
    "#5a3424", "#9a6040", "#d8a07a",                                                          # 25-27 skin
    "#c8402a", "#7a2418",                                                                     # 28-29 hoodie
    "#2a3a5a", "#1a2438",                                                                     # 30-31 denim
    "#0a1840", "#14307a", "#2456c0", "#4a8af0", "#a8d0ff",                                    # 32-36 dream blue
    "#6a5a2a", "#a08a3a", "#5a2a1a",                                                          # 37-39 old car / rust
    "#1a1a1e", "#2e2e34", "#4a4a52", "#74747e", "#a8a8b0", "#d4d4da",                         # 40-45 greys
    "#2a1a3a", "#5a2a5a", "#a04a6a", "#e0706a", "#f4a070", "#ffd09a", "#fff0d0", "#ffe070",   # 46-53 dawn
    "#1a3a24", "#2e6a3a", "#6aa04a",                                                          # 54-56 green
    "#4a2a6a", "#b46aff",                                                                     # 57-58 purple
    "#2a1810", "#5a3a24", "#8a5a34",                                                          # 59-61 wood
    "#e8eef4", "#d8ffe0"]                                                                     # 62 snow/paper, 63 fluorescent
PAL = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in PALETTE], np.int32)


def _nearest(rgb, exclude=None):
    d = ((PAL - np.array(rgb)) ** 2).sum(1).astype(float)
    if exclude is not None:
        d[exclude] = 1e18
    return int(np.argmin(d))


REMAP = np.arange(256, dtype=np.uint8)      # reflection: darker, slightly bluer palette neighbour
LIFT = np.arange(256, dtype=np.uint8)       # lightning flash: brighter neighbour
for i, c in enumerate(PAL):
    REMAP[i] = _nearest(c * .5 + np.array([0, 4, 14]))
    LIFT[i] = _nearest(np.minimum(255, c * 1.5 + np.array([40, 50, 70])))

# ------------------------------------------------------------------ pixel font (original 5x7)
F = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"], "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."], "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"], "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"], "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."], "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"], "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"], "N": ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."], "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"], "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."], "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."], "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."], "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."], "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."], "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"], "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."], "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."], "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."], "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ".": ["..", "..", "..", "..", "..", "##", "##"], ",": ["..", "..", "..", "..", "##", ".#", "#."], "'": ["##", ".#", "#.", "..", "..", "..", ".."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."], "!": ["#", "#", "#", "#", "#", ".", "#"],
    "-": ["....", "....", "....", "####", "....", "....", "...."], ":": [".", "#", ".", ".", ".", "#", "."], " ": ["...", "...", "...", "...", "...", "...", "..."],
}


def text_width(s):
    return sum(len(F.get(ch, F[" "])[0]) + 1 for ch in s) - 1


def draw_text(p, x, y, s, c, outline=None):
    s = s.upper()
    if outline is not None:
        m = np.zeros((p.h, p.w), bool)
    cx = x
    for ch in s:
        g = F.get(ch, F[" "])
        for j, row in enumerate(g):
            for i, v in enumerate(row):
                if v == "#" and 0 <= cx + i < p.w and 0 <= y + j < p.h:
                    if outline is not None:
                        m[y + j, cx + i] = True
                    else:
                        p.a[y + j, cx + i] = c
        cx += len(g[0]) + 1
    if outline is not None:
        g2 = m.copy()
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                g2 |= np.roll(np.roll(m, dy, 0), dx, 1)
        sh = np.roll(np.roll(m, 1, 0), 1, 1)
        p.a[g2 | sh] = outline
        p.a[m] = c


# ------------------------------------------------------------------ helpers
def bmask(h, w, level, block=2, phase=0):
    yy, xx = np.mgrid[0:h, 0:w]
    return BAYER[((yy // block) + phase) % 4, ((xx // block) + phase) % 4] < level


def grow(m):
    g = m.copy()
    g[1:] |= m[:-1]; g[:-1] |= m[1:]; g[:, 1:] |= m[:, :-1]; g[:, :-1] |= m[:, 1:]
    return g


def glow(p, src, rings, phase=0):
    core = np.isin(p.a, src); done = core.copy()
    for idx, lvl in rings:
        ring = grow(done) & ~done
        p.a[ring & (bmask(p.h, p.w, lvl, 2, phase) if lvl < 16 else True)] = idx
        done |= ring


def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def blit(p, arr, x, y, flip=False):
    a = arr[:, ::-1] if flip else arr
    h, w = a.shape
    x0, y0 = int(x), int(y)
    xs, ys = max(0, -x0), max(0, -y0)
    xe, ye = min(w, p.w - x0), min(h, p.h - y0)
    if xe <= xs or ye <= ys:
        return
    src = a[ys:ye, xs:xe]
    dst = p.a[y0 + ys:y0 + ye, x0 + xs:x0 + xe]
    m = src != T_
    dst[m] = src[m]


def cam(world, cx, cy, z):
    u = np.arange(W); v = np.arange(H)
    sx = np.clip(np.floor(cx + (u - W / 2 + .5) / z).astype(int), 0, world.shape[1] - 1)
    sy = np.clip(np.floor(cy + (v - H / 2 + .5) / z).astype(int), 0, world.shape[0] - 1)
    return world[np.ix_(sy, sx)]


def rain(a, t, seed, n, c, speed, length, slant=5, y0=0, y1=None, ground=None, alpha=1.0):
    r = random.Random(seed)
    Hh, Ww = a.shape
    y1 = Hh if y1 is None else y1
    for _ in range(int(n * alpha)):
        x0, yy0, v = r.uniform(0, Ww), r.uniform(0, Hh), r.uniform(.85, 1.15)
        y = int((yy0 + t * speed * v) % (Hh + length)) - length
        x = int(x0 + y / slant) % Ww
        for k in range(length):
            yy, xx = y + k, x + (k + y % slant) // slant
            if y0 <= yy < y1 and 0 <= xx < Ww:
                a[yy, xx] = c
    if ground is not None and ground + 3 < Hh - 1:
        for _ in range(int(n * alpha) // 3):
            x, y = r.randrange(2, Ww - 2), r.randrange(ground + 2, Hh - 1)
            ph = int(t * 12 + r.random() * 12) % 12
            if ph == 0:
                a[y, x] = c
            elif ph == 1:
                a[y - 1, x - 1] = c; a[y - 1, x + 1] = c
            elif ph == 2:
                a[y, x - 2] = c; a[y, x + 2] = c


def skyline(p, base, x0, x1, col, top, seed, lights=(), hmin=20, hmax=70, density=.15):
    rr = random.Random(seed); x = x0
    while x < x1:
        w, h = rr.randint(8, 18), rr.randint(hmin, hmax)
        p.rect(x, base - h, x + w, base, col); p.rect(x, base - h, x + w, base - h, top)
        for yy in range(base - h + 3, base - 3, 4):
            for xx in range(x + 2, x + w - 1, 3):
                if lights and rr.random() < density:
                    p.px(xx, yy, rr.choice(lights))
        x += w + rr.randint(1, 3)


def wet_reflect(p, water, t, depth=60, gaps=3):
    p.reflect(water, t, REMAP, gaps=gaps, depth=depth)


# ------------------------------------------------------------------ characters
def person(p, x, y, pose="stand", t=0.0, face=1, kid=False, umb=None, col=None, beard=False, cap=False):
    """~40px side-view person built from pixel clusters. y = feet baseline (or seat height for 'sit')."""
    c = dict(sk=27, skd=26, hair=1, hd=28, hdd=29, pn=31, pnd=30, sh=0)
    if col:
        c.update(col)
    L, B, Wd, hh = (9, 9, 7, 7) if kid else (14, 13, 9, 8)
    ph = int(t * 6) % 4
    walking = pose in ("walk", "push")
    bob = 1 if walking and ph in (1, 3) else 0
    hip = (y if pose == "sit" else y - L) - bob
    sy = hip - B
    lean = 3 if pose == "push" else (1 if pose in ("wash", "count") else 0)
    hl = Wd // 2
    for r in range(B):                                                   # torso (leans into the push)
        off = int(round(lean * (B - r) / B)) * face
        p.rect(x - hl + off, sy + r, x + hl + off, sy + r, c["hd"])
        p.px(x - hl * face + off if face > 0 else x + hl + off, sy + r, c["hdd"])
    p.rect(x - hl, hip - 2, x + hl, hip - 1, c["hdd"])
    hx0 = x - 3 + lean * face
    hy = sy - hh
    p.rect(hx0, hy, hx0 + 6, sy - 1, c["sk"])                             # head
    if pose == "back":
        p.rect(hx0, hy, hx0 + 6, sy - 2, c["hair"])
    else:
        p.rect(hx0, hy, hx0 + 6, hy + 1, c["hair"])
        bx = hx0 if face > 0 else hx0 + 5
        p.rect(bx, hy, bx + 1, hy + 4, c["hair"])
        ex = hx0 + (5 if face > 0 else 1)
        p.px(ex, hy + 3, 0); p.px(hx0 + (7 if face > 0 else -1), hy + 4, c["sk"])
        p.px(hx0 + (3 if face > 0 else 3), hy + 4, c["skd"])
        if beard:
            p.rect(hx0 + 1, hy + 5, hx0 + 6, sy - 1, 44)
    if cap:
        p.rect(hx0 - 1, hy - 1, hx0 + 7, hy, c["pn"]); p.rect(hx0 + (6 if face > 0 else -3), hy, hx0 + (9 if face > 0 else 0), hy, c["pn"])
    p.rect(hx0, sy - 1, hx0 + 6, sy - 1, c["hdd"])                         # collar / hood
    if pose == "sit":                                                     # legs: thighs forward, shins down
        p.rect(min(x, x + 9 * face), hip - 3, max(x, x + 9 * face), hip, c["pn"])
        kx = x + 9 * face
        p.rect(kx - 1, hip, kx + 1, hip + 10, c["pn"]); p.rect(kx - 1 + (1 if face > 0 else -2), hip + 10, kx + 1 + (2 if face > 0 else -1), hip + 11, c["sh"])
    else:
        if walking:
            o = {0: (-3, 3), 1: (-1, 1), 2: (3, -3), 3: (1, -1)}[ph]
        else:
            o = (-2, 2) if pose == "lean" else (0, 0)
        for k, dx in enumerate(o):
            lx = x - 2 + k * 3
            p.line(lx, hip, lx + dx, y - 2, c["pn"] if k else c["pnd"]); p.line(lx + 1, hip, lx + 1 + dx, y - 2, c["pn"] if k else c["pnd"])
            p.rect(lx + dx - (1 if face < 0 else 0), y - 1, lx + dx + 2 + (1 if face > 0 else 0), y, c["sh"])
    ax = x + (hl - 1) * face + lean * face                                 # arms
    if pose in ("stand", "back", "lean") or (pose == "walk" and False):
        if pose == "lean":
            p.rect(x - hl, sy + 4, x + hl, sy + 6, c["hdd"]); p.rect(x + hl * face - 1, sy + 4, x + hl * face, sy + 6, c["sk"])
        else:
            p.rect(ax - 1, sy + 1, ax, hip, c["hdd"]); p.rect(ax - 1, hip + 1, ax, hip + 2, c["sk"])
    elif pose == "walk":
        sw = {0: 2, 1: 0, 2: -2, 3: 0}[ph]
        p.line(ax, sy + 1, ax + sw * face, hip, c["hdd"]); p.line(ax - 1, sy + 1, ax - 1 + sw * face, hip, c["hdd"])
        p.px(ax + sw * face, hip + 1, c["sk"])
    elif pose == "push":
        p.rect(min(ax, ax + 7 * face), sy + 3, max(ax, ax + 7 * face), sy + 4, c["hdd"]); p.rect(ax + 7 * face, sy + 3, ax + 8 * face, sy + 4, c["sk"])
    elif pose in ("wash", "count"):
        mv = int(round(math.sin(t * (7 if pose == "wash" else 3)) * 1.5))
        p.line(ax, sy + 2, ax + 5 * face, sy + 8 + mv, c["hdd"]); p.line(ax - 1, sy + 2, ax + 4 * face, sy + 8 + mv, c["hdd"])
        p.rect(ax + 5 * face, sy + 8 + mv, ax + 6 * face, sy + 9 + mv, c["sk"])
    elif pose == "sit":
        p.line(ax, sy + 2, ax + 6 * face, hip - 3, c["hdd"]); p.px(ax + 7 * face, hip - 3, c["sk"])
    elif pose == "umbrella":
        p.rect(ax - 1, sy + 1, ax, hip, c["hdd"])
    if umb is not None:
        ux = x + (1 if pose != "back" else 0)
        top = hy - 9
        for k, w in enumerate((3, 6, 8, 10, 11, 11)):
            p.rect(ux - w, top + k, ux + w, top + k, umb)
        p.rect(ux - 5, top + 1, ux + 1, top + 1, LIFT[umb])
        for rx in (-11, -5, 0, 5, 11):
            p.px(ux + rx, top + 6, 0)
        p.line(ux, top + 6, ux, sy + 2, 0)


def coupe(state="new", spin=0.0, lights=True, driver=False, hood_open=False, front_wheel=True):
    """Original long-hood blue coupe (side view, facing right). Returns a 36x92 index sprite (T_ = clear)."""
    c = Pix(92, 36, T_)
    b = 33
    pal = {"new": (32, 33, 34, 35, 36), "rusty": (31, 33, 33, 34, 7), "primer": (40, 41, 42, 43, 44)}[state]
    dk, md, bd, hi, sp = pal
    pts = [(2, -5), (1, -13), (5, -16), (20, -18), (30, -27), (50, -27), (62, -18), (82, -15), (87, -12), (87, -6), (82, -4), (6, -4)]
    c.poly([(x, b + y) for x, y in pts], bd)
    c.poly([(x, b + y) for x, y in [(2, -9), (87, -9), (87, -5), (82, -4), (6, -4), (2, -5)]], md)
    c.rect(4, b - 6, 85, b - 4, dk)
    c.line(5, b - 16, 20, b - 18, hi); c.line(62, b - 18, 82, b - 15, hi); c.line(30, b - 27, 50, b - 27, sp)
    c.line(20, b - 18, 30, b - 27, hi); c.line(82, b - 15, 87, b - 12, hi)
    c.poly([(x, b + y) for x, y in [(23, -18), (31, -25), (48, -25), (58, -18)]], 4)                 # glass
    c.line(41, b - 25, 41, b - 18, dk)
    for k in range(4):
        c.px(33 + k, b - 23 + k, 12 if state == "new" else 7); c.px(50 + k, b - 23 + k, 7)
    c.line(23, b - 17, 60, b - 17, 44)                                                                 # chrome line
    c.line(41, b - 16, 41, b - 6, dk); c.rect(36, b - 14, 39, b - 14, dk)                            # door seam + handle
    if state == "rusty":
        r = random.Random(3)
        for _ in range(70):
            x, y = r.randint(4, 85), r.randint(b - 16, b - 5)
            if c.a[y, x] in (md, bd, dk):
                c.px(x, y, 39 if r.random() < .6 else 37)
    if state == "primer":
        for x in range(8, 80, 9):
            c.rect(x, b - 14, x + 3, b - 10, 34)
    if driver:
        c.rect(44, b - 24, 48, b - 19, 27); c.rect(44, b - 24, 48, b - 23, 1); c.px(48, b - 22, 0); c.rect(43, b - 22, 44, b - 18, 1)
    if lights:
        c.rect(84, b - 13, 87, b - 11, 13); c.px(85, b - 12, 23)
        c.rect(1, b - 13, 3, b - 11, 17)
    else:
        c.rect(84, b - 13, 87, b - 11, 44); c.rect(1, b - 13, 3, b - 11, 15)
    if hood_open:
        c.poly([(x, b + y) for x, y in [(60, -18), (66, -34), (86, -27), (84, -15)]], bd)
        c.line(60, b - 18, 66, b - 34, hi); c.rect(66, b - 17, 82, b - 13, 0); c.rect(69, b - 16, 74, b - 14, 42)
    for k, wx in enumerate((18, 70)):
        c.ellipse(wx, b - 4, 9, 9, T_ if False else 0)                                              # arch shadow
        if k == 1 and not front_wheel:
            c.rect(wx - 2, b - 4, wx + 2, b + 2, 42); c.rect(wx - 5, b + 2, wx + 5, b + 2, 42)
            continue
        c.ellipse(wx, b - 4, 7, 7, 40); c.ellipse(wx, b - 4, 5, 5, 44 if state != "rusty" else 43); c.ellipse(wx, b - 4, 1, 1, 45)
        for s in range(5):
            ang = spin + s * 2 * math.pi / 5
            c.line(wx, b - 4, wx + round(4 * math.cos(ang)), b - 4 + round(4 * math.sin(ang)), 42)
    c.a[b + 3:, :][c.a[b + 3:, :] == 0] = T_
    return c.a


def beater(t, hazard=True, steam=True):
    """Old boxy hatchback, mustard with rust. 30x66 sprite facing right."""
    c = Pix(66, 34, T_)
    b = 29
    c.poly([(x, b + y) for x, y in [(1, -4), (1, -21), (9, -23), (38, -23), (48, -14), (62, -12), (63, -4)]], 38)
    c.rect(1, b - 8, 63, b - 4, 37)
    c.poly([(x, b + y) for x, y in [(11, -21), (37, -21), (45, -14), (11, -14)]], 4); c.line(26, b - 21, 26, b - 14, 37)
    r = random.Random(5)
    for _ in range(45):
        x, y = r.randint(2, 62), r.randint(b - 13, b - 5)
        if c.a[y, x] in (37, 38):
            c.px(x, y, 39)
    c.line(30, b - 12, 34, b - 9, 37); c.line(34, b - 9, 38, b - 12, 37)                                # dent
    on = hazard and int(t * 2.2) % 2 == 0
    c.rect(61, b - 11, 63, b - 9, 24 if on else 20); c.rect(1, b - 12, 2, b - 10, 24 if on else 20)
    for wx in (12, 52):
        c.ellipse(wx, b - 3, 6, 6, 0); c.ellipse(wx, b - 3, 5, 5, 40); c.ellipse(wx, b - 3, 2, 2, 43)
    if steam:
        for k in range(9):
            sy = b - 14 - ((k * 3 + int(t * 9)) % 16)
            c.px(54 + int(round(math.sin(t * 3 + k) * 2)) + k % 3, sy, 45 if k % 2 else 44)
    return c.a


def sun_disc(p, cx, cy, r, core=53, rings=((52, 16), (51, 10), (50, 5))):
    p.ellipse(cx, cy, r, r, core)
    glow(p, [core], rings)


# ------------------------------------------------------------------ scenes (each returns a 180x320 index view)
_C = {}


def cached(key, fn):
    if key not in _C:
        _C[key] = fn()
    return _C[key]


def dealer_static(sold):
    p = Pix(210, 350, 0)
    p.grad(0, 120, [1, 2, 2, 3])
    skyline(p, 120, 0, 210, 2, 4, 11, lights=(21, 9), hmin=40, hmax=100)
    p.rect(10, 60, 200, 262, 3)                                                             # building
    for y in range(60, 262, 4):
        p.rect(10, y, 200, y, 4)
        for x in range(10 + (y // 4 % 2) * 5, 201, 10):
            p.px(x, y + 1, 4)
    p.rect(10, 60, 200, 63, 5); p.rect(10, 60, 200, 60, 7)
    for col in range(6):                                                                    # upper windows
        x = 20 + col * 30
        p.rect(x, 70, x + 14, 88, 1); p.rect(x + 1, 71, x + 13, 87, 22 if (col * 7) % 3 == 0 else 3)
        p.line(x + 7, 71, x + 7, 87, 1)
    p.rect(30, 100, 180, 116, 1)                                                            # neon sign FIFTH ST MOTORS
    draw_text(p, 105 - text_width("FIFTH ST MOTORS") // 2, 105, "FIFTH ST MOTORS", 12)
    glow(p, [12], [(10, 16), (9, 8), (8, 4)])
    p.rect(18, 126, 192, 236, 2)                                                            # showroom window frame
    p.rect(22, 130, 188, 232, 9 if not sold else 8)
    p.dither(22, 130, 188, 232, 10 if not sold else 9, 6)
    p.rect(22, 200, 188, 232, 44 if not sold else 42)                                       # glossy floor
    p.dither(22, 200, 188, 232, 45 if not sold else 43, 6)
    p.rect(22, 199, 188, 199, 12 if not sold else 10)
    for x in (60, 105, 150):                                                                # ceiling spotlights
        p.rect(x - 4, 130, x + 4, 132, 41); p.rect(x - 2, 133, x + 2, 133, 23 if not sold else 42)
        if not sold:
            cone = p.mask_poly([(x - 3, 134), (x + 3, 134), (x + 18, 199), (x - 18, 199)])
            p.a[cone & bmask(p.h, p.w, 4, 2)] = 23
    p.ellipse(105, 205, 50, 4, 45 if not sold else 42)                                      # turntable
    p.ellipse(105, 205, 50, 4, 43, outline=True)
    for x in range(22, 189, 33):
        p.rect(x, 130, x + 1, 232, 2)                                                       # mullions
    p.rect(18, 236, 192, 240, 5)
    p.rect(0, 240, 210, 350, 1); p.rect(0, 240, 210, 240, 6); p.rect(0, 241, 210, 241, 3)    # sidewalk + street
    for x in range(0, 210, 14):
        p.px(x, 248, 3)
    p.rect(0, 268, 210, 268, 4)
    return p


def scene_dealer(t, dur, cue, sold=False):
    base = cached(("dealer", sold), lambda: dealer_static(sold))
    p = Pix(base.w, base.h, 0); p.a = base.a.copy()
    if not sold:
        car = coupe("new", spin=0, lights=True)
        blit(p, car, 60, 166)
        sweep = int((t * 26) % 160) + 20                                                   # specular sweep across the paint
        for y in range(172, 196):
            for dx in range(3):
                x = sweep + dx + (y - 172) // 3
                if 60 <= x < 152 and p.a[y, x] in (33, 34, 35):
                    p.a[y, x] = 36
        glow(p, [13], [(23, 16), (22, 6)])
    else:
        p.rect(80, 150, 130, 170, 15); p.rect(82, 152, 128, 168, 16)
        draw_text(p, 105 - text_width("SOLD") // 2, 157, "SOLD", 13)
        p.line(90, 130, 86, 150, 42); p.line(120, 130, 124, 150, 42)
        glow(p, [16], [(15, 16), (14, 8)])
    wet_reflect(p, 240, t, depth=80)
    p.rect(0, 240, 210, 240, 6)
    if not sold:
        person(p, 104, 300, "back", t, face=1, umb=30)
    else:
        sway = 0
        person(p, 104, 300, "stand", t, face=-1)
        p.line(110, 288, 113, 300, 0); p.rect(111, 294, 116, 300, 30)                       # umbrella hanging, closed
    e = ease(t / max(dur, 1))
    z = 1.0 + (.05 if not sold else .09) * e
    v = cam(p.a, 105, 200 + (10 if sold else 0) * e, z)
    a = v.copy()
    rain(a, t, 2, 55, 5, 70, 2)
    rain(a, t, 3, 70 if not sold else 110, 10 if not sold else 9, 150, 5, ground=246)
    return a


def bedroom_static(grown):
    p = Pix(200, 340, 4)
    for x in range(0, 200, 10):                                                             # wallpaper stripes
        p.rect(x, 0, x + 1, 250, 5)
    for y in range(6, 250, 16):
        for x in range(5, 200, 10):
            p.px(x, y, 3)
    p.rect(118, 40, 190, 150, 40); p.rect(122, 44, 186, 146, 2)                             # window
    p.grad(44, 146, [1, 2, 3])
    p.rect(118, 40, 190, 150, 40)
    p.rect(122, 44, 186, 146, T_)                                                           # window glass is drawn per frame
    p.rect(152, 44, 154, 146, 40); p.rect(122, 94, 186, 96, 40)
    p.rect(114, 150, 194, 154, 61)                                                          # sill
    p.rect(0, 250, 200, 340, 60); p.rect(0, 250, 200, 251, 61)                              # floor
    for x in range(0, 200, 24):
        p.line(x, 252, x - 10, 340, 59)
    return p


def window_view(p, t, season="rain", lit=True):
    x0, y0, x1, y1 = 122, 44, 186, 146
    sky = {"rain": [1, 2, 3], "snow": [5, 6, 7], "sun": [7, 9, 11], "dusk": [46, 47, 48]}[season]
    sub = Pix(x1 - x0 + 1, y1 - y0 + 1, 0)
    sub.grad(0, sub.h, sky)
    skyline(sub, sub.h - 1, 0, sub.w, 2 if season in ("rain", "snow") else 6, 3 if season == "rain" else 7, 9,
            lights=(21, 22) if lit else (), hmin=25, hmax=70, density=.25)
    a = sub.a
    if season == "rain":
        rain(a, t, 7, 30, 6, 90, 3)
    elif season == "snow":
        r = random.Random(4)
        for _ in range(40):
            x, y = r.uniform(0, sub.w), r.uniform(0, sub.h)
            yy = int((y + t * 12) % sub.h); xx = int(x + math.sin(t + y) * 2) % sub.w
            a[yy, xx] = 62
    elif season == "sun":
        sun_disc(sub, 48, 22, 6, 23, ((22, 16), (11, 8)))
    p.a[y0:y1 + 1, x0:x1 + 1] = np.where(p.a[y0:y1 + 1, x0:x1 + 1] == T_, a, p.a[y0:y1 + 1, x0:x1 + 1])
    if season == "rain":                                                                    # rain shadows sliding on the wall
        r = random.Random(12)
        for _ in range(14):
            x, ph = r.randint(100, 200), r.random()
            y = int((ph * 260 + t * 22) % 260)
            p.rect(x, y, x, min(249, y + 6), 3)


def poster(p, x, y, w=54, h=34):
    p.rect(x, y, x + w, y + h, 62); p.rect(x + 2, y + 2, x + w - 2, y + h - 2, 7)
    p.grad_box = None
    p.rect(x + 2, y + 2 + (h - 4) * 2 // 3, x + w - 2, y + h - 2, 5)
    small = coupe("new", lights=True)[::2, ::2]
    blit(p, small, x + (w - small.shape[1]) // 2, y + h - small.shape[0] - 3)
    draw_text(p, x + 4, y + 4, "DREAM", 13)
    for cx, cy in ((x, y), (x + w - 3, y), (x, y + h - 3), (x + w - 3, y + h - 3)):
        p.rect(cx, cy, cx + 3, cy + 3, 44)                                                  # tape
    p.poly([(x + w - 6, y + h), (x + w, y + h - 6), (x + w, y + h)], 45)                     # curling corner


def scene_bedroom_kid(t, dur, cue):
    base = cached("bed", lambda: bedroom_static(False))
    p = Pix(base.w, base.h, 0); p.a = base.a.copy()
    window_view(p, t, "rain")
    poster(p, 26, 150)
    p.rect(8, 206, 108, 250, 60); p.rect(8, 200, 14, 250, 61)                               # bed
    p.rect(14, 214, 108, 232, 30); p.rect(14, 214, 108, 215, 7)                             # blanket
    p.rect(16, 206, 36, 214, 62)                                                            # pillow
    p.rect(24, 205, 31, 212, 27); p.rect(24, 205, 31, 207, 1); p.px(30, 209, 0)             # kid's head, eyes open toward poster
    blink = int(t * 1.3) % 6 == 0
    p.px(28, 208, 0 if not blink else 27)
    p.rect(140, 230, 152, 250, 61); p.rect(143, 218, 149, 229, 22)                          # nightlight lamp
    glow(p, [22], [(21, 16), (20, 8), (19, 4)])
    toy = coupe("new", lights=False)[::3, ::3]
    blit(p, toy, 60, 250 - toy.shape[0] + 1)
    dad_t = cue("dad", .45 * dur)                                                            # door opens, dad's silhouette
    p.rect(150, 160, 196, 250, 2)
    if t > dad_t - .5:
        k = ease((t - dad_t + .5) / 1.2)
        gap = int(4 + 18 * k)
        p.rect(150, 160, 150 + gap, 250, 21); p.dither(150, 250, 150 + gap + 20, 270, 20, 6)
        if k > .6:
            person(p, 160, 250, "stand", t, face=-1, col=dict(hd=41, hdd=40, pn=40, pnd=40, sk=40, skd=40, hair=40))
    e = ease(t / dur)
    v = cam(p.a, 96, 186, 1.0 + .06 * e)
    return v.copy()


def scene_bedroom_grind(t, dur, cue):
    base = cached("bed", lambda: bedroom_static(True))
    p = Pix(base.w, base.h, 0); p.a = base.a.copy()
    u = t / dur
    season = ["rain", "sun", "snow", "rain"][min(3, int(u * 4))]
    window_view(p, t, season)
    poster(p, 20, 60)
    months = ["JUN", "AUG", "OCT", "DEC", "FEB", "APR"]
    p.rect(84, 70, 106, 96, 62); p.rect(84, 70, 106, 75, 16)
    draw_text(p, 85 + (21 - text_width(months[0])) // 2, 80, months[min(5, int(u * 6))], 1)
    if t < cue("guitar", .45 * dur):                                                        # guitar on the wall until sold
        p.ellipse(100, 130, 7, 9, 61); p.ellipse(100, 140, 9, 9, 61); p.rect(99, 106, 101, 124, 59); p.ellipse(100, 135, 2, 2, 59)
    if t < cue("games", .38 * dur):
        for k in range(6):
            p.rect(20 + k * 6, 150, 24 + k * 6, 160, (16, 34, 22, 56, 58, 17)[k])
    p.rect(16, 161, 60, 163, 61)
    p.rect(30, 200, 150, 204, 61); p.rect(34, 205, 38, 250, 59); p.rect(142, 205, 146, 250, 59)   # desk
    p.rect(128, 184, 132, 199, 41); p.rect(122, 180, 136, 183, 42)                          # lamp
    p.dither(80, 184, 150, 199, 21, 3)
    fill = ease(u)                                                                           # coin jar fills up
    p.rect(98, 182, 116, 199, 9); p.rect(99, 183, 115, 198, 3)
    lvl = int(14 * fill)
    p.rect(99, 198 - lvl, 115, 198, 21); p.dither(99, 198 - lvl, 115, 198, 22, 6)
    p.rect(97, 181, 117, 182, 44)
    for k in range(5):
        p.px(80 + k * 3, 199, 22 if (k + int(t * 2)) % 3 else 23)
    if abs(t - cue("friends", .7 * dur)) < 3 and int(t * 4) % 2 == 0:                       # phone buzzing with plans
        p.rect(60, 194, 68, 199, 9); p.rect(61, 195, 67, 198, 11)
    person(p, 78, 220, "count", t, face=1)
    p.rect(64, 220, 82, 222, 61); p.rect(66, 223, 68, 250, 59)                              # chair
    glow(p, [23], [(22, 10)])
    e = ease(t / dur)
    v = cam(p.a, 98, 178, 1.0 + .06 * e)
    return v.copy()


def kitchen_static():
    p = Pix(200, 340, 43)
    for y in range(0, 246, 8):                                                              # dim tiled wall
        p.rect(0, y, 200, y, 42)
        for x in range(0 + (y // 8 % 2) * 4, 200, 8):
            p.rect(x, y, x, y + 7, 42)
    p.rect(0, 0, 200, 20, 41); p.rect(60, 104, 140, 106, 41); p.rect(70, 107, 130, 108, 23)  # lamp hood over the sink
    p.rect(118, 132, 190, 196, 41); p.rect(122, 136, 186, 192, 14)                           # pass-through to the dining room
    draw_text(p, 154 - text_width("NEMAR") // 2, 158, "NEMAR", 17)
    glow(p, [17], [(16, 16), (15, 8)])
    p.ellipse(34, 140, 12, 12, 62); p.ellipse(34, 140, 12, 12, 41, outline=True)             # clock at 2:00
    p.line(34, 140, 34, 131, 0); p.line(34, 140, 40, 137, 0)
    p.rect(8, 176, 100, 179, 61)                                                             # shelf + tip jar
    p.rect(70, 162, 84, 175, 9); p.rect(71, 163, 83, 174, 3); p.rect(71, 170, 83, 174, 21); p.rect(69, 161, 85, 162, 44)
    draw_text(p, 64, 152, "TIPS", 16)
    for k in range(5):
        p.ellipse(16 + k * 9, 172, 3, 2, 45); p.ellipse(16 + k * 9, 170, 3, 1, 62)
    return p


def kitchen_front(p):
    p.rect(0, 252, 200, 340, 41); p.rect(0, 252, 200, 254, 45); p.rect(0, 255, 200, 255, 40)  # steel counter
    p.rect(60, 250, 116, 256, 40); p.rect(62, 251, 114, 253, 8)                                # sink basin water line
    for k in range(10):                                                                        # bowl stack
        p.ellipse(136, 248 - k * 3, 10, 2, 62 if k % 2 else 45); p.ellipse(136, 248 - k * 3, 10, 2, 43, outline=True)
    for x in range(0, 200, 25):
        p.line(x, 258, x, 340, 40)


def scene_kitchen(t, dur, cue):
    base = cached("kitchen", kitchen_static)
    p = Pix(base.w, base.h, 0); p.a = base.a.copy()
    if int(t * 30) % 97 in (0, 1):
        p.rect(70, 107, 130, 108, 21)                                                         # bulb flicker
    person(p, 84, 262, "wash", t, face=1, col=dict(hd=45, hdd=43))
    p.rect(81, 237, 88, 247, 62)                                                              # apron bib
    kitchen_front(p)
    for k in range(10):                                                                       # steam from the sink
        sy = 242 - ((k * 4 + int(t * 10)) % 40)
        p.px(62 + int(round(math.sin(t * 2 + k) * 3)) + k * 5, sy, 45)
    drop = cue("jar", .55 * dur)
    if drop < t < drop + 1.2:
        k = (t - drop) / 1.2
        p.ellipse(77, int(140 + 26 * k), 1, 1, 23)
    glow(p, [23], [(22, 8)])
    e = ease(t / dur)
    v = cam(p.a, 92 + 6 * e, 214, 2.0)                                                    # exact 2x close-up, slow pan
    return v.copy()


def storm_static():
    p = Pix(420, 340, 0)
    p.grad(0, 200, [1, 2, 3, 3, 4])
    r = random.Random(8)
    for _ in range(26):                                                                     # storm cloud banks
        x, y, w = r.randint(-20, 420), r.randint(10, 120), r.randint(40, 110)
        for k in range(5):
            p.rect(x + k * 4, y + k * 3, x + w - k * 4, y + k * 3 + 2, (3, 4, 5, 4, 3)[k])
    skyline(p, 210, 0, 420, 2, 3, 3, lights=(21,), hmin=20, hmax=60, density=.08)
    p.rect(0, 210, 420, 340, 2); p.rect(0, 210, 420, 210, 5)
    for x in range(0, 420, 30):
        p.rect(x, 262, x + 14, 263, 44)                                                     # lane dashes
    return p


def scene_storm(t, dur, cue):
    base = cached("storm", storm_static)
    p = Pix(base.w, base.h, 0); p.a = base.a.copy()
    scroll = t * 7                                                                            # pushing the car to the right
    for k in range(8):                                                                       # street lamps passing (mid layer)
        lx = int((k * 70 - scroll * 1.0) % 420)
        p.rect(lx, 140, lx + 1, 250, 0); p.rect(lx - 6, 138, lx + 4, 140, 0); p.rect(lx - 5, 141, lx + 3, 141, 22)
        cone = p.mask_poly([(lx - 5, 142), (lx + 3, 142), (lx + 14, 250), (lx - 16, 250)])
        p.a[cone & bmask(p.h, p.w, 3, 2)] = 21
    car = beater(t)
    blit(p, car, 90, 250 - 30)
    person(p, 82, 252, "push", t, face=1, col=dict(hd=29, hdd=14))
    wet_reflect(p, 252, t, depth=70)
    p.rect(0, 252, 420, 252, 5)
    flashes = [cue("storm", .25 * dur) + .2, .62 * dur, .85 * dur]
    flash = any(0 <= t - f < .12 or .22 <= t - f < .3 for f in flashes)
    if any(0 <= t - f < .3 for f in flashes):
        f = [f for f in flashes if 0 <= t - f < .3][0]
        bx = 60 + int(f * 37) % 120; y = 0
        r = random.Random(int(f * 10))
        while y < 150:
            nx = bx + r.randint(-4, 4); p.line(bx, y, nx, y + 8, 13); bx, y = nx, y + 8
    e = ease(t / dur)
    v = cam(p.a, 122, 200, 1.0 + .05 * e)
    a = v.copy()
    rain(a, t, 4, 80, 4, 90, 3)
    rain(a, t, 5, 140, 7, 190, 7, slant=3, ground=int(H / 2 + (252 - 200) * (1.0 + .05 * e)))
    if flash:
        a = LIFT[a]
    return a


def scene_bank(t, dur, cue):
    p = Pix(200, 340, 43)
    p.rect(0, 0, 200, 340, 42)
    p.rect(20, 30, 180, 150, 41); p.rect(24, 34, 176, 146, 2)                               # big window with rain city
    p.grad(34, 146, [2, 3, 4])
    sub = Pix(152, 112, T_); skyline(sub, 111, 0, 152, 3, 5, 6, lights=(9, 21), hmin=30, hmax=90, density=.2)
    blit(p, sub.a, 24, 34)
    rain_a = p.a[34:147, 24:177]; rain(rain_a, t, 9, 25, 6, 80, 3)
    p.rect(99, 30, 101, 150, 41); p.rect(20, 88, 180, 90, 41)
    p.rect(0, 0, 200, 8, 44); p.rect(40, 3, 160, 5, 63)
    p.rect(20, 214, 180, 222, 59); p.rect(20, 214, 180, 214, 61); p.rect(30, 223, 36, 280, 59); p.rect(164, 223, 170, 280, 59)  # desk
    p.rect(100, 186, 136, 210, 40); p.rect(102, 188, 134, 206, 9); p.rect(116, 211, 120, 214, 40)                   # monitor (from behind: glow)
    p.dither(102, 188, 134, 206, 10, 4)
    person(p, 150, 214, "sit", t, face=-1, col=dict(hd=41, hdd=40, pn=40, pnd=40, sk=26, skd=25, hair=43))           # banker, lit by screen
    slump = t > cue("Declined", .3 * dur)
    person(p, 60, 214 + (2 if slump else 0), "sit", t, face=1)
    p.rect(0, 280, 200, 340, 41)
    dec = cue("Declined", .3 * dur)                                                          # paper close-up with stamp
    p.rect(30, 252, 170, 318, 62); p.rect(30, 252, 170, 252, 45)
    draw_text(p, 38, 258, "LOAN APPLICATION", 42)
    for k in range(5):
        p.rect(38, 270 + k * 7, 38 + (90 if k % 2 else 120), 271 + k * 7, 44)
    if t > dec:
        k = min(1.0, (t - dec) / .18)
        sc = 1 if k >= 1 else 2
        word = "DECLINED"
        tw = text_width(word)
        st = Pix(tw + 6, 13, T_); st.rect(0, 0, tw + 5, 12, 16); st.rect(1, 1, tw + 4, 11, 62); draw_text(st, 3, 3, word, 16)
        arr = np.repeat(np.repeat(st.a, sc, 0), sc, 1)
        blit(p, arr, 100 - arr.shape[1] // 2, 285 - arr.shape[0] // 2)
    e = ease(t / dur)
    v = cam(p.a, 100, 170 + 14 * e, 1.0 + .05 * e)
    return v.copy()


def garage_static():
    p = Pix(210, 340, 41)
    for y in range(0, 250, 6):
        p.rect(0, y, 210, y, 40)
    p.rect(0, 0, 210, 14, 40); p.rect(40, 6, 170, 8, 63)
    p.rect(10, 40, 90, 110, 61)                                                             # pegboard with tools
    for y in range(44, 108, 5):
        for x in range(14, 88, 5):
            p.px(x, y, 60)
    for k, (x, y, h) in enumerate(((20, 50, 22), (30, 48, 26), (42, 52, 18), (54, 50, 24), (68, 46, 30), (80, 52, 20))):
        p.rect(x, y, x + 2, y + h, 43); p.rect(x - 1, y, x + 3, y + 3, 44)
    p.rect(120, 60, 196, 120, 40); p.rect(124, 64, 192, 116, 1)                              # night window
    p.grad(64, 116, [1, 2])
    p.rect(150, 160, 200, 250, 16); p.rect(152, 162, 198, 248, 15)                           # tool chest
    for y in range(170, 248, 12):
        p.rect(152, y, 198, y, 14); p.rect(172, y + 4, 178, y + 5, 44)
    p.rect(0, 250, 210, 340, 42); p.rect(0, 250, 210, 251, 44)
    p.dither(0, 252, 210, 340, 43, 2)
    for x in (30, 90, 150):
        p.ellipse(x, 300, 14, 3, 40)                                                          # oil stains
    return p


def scene_garage(t, dur, cue):
    base = cached("garage", garage_static)
    p = Pix(base.w, base.h, 0); p.a = base.a.copy()
    if int(t * 30) % 53 in (0, 2):
        p.rect(40, 6, 170, 8, 43)
    u = t / dur
    start = cue("rebuilt", .55 * dur)
    prog = 0 if t < start else (t - start) / max(1, dur - start)
    state = "rusty" if prog < .34 else ("primer" if prog < .7 else "new")
    car = coupe(state, lights=prog >= .7, hood_open=prog < .7, front_wheel=prog >= .34)
    blit(p, car, 50, 250 - 34)
    months = ["MAR", "MAY", "JUL", "SEP", "NOV"]
    p.rect(96, 30, 116, 52, 62); p.rect(96, 30, 116, 34, 16)
    draw_text(p, 97 + (19 - text_width("MAR")) // 2, 40, months[min(4, int(prog * 5))] if t > start else "MAR", 1)
    person(p, 46, 250, "stand", t, face=1, beard=True, cap=True,
           col=dict(hd=30, hdd=31, pn=30, pnd=31, hair=44, sk=26, skd=25))                   # Ito
    if t > cue("needs", .45 * dur) and t < start + 2:
        p.rect(58, 228, 61, 231, 62); p.rect(59, 226, 60, 227, 45)                            # his mug steam
    if t > start:
        person(p, 150, 250, "wash", t, face=-1, col=dict(hd=30, hdd=31))
        if int(t * 8) % 3 == 0:                                                              # welding sparks
            r = random.Random(int(t * 30))
            for _ in range(10):
                p.px(138 + r.randint(-6, 6), 232 + r.randint(-6, 6), r.choice((23, 13, 22)))
    glow(p, [23, 13], [(22, 10)])
    e = ease(u)
    v = cam(p.a, 104, 196, 1.0 + .05 * e)
    return v.copy()


def drive_static():
    p = Pix(600, 340, 0)
    p.grad(0, 230, [46, 47, 48, 49, 50, 51])
    return p


def scene_drive(t, dur, cue):
    sky = cached("drive", drive_static)
    view = Pix(W, H, 0)
    view.a[:] = sky.a[:H, :W]
    u = t / dur
    sun_disc(view, 130, int(200 - 60 * ease(u)), 12)
    far = cached("drive_far", lambda: _layer(lambda p: skyline(p, 236, 0, 900, 47, 48, 21, lights=(52,), hmin=30, hmax=110, density=.06), 900))
    mid = cached("drive_mid", _drive_mid)
    off_far = int(t * 8) % 700
    off_mid = int(t * 34)
    blit(view, far.a[:, off_far:off_far + W], 0, 0)
    blit(view, mid.a[:, off_mid % (mid.w - W):off_mid % (mid.w - W) + W], 0, 0)
    view.rect(0, 250, W, H - 1, 46); view.rect(0, 250, W, 250, 50)
    wet_reflect(view, 250, t, depth=70)
    for x in range(0, W + 30, 30):
        xx = int(x - (t * 120) % 30)
        view.rect(xx, 280, xx + 14, 281, 51)
    bob = 1 if int(t * 6) % 2 else 0
    car = coupe("new", spin=-t * 12, lights=True, driver=True)
    blit(view, car, 40, 250 - 33 - bob)
    for k in range(4):                                                                       # exhaust puffs
        ex = 40 - ((k * 5 + int(t * 20)) % 22)
        view.px(ex, 247 - k % 2, 45)
    glow(view, [13], [(23, 16), (52, 6)])
    a = view.a
    stop = cue("stopped", 2.0) + .6
    if t < stop:
        rain(a, t, 6, 90, 50, 160, 5, ground=252, alpha=max(0.0, 1 - t / stop))
    return a


def _layer(fn, w):
    p = Pix(w, H, T_); fn(p); return p


def _drive_mid():
    p = Pix(1400, H, T_)
    r = random.Random(17); x = 0
    while x < 1400:
        w, h = r.randint(26, 50), r.randint(70, 150)
        if 640 <= x <= 700:                                                                   # the Fifth Street window again
            p.rect(x, 250 - 120, x + 90, 250, 47); p.rect(x + 6, 250 - 70, x + 84, 248, 50)
            p.rect(x + 6, 230, x + 84, 248, 51); p.rect(x + 20, 140, x + 70, 150, 46)
            draw_text(p, x + 45 - text_width("FIFTH ST") // 2, 142, "FIFTH ST", 52)
            x += 96; continue
        p.rect(x, 250 - h, x + w, 250, 46); p.rect(x, 250 - h, x + w, 250 - h, 48)
        for yy in range(250 - h + 6, 244, 9):
            for xx in range(x + 4, x + w - 4, 8):
                p.rect(xx, yy, xx + 3, yy + 4, 51 if r.random() < .25 else 47)
        x += w + r.randint(2, 10)
    return p


def overlook_static():
    p = Pix(200, 340, 0)
    p.grad(0, 190, [46, 47, 48, 49, 50, 51, 52])
    p.rect(0, 190, 200, 240, 48); p.dither(0, 190, 200, 240, 47, 8)                        # sea
    skyline(p, 192, 0, 200, 47, 48, 5, lights=(52,), hmin=12, hmax=40, density=.05)
    p.poly([(0, 236), (60, 226), (120, 232), (200, 220), (200, 340), (0, 340)], 54)          # hill
    p.line(0, 236, 60, 226, 56); p.line(60, 226, 120, 232, 55); p.line(120, 232, 200, 220, 56)
    p.dither(0, 240, 200, 340, 55, 4)
    return p


def scene_overlook(t, dur, cue):
    base = cached("over", overlook_static)
    p = Pix(base.w, base.h, 0); p.a = base.a.copy()
    sun_disc(p, 110, 160, 15)
    for y in range(194, 238, 3):                                                             # sun glitter on the sea
        w = int(14 - (y - 194) / 4)
        for x in range(110 - w, 110 + w, 3):
            if (x + y + int(t * 6)) % 4 == 0:
                p.px(x, y, 53 if (x * y) % 5 else 52)
    for k in range(4):                                                                       # birds
        bx = int(20 + k * 30 + t * 6) % 200; by = 70 + k * 9 + int(math.sin(t * 2 + k) * 3)
        if int(t * 4 + k) % 2:
            p.px(bx, by, 46); p.px(bx - 1, by - 1, 46); p.px(bx + 1, by - 1, 46)
        else:
            p.px(bx, by, 46); p.px(bx - 1, by + 1, 46); p.px(bx + 1, by + 1, 46)
    for x in range(0, 200, 4):                                                               # grass sway
        sw = 1 if math.sin(t * 2 + x * .3) > 0 else 0
        p.line(x, 300, x + sw, 294, 56)
    car = coupe("new", lights=False)
    blit(p, car, 58, 268 - 33)
    person(p, 150, 270, "lean", t, face=-1)
    e = ease(t / dur)
    z = 1.06 - .06 * e                                                                        # slow pull back for the ending
    v = cam(p.a, 100, 200, z)
    return v.copy()


SCENES = {"dealer_night": lambda t, d, c: scene_dealer(t, d, c, False), "dealer_sold": lambda t, d, c: scene_dealer(t, d, c, True),
          "bedroom_kid": scene_bedroom_kid, "kitchen": scene_kitchen, "storm_road": scene_storm, "bank": scene_bank,
          "bedroom_grind": scene_bedroom_grind, "garage": scene_garage, "dawn_drive": scene_drive, "overlook": scene_overlook}

# ------------------------------------------------------------------ timeline + captions
LEAD = {"s01_window": .4}
TAIL_EXTRA = {"s04_breakdown": 1.0, "s07_sold": 1.8, "s09_drive": 4.0, "s10_overlook": 4.5}
XFADE = .8


def wrap(s, maxw=168):
    words, lines, cur = s.upper().split(), [], ""
    for w_ in words:
        cand = (cur + " " + w_).strip()
        if text_width(cand) <= maxw:
            cur = cand
        else:
            lines.append(cur); cur = w_
    lines.append(cur)
    return lines


def caption_chunks(text, dur, pauses):
    sents = [s.strip() for s in re.findall(r"[^.?!]+[.?!]?", text) if s.strip()]
    chunks = []
    for s in sents:                                                                          # max two lines per card
        lines = wrap(s)
        for i in range(0, len(lines), 2):
            chunks.append(" ".join(lines[i:i + 2]))
    total = sum(len(c) for c in chunks)
    mids = [(a + b) / 2 for a, b in pauses]
    bounds, acc = [0.0], 0
    for c in chunks[:-1]:
        acc += len(c)
        guess = acc / total * dur
        near = min(mids, key=lambda m: abs(m - guess)) if mids else guess
        bounds.append(near if abs(near - guess) < 1.2 and near > bounds[-1] + .4 else guess)
    bounds.append(dur)
    return [(bounds[i], bounds[i + 1], chunks[i]) for i in range(len(chunks))]


def build_timeline():
    script = json.load(open(SCRIPT))
    tim = json.load(open(os.path.join(VO_DIR, "timings.json")))
    tl, t0 = [], 0.0
    for seg in script["segments"]:
        vo = tim[seg["id"]]["duration"]
        lead = LEAD.get(seg["id"], 1.4)
        dur = lead + vo + 1.6 + TAIL_EXTRA.get(seg["id"], 0)
        caps = [(t0 + lead + a, t0 + lead + b, s) for a, b, s in caption_chunks(seg["text"], vo, tim[seg["id"]]["pauses"])]
        tl.append(dict(id=seg["id"], scene=seg["scene"], start=t0, dur=dur, vo_start=t0 + lead, vo=vo, caps=caps, text=seg["text"]))
        t0 += dur
    return tl, t0


def make_cue(seg):
    def cue(word, default):
        for a, b, s in seg["caps"]:
            if word.upper() in s.upper():
                return a - seg["start"]
        return default
    return cue


def draw_caption(a, s):
    p = Pix(W, H, 0); p.a = a
    lines = wrap(s)
    y = 38
    band = np.zeros((H, W), bool); band[y - 4:y + 10 * len(lines[:2]) + 2, :] = True
    p.a[band & bmask(H, W, 10, 1)] = 0                                                     # dithered dark band for legibility
    for i, ln in enumerate(lines[:2]):
        draw_text(p, (W - text_width(ln)) // 2, y + i * 10, ln, 13, outline=0)
    return p.a


TL = None


def frame_indices(t):
    global TL
    if TL is None:
        TL = build_timeline()[0]
    i = max(k for k, s in enumerate(TL) if s["start"] <= t + 1e-6)
    seg = TL[i]
    lt = t - seg["start"]
    a = SCENES[seg["scene"]](lt, seg["dur"], make_cue(seg))
    if i > 0 and lt < XFADE:                                                                  # ordered-dither dissolve from the previous scene
        prev = TL[i - 1]
        b = SCENES[prev["scene"]](prev["dur"] + lt, prev["dur"], make_cue(prev))
        lvl = int(16 * lt / XFADE)
        m = bmask(H, W, lvl, 2)
        a = np.where(m, a, b)
    for s0, s1, s in seg["caps"]:
        if s0 <= t < s1 - .05:
            a = draw_caption(a.copy(), s)
    return a.astype(np.uint8)


# ------------------------------------------------------------------ score, sfx, mix
SR = 44100


def _env(n, a, r):
    e = np.ones(n)
    ai, ri = int(a * SR), int(r * SR)
    if ai:
        e[:ai] = np.linspace(0, 1, ai)
    if ri:
        e[-ri:] *= np.linspace(1, 0, ri)
    return e


def note(f, d, amp=.2, kind="pad"):
    n = int(d * SR); tt = np.arange(n) / SR
    if kind == "pad":
        s = sum(np.sin(2 * np.pi * f * k * tt + .4 * np.sin(2 * np.pi * .3 * tt)) / k ** 1.6 for k in (1, 2, 3))
        return s * _env(n, min(1.2, d / 3), min(1.6, d / 2)) * amp
    if kind == "pluck":
        s = np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt)
        return s * np.exp(-tt * 3.2) * amp * _env(n, .005, .05)
    if kind == "bass":
        return np.sin(2 * np.pi * f * tt) * _env(n, .05, .4) * amp


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


CHORDS = {"minor": [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]],          # Am F C G
          "low": [[50, 53, 57], [45, 48, 52], [46, 50, 53], [52, 56, 59]],            # Dm Am Bb E
          "hope": [[53, 57, 60, 64], [55, 59, 62], [48, 52, 55, 59], [57, 60, 64]],    # Fmaj7 G Cmaj7 Am
          "bright": [[48, 52, 55, 62], [55, 59, 62, 66], [57, 60, 64, 67], [53, 57, 60, 64]]}
MOOD = {"s01_window": "minor", "s02_poster": "minor", "s03_ramen": "minor", "s04_breakdown": "low", "s05_bank": "low",
        "s06_grind": "minor", "s07_sold": "low", "s08_garage": "hope", "s09_drive": "bright", "s10_overlook": "bright"}
RAIN = {"s01_window": .5, "s02_poster": .25, "s03_ramen": .12, "s04_breakdown": 1.0, "s05_bank": .2, "s06_grind": .25,
        "s07_sold": .8, "s08_garage": .15, "s09_drive": .25, "s10_overlook": 0.0}


def score(tl, total):
    n = int(total * SR) + SR
    mus = np.zeros(n); amb = np.zeros(n); sfx = np.zeros(n); vo = np.zeros(n)
    rng = np.random.default_rng(3)
    CH = 4.8
    for seg in tl:
        mood = CHORDS[MOOD[seg["id"]]]
        k = 0; t = seg["start"]
        while t < seg["start"] + seg["dur"] - .5:
            ch = mood[k % 4]; d = min(CH, seg["start"] + seg["dur"] - t) + 1.0
            i0 = int(t * SR)
            for m in ch:
                s = note(midi(m), d, .045); mus[i0:i0 + len(s)] += s[:n - i0]
            b = note(midi(ch[0] - 12), d, .06, "bass"); mus[i0:i0 + len(b)] += b[:n - i0]
            if MOOD[seg["id"]] in ("minor", "hope", "bright"):                                  # gentle arpeggio
                arp = ch + [ch[1] + 12]
                for j in range(8):
                    tj = t + j * CH / 8
                    s = note(midi(arp[j % len(arp)] + 12), 1.2, .05 if MOOD[seg["id"]] != "bright" else .07, "pluck")
                    ij = int(tj * SR); mus[ij:ij + len(s)] += s[:max(0, n - ij)]
            t += CH; k += 1
        i0, i1 = int(seg["start"] * SR), int((seg["start"] + seg["dur"]) * SR)
        noise = rng.standard_normal(i1 - i0)
        noise = np.convolve(noise, np.ones(30) / 30, mode="same") * 1.8 * RAIN[seg["id"]]
        amb[i0:i1] += noise
        w = wave.open(os.path.join(VO_DIR, seg["id"] + ".wav"))
        v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
        v = np.interp(np.arange(int(len(v) * SR / 24000)) * 24000 / SR, np.arange(len(v)), v)
        j0 = int(seg["vo_start"] * SR); vo[j0:j0 + len(v)] += v[:n - j0]
        cue = make_cue(seg)
        st = seg["start"]
        if seg["id"] == "s04_breakdown":                                                      # thunder
            for f in [cue("storm", .25 * seg["dur"]) + .2, .62 * seg["dur"], .85 * seg["dur"]]:
                i = int((st + f + .3) * SR); L = int(2.5 * SR)
                th = np.convolve(rng.standard_normal(L), np.ones(200) / 200, mode="same") * np.exp(-np.arange(L) / SR * 1.6) * 3
                sfx[i:i + L] += th[:max(0, n - i)]
        if seg["id"] == "s05_bank":                                                           # stamp thud
            i = int((st + cue("Declined", .3 * seg["dur"])) * SR); L = int(.25 * SR); tt = np.arange(L) / SR
            sfx[i:i + L] += np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 18) * .9
        if seg["id"] in ("s03_ramen", "s06_grind"):                                           # coin clinks
            times = [cue("jar", .55 * seg["dur"]) + 1.1] if seg["id"] == "s03_ramen" else list(np.arange(2, seg["dur"] - 2, 2.7))
            for c in times:
                i = int((st + c) * SR); L = int(.3 * SR); tt = np.arange(L) / SR
                sfx[i:i + L] += (np.sin(2 * np.pi * 2800 * tt) + .5 * np.sin(2 * np.pi * 4100 * tt)) * np.exp(-tt * 22) * .12
        if seg["id"] == "s09_drive":                                                          # engine starts and settles
            i = int((st + cue("key", 3.0) + .4) * SR); L = int((seg["dur"] - cue("key", 3.0)) * SR); tt = np.arange(L) / SR
            f = 38 + 30 * np.exp(-tt * 1.5)
            ph = 2 * np.pi * np.cumsum(f) / SR
            eng = (np.sign(np.sin(ph)) * .3 + np.sin(ph * 2) * .4) * (.5 + .5 * np.exp(-tt * .8)) * _env(L, .05, 1.5) * .12
            eng = np.convolve(eng, np.ones(12) / 12, mode="same")
            sfx[i:i + L] += eng[:max(0, n - i)]
        if seg["id"] == "s10_overlook":                                                       # birds
            for k in range(7):
                i = int((st + 1.5 + k * 2.3) * SR); L = int(.18 * SR); tt = np.arange(L) / SR
                sfx[i:i + L] += np.sin(2 * np.pi * (3200 + 900 * np.sin(tt * 60)) * tt) * np.exp(-tt * 14) * .05
    env = np.abs(vo)                                                                          # duck music under the voice
    env = np.convolve(env, np.ones(int(.25 * SR)) / int(.25 * SR), mode="same")
    duck = 1 - .45 * np.clip(env / (env.max() + 1e-9) * 6, 0, 1)
    fade = np.ones(n); fl = int(3 * SR); end = int(total * SR)
    fade[end - fl:end] = np.linspace(1, 0, fl); fade[end:] = 0
    fin = np.ones(n); fin[:int(.3 * SR)] = np.linspace(0, 1, int(.3 * SR))
    mix = (mus * duck * .9 + amb * .5 + sfx + vo * 1.0) * fade * fin
    mix = mix / (np.abs(mix).max() + 1e-9) * .9
    st = np.stack([mix, np.roll(mix, 60) * .97 + mus * duck * .03], 1)
    return (np.clip(st, -1, 1) * 32767).astype("<i2"), n


# ------------------------------------------------------------------ render
def _work(i):
    return frame_indices(i / FPS).tobytes()


def video(out):
    tl, total = build_timeline()
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "mix.wav")
        pcm, n = score(tl, total)
        with wave.open(wav, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
        frames = int(total * FPS)
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-i", wav, "-vf", f"scale={W * UP}:{H * UP}:flags=neighbor", "-c:v", "libx264", "-preset", "medium", "-tune", "animation",
               "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with mp.Pool(max(1, os.cpu_count() - 1)) as pool:
            for k, b in enumerate(pool.imap(_work, range(frames), chunksize=6)):
                p.stdin.write(PAL[np.frombuffer(b, np.uint8).reshape(H, W)].astype(np.uint8).tobytes())
                if k % 900 == 0:
                    print(f"frame {k}/{frames}", flush=True)
        p.stdin.close()
        if p.wait():
            sys.exit("ffmpeg failed")
    print(f"done {total:.1f}s")


if __name__ == "__main__":
    a = sys.argv
    if len(a) >= 4 and a[1] == "still":
        os.makedirs(a[2], exist_ok=True)
        for s in a[3:]:
            idx = frame_indices(float(s))
            Image.fromarray(PAL[idx].astype(np.uint8)).resize((W * 3, H * 3), Image.NEAREST).save(os.path.join(a[2], f"f{float(s):06.1f}.png"))
    elif len(a) == 3 and a[1] == "video":
        video(a[2])
    elif len(a) == 2 and a[1] == "timeline":
        tl, total = build_timeline()
        for s in tl:
            print(f"{s['start']:6.1f} {s['dur']:5.1f} {s['id']}")
        print(f"total {total:.1f}s")
    else:
        sys.exit(__doc__)
