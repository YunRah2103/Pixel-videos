"""Original neo-noir pixel preview V3. Source-drawn sprites, 360x640 -> exact 3x.
Visual exploration using Pillow/FFmpeg, not proof of external editor or V4 runtime use.
Run: python3 scripts/render_neonoir_v3.py
"""
from PIL import Image,ImageDraw,ImageChops
from pathlib import Path
import math,random,subprocess,json,hashlib
from render_neonoir_preview import BASE as OLD_BASE, P, rect,line,poly,text,W,H,WORLD
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'out/neonoir-v3';OUT.mkdir(parents=True,exist_ok=True)

def background():
 im=OLD_BASE.copy();d=ImageDraw.Draw(im)
 # Larger signage is legible at phone size; housings and supports are tangible.
 rect(d,194,264,137,27,'black');rect(d,195,265,135,1,'edge');rect(d,196,266,133,23,'#341d3a')
 line(d,[(198,268),(327,268),(327,287),(198,287),(198,268)],'#ac447d');text(d,205,272,'NIGHT OWL','#ffd4e8',2)
 rect(d,195,290,135,2,'black');rect(d,207,292,5,6,'black');rect(d,310,292,5,6,'black')
 # Window bowl graphics and stylised products, with deliberate one-pixel clusters.
 for cx,cy in [(204,375),(239,375),(273,375)]:
  poly(d,[(cx-10,cy),(cx+10,cy),(cx+7,cy+6),(cx-5,cy+7)],'#a3c7be');line(d,[(cx-10,cy),(cx+10,cy)],'#e0d9be')
  line(d,[(cx-6,cy-2),(cx+5,cy-2)],'#deab80');line(d,[(cx-3,cy-4),(cx-2,cy-8),(cx-4,cy-10)],'#589ca0')
  line(d,[(cx+3,cy-4),(cx+4,cy-9)],'#589ca0')
 # Weathered drainpipe, conduits, tile damage and torn street posters.
 line(d,[(364,246),(364,307),(359,313),(359,332)],'black',4);line(d,[(363,247),(363,306),(358,313)],'edge')
 for yy in [260,288,320]:rect(d,360,yy,7,3,'black');rect(d,361,yy,5,1,'rose')
 for x,y in [(126,379),(127,393),(371,407)]:
  poly(d,[(x,y),(x+15,y+1),(x+14,y+18),(x+10,y+16),(x+2,y+17)],'#797182');rect(d,x+2,y+3,10,3,'wine')
  for j in range(3):rect(d,x+3,y+8+j*2,6-j,1,'dark')
 # Aged facade marks; clustered cracks, irregular wet trails, repaired plaster.
 for x,y in [(179,261),(302,256),(185,172),(356,184),(68,374),(32,277)]:
  line(d,[(x,y),(x-2,y+4),(x+1,y+7),(x,y+12)],'#161b2b');line(d,[(x+1,y+8),(x+5,y+9)],'#161b2b')
  rect(d,x+2,y+2,3,1,'edge')
 # Decorative thin awning edge and warm hanging lantern.
 line(d,[(156,329),(415,329)],'#a4547d')
 line(d,[(174,326),(174,342)],'black',2)
 poly(d,[(168,341),(179,341),(182,346),(182,362),(178,366),(168,365),(165,361),(165,346)],'#672f52')
 rect(d,168,344,10,19,'#d07a88');rect(d,171,344,3,19,'#f7beac');line(d,[(166,348),(181,348)],'#944b6d');line(d,[(166,359),(181,359)],'#944b6d')
 rect(d,169,367,7,2,'black');line(d,[(173,369),(173,374)],'#b5747b')
 # Streetlight on the left, a pool of warm colour on the sidewalk.
 line(d,[(113,334),(113,426)],'black',3);line(d,[(112,334),(112,343)],'edge')
 line(d,[(111,336),(104,330),(92,330)],'black',3);rect(d,88,330,15,4,'black');rect(d,90,332,10,2,'warm')
 # Restore details behind the light with a controlled colour blend, no blur.
 light=Image.new('RGBA',im.size);ld=ImageDraw.Draw(light)
 poly(ld,[(92,334),(101,334),(126,450),(74,450)],(221,168,111,18));im=Image.alpha_composite(im.convert('RGBA'),light).convert('RGB');d=ImageDraw.Draw(im)
 # Elevated track is between the city and this building, not a painted backdrop.
 rect(d,0,139,WORLD,9,'black');line(d,[(0,139),(WORLD,139)],'#596075');line(d,[(0,143),(WORLD,143)],'#33384e')
 for x in range(0,WORLD,13):rect(d,x,145,7,2,'#32334c')
 # Tiled foreground curb with broken edge highlights.
 for x in range(0,WORLD,19):
  rect(d,x,474,14,1,'#76546f' if x%3 else '#58757b')
 return im
def colour_spill(im):
 pix=im.load()
 for y in range(218,452):
  for x in range(118,365):
   r,g,b=pix[x,y]
   if max(r,g,b)>145 or max(r,g,b)<28:continue
   d1=abs(x-158)/72+abs(y-269)/99
   d2=abs(x-240)/120+abs(y-380)/95
   if d1<1:
    weight=.25 if d1<.45 else .12
    tint=(169,55,122)
   elif d2<1:
    weight=.25 if d2<.55 else .12
    tint=(53,136,143)
   else:continue
   pix[x,y]=tuple(round(a*(1-weight)+bb*weight) for a,bb in zip((r,g,b),tint))
 return im
BG=colour_spill(background())

# A native-resolution articulated umbrella walker. No post-drawing sprite scaling.
def walker(f,lit=0):
 im=Image.new('RGBA',(90,118));d=ImageDraw.Draw(im)
 cycle=f%28;phase=cycle/28*2*math.pi;bob=round((1-math.cos(phase*2))*.6)
 hip=(43,78+bob)
 def foot(p):
  p=p%28
  if p<14:return (round(33+p*.96),111)
  u=(p-14)/14;return (round(46.44-u*13.44),111-round(math.sin(u*math.pi)*6))
 front=foot(cycle);rear=foot(cycle+14)
 # Rear leg under coat, then the sun-facing trouser with knee crease and boots.
 for end,col,shade in [(rear,'#142034','#26394c'),(front,'#263e50','#4c6a77')]:
  knee=(round((hip[0]+end[0])*.5)-3,94 if end[1]==111 else 91)
  poly(d,[(hip[0]-4,hip[1]-2),(hip[0]+3,hip[1]),(knee[0]+3,knee[1]),(end[0]+2,end[1]-3),(end[0]-3,end[1]-3),(knee[0]-3,knee[1]+1)],col)
  line(d,[(hip[0]+1,hip[1]+1),knee,(end[0]+1,end[1]-5)],shade)
  poly(d,[(end[0]-3,end[1]-5),(end[0]+3,end[1]-5),(end[0]+3,end[1]),(end[0]-8,end[1]),(end[0]-9,end[1]-2)],'#0c1523')
  line(d,[(end[0]-7,end[1]-1),(end[0]+1,end[1]-1)],'#65818c')
 # Coat silhouette, flaps, rain seams and lit shoulder.
 tail=round(math.sin(phase+.7)*2)
 poly(d,[(35,48+bob),(47,48+bob),(53,57+bob),(54,75),(58+tail,87),(44,89),(38,84),(28+tail,85),(33,69)],'#172437')
 poly(d,[(44,51+bob),(49,55+bob),(49,76),(54+tail,85),(45,86),(42,77)],'#345166')
 poly(d,[(34,53+bob),(40,54+bob),(37,72),(34,80),(30+tail,82)],'#263c52')
 line(d,[(48,54+bob),(50,69),(47,81)],'#67919b');line(d,[(40,57),(40,78)],'#0f1d30')
 rect(d,42,69,2,1,'#a4b1b0');rect(d,42,75,2,1,'#677d87')
 # Neck, detailed profile and hood/hair, all drawn at the same pixel density.
 rect(d,36,44+bob,7,6,'#9e7480')
 poly(d,[(31,30+bob),(41,28+bob),(47,32+bob),(48,40+bob),(44,48+bob),(35,48+bob),(30,42+bob)],'#142034')
 poly(d,[(32,34+bob),(38,32+bob),(44,34+bob),(43,38+bob),(34,38+bob)],'#3b526b')
 poly(d,[(31,37+bob),(37,37+bob),(38,41+bob),(36,45+bob),(31,44+bob),(28,41+bob),(31,40+bob)],'#c9999c')
 rect(d,30,38+bob,4,1,'#f2c6bd');rect(d,29,40+bob,2,1,'#7d637c');rect(d,33,44+bob,3,1,'#806076')
 # Arm holding the umbrella, bent elbow and readable fingers.
 line(d,[(37,54+bob),(30,64+bob),(24,58+bob)],'#182c40',7)
 line(d,[(36,54+bob),(30,63+bob),(25,58+bob)],'#4b697b',2)
 rect(d,22,54+bob,5,6,'#c69aa0');rect(d,23,54+bob,2,2,'#e5bdb7')
 # Scarf with a modest delayed secondary sway.
 poly(d,[(35,47+bob),(45,48+bob),(48,51+bob),(41,53+bob),(34,51+bob),(30,53+bob),(27,51+bob)],'#864767')
 line(d,[(35,48+bob),(44,49+bob)],'#c77c91')
 # Umbrella shaft then eight faceted panels; whole-pixel bob only.
 uy=bob
 line(d,[(26,15+uy),(25,63+uy),(28,66+uy),(31,63+uy)],'#192a3e',2)
 line(d,[(25,18+uy),(25,52+uy)],'#8b9caa')
 top=[(3,24+uy),(8,16+uy),(18,8+uy),(32,3+uy),(43,2+uy),(60,6+uy),(73,14+uy),(81,24+uy)]
 poly(d,top+[(70,22+uy),(59,26+uy),(46,23+uy),(33,27+uy),(18,23+uy),(3,24+uy)],'#111c32')
 poly(d,[(8,21+uy),(18,10+uy),(34,5+uy),(43,4+uy),(33,24+uy),(18,21+uy)],'#3b4e71')
 poly(d,[(43,4+uy),(60,8+uy),(73,17+uy),(78,22+uy),(60,24+uy),(46,21+uy)],'#6f3b63')
 poly(d,[(43,4+uy),(46,21+uy),(34,24+uy)],'#576385')
 line(d,[(8,20+uy),(19,10+uy),(34,5+uy),(43,4+uy)],'#88aab6')
 line(d,[(43,4+uy),(60,8+uy),(73,17+uy)],'#b06d91')
 for x,y in [(13,19),(29,12),(50,12),(65,18)]:rect(d,x,y+uy,3,1,'#a294b2')
 return im

# Detailed original tram sprite. Windows, bogies, vents and panel seams are separate.
def tram_sprite():
 im=Image.new('RGBA',(314,65));d=ImageDraw.Draw(im)
 poly(d,[(2,10),(11,3),(284,3),(305,12),(312,31),(312,53),(4,53)],'#151e30')
 poly(d,[(9,11),(18,6),(282,6),(300,14),(304,34),(304,48),(9,48)],'#5f516b')
 rect(d,12,10,266,5,'#aa7a83');rect(d,12,15,269,3,'#d6a590')
 rect(d,10,38,292,6,'#843e65');rect(d,10,43,292,2,'#d9829d')
 for i in range(9):
  x=17+i*28;rect(d,x,20,22,17,'#16283c');rect(d,x+2,21,18,12,'#e7bf91');rect(d,x+3,21,17,2,'#ffdfb3');rect(d,x+8,24,6,9,'#7f6b7b');rect(d,x+11,28,5,5,'#4a4b64');rect(d,x+2,34,18,1,'#b78b8d')
  rect(d,x+22,18,2,26,'#393248');rect(d,x,47,19,1,'#9b778b')
 for x in [62,232]:
  rect(d,x,52,45,5,'#111925');rect(d,x+6,56,10,5,'#0c1421');rect(d,x+28,56,10,5,'#0c1421');rect(d,x+8,56,6,2,'#546071');rect(d,x+30,56,6,2,'#546071')
 poly(d,[(284,18),(297,20),(302,34),(284,34)],'#274251');line(d,[(286,19),(295,21),(298,29)],'#94b1b3')
 rect(d,304,37,3,4,'#fbe0b0');rect(d,10,45,7,2,'#e686a6')
 for x in [33,130,220]:rect(d,x,0,28,4,'#283047');line(d,[(x+2,1),(x+26,1)],'#556077')
 line(d,[(159,3),(174,-8),(195,3)],'#172034')
 return im
TRAM=tram_sprite().transpose(Image.Transpose.FLIP_LEFT_RIGHT)

def reflections(im,f):
 # Reflect the real storefront pixels, broken into irregular puddles and strips.
 src=im.copy();dest=im.load();sp=src.load();rng=random.Random(51)
 for y in range(480,633):
  sy=round(467-(y-480)*1.24)
  if sy<0:continue
  step=(y-480)//3
  if step%6==4:continue
  shift=round(math.sin(f*.10+y*.17)*2+math.sin(f*.06+y*.41))
  attenuation=.36 if y<520 else .28 if y<575 else .20
  for x in range(42,400):
   # Fragment boundaries are spatially stable; ripples move their sampled content.
   if ((x//11+step*3)%13>8) or abs(x-231)>(154-(y-480)*.17):continue
   sx=max(0,min(WORLD-1,x+shift));r,g,b=sp[sx,sy]
   if max(r,g,b)<73:continue
   rr,gg,bb=dest[x,y];dest[x,y]=(round(rr*(1-attenuation)+r*attenuation),round(gg*(1-attenuation)+g*attenuation),round(bb*(1-attenuation)+b*attenuation))
 return im

# Original masked runner, designed at background scale on the same native grid.
# Stance foot advances 2.6px/frame locally against 2.6px/frame world travel.
def ninja_sprite(f):
 im=Image.new('RGBA',(76,68));d=ImageDraw.Draw(im)
 p=f%16;phase=p/16*2*math.pi;bob=round(math.cos(phase*2))
 hip=(42,41+bob)
 def foot(q):
  q=q%16
  if q<8:return (round(22+q*2.6),63)
  t=(q-8)/8
  return (round(42.8-t*20.8),63-round(math.sin(t*math.pi)*14))
 # Sheathed blade, shoulder strap and trailing scarf distinguish the silhouette.
 line(d,[(38,28+bob),(60,7+bob)],'#101b2b',4)
 line(d,[(39,27+bob),(60,7+bob)],'#536578')
 line(d,[(58,8+bob),(64,2+bob)],'#263a4c',3)
 line(d,[(55,8+bob),(61,14+bob)],'#9a7b82')
 for endpoint,col,edge in [(foot(p+8),'#121f2e','#32475a'),(foot(p),'#1c3042','#5d7a87')]:
  # Raised swing knee, bent lower leg and pointed boot; no rigid scissor legs.
  knee=(round((hip[0]+endpoint[0])*.5)-5,50 if endpoint[1]==63 else 44)
  poly(d,[(hip[0]-4,hip[1]-2),(hip[0]+3,hip[1]),(knee[0]+3,knee[1]-2),(endpoint[0]+3,endpoint[1]-3),(endpoint[0]-3,endpoint[1]-2),(knee[0]-3,knee[1]+2)],col)
  line(d,[(hip[0],hip[1]+1),knee,(endpoint[0]+1,endpoint[1]-4)],edge)
  poly(d,[(endpoint[0]-3,endpoint[1]-5),(endpoint[0]+3,endpoint[1]-4),(endpoint[0]+3,endpoint[1]),(endpoint[0]-7,endpoint[1]),(endpoint[0]-8,endpoint[1]-2)],'#0b1624')
  line(d,[(endpoint[0]-5,endpoint[1]-1),(endpoint[0]+1,endpoint[1]-1)],'#415d6c')
 # Forward-leaning tunic and cloth panels.
 poly(d,[(28,21+bob),(38,21+bob),(46,29+bob),(47,41+bob),(40,46+bob),(33,40+bob),(29,32+bob),(25,27+bob)],'#101c2c')
 poly(d,[(36,23+bob),(42,29+bob),(44,39+bob),(40,42+bob),(36,34+bob)],'#2e4559')
 line(d,[(38,24+bob),(43,31+bob),(44,37+bob)],'#65818b')
 line(d,[(29,25+bob),(40,36+bob)],'#526074',2)
 poly(d,[(33,38+bob),(45,38+bob),(47,41+bob),(36,42+bob)],'#703a56')
 # Opposed arms: one drives forward as the other extends behind.
 swing=math.sin(phase)
 near_elbow=(22-round(swing*4),33+bob);near_hand=(17+round(swing*3),26+bob)
 far_elbow=(48+round(swing*4),28+bob);far_hand=(51+round(swing*3),38+bob)
 line(d,[(36,25+bob),far_elbow,far_hand],'#172b3e',4)
 line(d,[far_elbow,far_hand],'#435e71')
 line(d,[(29,25+bob),near_elbow,near_hand],'#182b40',5)
 line(d,[(29,26+bob),near_elbow,near_hand],'#526d80')
 rect(d,near_hand[0]-2,near_hand[1]-2,4,3,'#a17d8d');rect(d,far_hand[0]-1,far_hand[1],3,3,'#867187')
 # Hood, narrow eye slit and tied mask: an original character, not a game sprite.
 poly(d,[(25,8+bob),(33,8+bob),(37,12+bob),(36,21+bob),(30,25+bob),(24,21+bob),(21,15+bob)],'#142336')
 poly(d,[(25,10+bob),(31,9+bob),(35,12+bob),(34,15+bob),(25,14+bob)],'#40566c')
 line(d,[(23,15+bob),(29,15+bob)],'#c5acae')
 rect(d,23,15+bob,2,1,'#f2d3c0')
 poly(d,[(22,17+bob),(31,17+bob),(32,22+bob),(27,23+bob),(23,20+bob)],'#152333')
 # Two cloth tails follow delayed wave phases, independently of legs.
 for i,length in enumerate([23,17]):
  yy=22+bob+i*3;tip=yy+round(math.sin(f*.27-i*.9)*3)-3
  poly(d,[(33,yy),(41,yy-1),(41+length,tip),(47+length,tip+2),(42,yy+3),(34,yy+3)],'#713b59' if i==0 else '#402d49')
  if i==0:line(d,[(36,yy),(43,yy),(41+length,tip)],'#b16a86')
 return im

def place_background_ninja(im,f):
 # A single continuous run enters after the tram and passes behind the umbrella.
 if 96<=f<300:
  x=423-round((f-96)*2.6);y=386
  d=ImageDraw.Draw(im)
  poly(d,[(x+20,450),(x+50,450),(x+54,452),(x+19,452)],'#151e2b')
  sprite=ninja_sprite(f-96);im.paste(sprite,(x,y),sprite)
  # Streetlamp pole is in front of the runner; retain physical depth ordering.
  pole=BG.crop((110,386,115,427));im.paste(pole,(110,386))
 return im

def frame(f):
 im=BG.copy();d=ImageDraw.Draw(im)
 # Elevated carriage moves independently of the front buildings and camera.
 tx=408-round(f*3.1);im.paste(TRAM,(tx,77),TRAM)
 d=ImageDraw.Draw(im)
 line(d,[(0,76),(WORLD,76)],'#121a2c');line(d,[(0,139),(WORLD,139)],'#596075')
 # Hanging cable and a subtle two-frame lamp fault.
 if f in [118,119,122]:
  rect(d,198,269,128,17,'#291c32');text(d,205,272,'NIGHT OWL','#b16c94',2)
 # Animated air-conditioner fan is a four-frame pixel cross.
 x,y=351,268
 for i in range(4):
  a=f*.24+i*math.pi/2;line(d,[(x,y),(x+round(math.cos(a)*5),y+round(math.sin(a)*4))],'#697281')
 im=place_background_ninja(im,f);d=ImageDraw.Draw(im)
 # Steam curls: overlapping stepped contours, not floating square particles.
 for i in range(3):
  age=(f*.42+i*21)%63;yy=453-round(age);xx=101+round(math.sin(age*.065+i)*6)
  if age<53:
   col='#3c4d5d' if age<24 else '#2c3a4c'
   line(d,[(xx-3,yy+5),(xx+3,yy+2),(xx+5,yy-2),(xx+2,yy-5),(xx-3,yy-7),(xx-4,yy-11)],col,2)
 im=reflections(im,f);d=ImageDraw.Draw(im)
 # Better articulated actor, with a light-coloured umbrella rim to separate silhouette.
 x=258-round(f*.96);y=414;hero=walker(f)
 # Soft-looking shadow is a stepped silhouette, never a blurred ellipse.
 poly(d,[(x+30,525),(x+52,525),(x+63,529),(x+48,532),(x+22,531),(x+18,528)],'#111b29')
 # Actual flipped sprite fragments beneath the actor.
 for j in range(8):
  strip=hero.crop((14,107-j*7,75,109-j*7)).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
  # Palette-darken the coloured reflection while preserving alpha.
  rr,gg,bb,aa=strip.split();strip=Image.merge('RGBA',(rr.point(lambda v:int(v*.36)),gg.point(lambda v:int(v*.40)),bb.point(lambda v:int(v*.47)),aa.point(lambda v:int(v*.65))))
  im.paste(strip,(x+14+round(math.sin(f*.13+j)*2),531+j*4),strip)
 im.paste(hero,(x,y),hero);d=ImageDraw.Draw(im)
 # Cat silhouette now has a head turn, blinking eyes and a two-joint tail.
 cx,cy=303,443;turn=1 if f>130 else 0
 poly(d,[(cx,cy),(cx+2,cy-8),(cx+4,cy-10),(cx+3+turn,cy-16),(cx+7+turn,cy-13),(cx+10+turn,cy-16),(cx+11,cy-10),(cx+14,cy-7),(cx+15,cy)],'black')
 if f%107 not in [30,31,32]:rect(d,cx+5+turn,cy-11,1,1,'cyan');rect(d,cx+9+turn,cy-11,1,1,'cyan')
 line(d,[(cx+13,cy-2),(cx+20,cy-3),(cx+23,cy-8+round(math.sin(f*.055)*2))],'black',2)
 # Depth-separated rain and local splashes remain deterministic on frame seeks.
 for band,count,speed,color in [(0,75,6,'#334357'),(1,33,9,'#61748a')]:
  r=random.Random(113+band)
  for i in range(count):
   xx=(r.randrange(WORLD)-round(f*(.7+band*.5)))%WORLD;yy=(r.randrange(H)+f*speed)%H
   line(d,[(xx,yy),(xx-1-band,yy+3+band*4)],color)
 # Drips from the actual awning lip rather than arbitrary screen positions.
 for i,xx in enumerate([163,196,285,339,403]):
  t=(f+i*17)%38
  if t<26:rect(d,xx-round(t*.08),332+round(t*t*.12),1,2,'#607383')
 for i in range(20):
  age=(f+i*9)%29
  if age<11:
   xx=(i*59+29)%WORLD;yy=489+(i*23)%130;rr=age//3+1
   line(d,[(xx-rr-1,yy),(xx-rr-3,yy+1),(xx+rr+3,yy+1),(xx+rr+1,yy)],'#43596b')
 # Strong near-frame silhouettes create depth without camera shake.
 poly(d,[(-2,548),(9,548),(11,630),(24,640),(-2,640)],'#0a1320');line(d,[(10,551),(12,629)],'#263c4b')
 rect(d,397,272,8,368,'black');rect(d,398,274,2,365,'wall')
 for yy in range(291,640,69):rect(d,395,yy,12,4,'dark');rect(d,396,yy,9,1,'edge')
 # Tiny camera move; all positions remain whole source pixels.
 cam=round(5+f*.075);return im.crop((cam,0,cam+W,H))

def main():
 BG.save(OUT/'background-source.png');TRAM.save(OUT/'tram-source.png')
 sheet=Image.new('RGBA',(90*8,118))
 for i in range(8):sheet.paste(walker(i*3),(i*90,0))
 sheet.save(OUT/'umbrella-walk-sheet.png')
 runner_sheet=Image.new('RGBA',(76*8,68))
 for i in range(8):runner_sheet.paste(ninja_sprite(i*2),(i*76,0))
 runner_sheet.save(OUT/'ninja-run-sheet.png')
 proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','360x640','-r','30','-i','-','-vf','scale=1080:1920:flags=neighbor','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'Neon_Street_10s_Ninja.mp4')],stdin=subprocess.PIPE)
 try:
  for f in range(300):
   im=frame(f);proc.stdin.write(im.tobytes())
   if f in [0,60,120,165,195,225,255,299]:im.save(OUT/f'frame-{f:03d}.png')
 finally:proc.stdin.close()
 if proc.wait():raise RuntimeError('FFmpeg failed')
 print('Rendered 300 frames / 10 seconds.',flush=True)
if __name__=='__main__':main()
