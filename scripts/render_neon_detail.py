#!/usr/bin/env python3
"""High-detail original rainy neon pixel film (3 scenes, hard cuts). Pillow + NumPy + FFmpeg only.

Native 360x360 canvas (x2 nearest = 720x720), 30 fps, 8.2 s, cuts at 2.5 s / 5.53 s.
  python3 scripts/render_neon_detail.py still OUT_DIR T [T ...]
  python3 scripts/render_neon_detail.py video OUT.mp4
All art is procedural and original. Audio is reused from render_neon_offline.audio().
"""
import importlib.util, math, os, random, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W = H = 360
SCALE = 2
FPS = 30
DUR = 8.2
CUTS = (2.5, 5.53)
BIG = 480
START = (0, 60, 70)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0


def hx(s):
    return tuple(int(s[i:i + 2], 16) for i in (1, 3, 5))


def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def R(d, x0, y0, x1, y1, c):
    x0, x1, y0, y1 = int(min(x0, x1)), int(max(x0, x1)), int(min(y0, y1)), int(max(y0, y1))
    d.rectangle([x0, y0, x1, y1], fill=c)


def dither_gradient(img, y0, y1, colors):
    """Banded gradient with 4x4 Bayer dithering between neighbouring palette colours."""
    n = len(colors) - 1
    ys = np.arange(y0, y1)[:, None]
    xs = np.arange(BIG)[None, :]
    u = (ys - y0) / max(1, y1 - y0 - 1) * n
    lo = np.clip(np.floor(u).astype(int), 0, n - 1)
    frac = u - lo
    pick = (frac > BAYER[ys % 4, xs % 4]).astype(int) + lo
    pal = np.array(colors, dtype=np.uint8)
    arr = np.asarray(img).copy()
    arr[y0:y1] = pal[np.clip(pick, 0, n)]
    return Image.fromarray(arr)


def glyph_run(d, x, y, n, col, seed, h=9, w=6, gap=3, thick=1):
    """Original made-up lettering: each glyph is 2-4 connected strokes on a w x h grid."""
    r = random.Random(seed)
    for i in range(n):
        gx = x + i * (w + gap)
        px, py = gx + r.randint(0, w - 1), y + r.randint(0, h - 1)
        for _ in range(r.randint(2, 4)):
            if r.random() < .5:
                nx = gx + r.randint(0, w - 1)
                d.line([px, py, nx, py], fill=col, width=thick); px = nx
            else:
                ny = y + r.randint(0, h - 1)
                d.line([px, py, px, ny], fill=col, width=thick); py = ny


def flicker(t, seed, rate=9):
    return 1.0 if math.sin(t * rate + seed) * math.sin(t * 2.3 + seed * 2) > -0.6 else 0.55


def glowpool(img, cx, cy, rx, ry, col, alpha):
    """Soft additive light pool (ellipse falloff), e.g. neon spill on wet asphalt."""
    a = np.asarray(img).astype(np.float32)
    y0, y1, x0, x1 = max(0, int(cy - ry)), min(H, int(cy + ry)), max(0, int(cx - rx)), min(BIG, int(cx + rx))
    if y1 <= y0 or x1 <= x0:
        return img
    yy, xx = np.mgrid[y0:y1, x0:x1]
    k = np.clip(1 - (((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2), 0, 1) ** 2 * alpha
    a[y0:y1, x0:x1] += k[..., None] * np.array(col, np.float32)
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def mist(img, y0, y1, col, alpha, t, seed=0):
    a = np.asarray(img).astype(np.float32)
    ys = np.arange(y0, y1)[:, None]
    xs = np.arange(BIG)[None, :]
    k = (np.sin(xs / 37.0 + t * .6 + seed) + np.sin(xs / 91.0 - t * .3 + ys / 23.0) + 2) / 4
    k = k * alpha * np.sin((ys - y0) / max(1, y1 - y0) * math.pi)
    a[y0:y1] = a[y0:y1] * (1 - k[..., None]) + np.array(col, np.float32) * k[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def reflect(img, water, t, strength=.5, tint=(0, 12, 24)):
    a = np.asarray(img).astype(np.float32)
    out = a.copy()
    for y in range(water, a.shape[0]):
        src = water - (y - water) - 1
        if src < 0:
            break
        sh = int(round(math.sin(y * .7 + t * 2.5) * (1 + (y - water) / 30)))
        k = max(0.0, strength - (y - water) / 160)
        out[y] = a[y] * (1 - k) + (np.roll(a[src], sh, axis=0) * .8 + np.array(tint)) * k
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def rain(img, t, seed, n, col, ground, speed=150, length=9):
    d = ImageDraw.Draw(img)
    r = random.Random(seed)
    for _ in range(n):
        x0, y0, v = r.uniform(0, BIG), r.uniform(0, H), r.uniform(.7, 1.3)
        y = (y0 + t * speed * v) % (H + length) - length
        x = (x0 + y * .15) % BIG
        d.line([x, y, x + 2, y + length], fill=col)
    for _ in range(n // 3):                                       # splashes on the wet ground
        x, ph = r.uniform(0, BIG), (t * 3 + r.random() * 5) % 1
        y = r.uniform(ground + 6, H - 4)
        e = 1 + ph * 3
        if ph < .6:
            d.ellipse([x - e, y - e / 3, x + e, y + e / 3], outline=col)


def trees(d, x0, x1, base, col, seed, hmin=18, hmax=34):
    r = random.Random(seed); x = x0
    while x < x1:
        h = r.randint(hmin, hmax); w = r.randint(5, 8)
        d.polygon([(x, base), (x + w, base), (x + w // 2, base - h)], fill=col)
        x += r.randint(3, 6)


def pole(d, x, g, col, h=120):
    d.line([x, g - h, x, g], fill=col, width=2)
    for dy, hw in ((h - 6, 14), (h - 22, 10)):
        d.line([x - hw, g - dy, x + hw, g - dy], fill=col, width=2)
        for ix in (-hw, -hw // 2, hw // 2, hw):
            d.point((x + ix, g - dy - 2), fill=mix(col, (200, 220, 230), .3))


def wire(d, x0, y0, x1, y1, col, sag):
    n = abs(x1 - x0)
    for i in range(n + 1):
        u = i / max(1, n)
        d.point((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u + math.sin(u * math.pi) * sag), fill=col)


def win(d, x0, y0, x1, y1, on, frame, panes=(2, 2)):
    R(d, x0 - 1, y0 - 1, x1 + 1, y1 + 1, frame)
    R(d, x0, y0, x1, y1, on)
    for i in range(1, panes[0]):
        xx = x0 + (x1 - x0) * i // panes[0]; d.line([xx, y0, xx, y1], fill=frame)
    for j in range(1, panes[1]):
        yy = y0 + (y1 - y0) * j // panes[1]; d.line([x0, yy, x1, yy], fill=frame)


def car(d, x, y, body, glass, tail, wheel):
    d.polygon([(x, y), (x + 4, y - 11), (x + 18, y - 17), (x + 48, y - 17), (x + 62, y - 9), (x + 72, y - 7), (x + 74, y)], fill=body)
    d.polygon([(x + 8, y - 10), (x + 20, y - 15), (x + 33, y - 15), (x + 33, y - 9)], fill=glass)
    d.polygon([(x + 36, y - 15), (x + 48, y - 15), (x + 58, y - 9), (x + 36, y - 9)], fill=glass)
    R(d, x, y - 2, x + 74, y, mix(body, (0, 0, 0), .35))
    d.point((x + 73, y - 5), fill=(255, 244, 168)); R(d, x, y - 6, x + 1, y - 4, tail)
    for wx in (x + 12, x + 58):
        d.ellipse([wx - 6, y - 6, wx + 6, y + 6], fill=wheel); d.ellipse([wx - 2, y - 2, wx + 2, y + 2], fill=mix(body, (255, 255, 255), .2))


# ------------------------------------------------------------------ scenes
def scene_roadside(t):
    G = 224
    img = Image.new("RGB", (BIG, H), hx("#0b4a64"))
    img = dither_gradient(img, 0, G, [hx(c) for c in ("#093e56", "#0e5a74", "#147088", "#1f8ba2", "#3aa6b8")])
    d = ImageDraw.Draw(img)
    for cx, cy, cw, c in ((30, 30, 120, "#2f95a8"), (200, 56, 90, "#3aa6b8"), (330, 22, 110, "#2f95a8"), (90, 98, 80, "#4ab3c4")):
        ox = int(t * 5) % 40
        for i in range(4):
            R(d, cx + ox + i * 6, cy + i * 3, cx + ox + cw - i * 6, cy + i * 3 + 2, hx(c))
    # tower with lit/dark faces, ribs, red ring, lights
    d.polygon([(200, G), (236, 60), (300, 18), (410, 52), (460, G)], fill=hx("#082a40"))
    d.polygon([(330, 22), (410, 52), (460, G), (350, G)], fill=hx("#0e3d58"))
    for x in range(214, 456, 9):
        d.line([x, G, 236 + (x - 214) * .55, 70], fill=hx("#0b3550"))
    for i in range(160):
        xx = 270 + i * 1.1
        yy = 86 + math.sin(i / 160 * math.pi) * -34 + 44
        d.point((xx, yy), fill=hx("#ff4a5a")); d.point((xx, yy + 1), fill=hx("#c01f3a")); d.point((xx, yy + 2), fill=hx("#7a1428"))
    rr = random.Random(4)
    for _ in range(70):
        d.point((rr.randint(250, 440), rr.randint(95, 190)), fill=hx("#e0b43c") if rr.random() < .7 else hx("#8fe0ee"))
    # far skyline + hills + trees
    r2 = random.Random(21); x = 300
    while x < BIG:
        w, h = r2.randint(10, 22), r2.randint(18, 60)
        R(d, x, G - 20 - h, x + w, G - 20, hx("#0c4358"))
        for k in range(3):
            d.point((x + r2.randint(1, w - 1), G - 20 - r2.randint(2, h)), fill=hx("#c6a43a"))
        x += w + r2.randint(1, 5)
    d.polygon([(0, 196), (60, 170), (130, 184), (200, 176), (200, G), (0, G)], fill=hx("#0b3a4d"))
    trees(d, 0, 200, 200, hx("#072c3c"), 8); trees(d, 0, 200, 214, hx("#082f40"), 9, 14, 24)
    # power infrastructure
    pc = hx("#08202c")
    for px in (70, 262, 420):
        pole(d, px, G, pc)
    for k in range(3):
        wire(d, 70, 120 + k * 8, 262, 126 + k * 8, pc, 12); wire(d, 262, 126 + k * 8, 420, 118 + k * 8, pc, 14)
        wire(d, 0, 104 + k * 7, 70, 120 + k * 8, pc, 8)
    # shop building
    R(d, 130, 168, 262, G, hx("#0b2733")); R(d, 126, 160, 266, 170, hx("#12384a"))
    for x in range(132, 262, 8):
        d.line([x, 171, x, G], fill=hx("#0d2e3b"))
    R(d, 150, 150, 166, 160, hx("#17475c")); d.line([152, 153, 164, 153], fill=hx("#2d6a82"))
    for i, x0 in enumerate((140, 168, 198, 228)):
        win(d, x0, 184, x0 + 20, 208, hx(("#f2e3a1", "#f7e9ad", "#e9d98c", "#f4dc92")[i]), hx("#0b2733"), (2, 2))
        R(d, x0 + 2, 186 + (i % 2) * 4, x0 + 6, 194, hx("#c9953a"))
    for i in range(0, 132, 12):
        R(d, 130 + i, 172, 136 + i, 180, hx("#2a7a8c") if (i // 12) % 2 == 0 else hx("#0b2733"))
    glyph_run(d, 140, 162, 9, mix(hx("#0b2733"), hx("#ff7a8a"), flicker(t, .7)), 17, 7, 5, 2)
    R(d, 264, 190, 300, G, hx("#0f3445")); R(d, 270, 196, 286, G - 2, hx("#5fd0e0")); R(d, 272, 198, 284, 206, hx("#b8f4ff"))
    R(d, 292, 190, 296, G, hx("#17475c"))
    car(d, 22, G - 2, hx("#7fa5b5"), hx("#1a4a62"), hx("#ff4a4a"), hx("#07141c"))
    d.line([0, 206, 128, 206], fill=hx("#0a2c3a"), width=2)
    for x in range(4, 128, 12):
        d.line([x, 206, x, G], fill=hx("#0a2c3a"))
    # ground
    R(d, 0, G, BIG, H, hx("#0a3a4e")); R(d, 0, G, BIG, G + 5, hx("#2a7a8c"))
    for x in range(0, BIG, 36):
        R(d, x, 262, x + 18, 264, hx("#4ab3c4") if flicker(t, x) > 0 else hx("#2a7a8c"))
    d.line([196, 150, 200, G], fill=hx("#0a2430"), width=2); R(d, 190, 148, 204, 152, hx("#1a5a70"))      # lamp
    img = glowpool(img, 197, G + 18, 46, 14, (60, 120, 130), .8)
    img = glowpool(img, 190, G + 22, 70, 16, (140, 120, 60), .55)
    img = reflect(img, G, t)
    for i in range(5):
        rr_ = (t * 8 + i * 6) % 24
        ImageDraw.Draw(img).ellipse([150 - rr_ * 1.4, 304 - rr_ / 2.4, 150 + rr_ * 1.4, 304 + rr_ / 2.4], outline=hx("#3a8ea2"))
    img = mist(img, G - 24, G + 18, hx("#6fc0cc"), .22, t, 1)
    rain(img, t, 1, 180, hx("#5fb3c4"), G)
    return img


def scene_izakaya(t):
    G = 280
    img = Image.new("RGB", (BIG, H))
    img = dither_gradient(img, 0, H, [hx(c) for c in ("#040a1e", "#06102a", "#08142e", "#030812", "#02050f")])
    d = ImageDraw.Draw(img)
    r = random.Random(32)
    for x0, x1, sd in ((0, 78, 33), (404, BIG, 34)):                            # neighbouring blocks
        rr = random.Random(sd); x = x0
        while x < x1:
            w, h = rr.randint(14, 26), rr.randint(90, 210)
            R(d, x, G - h, x + w, G, hx("#060b1a"))
            for _ in range(6):
                if rr.random() < .5:
                    R(d, x + rr.randint(1, w - 4), G - rr.randint(6, h), x + rr.randint(1, w - 4) + 2, G - rr.randint(6, h) + 3, hx("#3b3414"))
            x += w + 2
    R(d, 80, 0, 408, G, hx("#0a0f1f"))                                          # main building
    for y in range(0, G, 6):
        for x in range(80 + (y // 6 % 2) * 6, 408, 12):
            d.point((x, y), fill=hx("#0e1428"))
    d.polygon([(52, 150), (244, 112), (436, 150), (436, 162), (52, 162)], fill=hx("#101830"))       # tiled roof
    for yy in range(118, 162, 5):
        d.line([60 + (yy - 118), yy + 12, 428 - (yy - 118), yy + 12], fill=hx("#0b1226"))
    for x in range(60, 430, 10):
        d.point((x, 160), fill=hx("#1a2444"))
    for rw in range(3):                                                         # upper windows
        for cl in range(8):
            on = (cl * 3 + rw * 5) % 7 == 0
            R(d, 104 + cl * 36, 20 + rw * 30, 124 + cl * 36, 38 + rw * 30, hx("#6b5a1c") if on else hx("#0d1226"))
            d.line([104 + cl * 36, 29 + rw * 30, 124 + cl * 36, 29 + rw * 30], fill=hx("#06081a"))
    f = flicker(t, 1.3)
    red, deep, hot = mix(hx("#2a0508"), hx("#ff1b1b"), f), mix(hx("#2a0508"), hx("#a80c18"), f), mix(hx("#2a0508"), hx("#ffe9e0"), f)
    d.rounded_rectangle([176, 88, 322, 134], 22, outline=deep, width=3)                           # pill sign
    d.rounded_rectangle([180, 92, 318, 130], 18, outline=mix(deep, hx("#ff6a6a"), .4), width=1)
    d.ellipse([118, 78, 188, 146], fill=red)                                                       # disc sign
    d.ellipse([122, 82, 184, 142], outline=mix(red, (255, 255, 255), .45))
    d.polygon([(138, 112), (168, 112), (164, 132), (142, 132)], fill=hx("#1a0408"))                # bowl emblem
    d.arc([140, 100, 166, 124], 200, 340, fill=hot)
    for sx in (146, 154, 162):
        wob = int(math.sin(t * 3 + sx) * 2); d.line([sx + wob, 108, sx + wob, 98], fill=hot)
    glyph_run(d, 198, 98, 9, hot, 7, 9, 7, 4, 2)
    glyph_run(d, 192, 120, 11, mix(hx("#401018"), hx("#ffd0c0"), f), 9, 5, 5, 3, 1)
    R(d, 346, 0, 380, 92, mix(hx("#2a0508"), hx("#e01420"), flicker(t, 4.1)))                       # banner
    d.rectangle([346, 0, 380, 92], outline=hx("#7a1020"))
    for k in range(4):
        glyph_run(d, 355, 8 + k * 20, 2, hx("#ffd8c8"), 40 + k, 11, 8, 4, 2) if False else glyph_run(d, 353, 8 + k * 20, 3, hx("#ffd8c8"), 40 + k, 9, 5, 2, 1)
    for i in range(7):                                                                              # teal sign row
        R(d, 168 + i * 17, 174, 175 + i * 17, 182, mix(hx("#06323a"), hx("#17bfd0"), flicker(t, 3 + i, 4)))
    for lx, sw in ((98, 0), (388, 1)):                                                              # lanterns
        ox = int(math.sin(t * 1.7 + sw * 2) * 2)
        d.line([lx + 8, 196, lx + 8 + ox, 208], fill=hx("#3a0a10"))
        d.ellipse([lx - 2 + ox, 206, lx + 18 + ox, 232], fill=hx("#e82020")); d.line([lx + 8 + ox, 208, lx + 8 + ox, 230], fill=hx("#ff8a6a"))
    # shop front
    for i in range(0, 224, 14):
        R(d, 100 + i, 200, 112 + i, 214, hx("#d8c030") if (i // 14) % 2 == 0 else hx("#241c08"))
    R(d, 100, 214, 324, G, hx("#3b3414"))
    R(d, 112, 218, 312, G - 4, hx("#f4e11c"))
    for x in range(112, 312, 25):
        d.line([x, 218, x, G - 4], fill=hx("#9a8a10"))
    d.line([112, 248, 312, 248], fill=hx("#9a8a10"))
    for i in range(7):                                                                              # hanging bowls + shelves
        R(d, 124 + i * 26, 222, 134 + i * 26, 230, hx("#c9a418")); d.arc([124 + i * 26, 224, 134 + i * 26, 236], 0, 180, fill=hx("#8a7210"))
    R(d, 112, 258, 312, 262, hx("#8a6a10"))
    bob = int(math.sin(t * 4) * 1)
    d.polygon([(200, G - 4), (204, 240 + bob), (216, 232 + bob), (228, 240 + bob), (232, G - 4)], fill=hx("#16130a"))           # cook
    d.ellipse([208, 218 + bob, 224, 236 + bob], fill=hx("#16130a")); R(d, 205, 212 + bob, 227, 220 + bob, hx("#16130a"))
    steam_ = lambda x, y, n: [d.ellipse([x + math.sin(t * 2 + i) * 3 - 2, y - i * 5 - (t * 12) % 5 - 1, x + math.sin(t * 2 + i) * 3 + 2, y - i * 5 - (t * 12) % 5 + 1], fill=hx("#b8a838")) for i in range(n)]
    steam_(254, 252, 4)
    # clutter: AC units, pipes, balconies, cables, laundry
    for x in (92, 392):
        R(d, x - 10, 168, x + 12, 186, hx("#141c33")); d.line([x - 6, 174, x + 8, 174], fill=hx("#243050")); d.line([x - 6, 179, x + 8, 179], fill=hx("#243050"))
    for px in (84, 402):
        d.line([px, 20, px, 200], fill=hx("#1b2440"), width=2)
    for bx in (104, 176, 248, 320):
        R(d, bx, 142, bx + 34, 145, hx("#18213a")); d.line([bx, 145, bx, 156], fill=hx("#18213a"))
        for rx in range(bx, bx + 34, 4):
            d.line([rx, 145, rx, 150], fill=hx("#0c142a"))
    for k, (lx, c) in enumerate(((190, "#7a2030"), (200, "#203a7a"), (210, "#7a7a20"))):
        sw = int(math.sin(t * 2.2 + k) * 1)
        R(d, lx + sw, 148, lx + 6 + sw, 158, hx(c))
    for k in range(3):
        wire(d, 0, 60 + k * 6, 84, 92 + k * 6, hx("#0a1020"), 10); wire(d, 402, 92 + k * 6, BIG, 66 + k * 6, hx("#0a1020"), 10)
    img_pool = [(212, G + 24, 120, 26, (210, 190, 20), .7), (140, G + 20, 44, 14, (220, 30, 30), .6), (256, G + 28, 140, 22, (180, 40, 60), .3)]
    R(d, 0, G, BIG, H, hx("#03060f")); R(d, 0, G, BIG, G + 4, hx("#10172c"))
    for x in range(0, BIG, 48):
        R(d, x + 6, G + 40, x + 30, G + 42, hx("#10172c"))
    for gp in img_pool:
        img = glowpool(img, *gp)
    img = reflect(img, G, t, .38, (4, 6, 16))
    img = mist(img, G - 36, G + 8, hx("#2a3a6a"), .2, t, 3)
    rain(img, t, 2, 120, hx("#2c4066"), G, 160)
    return img


def scene_bridge(t):
    G = 248
    img = Image.new("RGB", (BIG, H))
    img = dither_gradient(img, 0, G, [hx(c) for c in ("#050f2e", "#07204a", "#0a2a52", "#0d3258", "#12406a")])
    d = ImageDraw.Draw(img)
    for x0, x1, sd, hmax in ((0, 290, 41, 70), (300, BIG, 42, 50)):                 # distant skyline + beacons
        rr = random.Random(sd); x = x0
        while x < x1:
            w, h = rr.randint(10, 22), rr.randint(20, hmax + 30)
            R(d, x, G - 20 - h, x + w, G - 20, hx("#081c3a"))
            for _ in range(4):
                d.point((x + rr.randint(1, w - 1), G - 20 - rr.randint(3, h)), fill=hx("#2a6aa8"))
            if rr.random() < .35 and int(t * 1.5 + x) % 3 == 0:
                d.point((x + w // 2, G - 22 - h), fill=hx("#ff3a4a"))
            x += w + rr.randint(1, 4)
    R(d, 282, 14, 414, 236, hx("#0c2a4e")); R(d, 300, 6, 396, 20, hx("#0e3158"))                  # tower
    d.line([348, 6, 348, -10], fill=hx("#1a4a7a"), width=2)
    if int(t * 1.6) % 2 == 0:
        d.ellipse([345, 0, 351, 6], fill=hx("#ff3a4a"))
    rr = random.Random(5)
    for row in range(26):
        for col in range(26):
            on = rr.random() < .25
            if on and (row * 7 + col * 3 + int(t * 3)) % 11 == 0:
                on = False
            R(d, 288 + col * 5, 44 + row * 7, 291 + col * 5, 47 + row * 7, hx("#1b5d90") if on else hx("#0a2442"))
    R(d, 296, 24, 400, 42, hx("#0e3158")); d.rectangle([296, 24, 400, 42], outline=hx("#1b4a80"))
    glyph_run(d, 318, 28, 4, hx("#4aa0d8"), 3, 10, 8, 6, 2)
    d.polygon([(40, 140), (260, 116), (408, 182), (408, 198), (260, 142), (40, 162)], fill=hx("#0a1838"))     # gantry
    d.polygon([(40, 140), (260, 116), (408, 182), (400, 180), (260, 120), (44, 144)], fill=hx("#14285a"))
    for x in range(48, 400, 14):
        yt = 140 + (x - 40) * (182 - 140) / 368 - (22 * (1 - (x - 40) / 220) if x < 260 else 0)
        d.line([x, yt, x + 7, yt + 18], fill=hx("#071230"))
    for x, h in ((72, 108), (140, 106), (208, 104), (300, 66)):
        d.polygon([(x, 150), (x + 4, 150), (x + 2, G), (x - 3, G)], fill=hx("#06122a"))
        d.line([x - 2, 175, x + 5, 200], fill=hx("#0a1c3e"))
    for k in range(5):
        R(d, 52 + k * 28, 190, 70 + k * 28, 232, hx("#081832"))
    f = flicker(t, 2.2, 6); g = mix(hx("#0a2a10"), hx("#9cff2a"), f)
    d.ellipse([268, 140, 300, 172], outline=g, width=3); d.line([284, 146, 284, 166], fill=g, width=2)       # green sign
    d.arc([272, 144, 296, 168], 20, 160, fill=mix(g, (255, 255, 255), .3))
    glyph_run(d, 306, 148, 5, g, 11, 12, 8, 3, 2)
    # ground, truck, stalls
    R(d, 0, G, BIG, H, hx("#05122a")); R(d, 0, G, BIG, G + 4, hx("#0c2a52"))
    R(d, 150, 206, 258, G, hx("#0a1830")); R(d, 150, 206, 258, 211, hx("#10264a"))
    d.ellipse([180, 214, 224, 244], outline=hx("#102a52"))                                                    # faint logo
    R(d, 258, 214, 286, G, hx("#cfd6df")); R(d, 262, 220, 280, 232, hx("#3a5a8a")); R(d, 280, 224, 286, 232, hx("#ff6a3c"))
    for wx in (176, 214, 272):
        d.ellipse([wx - 9, G - 9, wx + 9, G + 9], fill=hx("#03091a")); d.ellipse([wx - 3, G - 3, wx + 3, G + 3], fill=hx("#1a2a50"))
    R(d, 148, 230, 151, 236, hx("#ff3a3a"))
    for i in range(4):
        c = mix(hx("#0a3a40"), hx("#7af0e0"), flicker(t, 3 + i, 5))
        win(d, 322 + i * 34, 224, 346 + i * 34, 244, c, hx("#06222a"), (2, 1))
    R(d, 316, 212, 470, 221, hx("#0c2a40"))
    for i in range(0, 154, 14):
        R(d, 316 + i, 212, 322 + i, 221, hx("#12486a") if (i // 14) % 2 == 0 else hx("#0c2a40"))
    for lx in (36, 120, 300):                                                                                   # lamp posts + cones
        d.line([lx, 170, lx, G], fill=hx("#0a1c3a"), width=2); R(d, lx - 8, 166, lx + 8, 170, hx("#3b8fd0"))
        d.polygon([(lx - 5, 171), (lx + 5, 171), (lx + 16, G), (lx - 16, G)], fill=hx("#091f40"))
    px = int(60 + t * 12)                                                                                       # umbrella walker
    bob = int(abs(math.sin(t * 6)) * 2)
    d.pieslice([px - 12, 218 - bob, px + 12, 236 - bob], 180, 360, fill=hx("#3b8fd0"))
    d.line([px, 227 - bob, px, 232 - bob], fill=hx("#0a1830"))
    R(d, px - 2, 232 - bob, px + 2, 244 - bob, hx("#02060f")); d.ellipse([px - 3, 228 - bob, px + 3, 234 - bob], fill=hx("#02060f"))
    leg = int(math.sin(t * 6) * 3); d.line([px, 244 - bob, px + leg, G], fill=hx("#02060f")); d.line([px, 244 - bob, px - leg, G], fill=hx("#02060f"))
    for gp in ((300, G + 20, 70, 16, (50, 120, 170), .6), (350, G + 22, 90, 14, (90, 240, 220), .5), (284, G + 14, 50, 10, (255, 90, 50), .5),
               (284, 198, 22, 14, (150, 255, 40), .0)):
        img = glowpool(img, *gp)
    img = reflect(img, G, t, .45, (0, 10, 30))
    img = mist(img, G - 40, G + 10, hx("#3a5a98"), .18, t, 5)
    rain(img, t, 3, 150, hx("#3f6fa8"), G, 150)
    return img


def bloom(img, thresh=100, radius=3.0, gain=.8):
    a = np.asarray(img).astype(np.float32)
    mask = (a.max(axis=2, keepdims=True) > thresh) * a
    glow = np.asarray(Image.fromarray(mask.astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius))).astype(np.float32)
    return Image.fromarray((a + glow * gain).clip(0, 255).astype(np.uint8))


def frame(t):
    s = 0 if t < CUTS[0] else 1 if t < CUTS[1] else 2
    t0 = (0, *CUTS)[s]
    img = (scene_roadside, scene_izakaya, scene_bridge)[s](t)
    off = min(START[s] + int((t - t0) * 8), BIG - W)
    img = bloom(img.crop((off, 0, off + W, H)))
    a = np.asarray(img).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    a *= (1 - .35 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2)[..., None]
    a[::2] *= .97
    noise = np.random.default_rng(int(t * FPS)).normal(0, 1.6, a.shape[:2])[..., None]     # light film grain (deterministic)
    return Image.fromarray((a + noise).clip(0, 255).astype(np.uint8)).resize((W * SCALE, H * SCALE), Image.NEAREST)


def video(out):
    here = os.path.dirname(os.path.abspath(__file__))
    sp = importlib.util.spec_from_file_location("neon_basic", os.path.join(here, "render_neon_offline.py"))
    basic = importlib.util.module_from_spec(sp); sp.loader.exec_module(basic)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav"); basic.audio(wav)
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W * SCALE}x{H * SCALE}", "-r", str(FPS),
               "-i", "-", "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-c:a", "aac", "-b:a", "160k",
               "-t", str(DUR), "-movflags", "+faststart", out]
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
            frame(float(s_)).save(os.path.join(sys.argv[2], f"d{float(s_):.2f}.png"))
    elif len(sys.argv) == 3 and sys.argv[1] == "video":
        video(sys.argv[2])
    else:
        sys.exit(__doc__)
