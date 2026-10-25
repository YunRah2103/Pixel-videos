#!/usr/bin/env python3
"""Artist-first free portrait pixel film. Genuine independently moving licensed PNG
layers + original trolley cels. 270x480 native -> x4 nearest -> 1080x1920.
Art: Luis Zuno / Ansimuz, Cyberpunk Street Environment, CC BY 3.0.
"""
import hashlib,json,math,random,struct,subprocess,wave
from pathlib import Path
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent.parent
ART=ROOT/'.tools/pixel-v5/art/ansimuz_cyberpunk/cyberpunk-street-files/PNG/layers'
OUT=ROOT/'out/pixel-v5-portrait'
FRAME_DIR=OUT/'frames'
FRAME_DIR.mkdir(parents=True,exist_ok=True)
W,H,FPS,N,SCALE=270,480,30,150,4
if not all((ART/x).exists() for x in ('far-buildings.png','back-buildings.png','foreground.png')):
 raise RuntimeError('Real licensed artist planes missing: run python3 scripts/setup_free_pixel_v5.py --art')
planes=[Image.open(ART/n).convert('RGBA') for n in ('far-buildings.png','back-buildings.png','foreground.png')]
planes=[im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST) for im in planes]

def moving_plane(src,offset,y):
 im=Image.new('RGBA',(W,H))
 x=-round(offset)%src.width-src.width
 while x<W:
  im.alpha_composite(src,(x,y));x+=src.width
 return im

def trolley(wheelphase):
 im=Image.new('RGBA',(164,66));d=ImageDraw.Draw(im)
 ink=(8,12,28);gold=(255,174,102);teal=(54,198,221)
 d.ellipse((8,56,159,64),fill=(3,5,16,110))
 d.polygon([(17,43),(150,43),(159,54),(8,54)],fill=ink)
 for cx in (35,130):
  d.ellipse((cx-11,46,cx+11,65),fill=(6,11,23),outline=(108,118,133))
  d.ellipse((cx-7,50,cx+7,61),fill=(41,59,73),outline=(181,165,143))
  d.line((cx-5 if wheelphase%2 else cx,52,cx+5 if wheelphase%2 else cx,60),fill=gold,width=2)
  d.ellipse((cx-2,54,cx+2,58),fill=(255,217,151))
 d.polygon([(5,27),(16,16),(35,10),(117,9),(148,15),(158,28),(157,48),(149,52),(14,52),(5,46)],fill=(9,14,32),outline=(240,84,119))
 d.polygon([(9,27),(19,20),(38,14),(116,13),(143,19),(153,29),(152,45),(10,45)],fill=(143,37,74))
 d.polygon([(13,29),(21,21),(40,17),(116,16),(141,22),(150,30),(149,39),(13,39)],fill=(49,43,78))
 d.line((22,18,117,15),fill=gold,width=2)
 d.line((12,41,152,41),fill=gold,width=3)
 d.line((17,45,152,45),fill=teal,width=2)
 for xx in (26,46,66,86,106):
  d.polygon([(xx,20),(xx+14,20),(xx+15,33),(xx,33)],fill=(16,40,66),outline=(215,133,102))
  d.line((xx+2,22,xx+12,22),fill=(108,217,231))
  d.point((xx+5,28),fill=(224,149,109))
 for xx in (42,82,123):d.line((xx,20,xx,40),fill=gold)
 d.polygon([(128,20),(140,24),(149,32),(129,32)],fill=(22,65,86),outline=(110,222,226))
 d.line((67,10,73,0,102,0,110,10),fill=(123,154,155),width=2)
 d.line((74,0,102,0),fill=gold)
 d.rectangle((56,12,89,15),fill=(255,199,112))
 d.rectangle((18,36,29,39),fill=(255,205,125))
 d.rectangle((131,36,150,39),fill=teal)
 d.polygon([(148,33),(161,31),(163,36),(151,40)],fill=(255,226,171))
 d.rectangle((5,33,8,38),fill=(249,77,116))
 for xx in range(35,130,9):d.point((xx,43),fill=(255,223,167))
 return im

sprites=[trolley(k) for k in range(4)]
for i,s in enumerate(sprites):s.save(OUT/('trolley-cel-%d.png'%i))
rng=random.Random(79523)
rain=[(rng.randrange(W),rng.randrange(H),rng.randrange(2,6),rng.randrange(20,60)) for _ in range(55)]
glints=[(rng.randrange(W),rng.randrange(390,475),rng.randrange(1,6),
         rng.choice(((73,215,238),(235,66,115),(255,188,99)))) for _ in range(115)]

def frame(f):
 t=f/FPS
 cam=int(16*(f/(N-1))**1.6)
 canvas=Image.new('RGBA',(W,H),(6,12,28,255))
 for src,offset in zip(planes,(168+int(cam*.25),230+int(cam*.52),268+cam)):
  canvas.alpha_composite(moving_plane(src,offset,44))
 canvas.alpha_composite(planes[0].crop((0,0,270,44)),(0,0))
 pavement=planes[2].crop((260,345,530,384)).resize((270,51),Image.Resampling.NEAREST)
 canvas.alpha_composite(pavement,(0,429))
 d=ImageDraw.Draw(canvas,'RGBA')
 for j in range(24):
  yy=430+j*3;xx=(j*57+29)%W
  d.line((xx,yy,min(W-1,xx+5+j//5),yy),fill=(83,61,83,90))
 position=min(1,max(0,(t-.28)/4.25))
 x=round(-165+380*(position*position*(3-2*position)))
 ty=359+round(math.sin(t*6)*1.3)
 if t>=.28:
  d.ellipse((max(-20,x+7),ty+57,min(290,x+158),ty+65),fill=(1,6,17,140))
  canvas.alpha_composite(sprites[int(t*16)%4],(x,ty))
  d=ImageDraw.Draw(canvas,'RGBA')
  if 0<x<250:
   for k in range(9):
    d.line((x+150-k,ty+72+k*3,x+151+k,ty+72+k*3),
           fill=(255,170,87,max(12,102-k*11)))
 for ix,(xx,yy,length,c) in enumerate(glints):
  pulse=.5+.5*math.sin(.17*f+ix*1.6)
  d.line((xx,yy,min(W-1,xx+round(length*(.3+pulse))),yy),
         fill=(c[0],c[1],c[2],round(30+70*pulse)))
 if f>110:
  b=min(1,(f-110)/15)
  d.rectangle((221,216,264,232),fill=(9,29,48,220),
              outline=(30,177,211,round(110+120*b)),width=2)
  d.text((226,218),'OPEN',fill=(96,241,250,round(100+155*b)))
  for k in range(13):
   yy=382+k*6
   d.line((222-k//2,yy,261+k//2,yy),
          fill=(35,194,206,max(0,round((90-k*6)*b))))
 for ix,(xx,yy,length,speed) in enumerate(rain):
  q=(yy+f*speed//30)%H
  d.line((xx,q,xx,q+length),fill=(98,161,192,52 if ix%3 else 71))
 return canvas.convert('RGB')

checked=(0,18,36,54,72,90,108,126,149)
selected=[];hashes=[]
for f in range(N):
 im=frame(f)
 if f in checked:selected.append(im.copy())
 large=im.resize((1080,1920),Image.Resampling.NEAREST)
 large.save(FRAME_DIR/('frame_%04d.png'%f))
 if f==0:large.save(OUT/'preview-still.png')
 if f==90:large.save(OUT/'hero-still.png')
 if f%5==0:hashes.append(hashlib.sha256(im.tobytes()).hexdigest())
sheet=Image.new('RGB',(W*3,H*3),(10,11,22))
for i,im in enumerate(selected):sheet.paste(im,((i%3)*W,(i//3)*H))
sheet.save(OUT/'contact-sheet.png')
audio=OUT/'original-ambience.wav';rate=22050;source=[];rr=random.Random(420)
for i in range(rate*5):
 t=i/rate
 amp=.019*math.sin(2*math.pi*63*t)+.009*math.sin(2*math.pi*126*t)
 amp+=(rr.random()*2-1)*.011
 if t>3.7:amp+=.012*math.sin(2*math.pi*392*t)*math.exp(-8*(t-3.7))
 source.append(struct.pack('<h',round(max(-1,min(1,amp))*32767)))
with wave.open(str(audio),'wb') as outwav:
 outwav.setnchannels(1);outwav.setsampwidth(2);outwav.setframerate(rate)
 outwav.writeframes(b''.join(source))
movie=OUT/'pixel-v5-neon-portrait-5s.mp4'
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',
 str(FRAME_DIR/'frame_%04d.png'),'-i',str(audio),
 '-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',
 '-c:a','aac','-b:a','112k','-movflags','+faststart','-shortest',str(movie)],check=True)
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(movie),'-f','null','-'],check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0',
 '-count_frames','-show_entries','stream=width,height,nb_read_frames,r_frame_rate,codec_name',
 '-of','json',str(movie)]))['streams'][0]
assert probe['width']==1080 and probe['height']==1920
assert probe['r_frame_rate']=='30/1' and probe['nb_read_frames']=='150'
assert len(set(hashes))==30
(OUT/'render-qa.json').write_text(json.dumps({
 'frames':N,'seconds':5,'fps':FPS,'native_resolution':[W,H],
 'artist':'Luis Zuno / Ansimuz','license':'CC BY 3.0',
 'source':'https://opengameart.org/content/cyberpunk-street-environment',
 'independent_art_planes':['far-buildings.png','back-buildings.png','foreground.png'],
 'original_sprite_cels':4,'actual_tools':['Pillow','FFmpeg','FFprobe'],
 'not_claimed_as_used':['Tiled editor','Laigter editor','LibreSprite editor','SpookyGhost editor'],
 'ffprobe':probe,'full_ffmpeg_decode':'pass','unique_sample_frames':30,
 'artistic_approval':'pending human visual review'},indent=2))
(OUT/'ATTRIBUTION.txt').write_text(
 'Cyberpunk Street Environment by Luis Zuno (Ansimuz), CC BY 3.0; adapted for Pixel Videos.\n'
 'https://opengameart.org/content/cyberpunk-street-environment\n'
 'Original independently animated trolley and lighting: Pixel Videos.\n')
print('V5_PORTRAIT_PROOF_PASS',movie,probe,flush=True)
