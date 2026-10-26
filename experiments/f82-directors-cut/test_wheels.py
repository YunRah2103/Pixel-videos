import math,json
from pathlib import Path
from PIL import Image,ImageChops
from wheel_animation import spin
p=Path(__file__).resolve().parent
cfg=json.loads((p/'assets/wheels.json').read_text())
for kind in cfg:
    source=Image.open(p/'assets'/f'{kind}.png').convert('RGBA')
    assert ImageChops.difference(source,spin(source,cfg[kind],0)).getbbox() is None
    for angle in [math.pi/4,math.pi/2,math.pi,4.7]:
        out=spin(source,cfg[kind],angle)
        assert ImageChops.difference(source.getchannel('A'),out.getchannel('A')).getbbox() is None
        for y in range(source.height):
            for x in range(source.width):
                inside=any(((x-cx-lean*(y-cy))/rx)**2+((y-cy)/ry)**2<1 for cx,cy,rx,ry,lean in cfg[kind])
                if not inside:assert source.getpixel((x,y))==out.getpixel((x,y))
print('PASS: zero-angle identity, fixed silhouette and unchanged pixels outside all wheel interiors')
