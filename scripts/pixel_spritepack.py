#!/usr/bin/env python3
"""Deterministic uniform-cel atlas PNG+JSON builder; works for PixiJS/Phaser import."""
import argparse
import json
import math
from pathlib import Path
from PIL import Image

def pack(files, sheet, metadata, columns=0, padding=0):
    if not files:
        raise ValueError("Supply at least one sprite frame")
    if padding < 0:
        raise ValueError("Padding cannot be negative")
    if len({p.name for p in files}) != len(files):
        raise ValueError("All source frame basenames must be unique")
    frames = []
    for path in files:
        with Image.open(path) as f:
            frames.append(f.convert("RGBA"))
    size = frames[0].size
    if any(f.size != size for f in frames):
        raise ValueError("All cels must share the same native-pixel dimensions")
    n = len(frames)
    cols = columns or math.ceil(math.sqrt(n))
    if cols < 1:
        raise ValueError("columns must be >= 1")
    rows = math.ceil(n / cols)
    w,h = size
    output = Image.new("RGBA", (cols*w + (cols-1)*padding, rows*h + (rows-1)*padding), (0,0,0,0))
    entries = {}
    for i,(path,im) in enumerate(zip(files,frames)):
        x,y = (i%cols)*(w+padding), (i//cols)*(h+padding)
        output.paste(im,(x,y))
        entries[path.name] = {"frame":{"x":x,"y":y,"w":w,"h":h},"rotated":False,"trimmed":False,
             "spriteSourceSize":{"x":0,"y":0,"w":w,"h":h},"sourceSize":{"w":w,"h":h}}
    sheet.parent.mkdir(parents=True,exist_ok=True)
    metadata.parent.mkdir(parents=True,exist_ok=True)
    output.save(sheet)
    metadata.write_text(json.dumps({"frames":entries,"meta":{"image":sheet.name,"size":{"w":output.width,"h":output.height},"scale":"1"}},indent=2)+"\n",encoding="utf-8")
    return len(entries)

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("frames",nargs="+",type=Path)
    a.add_argument("--sheet",type=Path,required=True)
    a.add_argument("--data",type=Path,required=True)
    a.add_argument("--columns",type=int,default=0)
    a.add_argument("--padding",type=int,default=0)
    x=a.parse_args()
    print(f"Packed {pack(x.frames,x.sheet,x.data,x.columns,x.padding)} frames into {x.sheet}")
if __name__=="__main__":
    main()
