"""Original native-pixel neo-noir street animation; no external game assets.
A visual direction proof using Pillow + FFmpeg, not the finished V4 runtime.
Run: python3 scripts/render_neonoir_preview.py
"""
from PIL import Image, ImageDraw
from pathlib import Path
import math,random,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'out/neonoir-preview';OUT.mkdir(parents=True,exist_ok=True)
W,H=360,640;WORLD=420
P=dict(sky='#131527',far='#20223a',farline='#31334d',black='#101522',dark='#1b2031',wall='#2a2c42',brick='#36334b',edge='#4a3d56',rose='#cb568f',pink='#ffc4e3',pale='#ffe1c1',cyan='#8ce9dc',teal='#398e99',shadow='#225565',purple='#644467',warm='#d6a06a',wine='#7d3c63')
F={
'A':['01110','10001','10001','11111','10001','10001','10001'], 'B':['11110','10001','10001','11110','10001','10001','11110'],
'C':['01111','10000','10000','10000','10000','10000','01111'],'D':['11110','10001','10001','10001','10001','10001','11110'],
'E':['11111','10000','10000','11110','10000','10000','11111'],'F':['11111','10000','10000','11110','10000','10000','10000'],
'G':['01111','10000','10000','10111','10001','10001','01111'],'H':['10001','10001','10001','11111','10001','10001','10001'],
'I':['111','010','010','010','010','010','111'],'J':['00111','00010','00010','00010','10010','10010','01100'],
'K':['10001','10010','10100','11000','10100','10010','10001'],'L':['10000','10000','10000','10000','10000','10000','11111'],
'M':['10001','11011','10101','10101','10001','10001','10001'],'N':['10001','11001','10101','10011','10001','10001','10001'],
'O':['01110','10001','10001','10001','10001','10001','01110'],'P':['11110','10001','10001','11110','10000','10000','10000'],
'R':['11110','10001','10001','11110','10100','10010','10001'],'S':['01111','10000','10000','01110','00001','00001','11110'],
'T':['11111','00100','00100','00100','00100','00100','00100'],'U':['10001','10001','10001','10001','10001','10001','01110'],
'V':['10001','10001','10001','10001','10001','01010','00100'],'W':['10001','10001','10001','10101','10101','10101','01010'],
'Y':['10001','10001','01010','00100','00100','00100','00100'],'Z':['11111','00001','00010','00100','01000','10000','11111'],
'2':['01110','10001','00001','00010','00100','01000','11111'],'4':['00010','00110','01010','10010','11111','00010','00010'],
'0':['01110','10001','10011','10101','11001','10001','01110'], ' ':['000']*7}
def rect(d,x,y,w,h,c):
 if w>0 and h>0:d.rectangle((int(x),int(y),int(x+w-1),int(y+h-1)),fill=P.get(c,c))
def line(d,pts,c,w=1):d.line([(round(x),round(y)) for x,y in pts],fill=P.get(c,c),width=w)
def poly(d,pts,c):d.polygon([(round(x),round(y)) for x,y in pts],fill=P.get(c,c))
def text(d,x,y,s,c,scale=1):
 for ch in s:
  glyph=F.get(ch,F[' ']);
  for yy,row in enumerate(glyph):
   for xx,v in enumerate(row):
    if v=='1':rect(d,x+xx*scale,y+yy*scale,scale,scale,c)
  x+=(len(glyph[0])+1)*scale

def window(d,x,y,w,h,col='warm',lit=True):
 rect(d,x-3,y-3,w+6,h+7,'black');rect(d,x-1,y-1,w+2,h+2,'edge');rect(d,x,y,w,h,col if lit else 'farline')
 rect(d,x+2,y+2,w-4,2,'pale' if lit else 'wall');rect(d,x+w//2-1,y,2,h,'dark');rect(d,x,y+h//2,w,2,'dark')
 rect(d,x-4,y+h+2,w+8,3,'brick');line(d,[(x-4,y+h+2),(x+w+3,y+h+2)],'edge')
 if lit:
  for j in range(2):rect(d,x+3+j*(w//2),y+h//2+3,2,h//2-5,'wine')
def brickwall(d,x,y,w,h,base='wall',seed=4):
 rect(d,x,y,w,h,base);rng=random.Random(seed)
 for yy in range(y+4,y+h,11):
  line(d,[(x,yy),(x+w-1,yy)],'dark')
  for xx in range(x-16+(yy//11%2)*14,x+w,28):
   if xx>=x:line(d,[(xx,yy),(xx,yy+10)],'dark')
   if xx+4>=x and xx+20<x+w and rng.random()<.6:rect(d,xx+4,yy+2,16,1,'brick')
 for _ in range(w*h//240):
  xx=rng.randrange(x,x+w);yy=rng.randrange(y,y+h);rect(d,xx,yy,rng.randrange(1,4),1,'edge' if rng.random()<.35 else 'dark')
def ac(d,x,y):
 rect(d,x,y,29,18,'black');rect(d,x+1,y+1,27,15,'edge');rect(d,x+3,y+3,23,11,'wall')
 for yy in range(y+4,y+14,3):line(d,[(x+4,yy),(x+24,yy)],'farline')
 line(d,[(x+3,y+17),(x+3,y+21),(x+26,y+21),(x+26,y+17)],'black',2)
def base_scene():
 im=Image.new('RGB',(WORLD,H),P['sky']);d=ImageDraw.Draw(im);rng=random.Random(12)
 # Layered skyline; silhouette detail instead of empty sky.
 for x,y,w,h in [(-12,105,46,205),(34,61,38,240),(80,130,28,190),(113,84,63,250),(186,12,51,280),(242,74,37,250),(289,39,65,270),(362,99,49,230)]:
  rect(d,x,y,w,h,'far');line(d,[(x,y),(x+w,y),(x+w,y+h)],'farline');rect(d,x+7,y-5,8,5,'far')
  for yy in range(y+12,y+h-6,13):
   for xx in range(x+5,x+w-5,8):
    if rng.random()<.4:rect(d,xx,yy,3,5,'#59516c' if rng.random()<.7 else '#927c85')
  line(d,[(x+w//2,y-22),(x+w//2,y)],'farline')
 # Dark mid-depth alley with a small distant tiled shop.
 rect(d,93,276,69,174,'dark');
 for yy in range(282,424,15):line(d,[(94,yy),(162,yy)],'wall')
 rect(d,107,338,44,7,'shadow');rect(d,110,339,38,2,'teal')
 rect(d,111,354,33,55,'black');rect(d,114,357,27,21,'shadow');line(d,[(128,358),(128,407)],'teal');rect(d,112,411,31,4,'edge')
 # Left residential facade and fire escape.
 brickwall(d,-10,106,105,345,seed=17)
 rect(d,-10,103,108,6,'black');rect(d,-10,110,108,3,'edge')
 for yy in [142,215,290]:
  for xx in [7,56]:window(d,xx,yy,23,38,lit=(xx==7 or yy==215))
 ac(d,13,338);ac(d,62,268)
 line(d,[(89,121),(89,432),(96,439)],'black',4);line(d,[(87,121),(87,429)],'edge')
 # Articulated steel escape platforms, railings and diagonal stairs.
 for y in [198,273,345]:
  rect(d,-5,y,93,5,'black');line(d,[(-5,y),(88,y)],'edge');line(d,[(-5,y-16),(88,y-16)],'farline')
  for x in range(0,89,9):line(d,[(x,y-16),(x,y-1)],'black')
 for y in [200,275]:
  line(d,[(19,y),(65,y+68)],'black',4);line(d,[(31,y),(77,y+68)],'black',3)
  for j in range(11):line(d,[(19+j*4,y+j*6),(32+j*4,y+j*6)],'edge')
 # Right main shop facade, stepped cornice and weathered upper plaster.
 brickwall(d,164,156,247,292,base='wall',seed=32)
 for y,h,c in [(148,6,'black'),(154,4,'edge'),(158,4,'dark'),(246,6,'black'),(249,2,'rose')]:rect(d,158,y,260,h,c)
 for xx in [184,246,310,374]:window(d,xx,181,34,47,col='teal',lit=(xx!=310))
 for xx in [183,245,309]:
  rect(d,xx-3,236,42,3,'black');rect(d,xx-2,234,40,1,'edge')
 ac(d,337,259)
 # Roof equipment and suspended utility cables.
 rect(d,190,133,30,16,'dark');rect(d,193,132,25,2,'farline');line(d,[(203,133),(203,118),(226,118)],'black',2)
 for y,shift in [(109,0),(119,8),(133,16)]:
  line(d,[(-5,y),(58,y+14),(141,y+19+shift),(238,y+12),(WORLD,y-5)],'black')
 # Decorative bricks and lower shop sill.
 rect(d,164,436,247,12,'black');line(d,[(165,438),(410,438)],'edge')
 for xx in range(167,412,18):rect(d,xx,442,15,3,'brick')
 # Wide awning with alternating folds.
 poly(d,[(164,298),(402,298),(417,325),(153,325)],'black')
 for i in range(13):
  x=163+i*19;poly(d,[(x,301),(x+12,301),(x+17,320),(x-5,320)],'wine' if i%2 else 'brick')
 line(d,[(154,324),(416,324)],'rose');rect(d,155,325,261,7,'dark')
 # Glazed shop entrance and lit window panels.
 rect(d,181,337,114,91,'black');rect(d,185,341,106,80,'shadow');rect(d,187,342,102,3,'cyan')
 for xx in [189,223,257]:
  rect(d,xx,349,27,49,'#2b6371');rect(d,xx,349,27,2,'teal');rect(d,xx+3,356,2,31,'#548f96')
  for y in [365,384]:
   rect(d,xx+2,y,23,2,'dark');
   for j in range(4):rect(d,xx+3+j*5,y-7,3,6,'warm' if j%2 else 'rose')
  rect(d,xx+6,390,14,5,'shadow');rect(d,xx+3,401,23,8,'dark')
 for xx in [182,218,253,290]:rect(d,xx,340,3,83,'black');rect(d,xx,342,1,78,'teal')
 rect(d,183,419,111,5,'edge')
 # Entry door.
 rect(d,306,334,55,97,'black');rect(d,310,338,47,87,'edge');rect(d,313,341,41,80,'dark')
 rect(d,317,345,33,45,'#264654');line(d,[(319,347),(347,347),(347,387)],'teal');rect(d,342,399,3,2,'warm')
 for i in range(3):rect(d,304-i*3,429+i*4,60+i*6,3,'edge' if i==0 else 'wall')
 # Vertical sign with actual pixel lettering.
 rect(d,144,222,33,96,'black');rect(d,147,225,27,90,'wine');line(d,[(148,226),(173,226),(173,314)],'pink')
 for i,ch in enumerate('OPEN'):text(d,153,234+i*19,ch,'pink',2)
 # Main neon panel.
 rect(d,196,266,132,23,'black');line(d,[(198,267),(326,267),(326,287),(198,287),(198,267)],'wine');text(d,204,274,'NIGHT OWL','pink')
 rect(d,367,348,32,53,'black');rect(d,370,351,26,47,'shadow');text(d,373,358,'24','cyan',2);text(d,374,382,'H','teal')
 # Trash bags, crates, plant and curb details.
 for x,y in [(108,431),(126,438)]:
  poly(d,[(x-9,y+7),(x-7,y-7),(x-2,y-10),(x+2,y-15),(x+5,y-12),(x+3,y-9),(x+10,y-5),(x+12,y+8)],'black');line(d,[(x-5,y-5),(x-6,y+4),(x-2,y+6)],'wall')
 for x,y in [(175,425),(189,432)]:
  rect(d,x,y,16,15,'dark');line(d,[(x,y),(x+15,y),(x+15,y+14)],'edge');line(d,[(x,y+6),(x+15,y+6)],'brick');line(d,[(x+3,y),(x+3,y+14)],'brick')
 rect(d,372,425,14,18,'wine');line(d,[(370,424),(387,424)],'rose',2)
 for dx,dy in [(-9,-13),(7,-22),(-3,-28),(13,-9)]:line(d,[(379,425),(379+dx,425+dy)],'shadow',2);line(d,[(379+dx,425+dy),(383+dx,421+dy)],'teal',2)
 # Sidewalk tiles and rain drain.
 rect(d,0,450,WORLD,26,'wall');rect(d,0,450,WORLD,2,'edge');rect(d,0,473,WORLD,5,'black');line(d,[(0,474),(WORLD,474)],'rose')
 for y in [455,465]:line(d,[(0,y),(WORLD,y)],'dark')
 for x in range(-12,WORLD,31):line(d,[(x,450),(x-7,472)],'dark')
 rect(d,81,466,26,5,'black')
 for x in range(83,106,4):rect(d,x,466,1,4,'edge')
 # Dark wet roadway with large broken reflective zones.
 rect(d,0,478,WORLD,H-478,'#141e2b')
 for i in range(330):
  x=rng.randrange(WORLD);y=rng.randrange(479,H);col=['#1b2b3a','#223447','#253244','#2d3045'][i%4]
  rect(d,x,y,rng.randrange(2,15),1,col)
 for x,y,w in [(30,522,43),(239,551,61),(76,609,67)]:
  poly(d,[(x,y),(x+w,y),(x+w+7,y+4),(x-5,y+4)],'dark');line(d,[(x,y),(x+w,y)],'edge')
 # Asphalt patch and scarred lane stripe; no smooth vector glow.
 for x in range(-18,WORLD,112):
  poly(d,[(x,581),(x+59,581),(x+51,585),(x-8,585)],'#6b6267')
  for j in [3,11,37]:rect(d,x+j,583,3,2,'#26303d')
 return im
def light_scene(im):
 # Palette-stepped local light on eligible surface colours; no blur or global glow.
 pix=im.load();eligible={P[x] for x in ['wall','brick','edge','dark']}
 eligible={tuple(bytes.fromhex(x[1:])) for x in eligible}
 for y in range(171,477):
  for x in range(WORLD):
   original=pix[x,y]
   if original not in eligible:continue
   candidates=[]
   for lx,ly,rx,ry,tint in [(159,269,68,115,(242,82,159)),(240,378,94,88,(73,199,191)),(19,233,31,145,(221,156,100))]:
    distance=abs(x-lx)/rx+abs(y-ly)/ry
    level=0.0 if distance>1 else (.24 if distance<.3 else .16 if distance<.6 else .08)
    candidates.append((level,tint))
   amount,tint=max(candidates,key=lambda t:t[0])
   if amount:pix[x,y]=tuple(round(a*(1-amount)+b*amount) for a,b in zip(original,tint))
 return im
BASE=light_scene(base_scene())

def person(f):
 im=Image.new('RGBA',(42,62));d=ImageDraw.Draw(im);phase=(f%24)/24*2*math.pi;stride=math.sin(phase);bob=round(abs(math.cos(phase))*1)
 # Eight-plus discrete poses arise from integer-snapped articulated legs.
 hip=(23,38+bob);rear=(23-round(stride*6),49);front=(23+round(stride*6),49)
 line(d,[hip,rear,(rear[0]-round(stride*4),58)],'#101a29',5)
 line(d,[hip,front,(front[0]+round(stride*3),58)],'#293c50',5)
 line(d,[(rear[0]-round(stride*4)-4,58),(rear[0]-round(stride*4)+1,58)],'#101522',3)
 line(d,[(front[0]+round(stride*3)-4,58),(front[0]+round(stride*3)+2,58)],'#101522',3)
 line(d,[(front[0]+round(stride*3)-3,57),(front[0]+round(stride*3)+1,57)],'#67878e')
 # Coat, collar, lifted scarf, asymmetric hood and readable face.
 poly(d,[(18,18+bob),(29,19+bob),(32,30+bob),(30,43),(18,44),(14+round(math.sin(phase)*2),39),(18,28)],'#182333')
 poly(d,[(26,21+bob),(29,23+bob),(30,36),(26,40),(23,39),(25,28)],'#344858')
 line(d,[(28,22+bob),(29,34),(27,40)],'#52717b')
 line(d,[(20,24+bob),(17-round(stride*3),34),(18-round(stride*3),40)],'#24374a',4)
 poly(d,[(17,7+bob),(27,6+bob),(31,10+bob),(29,19+bob),(20,20+bob),(16,16+bob)],'#111b2a')
 poly(d,[(18,9+bob),(22,7+bob),(28,8+bob),(29,11+bob),(27,12+bob),(19,12+bob)],'#34495b')
 poly(d,[(17,12+bob),(22,12+bob),(22,18+bob),(18,17+bob),(16,15+bob)],'#ba8f91')
 rect(d,17,12+bob,3,1,'#e2bab2');rect(d,16,14+bob,2,2,'#715a78')
 poly(d,[(20,19+bob),(29,19+bob),(32+round(math.sin(phase)*2),23+bob),(25,22+bob),(18,21+bob)],'#804762')
 return im

def frame(f):
 im=BASE.copy();d=ImageDraw.Draw(im);rng=random.Random(25)
 # Moving broken light reflections: authored source columns + discrete ripples.
 for origin,width,c0,c1 in [(159,24,'#623752','#a55c81'),(236,87,'#244955','#3a6975'),(383,28,'#284c5c','#4c9399')]:
  for j in range(31):
   y=480+j*4;span=round(width*(1+j*.045));center=origin+round(math.sin(j*.91+f*.12)*3)
   x=center-span//2+rng.randrange(-5,6);length=max(2,span-rng.randrange(0,max(2,span//2)))
   rect(d,x,y,length,1,c1 if j%5==0 else c0)
   if j%3==0:rect(d,x+length//4+round(math.sin(f*.09+j)*2),y+1,length//3,1,c0)
 # Occasional two-frame sign flicker, not a whole-image effect.
 if 91<=f<=93 or f==96:
  rect(d,148,226,24,87,'wine')
  for i,ch in enumerate('OPEN'):text(d,153,234+i*19,ch,'rose',2)
 # Steam: translucent-looking discrete palette shapes, no blur.
 for i in range(5):
  t=(f*.7+i*12)%60;y=453-round(t);x=101+round(math.sin(t*.1+i)*5)
  if t<45:
   col='#364554' if t<20 else '#2b3548';poly(d,[(x-4,y),(x-6,y-3),(x-4,y-6),(x+3,y-6),(x+5,y-3),(x+3,y)],col)
 # Main walker travels across the street; grounded motion plus local reflection.
 x=282-round(f*1.13);y=419;p=person(f).resize((63,93),Image.Resampling.NEAREST)
 for j in range(7):
  yy=512+j*4;ww=14-j
  rect(d,x+29-ww//2+round(math.sin(f*.16+j)*2),yy,ww,1,'#293647')
 im.paste(p,(x,y),p);d=ImageDraw.Draw(im)
 # Shop cat, tail and ear flicks, at native pixels.
 cx=303;cy=443
 poly(d,[(cx,cy),(cx+2,cy-8),(cx+4,cy-10),(cx+3,cy-16),(cx+7,cy-13),(cx+10,cy-16),(cx+11,cy-10),(cx+14,cy-7),(cx+15,cy)],'black')
 rect(d,cx+5,cy-11,1,1,'cyan');rect(d,cx+9,cy-11,1,1,'cyan')
 line(d,[(cx+13,cy-2),(cx+20,cy-3),(cx+22,cy-7+round(math.sin(f*.07)*2))],'black',2)
 # Rain in distinct depth bands; no random full-screen noise regenerated per frame.
 for band,count,speed,color in [(0,90,6,'#34485a'),(1,40,9,'#53677b')]:
  r=random.Random(113+band)
  for i in range(count):
   xx=(r.randrange(WORLD)-round(f*(1.0+band*.5)))%WORLD;yy=(r.randrange(H)+f*speed)%H
   length=3+band*3;line(d,[(xx,yy),(xx-1-band,yy+length)],color)
 # Low pavement splashes with coherent expanding pixel rings.
 for i in range(14):
  phase=(f+i*7)%23
  if phase<10:
   xx=(i*47+19)%WORLD;yy=488+(i*19)%136;rr=phase//3+1
   line(d,[(xx-rr,yy),(xx-rr-2,yy+1),(xx+rr+2,yy+1),(xx+rr,yy)],'#3b5263')
 # A foreground drainpipe anchors the right edge, with lit collars.
 rect(d,397,272,8,368,'black');rect(d,398,274,2,365,'wall')
 for yy in range(291,640,69):rect(d,395,yy,12,4,'dark');rect(d,396,yy,9,1,'edge')
 # Slow whole-pixel camera drift, exposing genuine scene detail.
 cam=round(f*.09);return im.crop((cam,0,cam+W,H))

def main():
 BASE.save(OUT/'editable-pixel-background.png')
 frames=180
 proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','360x640','-r','30','-i','-','-vf','scale=1080:1920:flags=neighbor','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'Neon_Street_Pixel_Preview.mp4')],stdin=subprocess.PIPE)
 try:
  for f in range(frames):
   im=frame(f);proc.stdin.write(im.tobytes())
   if f in [0,45,90,135,179]:im.save(OUT/f'frame-{f:03d}.png')
 finally:proc.stdin.close()
 if proc.wait():raise RuntimeError('FFmpeg encode failure')
 print('Rendered 180 original animated frames.',flush=True)
if __name__=='__main__':main()
