"""Hand-placed, independent frame-animated native-pixel street details.

No particle engine, shader, blur, random screen noise or false GUI credits.
Every mark is drawn on the original 270x480 composition before integer scaling.
"""
import math
from PIL import ImageDraw

def paint_micro_life(scene, frame):
    d=ImageDraw.Draw(scene,'RGBA')
    # Quiet three-stage gutter drip, away from the OPEN sign, once per 29 frames.
    for i,(origin_x,origin_y) in enumerate(((81,298),(151,326),(207,304))):
        age=(frame+i*11)%29
        if age < 22:
            xx=origin_x + (age//12)
            yy=origin_y + round((age/21)**1.5 * 44)
            if 0 <= xx < scene.width and 0 <= yy < scene.height:
                d.line((xx,yy,xx,yy+min(2,age//8)),fill=(103,181,202,95))
        else:
            yy=origin_y+45
            d.line((origin_x-2,yy,origin_x+2,yy),fill=(71,150,178,43))
    # One small stair-stepped steam vent; 3 independent ribbons drift differently.
    for ribbon in range(3):
        for step in range(7):
            phase=(frame*0.32+step*2+ribbon*9)%29
            xx=108+ribbon*3+round(2*math.sin(.22*phase+ribbon))
            yy=415-round(phase*1.3)
            if 0 <= xx < scene.width and 0 <= yy < scene.height:
                a=max(8,round((1-phase/29)*38))
                d.line((xx,yy,xx+min(2,step//3),yy),
                       fill=(100,153,168,a))
    # Sparse static-placement light activity instead of multiplying glints.
    for i,(x,y) in enumerate(((47,211),(187,241),(239,262))):
        phase=(frame+i*17)%73
        if phase in (0,1,2,3,57,58):
            d.point((x,y),fill=(251,190,130,100))
        elif phase < 30:
            d.point((x,y),fill=(105,170,177,43))
    # Puddle edges break and reform in short native-pixel ripples.
    for i,(x,y) in enumerate(((38,437),(123,452),(196,467))):
        q=(frame+i*13)%41
        if q < 26:
            span=1+q//9
            d.line((x-span,y,x+span,y),fill=(71,164,182,max(5,65-q*2)))
