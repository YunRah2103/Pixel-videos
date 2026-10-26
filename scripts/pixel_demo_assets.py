#!/usr/bin/env python3
"""Generate tiny synthetic QA fixtures ONLY. Not intended as finished video artwork."""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw

PALETTE={"clear":(0,0,0,0),"outline":(23,25,36,255),"body":(191,53,63,255),"light":(246,181,93,255),
"glass":(71,141,164,255),"wheel":(36,38,45,255),"road":(84,83,86,255)}
def make(out):
    out.mkdir(parents=True,exist_ok=True)
    files=[]
    for k in range(4):
        im=Image.new("RGBA",(64,32),PALETTE["clear"])
        d=ImageDraw.Draw(im)
        # Fixed hatchback silhouette, wheels with small cyclic spoke shifts.
        d.polygon([(8,17),(13,10),(23,7),(43,7),(51,16),(56,18),(56,23),(8,23)],fill=PALETTE["outline"])
        d.polygon([(11,17),(16,11),(24,9),(42,9),(49,16),(53,18),(53,21),(11,21)],fill=PALETTE["body"])
        d.polygon([(21,10),(40,10),(46,16),(18,16)],fill=PALETTE["glass"])
        d.line([(14,18),(51,18)],fill=PALETTE["light"])
        for cx in (19,46):
            d.ellipse((cx-5,19,cx+5,29),fill=PALETTE["outline"])
            d.ellipse((cx-3,21,cx+3,27),fill=PALETTE["wheel"])
            d.point((cx+(0,1,0,-1)[k],24),fill=PALETTE["light"])
        name=out/f"rally-car-{k:02d}.png"
        im.save(name); files.append(name)
    return files
if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--out",type=Path,default=Path("out/toolbox-fixtures"))
    args=p.parse_args()
    print("\n".join(map(str,make(args.out))))
