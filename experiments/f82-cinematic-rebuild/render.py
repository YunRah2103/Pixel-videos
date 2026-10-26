from PIL import Image,ImageDraw,ImageFont,ImageChops
from pathlib import Path
import math,subprocess,json,argparse
P=Path(__file__).resolve().parent; A=P/'assets';W,H=360,640
NEAR=Image.Resampling.NEAREST
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',19)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',10)
bg=Image.open(A/'environment.png').convert('RGB')
cars={k:Image.open(A/(k+'.png')).convert('RGBA') for k in ['front','side','rear']}
wheelcfg=json.loads((A/'wheels.json').read_text())

def scroll(im,shift,y0,y1,origin):
 width=im.width;xx=int(origin-shift)%width
 # mirrored repetition avoids hard left/right colour seam
 tile=Image.new('RGB',(width*2,im.height));tile.paste(im,(0,0));tile.paste(im.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(width,0))
 xx=int(origin-shift)%(width*2)
 tile2=Image.new('RGB',(width*4,im.height));tile2.paste(tile,(0,0));tile2.paste(tile,(width*2,0))
 return tile2.crop((xx,y0,xx+W,y1))
def environment(travel,origin=360,low=False):
 src=bg if not low else bg.resize((1200,800),NEAR).crop((0,130,1200,770))
 im=scroll(src,travel*.025,0,H,origin)
 # authored roadside layer, dithered boundary follows vegetation texture
 near=scroll(src,travel*.25,310,360,origin)
 mask=Image.new('L',near.size,255);md=ImageDraw.Draw(mask)
 for yy in range(16):
  for xx in range(W):
   if (xx*3+yy*5)%17>yy:md.point((xx,yy),fill=0)
 im.paste(near,(0,310),mask)
 im.paste(scroll(src,travel,360,480,origin),(0,360))
 im.paste(scroll(src,travel*1.8,480,H,origin),(0,480))
 return im.convert('RGBA')
def paintcar(im,kind,width,x,bottom,travel=0,rotation=True,headlights=1):
 source=cars[kind];scale=width/source.width
 car=source.resize((width,round(source.height*scale)),NEAR)
 y=bottom-car.height
 d=ImageDraw.Draw(im)
 # ground contact is tight to tyres rather than floating beneath the car
 d.ellipse((x+8,bottom-8,x+width-4,bottom+3),fill=(17,20,27,255))
 im.alpha_composite(car,(x,y))
 if rotation:
  for cfg in wheelcfg[kind]:
   cx,cy,rx,ry=cfg
   rim=source.crop((cx-rx,cy-ry,cx+rx,cy+ry))
   angle=travel/max(1,rx*scale)*180/math.pi
   rim=rim.rotate(angle,resample=NEAR)
   rim=rim.resize((max(2,round(2*rx*scale)),max(2,round(2*ry*scale))),NEAR)
   mask=Image.new('L',rim.size);ImageDraw.Draw(mask).ellipse((1,1,rim.width-2,rim.height-2),fill=255);rim.putalpha(mask)
   im.alpha_composite(rim,(round(x+(cx-rx)*scale),round(y+(cy-ry)*scale)))
 return im

def label(im,s,y):
 # text is rasterised to a binary mask at the same logical resolution
 mask=Image.new('1',(W,40));d=ImageDraw.Draw(mask);box=d.textbbox((0,0),s,font=font);d.text(((W-box[2])//2,0),s,font=font,fill=1)
 im.paste('#ffdf97',(0,y),mask)

def frame(n):
 t=n/30
 if t<2:
  u=t; travel=20*u-5*u*u;im=environment(travel,130)
  x=round(20-7*u);bottom=465+round(math.sin(u*2))
  paintcar(im,'front',320,x,bottom,travel,True)
  # brief initial pixel headlight flicker is restrained and local
  if n>8 and n<15:
   d=ImageDraw.Draw(im);d.line((x+8,bottom-82,x+40,bottom-80),fill='#fff0b3',width=1)
  label(im,'BMW F82 M4',72)
 elif t<5:
  u=t-2;travel=55*u+43*u*u
  im=environment(travel,300)
  x=round(83-37*min(1,u/.8)+6*math.sin(u*1.5));bottom=470+round(math.sin(travel*.06)*.8)
  paintcar(im,'side',254,x,bottom,travel)
 elif t<8:
  u=t-5;travel=170*u+24*u*u
  im=environment(travel,600,True)
  # independently authored rear three-quarter, lower road-level view
  width=round(318-30*min(1,u/3));x=max(8,round(30-12*u));bottom=495-round(8*u)
  paintcar(im,'rear',width,x,bottom,travel)
 else:
  u=t-8;travel=70*(1-math.exp(-u*3))
  im=environment(travel,700)
  x=round(34-18*min(1,u/.8));bottom=470+round(math.sin(u*6)*max(0,1-u))
  paintcar(im,'front',322,x,bottom,travel,rotation=u<1.1)
  label(im,'THE ULTIMATE M4?',91)
 return im.convert('RGB')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');a=ap.parse_args()
 if a.stills:
  for n in [0,30,60,90,149,150,180,239,240,270,299]:frame(n).save(P/f'key_{n:03}.png')
 else:
  enc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','360x640','-r','30','-i','-','-vf','scale=1080:1920:flags=neighbor','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(P/'BMW_F82_Cinematic_Rebuild.mp4')],stdin=subprocess.PIPE)
  for n in range(300):enc.stdin.write(frame(n).tobytes())
  enc.stdin.close();assert enc.wait()==0
