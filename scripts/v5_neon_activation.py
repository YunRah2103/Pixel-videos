"""Six editable native-pixel cels: timed OPEN sign + localized storefront light.
No glow/blur filters, AI calls or paid services. Licensed architecture unchanged.
"""
from PIL import Image, ImageDraw

GLYPHS={
 'O':('01110','10001','10001','10001','10001','10001','01110'),
 'P':('11110','10001','10001','11110','10000','10000','10000'),
 'E':('11111','10000','10000','11110','10000','10000','11111'),
 'N':('10001','11001','10101','10011','10001','10001','10001')
}

def sign_cel(phase):
    sprite=Image.new('RGBA',(44,16),(0,0,0,0));d=ImageDraw.Draw(sprite,'RGBA')
    d.rectangle((1,1,42,14),fill=(7,22,38,255),outline=(31,105,125,255))
    d.line((3,3,40,3),fill=(27,75,96))
    d.line((3,12,40,12),fill=(25,58,84))
    for x in (3,40):d.point((x,7),fill=(236,162,102))
    if phase==0:
        return sprite
    lit=min(4,phase)
    for ix,ch in enumerate('OPEN'):
        px=10+ix*6
        for y,row in enumerate(GLYPHS[ch]):
            for x,on in enumerate(row):
                if on=='1':
                    if ix<lit:
                        col=(105,238,244,255) if phase>=5 else (62,192,214,255)
                    else:
                        col=(23,73,89,255)
                    d.point((px+x,4+y),fill=col)
    if phase>=5:
        d.line((3,1,40,1),fill=(64,216,229))
        d.line((3,14,40,14),fill=(30,145,170))
    return sprite

CELS=[sign_cel(i) for i in range(6)]

def save_sign_cels(directory):
    directory.mkdir(parents=True,exist_ok=True)
    for i,cel in enumerate(CELS):cel.save(directory/('open-sign-cel-%d.png'%i))
    return CELS

def paint_neon_activation(scene, frame, sign):
    if frame<109:return 0
    phase=0 if frame<114 else min(5,1+(frame-114)//4)
    if frame in (134,135):phase=3
    scene.alpha_composite(CELS[phase],(round(sign['x']),round(sign['y'])))
    glow=max(0,(phase-1)/4)
    if glow==0:return phase
    d=ImageDraw.Draw(scene,'RGBA')
    # Architectural fixture immediately beneath sign; no long artificial bar.
    for edge in range(3):
        alpha=round((67-edge*21)*glow)
        d.line((224+edge,233,224+edge,244),fill=(38,202,220,alpha))
    d.line((221,244,262,244),fill=(42,187,210,round(62*glow)),width=1)
    # Broken native-pixel light pools on the existing wet road.
    for k in range(13):
        yy=385+k*7
        if yy>=scene.height:break
        width=6+k//2
        alpha=round(max(0,105-k*6)*glow)
        if (k+frame//6)%6==2:alpha//=3
        d.line((max(0,234-width),yy,min(scene.width-1,235+width),yy),
               fill=(37,203,224,alpha))
    return phase
