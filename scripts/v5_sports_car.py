"""Original Pixel Videos V5 hand-specified 24-cel neo-retro GT coupe.

Native 164x66 pixel art. True two-door long-bonnet coupe, not a tram.
Individual intentional Pillow clusters/ramps; no blur, no GUI authorship claim.
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw

INK=(11,12,29,255)
OUTLINE=(45,24,47,255)
SHADOW=(8,25,39,255)
BASE=(24,87,103,255)
MID=(31,137,148,255)
LIGHT=(87,197,199,255)
PEARL=(168,228,213,255)
PINK=(235,96,138,255)
ROSE=(161,57,101,255)
AMBER=(255,193,122,255)
GLASS=(13,29,53,255)

def wheel(d,cx,phase):
    d.ellipse((cx-14,39,cx+14,67),fill=INK)
    d.ellipse((cx-12,42,cx+12,66),fill=(9,17,31,255))
    d.ellipse((cx-10,44,cx+10,64),fill=(49,48,67,255),outline=(98,114,120,255),width=1)
    d.ellipse((cx-8,46,cx+8,62),fill=(18,37,53,255),outline=(178,176,157,255))
    angle=(phase%24)*2*math.pi/24
    for spoke in range(5):
        a=angle+spoke*2*math.pi/5
        ux,uy=round(math.cos(a)*7),round(math.sin(a)*7)
        d.line((cx+round(ux*.35),54+round(uy*.35),cx+ux,54+uy),
               fill=(199,208,194,255),width=2)
    d.point((cx+round(math.cos(angle)*8),54+round(math.sin(angle)*8)),fill=PINK)
    d.ellipse((cx-2,52,cx+2,56),fill=AMBER,outline=INK)
    d.point((cx,54),fill=PEARL)

def car_cel(phase):
    im=Image.new('RGBA',(164,66),(0,0,0,0))
    d=ImageDraw.Draw(im,'RGBA')
    d.ellipse((13,57,155,65),fill=(3,5,16,100))
    for cx in (36,128):
        d.ellipse((cx-15,39,cx+15,68),fill=INK)
    contour=[(4,39),(9,35),(31,32),(43,31),(57,21),(67,15),
             (76,11),(112,11),(120,15),(132,28),(142,33),
             (154,36),(161,41),(163,47),(161,53),(153,56),
             (13,56),(5,52)]
    d.polygon(contour,fill=OUTLINE)
    d.polygon([(7,40),(19,36),(44,34),(58,24),(71,16),(78,14),
               (111,14),(118,19),(132,32),(150,38),(159,42),
               (160,49),(153,53),(13,53),(8,49)],fill=BASE)
    d.polygon([(8,46),(23,49),(56,48),(90,49),(119,47),
               (152,47),(160,49),(154,54),(14,54)],fill=SHADOW)
    d.line((54,50,112,50),fill=(20,79,96),width=2)
    d.line((52,52,113,52),fill=(68,149,149),width=1)
    d.polygon([(8,39),(27,35),(43,34),(52,36),(43,39),(20,41)],fill=ROSE)
    d.polygon([(39,35),(57,31),(89,33),(113,34),(151,39),
               (148,43),(115,40),(68,39),(38,41)],fill=MID)
    d.polygon([(110,32),(132,32),(152,38),(157,42),
               (127,39),(115,36)],fill=LIGHT)
    d.line((115,35,143,37),fill=PEARL,width=1)
    d.line((18,41,48,41),fill=PINK,width=1)
    d.line((52,43,112,43),fill=(83,168,173),width=1)
    d.line((148,44,160,44),fill=(255,170,144),width=1)
    # Only TWO cockpit glazing sections. Roof sits below the bonnet's hard points.
    d.polygon([(54,30),(67,18),(78,14),(110,14),(120,19),
               (135,33),(119,34),(61,34)],fill=INK)
    d.polygon([(57,30),(69,19),(79,16),(90,16),(90,31)],fill=GLASS)
    d.polygon([(94,16),(109,16),(117,21),(130,31),(94,31)],fill=GLASS)
    d.polygon([(58,28),(70,20),(78,17),(87,17),(84,20),
               (71,22),(63,30)],fill=(58,116,137))
    d.line((96,18,111,18),fill=(88,189,202),width=2)
    d.line((113,20,126,30),fill=PEARL,width=1)
    d.line((95,29,124,29),fill=(35,79,103),width=1)
    d.line((77,13,110,13),fill=(248,139,146),width=1)
    d.line((91,16,91,33),fill=OUTLINE,width=3)
    d.line((65,31,121,32),fill=PINK,width=1)
    d.line((81,14,106,14),fill=(255,192,160),width=1)
    d.polygon([(45,33),(56,27),(58,31),(50,37)],fill=(25,72,89))
    d.line((92,34,91,49),fill=(12,45,62),width=1)
    d.line((92,47,95,49),fill=(17,57,75),width=1)
    d.rectangle((96,38,102,39),fill=(247,183,148))
    d.point((103,39),fill=INK)
    d.polygon([(114,36),(122,36),(120,41),(114,41)],fill=(16,61,81))
    d.line((116,37,119,37),fill=LIGHT,width=1)
    # Short ducktail, rear brake lens, front headlight prism.
    d.line((7,34,21,34),fill=(244,118,148),width=2)
    d.rectangle((6,41,13,44),fill=(246,80,111))
    d.line((7,42,12,42),fill=(255,164,143),width=1)
    d.rectangle((7,49,16,51),fill=(21,30,49))
    d.line((10,54,23,54),fill=(180,107,132),width=1)
    d.polygon([(129,36),(154,39),(160,43),(148,42)],fill=(42,151,161))
    d.rectangle((148,39,156,41),fill=AMBER)
    d.line((148,39,155,39),fill=(255,234,172),width=1)
    d.line((158,43,162,45),fill=PEARL,width=2)
    d.line((153,49,161,49),fill=(39,45,63),width=2)
    d.line((151,53,160,53),fill=(218,111,133),width=1)
    d.line((135,34,143,35),fill=PINK,width=1)
    for cx in (36,128):
        wheel(d,cx,phase)
        d.arc((cx-16,38,cx+16,69),185,352,fill=(254,139,153),width=1)
        d.point((cx-12,43),fill=LIGHT)
    d.line((51,52,113,52),fill=(15,62,76),width=1)
    for px,py,colour in ((25,38,PEARL),(30,37,PEARL),(45,43,PINK),
                         (59,45,PEARL),(104,45,PEARL),(146,46,ROSE)):
        d.point((px,py),fill=colour)
    if phase%24 in (6,7,8):
        d.point((104,25),fill=(237,165,133))
    else:
        d.point((104,26),fill=(162,115,108))
    return im

def save_car_cels(folder):
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    frames=[car_cel(i) for i in range(24)]
    for i,sprite in enumerate(frames):
        sprite.save(folder/f'car-cel-{i}.png')
    return frames
