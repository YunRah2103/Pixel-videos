#!/usr/bin/env python3
"""Genuine five-second original pixel animation using licensed, layered artist source.
Background: Cyberpunk Street by Ansimuz (CC BY 3.0).
Character: Warped City 2 by Ansimuz (CC0).
NO image generation or paid AI service. 320x180 native, x6 nearest, 1920x1080.
"""
import hashlib,json,math,random,subprocess,wave,struct
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent.parent
ASSETS=ROOT/'.tools/v5-free/art'
OUT=ROOT/'out/studio-v5-test'
FRAMES=OUT/'frames'
FRAMES.mkdir(parents=True,exist_ok=True)
W,H=320,180
FPS=30
FRAMES_N=150
SCALE=6
street=ASSETS/'ansimuz_street/cyberpunk-street-files/PNG/layers'
warped=ASSETS/'ansimuz_warped_city2/cyberpunk city 2 files'
layers={
 'far':Image.open(street/'far-buildings.png').convert('RGBA'),
 'back':Image.open(street/'back-buildings.png').convert('RGBA'),
 'front':Image.open(street/'foreground.png').convert('RGBA')}
def spriteframes(folder,prefix,n):
 result=[]
 for i in range(1,n+1):
  f=folder/(prefix+str(i)+'.png')
  if not f.is_file():raise FileNotFoundError('Artist animation missing '+str(f))
  im=Image.open(f).convert('RGBA')
  box=im.getbbox()
  if not box:raise ValueError('Artist animation blank '+str(f))
  result.append((im.crop(box),box))
 return result
runner=spriteframes(warped/'Sprites/Player/Run','Run',8)
idle=spriteframes(warped/'Sprites/Player/Idle','Idle',4)
rain_random=random.Random(2103)
rain=[(rain_random.randrange(W),rain_random.randrange(H),rain_random.randrange(22,70),
       rain_random.choice([(82,147,177,100),(116,172,192,120),(79,117,155,80)])) for _ in range(94)]
glints=[(rain_random.randint(1,W-3),rain_random.randint(145,H-2),rain_random.randint(1,4),
         rain_random.choice([(255,143,62,110),(230,65,152,85),(49,221,218,90)]),
         rain_random.random()*6.28) for _ in range(90)]
def tiled(source,ox):
 width=source.width
 canvas=Image.new('RGBA',(W,H),(0,0,0,0))
 position=-round(ox)%width-width
 while position<W:
  canvas.alpha_composite(source,(position,-4))
  position+=width
 return canvas
def animsprite(scene,source,bx,baseline,t):
 img,original_box=source
 scene.alpha_composite(img,(int(bx-img.width/2),int(baseline-img.height)))
def draw_frame(frame):
 t=frame/FPS
 ease=frame/(FRAMES_N-1)
 camera=22*(ease*ease*(3-2*ease))
 scene=tiled(layers['far'],camera*.18)
 scene.alpha_composite(tiled(layers['back'],camera*.42))
 scene.alpha_composite(tiled(layers['front'],camera))
 # Actor enters, crosses the street, then stops in the pool of shop light.
 move=min(1,t/3.25)
 actor_x=-20+194*(move*move*(3-2*move))
 if t<3.25:
  pose=runner[int(t*10)%len(runner)]
  base=174+(int(t*8)%2)
 else:
  pose=idle[int((t-3.25)*5)%len(idle)]
  base=174
 if actor_x>-40:
  animsprite(scene,pose,actor_x,base,t)
 # Extra animated object: illuminated shop-window sign from CC0 Warped City.
 signbase=warped/'Environment/props/banner-e'
 sign=Image.open(signbase/('banner-e'+str(1+(int(t*4)%4))+'.png')).convert('RGBA')
 # The sign is an independent sprite: an original artist-designed four-frame loop.
 scene.alpha_composite(sign,(273,93))
 draw=ImageDraw.Draw(scene,'RGBA')
 # Distance fog/rain that stays at native pixel resolution.
 for rx,ry,v,col in rain:
  y=int((ry+t*v)%H)
  x=int((rx+5*t)%W)
  if 4<y<166:
   draw.line((x,y,x,y+rain_random.choice([1,2])),fill=col,width=1)
 for x,y,length,col,phase in glints:
  brightness=.65+.35*math.sin(t*4.5+phase)**2
  draw.line((x,y,x+length,y),fill=(col[0],col[1],col[2],int(col[3]*brightness)),width=1)
 # Deliberate payoff after the runner reaches the shop: small neon reveal.
 if t>=3.25:
  pulse=min(1,(t-3.25)*1.3)
  rgb=(int(110+120*pulse),int(75+116*pulse),180,210)
  draw.rectangle((288,127,311,129),fill=rgb)
  for x in range(290,311,4):draw.point((x,128),fill=(255,238,205,255))
 return scene.convert('RGB')
def synth_audio():
 # Original quiet rain/traffic ambience, not a sample or a paid audio service.
 p=OUT/'self-generated-rain.wav'
 rate=22050
 r=random.Random(726)
 lp=0.0
 with wave.open(str(p),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
  chunks=[]
  for i in range(5*rate):
   tt=i/rate
   noise=r.random()*2-1
   lp=.966*lp+.034*noise
   wash=(noise*.025+lp*.10)
   distant=math.sin(tt*2*math.pi*63)*.018*(.5+.5*math.sin(tt*.9))
   foot=0.0
   for beat in (1.0,1.45,1.9,2.35,2.8):
    if 0<tt-beat<.05:foot+=math.exp(-(tt-beat)*95)*.09
   sample=int(max(-1,min(1,wash+distant+foot))*32767)
   chunks.append(struct.pack('<h',sample))
  w.writeframes(b''.join(chunks))
 return p
thumbs=[]
for f in range(FRAMES_N):
 img=draw_frame(f)
 if f in [0,18,36,54,72,90,108,126,149]:thumbs.append(img.copy())
 enlarged=img.resize((W*SCALE,H*SCALE),Image.Resampling.NEAREST)
 enlarged.save(FRAMES/('frame_%04d.png'%f))
 if f==0:enlarged.save(OUT/'first-frame.png')
print('ART_ASSET_RENDER_FRAMES',FRAMES_N,'using real distinct licensed layers and sprite cels',flush=True)
contact=Image.new('RGB',(W*3,H*3),(10,12,18))
for i,img in enumerate(thumbs):contact.paste(img,((i%3)*W,(i//3)*H))
contact.save(OUT/'contact-sheet.png')
audio=synth_audio()
mp4=OUT/'pixel-studio-v5-artist-led-5s.mp4'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error',
 '-framerate','30','-i',str(FRAMES/'frame_%04d.png'),'-i',str(audio),
 '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-r','30',
 '-c:a','aac','-b:a','128k','-movflags','+faststart','-shortest',str(mp4)],check=True)
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(mp4),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
 '-show_entries','stream=codec_name,width,height,nb_frames,duration','-of','json',str(mp4)]))
s=probe['streams'][0]
assert s['width']==1920 and s['height']==1080 and int(s['nb_frames'])==150
hashes={hashlib.sha256((FRAMES/('frame_%04d.png'%i)).read_bytes()).hexdigest() for i in range(0,150,5)}
assert len(hashes)>=25
notes={
 'video':str(mp4.relative_to(ROOT)),'width':1920,'height':1080,'fps':30,
 'frames':150,'native_resolution':[W,H],'unique_checked_samples':len(hashes),
 'full_decode':'pass','actual_tools':['Pillow','FFmpeg','FFprobe','Ansimuz licensed PNG layers and animation cels'],
 'not_claimed':['PixelLab','PixelOver','SpookyGhost editing','Laigter editing','LibreSprite editing','Tiled editing'],
 'licence_credits':[
  {'artist':'Luis Zuno (Ansimuz)','work':'Cyberpunk Street Environment','licence':'CC BY 3.0',
   'url':'https://opengameart.org/content/cyberpunk-street-environment'},
  {'artist':'Luis Zuno (Ansimuz)','work':'Warped City 2','licence':'CC0',
   'url':'https://opengameart.org/content/warped-city-2'}],
 'quality_limitation':'Test of authored free assets and real animation; visual appeal still requires human review.'}
(OUT/'render-qa.json').write_text(json.dumps(notes,indent=2)+'\n')
(OUT/'ATTRIBUTION.txt').write_text(
 'Cyberpunk Street Environment by Luis Zuno (Ansimuz), CC BY 3.0; '+
 'https://opengameart.org/content/cyberpunk-street-environment\n'+
 'Warped City 2 by Luis Zuno (Ansimuz), CC0; '+
 'https://opengameart.org/content/warped-city-2\n'+
 'New background parallax, light passes, sound synthesis and film adaptation: Pixel Videos V5.\n')
print('V5_REAL_MP4_PASS',str(mp4),'sample_frames',len(hashes),flush=True)
