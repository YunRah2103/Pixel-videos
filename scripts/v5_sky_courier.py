"""Original eight-cel skyline courier for the licensed neon-street film.
Separate editable pixel artwork routed using a real Tiled object layer.
No AI services, blur, flattened image, or external art in this sprite.
"""
import math
from PIL import Image, ImageDraw
INK=(10,17,35,255)
STEEL=(29,66,83,255)
TEAL=(74,184,194,255)
GOLD=(242,173,110,255)
ICE=(156,235,220,255)

def courier_cel(phase):
    """Hand-pixelled clockwork delivery blimp, deliberately NOT another road car."""
    im=Image.new('RGBA',(66,34),(0,0,0,0))
    d=ImageDraw.Draw(im,'RGBA')
    # Peach-coloured airship gasbag with hand-selected fabric segments, keel, tail.
    d.polygon([(2,14),(7,8),(17,4),(33,3),(49,6),(58,10),(61,15),
               (57,20),(48,23),(17,23),(7,19)],fill=(23,17,42),outline=(236,120,101))
    d.polygon([(6,13),(12,9),(22,6),(43,6),(53,10),(58,15),
               (53,19),(41,21),(18,21),(8,18)],fill=(198,75,112))
    d.polygon([(12,10),(22,6),(43,6),(51,9),(41,11),(21,12)],fill=(255,176,120))
    d.line((10,15,52,15),fill=(251,145,107),width=2)
    d.line((18,7,15,19),fill=(111,37,83),width=1)
    d.line((39,7,42,20),fill=(107,43,81),width=1)
    d.line((53,13,59,13),fill=(255,227,165))
    # Dorsal fins and folded back rudder emphasize floating craft silhouette.
    d.polygon([(7,12),(0,7),(3,19),(9,18)],fill=(88,39,83))
    d.line((1,7,5,13),fill=(250,149,117))
    d.line((21,5,30,3,43,6),fill=(255,211,149))
    # Slender suspension, angular hanging gondola, warm navigation light.
    for x in (23,43):d.line((x,21,x-1,26),fill=(241,173,143))
    d.polygon([(20,26),(45,26),(48,29),(41,33),(25,33),(19,29)],
              fill=(12,28,47),outline=(237,146,111))
    d.rectangle((26,27,39,30),fill=(50,154,167),outline=(222,187,135))
    d.line((29,28,36,28),fill=(177,237,218))
    d.rectangle((43,29,46,31),fill=(245,216,157))
    # Faint blades rotate with real eight-cel phase, hanging rear lantern flickers.
    angle=(phase%8)*math.pi/4
    dx=round(4*math.cos(angle));dy=round(3*math.sin(angle))
    d.line((60-dx,15-dy,60+dx,15+dy),fill=(109,215,205))
    d.point((60,15),fill=(251,203,145))
    d.rectangle((19,30,21,32),fill=(248,185,109) if phase%2 else (244,122,108))
    return im

CELS=[courier_cel(i) for i in range(8)]

def save_courier_cels(directory):
    directory.mkdir(parents=True,exist_ok=True)
    for i,cel in enumerate(CELS):cel.save(directory/('courier-cel-%d.png'%i))
    return CELS

def paint_sky_courier(canvas,frame,start,finish):
    """Cross behind artist-authored near architecture: composite after far plane."""
    t=frame/30.0
    travel=max(0,min(1,(t-.30)/3.95))
    if travel<=0 or travel>=1:return None
    ease=travel*travel*(3-2*travel)
    x=round(start['x']+(finish['x']-start['x'])*ease)
    y=round(start['y']+(finish['y']-start['y'])*ease+2*math.sin(t*3))
    canvas.alpha_composite(CELS[(frame//3)%8],(x,y))
    d=ImageDraw.Draw(canvas,'RGBA')
    for n in range(5):
        xx=x+62+5*n;yy=y+22+(n%2)
        if 0<=xx<canvas.width and 0<=yy<canvas.height and (frame+n*3)%9<7:
            d.line((xx,yy,xx+min(3,n),yy),fill=(242,151,109,max(0,80-n*15)))
    return (x,y)
