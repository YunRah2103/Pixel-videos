"""Rotate authored inner spokes in wheel-plane coordinates; silhouette stays fixed."""
import math
from PIL import Image

def spin(source,config,angle):
    result=source.copy()
    if abs(angle % (2*math.pi))<1e-9:return result
    src=source.load(); dst=result.load()
    for cx,cy,rx,ry,lean in config:
        for y in range(max(0,int(cy-ry-2)),min(source.height,int(cy+ry+3))):
            for x in range(max(0,int(cx-rx-abs(lean)*ry-2)),min(source.width,int(cx+rx+abs(lean)*ry+3))):
                v=(y-cy)/ry; u=(x-cx-lean*(y-cy))/rx
                radius=u*u+v*v
                if radius>=1:continue
                # Preserve the central cap and warm stationary brake caliper.
                r,g,b,a=src[x,y]
                if radius<.025 or (r>80 and r>g*1.1 and g>b*1.4):continue
                cs=math.cos(angle);sn=math.sin(angle)
                us=u*cs-v*sn;vs=u*sn+v*cs
                sy=round(cy+vs*ry);sx=round(cx+us*rx+lean*vs*ry)
                if 0<=sx<source.width and 0<=sy<source.height:
                    rr,gg,bb,aa=src[sx,sy]
                    # Original opacity is invariant, including the tyre contour.
                    if rr>80 and rr>gg*1.1 and gg>bb*1.4:rr,gg,bb=32,34,36
                    dst[x,y]=(rr,gg,bb,a)
    return result
