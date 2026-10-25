"""Pixel Studio V5: independent sprite-linked puddle reflections and practical light.

All operations use native RGBA pixels, no blur, credits, online models, or
flattened stills. The reflections sample the *current animation cel*, not a
pre-rendered background. Source remains editable and 100% free.
"""
import math
from PIL import Image, ImageDraw

def reflect_sprite(scene, sprite, x, y, frame, ground_y=421):
    """Mirror the actual moving cel over broken puddle bands at road level."""
    if x >= scene.width or x + sprite.width <= 0:
        return
    reflected = sprite.transpose(Image.Transpose.FLIP_TOP_BOTTOM).resize(
        (sprite.width, 49), Image.Resampling.NEAREST)
    source = reflected.load()
    overlay = Image.new('RGBA', scene.size, (0, 0, 0, 0))
    dest = overlay.load()
    for row in range(reflected.height):
        yy = ground_y + row
        if yy < 0 or yy >= scene.height:
            break
        strength = (1 - row / reflected.height) ** 1.4
        if (row + frame // 8) % 9 in (0, 1):
            strength *= .34  # water ripple gaps; no Gaussian blur
        horizontal_wave = round(2 * math.sin(row * .29 + frame * .11))
        for col in range(reflected.width):
            xx = x + col + horizontal_wave
            if xx < 0 or xx >= scene.width:
                continue
            r, g, b, a = source[col, row]
            if not a:
                continue
            alpha = round(a * strength * .40)
            if alpha:
                dest[xx, yy] = (
                    min(255, round(r * .45 + 8)),
                    min(255, round(g * .70 + 11)),
                    min(255, round(b * .82 + 19)), alpha)
    scene.alpha_composite(overlay)

def passing_headlight(scene, x, y, frame, reveal=0.0):
    """Moving trolley lamp streaks and a late cyan storefront reflection."""
    draw = ImageDraw.Draw(scene, 'RGBA')
    nose = x + 154
    for row in range(16):
        yy = y + 66 + 3 * row
        if yy >= scene.height:
            break
        if (row + frame // 6) % 6 in (0, 1):
            continue
        width = 2 + row // 2
        centre = nose + round(row * .43)
        left, right = max(0, centre - width), min(scene.width - 1, centre + width)
        if left <= right:
            brightness = max(5, 81 - row * 5)
            draw.line((left, yy, right, yy), fill=(247, 170, 98, brightness))
            if row % 3 == 0:
                draw.point((min(scene.width - 1, max(0, centre)), yy),
                           fill=(255, 214, 154, brightness + 20))
    if reveal > 0:
        for row in range(17):
            yy = 394 + 5 * row
            if yy >= scene.height:
                break
            if row % 5 == 2:
                continue
            width = 9 + row // 2
            drift = round(math.sin(frame * .18 + row * .93) * 3)
            opacity = round(max(0, 104 - row * 5) * reveal)
            if opacity:
                draw.line((max(0, 236 - width + drift), yy,
                           min(scene.width - 1, 236 + width + drift), yy),
                          fill=(46, 219, 230, opacity))

def wheel_contact_spray(scene, x, y, frame):
    """Sparse finite-life droplets tied to the wheels' actual position."""
    draw = ImageDraw.Draw(scene, 'RGBA')
    for wheel in (35, 130):
        centre = x + wheel
        for seed in range(7):
            age = (frame * 2 + seed * 13 + wheel) % 23
            xx = centre - age * .82 + (seed % 3 - 1) * 2
            yy = y + 61 - round(math.sin((age / 23) * math.pi) *
                                 (2 + seed % 4))
            if 0 <= xx < scene.width and 0 <= yy < scene.height:
                draw.point((round(xx), round(yy)),
                           fill=(104, 173, 188, max(0, 70 - age * 3)))
