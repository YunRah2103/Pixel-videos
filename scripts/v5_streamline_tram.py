"""Original detailed, separately editable eight-cel streamlined retro tram artwork.
Native 164x66 RGBA; hand-specified vector-of-pixel polygons and discrete brushwork.
Uses only Pillow; no paid image generation, account, API or hidden source assets.
"""
import math
from PIL import Image, ImageDraw
INK=(8,11,25,255)
WINE=(119,33,69,255)
PAINT=(32,83,101,255)
GLASS=(17,33,57,255)
CYAN=(85,208,222,255)
CREAM=(255,220,158,255)
GOLD=(240,161,98,255)

def tram_cel(phase):
    im=Image.new('RGBA',(164,66),(0,0,0,0))
    d=ImageDraw.Draw(im,'RGBA')
    d.ellipse((8,58,159,65),fill=(3,7,17,130))
    d.polygon([(9,39),(155,38),(162,47),(158,55),(8,55),(3,48)],fill=INK)
    d.line((10,55,151,55),fill=(18,34,52),width=2)
    for cx in (34,129):
        d.ellipse((cx-12,45,cx+12,65),fill=(5,9,24),outline=(155,91,97),width=2)
        d.ellipse((cx-8,49,cx+8,62),fill=(20,35,48),outline=(185,168,148))
        for spoke in range(4):
            angle=(phase%8)*math.pi/4+spoke*math.pi/2
            dx=round(math.cos(angle)*5)
            dy=round(math.sin(angle)*4)
            d.line((cx-dx,56-dy,cx+dx,56+dy),fill=GOLD,width=1)
        d.ellipse((cx-2,54,cx+2,58),fill=CREAM)
        d.point((cx,56),fill=(78,174,186))
    # Tilted body-panel endpoints and layered sculpted nose, not rectangle primitives.
    d.polygon([(3,33),(6,27),(13,19),(22,13),(38,9),(56,8),(110,8),
               (130,11),(145,16),(155,24),(160,34),(158,45),
               (150,51),(14,51),(5,46)],fill=INK,outline=(217,106,115),width=1)
    d.polygon([(7,32),(13,24),(24,17),(43,12),(110,12),(130,15),
               (145,19),(154,28),(155,43),(149,47),(13,47),(8,43)],fill=WINE)
    d.polygon([(9,33),(30,31),(106,32),(151,34),(153,43),(143,47),
               (17,47),(9,42)],fill=PAINT)
    d.line((12,42,152,42),fill=CREAM,width=2)
    d.line((14,46,149,46),fill=CYAN,width=2)
    d.line((19,49,147,49),fill=(80,54,82),width=1)
    d.polygon([(26,14),(44,9),(110,9),(132,14),(120,15),(42,15)],
              fill=(169,70,96))
    d.line((45,11,104,11),fill=CREAM)
    d.line((25,18,139,18),fill=(253,158,109),width=2)
    for x in (41,66,92,118):
        d.line((x,12,x+3,10),fill=(94,40,66))
    # Five framed panels each painted with a different warm passenger/light pattern.
    for i,(left,right) in enumerate(((22,37),(41,57),(61,77),(81,96),(101,117))):
        d.polygon([(left+1,21),(right-2,21),(right,32),(left,32)],
                  fill=(228,139,97),outline=(248,185,129))
        d.polygon([(left+3,23),(right-3,23),(right-2,30),(left+3,30)],fill=GLASS)
        d.line((left+4,23,right-4,23),fill=(95,199,212))
        if i in (0,2,3):
            d.ellipse((left+6,26,left+8,28),fill=(199,126,93))
            d.rectangle((left+5,29,left+10,31),fill=(53,68,81))
        if i%2==0:
            d.line((left+4,24,left+4,28),fill=(97,227,231))
        d.line((right,20,right+1,35),fill=(45,20,46))
    # Clear centre doorway, wraparound driver's windscreen, nose light prism.
    d.line((80,20,80,43),fill=CREAM)
    d.line((97,21,97,44),fill=(23,18,43))
    d.rectangle((83,34,94,39),fill=(52,64,76),outline=GOLD)
    d.point((94,37),fill=CREAM)
    d.polygon([(125,20),(137,22),(148,27),(152,32),(148,35),(126,33)],
              fill=(12,35,57),outline=(89,222,225))
    d.line((129,23,142,25),fill=(138,230,230))
    d.line((148,28,150,32),fill=CREAM)
    d.polygon([(55,16),(88,15),(91,19),(56,19)],fill=(247,200,129))
    d.line((60,17,84,17),fill=(24,45,63))
    for x in range(22,146,9):
        d.point((x,39),fill=(197,147,103))
    for x in (16,19,22):
        d.line((x,35,x,38),fill=(19,31,47))
    d.rectangle((11,38,16,41),fill=(249,76,111))
    d.rectangle((142,36,152,39),fill=(253,223,143))
    d.polygon([(152,35),(160,33),(163,35),(163,39),(155,40)],fill=CREAM)
    d.line((155,36,162,35),fill=(255,253,218))
    d.line((69,9,77,0,102,0,110,9),fill=(116,159,165),width=2)
    d.line((78,0,101,0),fill=(249,183,132))
    d.point((70,9),fill=CYAN)
    d.point((110,9),fill=CYAN)
    return im

def save_tram_cels(folder):
    folder.mkdir(parents=True,exist_ok=True)
    frames=[tram_cel(i) for i in range(8)]
    for i,sprite in enumerate(frames):
        sprite.save(folder/('trolley-cel-%d.png'%i))
    return frames
