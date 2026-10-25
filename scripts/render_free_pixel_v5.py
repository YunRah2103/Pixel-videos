#!/usr/bin/env python3
"""Render a real five-second native-pixel film from four separate, CC0 artist-made
Ansimuz industrial parallax layers. No ImageGen, no paid models, no flattened still.
Original pixel-cel tram, separate rain, light and reflection artwork are animated.
"""
import argparse,hashlib,json,math,random,shutil,subprocess,wave
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parent.parent
ART=ROOT/'.tools/pixel-v5/art/ansimuz_industrial'
OUT=ROOT/'out/pixel-v5'
W,H=270,480
FPS=30
FRAMES=150
UPSCALE=4
COLORS={"deep":(9,14,28,255),"navy":(18,25,49,255),
"pink":(235,73,178,255),"cyan":(60,215,235,255),
"orange":(255,177,87,255),"cream":(245,219,173,255),
"dark":(10,16,31,255),"blue":(46,103,167,255)}
rng=random.Random(1026)
rain=[(rng.randrange(W),rng.randrange(H),rng.choice((6,8,10)),rng.randint(4,8)) for _ in range(74)]
fireflies=[(rng.randrange(W),rng.randrange(70,280),rng.random()*3) for _ in range(20)]
sheet=None

def shell(command):
 p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
 if p.returncode:raise RuntimeError("Command failed: "+str(command)+" stderr="+p.stderr[-2500:])
 return p.stdout

def layer_paths():
 if not (ART/'ASSET_PROVENANCE.json').exists():raise RuntimeError("CC0 artist archive not downloaded; use python3 scripts/setup_free_pixel_v5.py --art")
 files=[p for p in ART.rglob("*.png") if p.is_file() and
         "__MACOSX" not in p.parts and not p.name.startswith("._") and
         "preview" not in p.name.lower()]
 if not files:raise RuntimeError("Artist archive contains no actual PNG")
 def pick(label):
  def norm(p):return p.stem.lower().replace("_","-").replace(" ","-")
  if label=="far":matches=[p for p in files if "far" in norm(p) and ("build" in norm(p) or "city" in norm(p))]
  elif label=="city":matches=[p for p in files if "build" in norm(p) and "far" not in norm(p)]
  elif label=="front":matches=[p for p in files if "foreground" in norm(p) or norm(p) in ("front","fg")]
  else:matches=[p for p in files if norm(p) in ("bg","background","sky")]
  if not matches:raise RuntimeError("No suitable "+label+" layer. Discovered: "+str([(p.name,Image.open(p).size) for p in files]))
  return min(matches,key=lambda p:len(p.name))
 selected=[pick(x) for x in ("sky","far","city","front")]
 if len(set(selected))!=4:raise RuntimeError("Four independent source layers are required")
 return selected

def load_layers():
 selected=layer_paths()
 out=[]
 for p in selected:
  im=Image.open(p).convert("RGBA")
  # source art is authored at ~272x160. Three native pixels per art pixel
  scale=3
  im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
  if im.height>H:im=im.crop((0,im.height-H,im.width,im.height))
  # Repeat horizontally as a native-pixel tile so camera never hits a seam.
  tiled=Image.new("RGBA",(im.width*3,H),(0,0,0,0))
  for i in range(3):tiled.alpha_composite(im,(i*im.width,H-im.height))
  out.append({"original":str(p.relative_to(ART)),"width":im.width,"image":tiled,"tile":im.width})
 print("ARTIST_LAYERS",json.dumps([{k:v for k,v in x.items() if k!="image"} for x in out]))
 return out

# Original authored 16-bit-style transit silhouette, not filled rectangle car.
TRAM=[
".............DDD.............................",
"..........DDDDDDDDD........................",
"......DDDDCCCCCCCCDDDDD.....................",
"....DDDCCCCCCCCCCCCCCCDDDD..................",
"...DDCCCCCCGCCGCCGCCCCCCDDD................",
"..DDCCCCCCCCCCCCCCCCCCCCCCCDDD..............",
".DDDCCWMMMMMMWMMMMMMWMMMMMMCCDD.............",
".DDCCWWMMMMMWWMMMMMWWMMMMMMMCCDDD...........",
"DDCCWWMMMMMWWMMMMMWWMMMMMMMMMCCDDDDD........",
"DDCCWWMMMMMWWMMMMMWWMMMMMMMMMMCCCDD........",
"DDCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCDD........",
".DDDDDCCCCCCCCCCCCCCCCCCCCCCCDDDDDD.........",
"...DDDDDDDDDDDDDDDDDDDDDDDDDDDDD...........",
".....DDAADDDDDDDDDDDDDDDDDAAD..............",
"......AA....................AA..............",
]
PAL={"D":(18,25,44,255),"C":(44,94,125,255),"G":(238,162,108,255),
"W":(112,204,221,255),"M":(203,224,217,255),"A":(255,146,95,255)}
def sprite_from_pixels():
 width=max(map(len,TRAM))
 img=Image.new("RGBA",(width,len(TRAM)),(0,0,0,0))
 px=img.load()
 for y,row in enumerate(TRAM):
  for x,c in enumerate(row):
   if c!='.':px[x,y]=PAL[c]
 return img.resize((width*2,len(TRAM)*2),Image.Resampling.NEAREST)

def light_overlay(f):
 img=Image.new("RGBA",(W,H),(0,0,0,0))
 d=ImageDraw.Draw(img)
 # Crisp native-pixel lights, no gaussian blur, never fullscreen gradient.
 shimmer=int((math.sin(f*.17)+1)*1)
 for x,y,c in [(34,316,COLORS["cyan"]),(224,296,COLORS["pink"]),(144,256,COLORS["orange"])]:
  intensity=48 if f%73<67 else 20
  d.rectangle((x-5,y-11,x+5,y+11),fill=(c[0],c[1],c[2],intensity))
  d.rectangle((x-1,y-7,x+1,y+7),fill=(c[0],c[1],c[2],185))
  for k in range(4):
   ry=y+18+k*17;w=2+((k+f//5)%4)
   d.rectangle((x-w,ry,x+w,ry+1),fill=(c[0],c[1],c[2],90-k*13))
 return img

def weather_layer(f):
 img=Image.new("RGBA",(W,H),(0,0,0,0))
 d=ImageDraw.Draw(img)
 for i,(x,y,speed,n) in enumerate(rain):
  yy=(y+f*speed)%(H+26)-13
  xx=x+((f//13+i)%3)
  alpha=62 if i%3 else 89
  d.line((xx,yy,xx+1,yy+n),fill=(112,159,191,alpha),width=1)
 for i,(x,y,ph) in enumerate(fireflies):
  xx=round(x+math.sin(f*.028+ph)*3)
  yy=round(y+math.sin(f*.035+ph)*2)
  a=145 if (f+i*17)%40<23 else 45
  d.rectangle((xx,yy,xx+1,yy+1),fill=(255,166,94,a))
 return img

def make_sound():
 # All tones are generated deterministically. No third-party music/SFX/samples.
 rate=24000
 t=np.arange(FRAMES*rate//FPS)/rate
 hiss=np.random.default_rng(302).normal(0,0.012,len(t))
 hum=(0.018*np.sin(t*2*math.pi*81)+0.008*np.sin(t*2*math.pi*122))
 rush=np.where((t>1.3)&(t<3.5),0.038*np.sin(2*np.pi*(93+19*np.clip(t-1.3,0,2.2))*t),0)
 # A soft moving train that approaches, peaks and recedes.
 env=np.exp(-((t-2.3)/1.15)**2)
 sound=np.clip(hiss+hum+env*rush,-.7,.7)
 path=OUT/"original-ambient.wav"
 with wave.open(str(path),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
  w.writeframes((sound*32767).astype("<i2").tobytes())
 return path

def make_frames(layers):
 frame_dir=OUT/"frames";frame_dir.mkdir(parents=True,exist_ok=True)
 tram=sprite_from_pixels()
 original_tracks=[]
 for f in range(FRAMES):
  base=Image.new("RGBA",(W,H),COLORS["deep"])
  # Each artwork plane has an independent, deterministic pixel-snapped camera.
  # Genuine translated layers (not motion over a flattened AI image).
  for idx,layer in enumerate(layers):
   speed=(0.18,0.39,0.77,1.08)[idx]
   shift=int(f*speed)
   width=layer["tile"]
   crop=layer["image"].crop((width//2+shift,0,W+width//2+shift,H))
   # use native pixel art source as-is: exact canvas, true alpha
   base.alpha_composite(crop)
  # The independent tram/cel moves noticeably through the street, over real buildings.
  if 25<=f<128:
   x=int(-106+(f-25)*3.8)
   y=328+round(math.sin(f*.11))
   base.alpha_composite(tram,(x,y))
   original_tracks.append((f,x,y))
  base.alpha_composite(light_overlay(f))
  base.alpha_composite(weather_layer(f))
  if f>=105:
   # final reveal: a rare golden beam reflected as a crisp pixel streak
   draw=ImageDraw.Draw(base,"RGBA")
   for n in range(9):
    draw.rectangle((198-n,420+n*5,202+n,422+n*5),fill=(245,171,87,max(10,88-n*9)))
  base.convert("RGB").save(frame_dir/("frame-%03d.png"%f))
 sheet_frames=[0,18,36,54,72,90,108,126,149]
 sheet=Image.new("RGB",(W*3,H*3),(12,14,25))
 for i,f in enumerate(sheet_frames):
  im=Image.open(frame_dir/("frame-%03d.png"%f))
  sheet.paste(im,((i%3)*W,(i//3)*H))
 sheet.save(OUT/"contact-sheet.png")
 Image.open(frame_dir/"frame-054.png").save(OUT/"approved-artwork-candidate.png")
 return frame_dir,original_tracks

def verify(movie,frame_dir,tracks,layers):
 probe=json.loads(shell(["ffprobe","-v","error","-select_streams","v:0","-count_frames",
 "-show_entries","stream=width,height,r_frame_rate,nb_read_frames,codec_name,pix_fmt:format=duration","-of","json",str(movie)]))
 st=probe["streams"][0]
 expected={"width":1080,"height":1920,"r_frame_rate":"30/1","nb_read_frames":"150","codec_name":"h264","pix_fmt":"yuv420p"}
 for k,v in expected.items():
  if str(st.get(k))!=str(v):raise RuntimeError("Incorrect video "+k+" "+str(st.get(k)))
 shell(["ffmpeg","-v","error","-xerror","-i",str(movie),"-f","null","-"])
 sample={f:hashlib.sha256((frame_dir/("frame-%03d.png"%f)).read_bytes()).hexdigest()
         for f in (0,18,36,54,72,90,108,126,149)}
 if len(set(sample.values()))!=len(sample):raise RuntimeError("Animation frames repeat: video is static")
 if len(tracks)<70:raise RuntimeError("Hero transit did not move throughout film")
 report={"complete":True,"frames":150,"width":1080,"height":1920,"fps":30,
 "duration_seconds":5,"full_decode_pass":True,"nonidentical_sample_frames":len(set(sample.values())),
 "moving_cel_positions":{"first":tracks[0],"last":tracks[-1]},
 "asset_provenance":json.loads((ART/"ASSET_PROVENANCE.json").read_text()),
 "actual_separate_art_layers":[x["original"] for x in layers],
 "scene_composition":"4 real CC0 art planes with independent camera offsets + custom cels, light art, rain and original audio",
 "subjective_quality_not_guaranteed":True,"notes":"An original artist-derived proof, not a claim of matching user's premium reference. Review MP4 at phone size."}
 (OUT/"render-qa.json").write_text(json.dumps(report,indent=2)+"\n")
 print("PIXEL_V5_REAL_ANIMATED_MP4_PASS",json.dumps(report)[:1600])
def main():
 if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):raise RuntimeError("FFmpeg/FFprobe required")
 OUT.mkdir(parents=True,exist_ok=True)
 layers=load_layers()
 frames,tracks=make_frames(layers)
 sound=make_sound()
 output=OUT/"artist-led-city-5s-1080x1920.mp4"
 shell(["ffmpeg","-y","-hide_banner","-loglevel","error","-framerate",str(FPS),"-i",
 str(frames/"frame-%03d.png"),"-i",str(sound),
 "-vf","scale=1080:1920:flags=neighbor","-c:v","libx264","-preset","fast","-crf","18",
 "-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-shortest","-movflags","+faststart",str(output)])
 verify(output,frames,tracks,layers)
if __name__=="__main__":
 main()
