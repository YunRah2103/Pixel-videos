#!/usr/bin/env python3
"""Strict technical pixel-art PNG QA; never claims subjective artistic quality."""
import argparse
import json
from collections import Counter
from pathlib import Path
from PIL import Image

def inspect(path, native=None, source=None, scale=None, max_colors=None):
    with Image.open(path) as file:
        im = file.convert("RGBA")
    w, h = im.size
    colors = len(Counter(im.getdata()))
    alpha = im.getchannel("A")
    occupied = alpha.getbbox()
    issues = []
    if occupied is None:
        issues.append("fully transparent artwork")
    if native and (w, h) != tuple(native):
        issues.append(f"dimensions {(w,h)} != expected {tuple(native)}")
    if max_colors and colors > max_colors:
        issues.append(f"{colors} distinct RGBA values > palette limit {max_colors}")
    if source:
        if not scale or scale < 1 or int(scale) != scale:
            issues.append("integer positive --scale required with --source")
        else:
            with Image.open(source) as f:
                original = f.convert("RGBA")
            expected = original.resize((original.width * scale, original.height * scale), Image.Resampling.NEAREST)
            if expected.size != im.size or expected.tobytes() != im.tobytes():
                issues.append("not a bit-exact nearest-neighbour integer upscale")
    return {"file": str(path), "size": [w,h], "rgba_colors": colors, "occupied": occupied is not None, "ok": not issues, "issues": issues}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+", type=Path)
    ap.add_argument("--size", help="Expected WxH of each inspected PNG")
    ap.add_argument("--source", type=Path, help="Native PNG to compare with one scaled result")
    ap.add_argument("--scale", type=int)
    ap.add_argument("--max-colors", type=int)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    size = tuple(map(int,args.size.lower().split("x"))) if args.size else None
    if size and (len(size) != 2 or min(size) < 1):
        ap.error("size must be positive WxH")
    if args.source and len(args.files) != 1:
        ap.error("--source requires exactly one output PNG")
    out = [inspect(f, native=size, source=args.source, scale=args.scale, max_colors=args.max_colors) for f in args.files]
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for r in out:
            print(("PASS" if r["ok"] else "FAIL"),r["file"],"size",r["size"],"colors",r["rgba_colors"],"; ".join(r["issues"]))
    raise SystemExit(0 if all(r["ok"] for r in out) else 1)
if __name__ == "__main__":
    main()
