#!/usr/bin/env python3
"""Pixel Garage V3 movement: rich, original sprite art + acceleration + parallax, 300f 10.0s vertical.
No crop shots. Car and axles remain fully on screen, native nearest scaling only.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import math,subprocess,argparse
ROOT=Path(__file__).resolve().parent; A=ROOT/'v3_assets';W,H,FPS=360,640,30
NAMES=['01_sky','01a_canopy','02_mountains_lake','03_mid_forest','04_near_forest','06_road','05_guardrail','07_verge']
LAY={name:Image.open(A/(name+'.png')).convert('RGBA') for name in NAMES}
BODY=Image.open(A/'08_coupe_body.png').convert('RGBA'); WH=Image.open(A/'09_wheel.png').convert('RGBA')
WHEELS=[WH.rotate(v,resample=Image.Resampling.NEAREST,expand=False) for v in range(0,360,6)]

def distance(t):
 # 120px/s initially, high but visibly accelerated 405px/s by the ending.
 return 120*t+14.25*t*t

def tile(dst,im,xoff):
 w=im.width;pos=round(xoff)%w
 # crop from right each first cycle, no visible seam if landscape fully tiles in 960px.
 for x in range(-pos,W,w):dst.paste(im,(x,0),im)

def frame(f):
 t=f/FPS;d=distance(t)
 out=Image.new('RGBA',(W,H),'#101b35')
 # Real independent world depths. Foreground and lane-markings cross screen ~3x faster than treeline.
 depths=[.005,.12,.028,.17,.43,1.,1.03,1.28]
 origins=[585,570,560,519,480,137,114,96]
 for i,name in enumerate(NAMES):tile(out,LAY[name],origins[i]+d*depths[i])
 # Road-contact shadow held to the wheels and actual rolling surface, no particle fake-outs.
 dr=ImageDraw.Draw(out)
 cx=round(15+22*(.5-.5*math.cos(math.pi*min(1,t/10)))+1.3*math.sin(.5*t))
 # a full-vehicle track of +/-4px, no zoom cropping.
 yy=round(401+math.sin(t*13)*1.0+math.sin(t*19)*.6)
 # Golden roadside inset shadow underneath the chassis and tire contact patches
 dr.polygon([(cx+30,539),(cx+295,539),(cx+294,547),(cx+23,545)],fill='#0c1a29')
 # Individual rotating true spoke cels, angle computed from rolling road distance.
 angle=round((d/31*180/math.pi+25)/6)%60
 wheel=WHEELS[angle]
 for wheelcx in (75,243):out.paste(wheel,(cx+wheelcx-32,yy+111-32),wheel)
 # Animated suspension body rides sprung geometry, wheels track ground.
 # Minimal 1-2 pixel pitch displacement; no shakes or filters.
 bounce=round(.8*math.sin(t*13.0)+.4*math.sin(t*8.7))
 out.paste(BODY,(cx,yy+bounce),BODY)
 # Distinct tire side-wall static detail stays clear during spin
 return out.convert('RGB')

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stills-only',action='store_true');parser.add_argument('--output',default=str(ROOT/'nightfall_run_v3_10s.mp4'));a=parser.parse_args()
 stills=ROOT/'v3_stills';stills.mkdir(exist_ok=True)
 for f in (0,36,80,142,200,260,299):
  frame(f).resize((1080,1920),Image.Resampling.NEAREST).save(stills/f'frame_{f:03d}.png')
 print('Static frames ready',flush=True)
 if a.stills_only:return
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate','30','-i','pipe:0','-vf','scale=1080:1920:flags=neighbor,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart','-an','-frames:v','300',a.output]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for f in range(300):
  try:p.stdin.write(frame(f).tobytes())
  except BrokenPipeError:break
  if f%75==0:print('Rendered',f,flush=True)
 p.stdin.close();ret=p.wait()
 if ret:raise RuntimeError('FFmpeg failed '+str(ret))
 print('Finished',a.output,flush=True)
if __name__=='__main__':main()