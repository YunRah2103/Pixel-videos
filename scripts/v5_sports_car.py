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
    # Recessed black tyre, machined lip, dual-material deep-dish alloy.
    d.ellipse((cx-10,44,cx+10,64),fill=(44,48,67,255),outline=(115,140,150,255),width=1)
    d.arc((cx-11,43,cx+11,65),188,336,fill=(190,237,222,255),width=1)
    d.arc((cx-11,43,cx+11,65),12,159,fill=(72,164,187,255),width=1)
    d.ellipse((cx-8,46,cx+8,62),fill=(14,35,53,255),outline=(166,203,202,255))
    angle=(phase%24)*2*math.pi/24
    for spoke in range(5):
        a=angle+spoke*2*math.pi/5
        ux,uy=round(math.cos(a)*7),round(math.sin(a)*7)
        d.line((cx+round(ux*.35),54+round(uy*.35),cx+ux,54+uy),
               fill=(203,221,215,255),width=2)
        # Offset inner vein makes spokes legible at real integer-pixel size.
        d.point((cx+round(ux*.73)-1,54+round(uy*.73)),
                fill=(88,174,188,255))
    d.point((cx+round(math.cos(angle)*8),54+round(math.sin(angle)*8)),fill=PINK)
    d.ellipse((cx-3,51,cx+3,57),fill=(32,52,68,255),outline=(180,214,201,255))
    d.ellipse((cx-2,52,cx+2,56),fill=AMBER,outline=INK)
    d.point((cx,54),fill=PEARL)

def car_cel(phase):
    im=Image.new('RGBA',(164,66),(0,0,0,0))
    d=ImageDraw.Draw(im,'RGBA')
    d.ellipse((13,57,155,65),fill=(3,5,16,100))
    for cx in (36,128):
        d.ellipse((cx-15,39,cx+15,68),fill=INK)
    # Front points RIGHT. Shift the entire roof/cockpit 12 native pixels
    # toward the tail (LEFT), retaining fixed 164px body and 92px wheelbase.
    # This trades the earlier excessive rear deck for a visibly longer bonnet.
    contour=[(4,39),(9,35),(31,32),(40,31),(45,27),(55,16),
             (64,11),(100,11),(108,15),(122,28),(138,33),
             (154,36),(161,41),(163,47),(161,53),(153,56),
             (13,56),(5,52)]
    d.polygon(contour,fill=OUTLINE)
    d.polygon([(7,40),(19,36),(40,34),(46,27),(59,16),(66,14),
               (99,14),(107,19),(122,32),(150,38),(159,42),
               (160,49),(153,53),(13,53),(8,49)],fill=BASE)
    d.polygon([(8,46),(23,49),(56,48),(90,49),(119,47),
               (152,47),(160,49),(154,54),(14,54)],fill=SHADOW)
    d.line((54,50,112,50),fill=(20,79,96),width=2)
    d.line((52,52,113,52),fill=(68,149,149),width=1)
    # Sculpted double-plane lower side skirt never intersects the tyres.
    d.polygon([(52,48),(68,49),(97,49),(113,48),(112,51),(55,51)],
              fill=(13,53,71,255))
    d.line((58,49,106,49),fill=(91,178,179,255),width=1)
    d.line((56,53,109,53),fill=(5,19,34,255),width=1)
    d.polygon([(8,39),(27,35),(43,34),(52,36),(43,39),(20,41)],fill=ROSE)
    d.polygon([(39,35),(48,31),(79,33),(104,34),(151,39),
               (148,43),(115,40),(68,39),(38,41)],fill=MID)
    d.polygon([(110,32),(132,32),(152,38),(157,42),
               (127,39),(115,36)],fill=LIGHT)
    d.line((115,35,143,37),fill=PEARL,width=1)
    d.line((128,38,153,40),fill=(120,228,220),width=1)
    d.line((106,39,128,39),fill=(43,196,211),width=1)
    d.line((18,41,48,41),fill=PINK,width=1)
    d.line((52,43,112,43),fill=(83,168,173),width=1)
    d.line((148,44,160,44),fill=(255,170,144),width=1)
    # TRUE 2-door GT greenhouse: cabin moved 12 pixels toward the rear axle.
    # Rear quarterglass (left) is small; driver window (right) follows raked screen.
    # Contiguous canopy roof AND both window polygons move as one, so no
    # paint/glass overlaps or free-floating chrome lines are introduced.
    d.polygon([(42,30),(55,18),(66,14),(98,14),(108,19),
               (123,33),(107,34),(49,34)],fill=INK)
    d.polygon([(45,30),(57,19),(67,16),(76,16),(76,31)],fill=GLASS)
    d.polygon([(80,16),(97,16),(105,21),(118,31),(80,31)],fill=GLASS)
    # Small recessed rear quarter window and one uninterrupted main door glass.
    d.polygon([(46,28),(58,20),(66,17),(73,17),(71,20),
               (59,23),(51,30)],fill=(58,116,137))
    d.line((83,18,99,18),fill=(88,189,202),width=2)
    d.line((105,20,116,30),fill=PEARL,width=1)
    d.line((83,29,112,29),fill=(35,79,103),width=1)
    d.line((65,13,98,13),fill=(248,139,146),width=1)
    # B-pillar and door shutline align; no 4-door/saloon appearance.
    d.line((78,16,78,33),fill=OUTLINE,width=3)
    d.line((53,31,109,32),fill=PINK,width=1)
    d.line((69,14,94,14),fill=(255,192,160),width=1)
    d.line((64,12,97,12),fill=(101,210,208),width=1)
    d.line((67,11,94,11),fill=(255,159,164),width=1)
    d.line((44,32,51,26),fill=(164,229,214),width=1)
    # Move the side mirror, handle and full door boundary with the occupant.
    d.polygon([(105,32),(114,33),(116,36),(108,37)],fill=(25,72,89))
    d.line((80,34,79,49),fill=(12,45,62),width=1)
    d.line((80,47,83,49),fill=(17,57,75),width=1)
    d.rectangle((84,38,90,39),fill=(247,183,148))
    d.point((91,39),fill=INK)
    d.polygon([(103,36),(111,36),(109,41),(103,41)],fill=(16,61,81))
    d.line((105,37,108,37),fill=LIGHT,width=1)
    # Long front bonnet from windscreen x123 to nose x163.
    d.line((124,33,143,35),fill=(157,233,222),width=1)
    d.line((131,36,152,39),fill=(89,212,222),width=1)
    d.line((126,42,146,43),fill=(37,104,133),width=1)
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
    # Crisp, wedge-cut front splitter, intake and low diffuser.
    d.polygon([(144,50),(151,49),(160,49),(162,51),(158,54),(150,54)],
              fill=(9,21,39,255))
    d.line((151,53,160,53),fill=(231,133,157),width=1)
    d.line((9,52,18,53),fill=(245,116,155),width=1)
    d.line((124,34,143,35),fill=PINK,width=1)
    for cx in (36,128):
        wheel(d,cx,phase)
        d.arc((cx-16,38,cx+16,69),185,352,fill=(254,139,153),width=1)
        d.point((cx-12,43),fill=LIGHT)
    d.line((51,52,113,52),fill=(15,62,76),width=1)
    d.line((57,45,85,45),fill=(145,226,218),width=1)
    d.line((102,45,117,44),fill=(97,207,218),width=1)
    d.point((57,44),fill=PEARL)
    d.point((118,43),fill=PEARL)
    for px,py,colour in ((25,38,PEARL),(30,37,PEARL),(45,43,PINK),
                         (59,45,PEARL),(104,45,PEARL),(146,46,ROSE)):
        d.point((px,py),fill=colour)
    if phase%24 in (6,7,8):
        d.point((92,25),fill=(237,165,133))
    else:
        d.point((92,26),fill=(162,115,108))
    return im

def save_car_cels(folder):
    folder=Path(folder)
    folder.mkdir(parents=True,exist_ok=True)
    frames=[car_cel(i) for i in range(24)]
    for i,sprite in enumerate(frames):
        sprite.save(folder/f'car-cel-{i}.png')
    return frames
