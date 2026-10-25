"""Original, editable twelve-cel umbrella walker and motivated night-light payoff.

Rendered at the film's native 270x480 pixel scale, with no AI/API costs.
Each cel is an independent RGBA sprite; architecture remains licensed separately.
"""
import math
from PIL import Image, ImageDraw

def umbrella_pedestrian(phase=0, reveal=False):
    sprite=Image.new('RGBA',(45,57),(0,0,0,0))
    p=ImageDraw.Draw(sprite,'RGBA')
    plum=(39,18,47,255); rim=(242,87,142,255); yellow=(253,179,86,255)
    ink=(13,15,31,255); cyan=(94,212,223,255)
    theta=2*math.pi*(phase%12)/12
    bob=round(.85*math.sin(2*theta)) if not reveal else 0
    gait=(round(5*math.sin(theta)),round(-5*math.sin(theta))) if not reveal else (0,0)
    sway=round(1.6*math.sin(theta-.65)) if not reveal else 0
    p.ellipse((13,53,31,56),fill=(3,6,15,118))
    # Individually articulated planted feet and gait instead of static translation.
    p.line((20,42,18+gait[0],51),fill=ink,width=4)
    p.line((24,42,27+gait[1],51),fill=(26,26,51,255),width=4)
    p.line((14+gait[0],51,20+gait[0],51),fill=(8,13,29),width=3)
    p.line((24+gait[1],51,30+gait[1],51),fill=(8,13,29),width=3)
    # Raincoat, hood and face all have deliberately distinct pixel colour blocks.
    p.polygon([(17,29+bob),(25,28+bob),(31,37+bob),(29,46+bob),(13,46+bob),(11,39+bob)],fill=(223,119,57),outline=ink)
    p.line((18,31+bob,16,44+bob),fill=yellow,width=2)
    p.line((25,31+bob,29,42+bob),fill=(129,60,71),width=2)
    p.polygon([(16,45+bob),(29,45+bob),(31,48+bob),(13,48+bob)],fill=(124,38,76))
    p.ellipse((16,20+bob,28,32+bob),fill=(253,191,129),outline=ink)
    p.polygon([(14,26+bob),(17,18+bob),(25,17+bob),(30,23+bob),(27,27+bob),(26,21+bob),(18,23+bob)],fill=yellow)
    p.point((26,26+bob),fill=ink)
    if reveal:
        p.point((27,25+bob),fill=cyan)
        p.line((17,36+bob,26,32+bob),fill=yellow,width=2)
    # Independent umbrella canopy and hand-held shaft.
    p.line((26,36+bob,32+sway,31+bob,33+sway,18+bob),fill=(17,25,47),width=3)
    p.line((33+sway,18+bob,33,45+bob),fill=(226,193,158),width=1)
    p.arc((32,41+bob,38,47+bob),0,160,fill=yellow,width=1)
    p.polygon([(4+sway,19+bob),(6+sway,13+bob),(11+sway,8+bob),(20+sway,5+bob),(32+sway,6+bob),(40+sway,13+bob),(42+sway,19+bob),
               (32+sway,16+bob),(23+sway,19+bob),(15+sway,16+bob)],fill=plum,outline=rim)
    p.line((11+sway,13+bob,20+sway,6+bob,32+sway,7+bob),fill=(120,70,133),width=2)
    p.line((20+sway,7+bob,23+sway,18+bob),fill=(84,38,98),width=1)
    p.line((33+sway,9+bob,33+sway,16+bob),fill=(114,46,103),width=1)
    p.point((5+sway,18+bob),fill=cyan)
    p.point((40+sway,17+bob),fill=yellow)
    p.line((19,34+bob,19,42+bob),fill=(255,183,104),width=1)
    p.point((28,37+bob),fill=(248,155,94))
    p.point((21,47+bob),fill=(255,192,125))
    return sprite

WALK_CELS=[umbrella_pedestrian(i) for i in range(12)]
REVEAL_CEL=umbrella_pedestrian(0,True)

def save_character_cels(destination):
    for i,cel in enumerate(WALK_CELS):
        cel.save(destination/('pedestrian-cel-%d.png'%i))
    REVEAL_CEL.save(destination/'pedestrian-reveal-cel.png')

def draw_secondary_story(canvas,frame,fps=30,start_x=284,stop_x=178,baseline_y=358):
    t=frame/fps
    walk=min(1,max(0,(t-.2)/2.6))
    # A whole-walk ease with no harsh arrival snap; integer placement only.
    eased=walk*walk*(3-2*walk)
    ax=round(start_x+(stop_x-start_x)*eased)
    base_y=round(baseline_y)
    idx=(frame//2)%len(WALK_CELS) if t<2.8 else 0
    cel=WALK_CELS[idx] if t<3.6 else REVEAL_CEL
    x=ax-22
    p=ImageDraw.Draw(canvas,'RGBA')
    p.ellipse((ax-11,base_y-3,ax+15,base_y+2),fill=(9,10,28,130))
    # Sharp reflections are physically linked to the moving pedestrian.
    for n in range(6):
        yy=base_y+10+n*8
        length=max(2,12-n*2)
        col=(233,94,127,55-n*12) if t<3.6 else (95,214,222,90-n*17)
        p.line((ax-length//2,yy,ax+length//2,yy),fill=col,width=1)
    canvas.alpha_composite(cel,(x,base_y-56))
    if t>3.65:
        glow=min(1,(t-3.65)*1.45)
        p=ImageDraw.Draw(canvas,'RGBA')
        for j in range(7):
            yy=366+j*13
            width=3+j*3
            p.line((221-width,yy,224+width,yy),
                   fill=(69,208,225,max(0,int((83-j*10)*glow))),width=1)
        p.line((x+5,base_y-38,x+13,base_y-48),
               fill=(78,234,233,int(176*glow)),width=1)
