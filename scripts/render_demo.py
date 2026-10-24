#!/usr/bin/env python3
"""Dependency-light offline proof renderer for Pixel Videos.

Renders ORIGINAL procedural pixel art using Pillow and pipes frames into FFmpeg.
It is deliberately separate from Remotion; the Remotion entry point is src/index.ts.
"""
from __future__ import annotations
import argparse
import math
import os
import random
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

W, H = 360, 640
FPS = 30
SKY = [
    '#203b64','#2b456f','#35507a','#495b85','#5b658e','#6b6e97',
    '#81759b','#987e9f','#b1879e','#c48c9b','#d7969b','#e4a19a',
    '#eca99a','#f3b79c','#f5c5a4','#f9d0ac','#f8d9b4','#f0cbaa',
]

def rect(draw, x, y, w, h, color):
    x, y = round(x), round(y)
    draw.rectangle((x, y, x + w - 1, y + h - 1), fill=color)

def cloud(draw, x, y, s=1, shade=False):
    base = '#90769e' if shade else '#f9c6b3'
    dark = '#655f88' if shade else '#d69cab'
    for dx, dy, w, h, c in [
        (0, 12, 72, 11, dark), (11, 5, 58, 15, base),
        (25, -2, 29, 18, base), (70, 12, 22, 13, dark),
        (13, 22, 86, 7, dark), (35, 27, 54, 4, '#a17f9e'),
    ]:
        rect(draw, x + dx * s, y + dy * s, max(1, round(w*s)), max(1, round(h*s)), c)

def building(draw, x, y, width, height, fill, seed):
    rect(draw, x, y-height, width, height, fill)
    rect(draw, x-2, y-height-4, width+4, 4, '#354d69')
    for row in range(6, height-5, 13):
        for col in range(5, width-3, 10):
            c = '#f4c99d' if (seed+row//13+col//10) % 4 else '#52738d'
            rect(draw, x+col, y-height+row, 4, 5, c)

def render(frame):
    image = Image.new('RGB', (W, H), SKY[0])
    d = ImageDraw.Draw(image)
    for i, c in enumerate(SKY):
        rect(d, 0, i*19, W, 20, c)
    star_rng = random.Random(1397)
    for i in range(55):
        x, y = star_rng.randrange(350), star_rng.randrange(160)
        rect(d, x, y, 1+(i%7==0), 1, '#e6d7d4' if i%3==0 else '#7c96ae')
    for r, c in [(48,'#f0b8a4'), (41,'#f4c5a6'), (34,'#fbd0aa'), (26,'#f8d7af'), (19,'#ffe3b8')]:
        rect(d, 273-r, 243-r, r*2, r*2, c)
    drift = frame*0.14
    cloud(d, -38 - 0.5*drift, 135, 1.6, True)
    cloud(d, 146 - 0.4*drift, 72, 1.0)
    cloud(d, 258 - 0.6*drift, 184, 1.2, True)
    cloud(d, -40 + (frame*0.1)%470, 215, 0.9)
    d.polygon([(0,338),(25,318),(48,323),(66,300),(93,325),(116,302),
               (143,317),(174,291),(195,307),(226,289),(257,315),
               (291,303),(321,317),(360,306),(360,419),(0,419)],fill='#657895')
    d.polygon([(0,357),(42,332),(78,349),(110,332),(146,355),(181,321),
               (210,343),(241,328),(279,349),(311,331),(360,352),(360,420),(0,420)],fill='#3d617f')
    rect(d, 0, 360, W, 168, '#3b6b87')
    for i in range(21):
        rect(d, 0, 362+i*8, 360, 2, '#547c96' if i%3==0 else '#356480')
    for i in range(150):
        x = (i*79 + int(frame*(i%4+1)*0.34)) % 388 - 15
        y = 361 + (i*17)%164
        refl = 220 < x < 319
        rect(d, x, y, 11 if refl else 4 + (i%9), 1+(i%8==0), '#f4c299' if refl else '#7192a3')
    for j, args in enumerate([
        (-3,377,40,72,'#475d79'),(34,375,44,95,'#455a7a'),
        (78,378,28,59,'#4a6685'),(105,379,45,105,'#405978'),
        (149,379,37,70,'#516681'),(180,378,41,87,'#455a76'),
        (226,380,38,54,'#4b6481'),(270,378,39,72,'#425a76'),
        (309,380,53,92,'#405673')]):
        building(d, *args, j)
    rect(d, 0, 377, W, 7, '#354f69')
    boatx = int(390 - frame*0.85)
    rect(d, boatx, 432, 55, 5, '#263c56')
    rect(d, boatx+8, 437, 35, 5, '#233648')
    rect(d, boatx+14, 412, 25, 19, '#e3bea3')
    rect(d, boatx+17, 410, 20, 3, '#f6d5b3')
    rect(d, boatx+25, 391, 3, 19, '#243a56')
    rect(d, 0, 505, 360, 135, '#303f53')
    rect(d, 0, 506, 360, 9, '#86939c')
    rect(d, 0, 515, 360, 4, '#4b6075')
    for i in range(15):
        rect(d, i*27-10, 553+(i%3)*2, 22, 1, '#536478')
    rect(d, 0, 479, 360, 5, '#807b8f')
    for i in range(11):
        rect(d, i*36+8, 483, 4, 29, '#657488')
        rect(d, i*36+7, 475, 6, 7, '#aaa19b')
    rect(d, 63, 425, 5, 85, '#354459')
    rect(d, 51, 425, 27, 5, '#516781')
    rect(d, 55, 433, 19, 5, '#f6d6a9')
    rect(d, 59, 438, 11, 7, '#ffe0ae')
    # Character stands on the promenade; tiny 1-2px head movement
    personx = 208 + round(math.sin(frame*.047)*1)
    rect(d, personx+4, 441, 10, 12, '#e9baa6')
    rect(d, personx+2, 439, 14, 5, '#30374d')
    rect(d, personx, 454, 18, 26, '#283d58')
    rect(d, personx-3, 459, 4, 20, '#2a3c57')
    rect(d, personx+16, 459, 4, 20, '#2a3c57')
    rect(d, personx+3, 480, 5, 30, '#283147')
    rect(d, personx+11, 480, 5, 30, '#283147')
    for i in range(47):
        x = (i*83)%359
        height = 11+(i*13)%26
        sway = round(math.sin(frame*0.06+i)*2)
        rect(d, x, 640-height, 2, height, '#345d5e' if i%2 else '#517c74')
        rect(d, x+sway, 636-height, 5, 4, '#86a888' if i%3==0 else '#4d7b69')
    rect(d, 0, 631, 360, 9, '#2d4650')
    return image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=int, default=6)
    ap.add_argument('--out', default='out/sunset-harbor-offline.mp4')
    ap.add_argument('--poster', default='out/sunset-harbor-poster.png')
    args = ap.parse_args()
    if not shutil.which('ffmpeg'):
        raise SystemExit('FFmpeg not found. Install FFmpeg first.')
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    Image.Image.save(render(92), args.poster)
    cmd = ['ffmpeg','-hide_banner','-loglevel','error','-y',
           '-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24',
           '-s',f'{W}x{H}','-r',str(FPS),'-i','-',
           '-vf','scale=1080:1920:flags=neighbor,format=yuv420p',
           '-c:v','libx264','-preset','veryfast','-crf','18',
           '-pix_fmt','yuv420p','-movflags','+faststart',str(dest)]
    with subprocess.Popen(cmd, stdin=subprocess.PIPE) as p:
        try:
            assert p.stdin
            for frame in range(FPS*args.seconds):
                p.stdin.write(render(frame).tobytes())
        finally:
            if p.stdin:
                p.stdin.close()
        if p.wait() != 0:
            raise SystemExit('FFmpeg failed')
    print(f'Created {dest} / {args.poster}')

if __name__ == '__main__':
    main()
