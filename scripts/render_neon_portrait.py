#!/usr/bin/env python3
"""Artist-first free portrait pixel film. Genuine independently moving licensed PNG
layers + original trolley cels. 270x480 native -> x4 nearest -> 1080x1920.
Art: Luis Zuno / Ansimuz, Cyberpunk Street Environment, CC BY 3.0.
"""
import hashlib,json,math,random,struct,subprocess,wave
from pathlib import Path
from PIL import Image,ImageDraw
from v5_pedestrian import draw_secondary_story, save_character_cels
from v5_reflections import reflect_sprite, passing_headlight, wheel_contact_spray
from v5_sky_courier import paint_sky_courier, save_courier_cels

ROOT=Path(__file__).resolve().parent.parent
ART=ROOT/'.tools/pixel-v5/art/ansimuz_cyberpunk/cyberpunk-street-files/PNG/layers'
OUT=ROOT/'out/pixel-v5-portrait'
FRAME_DIR=OUT/'frames'
FRAME_DIR.mkdir(parents=True,exist_ok=True)
W,H,FPS,N,SCALE=270,480,30,150,4
LAYOUT_FILE=OUT/'tiled-layout.json'
if not LAYOUT_FILE.is_file():
 raise RuntimeError('Tiled-exported storyboard missing: export studio/v5/neon-portrait.tmx with tiled --export-map')
TILED=json.loads(LAYOUT_FILE.read_text())
OBJECTS={o.get('name'):o for layer in TILED['layers'] for o in layer.get('objects',[])}
for required in ('tram-start','tram-finish','open-sign','pedestrian-start','pedestrian-stop','courier-start','courier-finish'):
 if required not in OBJECTS:raise RuntimeError('Missing Tiled stage object '+required)
TRAM_START=OBJECTS['tram-start']
TRAM_FINISH=OBJECTS['tram-finish']
SIGN=OBJECTS['open-sign']
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

from v5_streamline_tram import save_tram_cels
sprites=save_tram_cels(OUT)
courier_cels=save_courier_cels(OUT)
save_character_cels(OUT)
rng=random.Random(79523)
rain=[(rng.randrange(W),rng.randrange(H),rng.randrange(2,6),rng.randrange(20,60)) for _ in range(55)]
glints=[(rng.randrange(W),rng.randrange(390,475),rng.randrange(1,6),
         rng.choice(((73,215,238),(235,66,115),(255,188,99)))) for _ in range(115)]

def frame(f):
 t=f/FPS
 cam=int(16*(f/(N-1))**1.6)
 canvas=Image.new('RGBA',(W,H),(6,12,28,255))
 for layer_index,(src,offset) in enumerate(zip(planes,(168+int(cam*.25),230+int(cam*.52),268+cam))):
  canvas.alpha_composite(moving_plane(src,offset,44))
  if layer_index == 0:
   # Hand-authored eight-cel aerial vehicle, naturally occluded by near architecture.
   paint_sky_courier(canvas,f,OBJECTS['courier-start'],OBJECTS['courier-finish'])
 canvas.alpha_composite(planes[0].crop((0,0,270,44)),(0,0))
 pavement=planes[2].crop((260,345,530,384)).resize((270,51),Image.Resampling.NEAREST)
 canvas.alpha_composite(pavement,(0,429))
 d=ImageDraw.Draw(canvas,'RGBA')
 for j in range(24):
  yy=430+j*3;xx=(j*57+29)%W
  d.line((xx,yy,min(W-1,xx+5+j//5),yy),fill=(83,61,83,90))
 position=min(1,max(0,(t-.15)/4.15))
 x=round(TRAM_START['x']+(TRAM_FINISH['x']-TRAM_START['x'])*(position*position*(3-2*position)))
 ty=round(TRAM_START['y']+math.sin(t*6)*1.3)
 if t>=.15:
  d.ellipse((max(-20,x+7),ty+57,min(290,x+158),ty+65),fill=(1,6,17,140))
  moving_cel=sprites[int(t*16)%len(sprites)]
  reflect_sprite(canvas,moving_cel,x,ty,f,ground_y=421)
  passing_headlight(canvas,x,ty,f,min(1,max(0,(t-3.65)*1.45)))
  canvas.alpha_composite(moving_cel,(x,ty))
  wheel_contact_spray(canvas,x,ty,f)
  d=ImageDraw.Draw(canvas,'RGBA')
  if 0<x<250:
   for k in range(9):
    d.line((x+150-k,ty+72+k*3,x+151+k,ty+72+k*3),
           fill=(255,170,87,max(12,102-k*11)))
 # An original independently animated character crosses beneath the shop lights.
 draw_secondary_story(canvas,f,FPS,OBJECTS['pedestrian-start']['x'],OBJECTS['pedestrian-stop']['x'],OBJECTS['pedestrian-start']['y'])
 for ix,(xx,yy,length,c) in enumerate(glints):
  pulse=.5+.5*math.sin(.17*f+ix*1.6)
  d.line((xx,yy,min(W-1,xx+round(length*(.3+pulse))),yy),
         fill=(c[0],c[1],c[2],round(30+70*pulse)))
 if f>110:
  b=min(1,(f-110)/15)
  d.rectangle((int(SIGN['x']),int(SIGN['y']),int(SIGN['x']+SIGN['width']-1),int(SIGN['y']+SIGN['height'])),fill=(9,29,48,220),
              outline=(30,177,211,round(110+120*b)),width=2)
  d.text((int(SIGN['x']+5),int(SIGN['y']+2)),'OPEN',fill=(96,241,250,round(100+155*b)))
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
 'original_sprite_cels':len(sprites),'courier_sprite_cels':len(courier_cels),
 'skyline_motion':'eight frame original hand-specified peach delivery blimp, timed and placed with exported Tiled objects; naturally passes behind architecture',
 'skyline_motion_source':'Tiled objects courier-start and courier-finish',
 'pedestrian_sprite_cels':5,'secondary_story':'umbrella pedestrian walks, stops, turns toward the neon OPEN reveal',
 'pedestrian_route_source':'Tiled-authored pedestrian-start/pedestrian-stop storyboard coordinates','tiled_export_file':str(LAYOUT_FILE.relative_to(ROOT)),'actual_tools':['Tiled CLI map export','Pillow','FFmpeg','FFprobe'],
 'not_claimed_as_used':['Tiled GUI manual drawing','Laigter editor','LibreSprite editor','SpookyGhost editor'],
 'pedestrian_art_provenance':'Original Pixel Videos hand-authored pixel-drawn sprite cels; see scripts/v5_pedestrian.py',
 'tram_sprite_provenance':'Eight original script-authored streamlined transit cels; see scripts/v5_streamline_tram.py',
 'native_puddle_reflections':'Current moving trolley sprite cel mirrored in broken native-pixel bands; not a static still',
 'original_directed_pixel_lights':['tracked trolley headlamp','moving wheel-contact droplets','final cyan shop-sign reflection'],
 'artistic_review_note':'Compare storyboard still + moving light interactions; source is licensed and final approval remains pending.',
 'ffprobe':probe,'full_ffmpeg_decode':'pass','unique_sample_frames':30,
 'artistic_approval':'pending human visual review'},indent=2))
(OUT/'ATTRIBUTION.txt').write_text(
 'Cyberpunk Street Environment by Luis Zuno (Ansimuz), CC BY 3.0; adapted for Pixel Videos.\n'
 'https://opengameart.org/content/cyberpunk-street-environment\n'
 'Original independently animated trolley, umbrella-walker and lighting: Pixel Videos.\n')
print('V5_PORTRAIT_PROOF_PASS',movie,probe,flush=True)
