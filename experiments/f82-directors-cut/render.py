from PIL import Image,ImageDraw,ImageFont,ImageChops
from pathlib import Path
import math,subprocess,json,argparse
import numpy as np
from wheel_animation import spin
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
 im=scroll(src,travel*.10,0,H,origin)
 # Asphalt and close foliage move independently; no split through tree trunks.
 im.paste(scroll(src,travel,360,480,origin),(0,360))
 im.paste(scroll(src,travel*1.5,480,H,origin),(0,480))
 return im.convert('RGBA')
def paintcar(im,kind,width,x,bottom,travel=0,rotation=True,headlights=1):
 source=cars[kind];scale=width/source.width
 if rotation:
  # Both wheels share the same physical rolling radius. Perspective changes
  # the visible ellipse, not angular velocity.
  angle=travel/max(1,27*scale)
  source=spin(source,wheelcfg[kind],angle)
 # A small moving warm reflection follows the sculpted painted panels only.
 arr=np.array(source); yy,xx=np.indices(arr.shape[:2]); gold=(arr[:,:,0]>110)&(arr[:,:,1]>65)&(arr[:,:,0]>arr[:,:,2]*1.6)&(arr[:,:,3]>0)
 band=np.clip(1-np.abs(xx-(travel*.13%500-50))/22,0,1)*.10*gold
 arr[:,:,:3]=np.clip(arr[:,:,:3].astype(float)*(1+band[:,:,None]),0,255).astype('uint8');source=Image.fromarray(arr)
 car=source.resize((width,round(source.height*scale)),NEAR)
 y=bottom-car.height
 d=ImageDraw.Draw(im)
 d.ellipse((x+8,bottom-8,x+width-4,bottom+3),fill=(17,20,27,255))
 im.alpha_composite(car,(x,y))
 return im

def label(im,s,y):
 # text is rasterised to a binary mask at the same logical resolution
 mask=Image.new('1',(W,40));d=ImageDraw.Draw(mask);box=d.textbbox((0,0),s,font=font);d.text(((W-box[2])//2,0),s,font=font,fill=1)
 im.paste('#ffdf97',(0,y),mask)


finale=Image.open(A/'finale.png').convert('RGB')
def cropzoom(im,zoom,x,y):
 return im.resize((round(W*zoom),round(H*zoom)),NEAR).crop((x,y,x+W,y+H))
def frame(n):
 t=n/30
 if t<.85:
  u=t/.85;travel=14*u
  im=environment(travel,360,True)
  paintcar(im,'front',640,round(-15-45*u),475,travel)
  # Tight moving reveal of the grille, bonnet, lamp and front wheel.
 elif t<2:
  u=(t-.85)/1.15;travel=45*u
  im=environment(travel,310)
  paintcar(im,'front',326,round(24-10*u),467,travel)
  label(im,'BMW F82 M4',104)
 elif t<4.2:
  u=t-2;travel=90*u+65*u*u
  im=environment(travel,690)
  x=round(66-40*(1-math.exp(-u*3)))
  paintcar(im,'side',274,x,462+round(math.sin(travel*.07)*.7),travel)
  im=cropzoom(im,1.06,10,30)
 elif t<5.5:
  u=t-4.2;travel=260*u+36*u*u
  im=environment(travel,670,True)
  # Actual wheel-level tracking close-up; all cropped bodywork is intentional.
  paintcar(im,'side',660,round(30-35*u),474+round(math.sin(travel*.04)*.7),travel)
 elif t<7.8:
  u=t-5.5;travel=175*u+32*u*u
  im=environment(travel,600,True)
  width=round(328-28*u)
  paintcar(im,'rear',width,round(16+12*u),466-round(5*u),travel)
 elif t<8.15:
  # Short settle into the newly illustrated sunset composition.
  u=(t-7.8)/.35;z=1.035-.035*(1-(1-u)**3)
  im=cropzoom(finale,z,round((W*z-W)/2),round((H*z-H)/2))
 else:
  im=finale.copy()
  # Subtle local motion of warm-lit foreground flower tips, away from the car.
  if n%24<12:
   d=ImageDraw.Draw(im)
   for x,y in [(57,600),(249,563),(307,554)]:d.point((x,y),fill='#ffc65d')
 if t>=8.45:label(im,'THE ULTIMATE M4?',72)
 return im.convert('RGB')
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');args=ap.parse_args()
 if args.stills:
  for n in [0,15,30,45,60,90,120,130,150,180,220,240,270,299]:frame(n).save(P/f'key_{n:03}.png')
 else:
  cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','360x640','-r','30','-i','-','-i',str(P/'Original_Score.wav'),'-map','0:v:0','-map','1:a:0','-vf','scale=1080:1920:flags=neighbor','-c:v','libx264','-crf','17','-preset','fast','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-t','10','-movflags','+faststart',str(P/'BMW_F82_Directors_Cut.mp4')]
  enc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
  for n in range(300):enc.stdin.write(frame(n).tobytes())
  enc.stdin.close();assert enc.wait()==0
