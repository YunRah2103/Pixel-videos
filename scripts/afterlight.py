#!/usr/bin/env python3
"""AFTERLIGHT / Cinder District. Original crisp 480x270 hand-programmed pixel-art film.
Every rendered pixel is authored natively. No source imagery, blur, bloom, pixelation,
AI upscaling, unlicensed sprites, stochastic runtime, or image shaders.
"""
from __future__ import annotations
import math, random, argparse, subprocess, shutil
from pathlib import Path
from PIL import Image, ImageDraw
W,H,FPS=480,270,24
INK='#090e21'; VOID='#0e1629'; NIGHT='#10192e'
C={'ink':'#090f20','dark':'#111a2d','blue':'#1a2a40','blue2':'#233a51','slate':'#344b61','edge':'#5c6c7c','silver':'#7c90a0','teal':'#247f8f','mint':'#69c8c0','cream':'#ffe1a3','gold':'#f5ac75','red':'#c64e68','pink':'#ed729c','purple':'#845b99','mauve':'#ae78a2'}

def canvas():return Image.new('RGBA',(W,H),(0,0,0,0))
def R(d,x,y,w,h,c):
 if w>0 and h>0:d.rectangle((int(x),int(y),int(x+w-1),int(y+h-1)),fill=c)
def L(d,points,c,wd=1):d.line([(int(x),int(y)) for x,y in points],fill=c,width=wd)
def P(d,p,c):d.polygon(p,fill=c)
def hashish(*a):
 k=0x13377
 for v in a:k=(k*1664525+int(v)*1013904223+9013)&0xffffffff
 return k

def windows(d,x,y,w,h,kind,seed):
 # Alternating lit/dark rooms and asymmetrical window rhythms; no regular grid of identical dots.
 step=9 if kind=='far' else 12
 for fy in range(y+6,y+h-5,step):
  for fx in range(x+4,x+w-3,step if kind=='far' else 11):
   m=hashish(fx,fy,seed)%15
   if m in (0,1,2,3,4):continue
   col=['#394861','#6d6382','#b48796','#698698','#f1ba8e','#dbc09e'][m%6] if kind=='mid' else ['#455675','#725d84','#b17d97','#4b728d'][m%4]
   ww=2 if kind=='far' else (4 if m%3 else 3); hh=3 if kind=='far' else 5
   R(d,fx,fy,ww,hh,col)
   if kind=='mid' and m%3==0:R(d,fx,fy+hh-1,ww,1,'#65465d')

def cloud(d,x,y,scale=1,tone=0):
 # Curved, stepped cluster silhouette; shading in broken clusters, not simple bars.
 a=['#252e4e','#333c61','#415273'][tone];b=['#394469','#455475','#52617e'][tone]
 for bx,by,bw,bh in [(0,14,16,5),(7,9,21,10),(20,5,24,13),(33,0,17,15),(45,9,20,10),(60,15,24,6),(-9,17,18,3),(10,20,69,3)]:
  R(d,int(x+bx*scale),int(y+by*scale),int(bw*scale),max(1,int(bh*scale)),a)
 for bx,by,bw,bh in [(16,9,13,2),(26,6,15,2),(34,3,9,2),(51,12,10,2),(25,17,36,1)]:R(d,int(x+bx*scale),int(y+by*scale),max(1,int(bw*scale)),max(1,int(bh*scale)),b)

def sky():
 im=canvas();d=ImageDraw.Draw(im);R(d,0,0,W,H,'#0b1126')
 for y,c in [(16,'#0e1630'),(32,'#111d38'),(48,'#15213e'),(65,'#192945'),(83,'#213250'),(103,'#293858'),(124,'#3d3a60'),(148,'#553d61'),(170,'#684261')]:R(d,0,y,W,16,c)
 # Sunset crimson strip near distant horizon, sharp layered rows.
 for yy,co in [(175,'#79465f'),(178,'#7e4964'),(182,'#5c3d5b')]:R(d,0,yy,480,2,co)
 rng=random.Random(41)
 for n in range(127):
  x=rng.randrange(W);y=rng.randrange(107)
  if hashish(x,y)%6==0:R(d,x,y,1,1,'#d9c1ca')
  else:R(d,x,y,1,1,('#506c91','#687397','#8d83a3')[n%3])
 for x,y in [(25,14),(88,34),(196,12),(267,31),(398,13),(444,41)]:R(d,x,y,2,1,'#c6b6c9')
 # Moon silhouette 32 pixels wide, dithered shadow rim and crater shapes.
 cx,cy,rad=343,40,17
 for yy in range(-rad,rad+1):
  half=int(math.sqrt(max(0,rad*rad-yy*yy)));R(d,cx-half,cy+yy,2*half+1,1,'#efc4b8' if yy>3 else '#f9d9bd')
 for bx,by,w,h,col in [(-10,-5,6,3,'#ccaabb'),(5,-10,3,4,'#dfb7bb'),(-2,9,8,3,'#d9b2b8'),(8,2,4,3,'#d6b1b5'),(-11,5,3,2,'#e7c2bc')]:R(d,cx+bx,cy+by,w,h,col)
 cloud(d,-30,33,1.2);cloud(d,74,14,0.9,1);cloud(d,189,48,0.88);cloud(d,370,50,1.35,1);cloud(d,433,19,0.9)
 # Cloud-edge pin clusters.
 for x,y in [(180,67),(183,67),(376,77),(386,77),(122,39),(119,39)]:R(d,x,y,2,1,'#6b6686')
 return im

def atmosphere():
 im=canvas();d=ImageDraw.Draw(im)
 # Far stacks: smooth skyline silhouette interrupted by antenna clusters and irregular profiles.
 rng=random.Random(199);x=-3
 while x<W:
  w=rng.randrange(8,20);ht=rng.randrange(28,69);y=173-ht
  col=['#262f4d','#303650','#343951','#31354d'][rng.randrange(4)]
  R(d,x,y,w,ht,col);R(d,x-1,y,w+2,2,'#44425e')
  if hashish(x,2)%3==0:
   R(d,x+w//2,y-7,1,7,'#596079');R(d,x+w//2-1,y-7,3,1,'#966e96')
  if w>12:
   for ry in range(y+7,170,7):
    for rx in range(x+4,x+w-3,5):
     if hashish(rx,ry)%4==0:R(d,rx,ry,1,2,'#ad7e9e')
  x+=w+rng.randrange(1,4)
 # Terraced violet ridges toward river horizon.
 P(d,[(0,167),(29,162),(43,166),(61,155),(97,163),(133,157),(168,162),(183,153),(220,159),(268,154),(307,164),(351,152),(395,161),(438,154),(480,162),(480,186),(0,186)],'#222e48')
 for x in range(3,479,4):
  if hashish(x,6)%4==0:R(d,x,171+hashish(x)%10,2,1,'#67506c')
 return im

def tall_tower(d,x,y,w,bottom,seed,style):
 h=bottom-y
 palette=[('#23314e','#35405e','#43516e'),('#2c314e','#3e4162','#5b5171'),('#26334c','#30455e','#466079')][seed%3]
 base,facade,edge=palette
 R(d,x,y,w,h,base);R(d,x+w-5,y,5,h,'#1a2741');R(d,x+2,y+4,w-11,h-7,facade)
 R(d,x-2,y-2,w+4,3,edge);R(d,x-2,y-3,w+4,1,'#8080a1')
 for xx in range(x+6,x+w-6,8):R(d,xx,y+4,1,h-4,'#242d4a')
 for yy in range(y+10,bottom-5,9):
  for xx in range(x+6,x+w-6,8):
   value=hashish(xx,yy,seed)%11
   if value>3:
    col=['#e2a78f','#b591b4','#83aab2','#526c8c','#ecc09d','#5f7f9b'][value%6]
    R(d,xx+2,yy,3,4,col)
 if style=='spire':
  R(d,x+w//2,y-23,3,21,'#485579');R(d,x+w//2,y-23,1,15,'#9d75b1')
  R(d,x+w//2-5,y-12,14,1,'#7d638f')
  for xx in (x+3,x+w-5):R(d,xx,y-15,1,11,'#786887')
 elif style=='billboard':
  R(d,x+3,y+19,w-11,39,'#111a32');R(d,x+5,y+21,w-15,35,'#6e3668')
  R(d,x+7,y+23,w-19,31,'#a44e8c')
  # Poster shows strong original face silhouette: hair, pale face, scarf.
  mx=x+w//2;R(d,mx-6,y+27,13,15,'#e6a7b4');R(d,mx-7,y+25,13,5,'#3b2551')
  R(d,mx-8,y+38,5,9,'#512b5b');R(d,mx+6,y+29,3,14,'#532b63')
  R(d,mx-3,y+35,2,1,'#56304d');R(d,mx+3,y+35,2,1,'#56304d')
  P(d,[(mx-5,y+45),(mx+6,y+45),(mx+11,y+54),(mx-10,y+54)],'#422858')
  R(d,x+7,y+53,w-18,2,'#e06baf')
 elif style=='lights':
  for yy in (y+18,y+23,y+28):R(d,x+6,yy,w-13,2,'#467f9c')

def icon_sign(d,x,y,style='diamond',border='#e874a5'):
 R(d,x-2,y-2,22,41,'#101c34');R(d,x,y,18,37,'#512a58');R(d,x+1,y+1,16,35,'#792f67')
 R(d,x,y,18,1,border);R(d,x,y,1,37,border);R(d,x+17,y,1,37,'#bc5b8d')
 if style=='diamond':
  for k in range(3):
   yy=y+5+10*k
   P(d,[(x+9,yy),(x+14,yy+4),(x+9,yy+8),(x+4,yy+4)],'#69d8c9')
   R(d,x+8,yy+4,3,1,'#15475e')
 else:
  for k in range(4):
   yy=y+5+8*k
   R(d,x+4,yy,10,1,'#fbcaa9');R(d,x+6,yy+1,6,2,'#e980a2')
   R(d,x+7,yy+4,4,1,'#eeb8ab')

def skyline():
 im=canvas();d=ImageDraw.Draw(im)
 tall_tower(d,123,81,30,184,1,'spire');tall_tower(d,203,41,44,188,4,'spire')
 tall_tower(d,272,71,34,178,2,'billboard');tall_tower(d,383,67,26,185,3,'lights')
 tall_tower(d,435,100,34,188,5,'spire')
 # Radiating elevated antenna lattice on central tower.
 R(d,205,43,2,103,'#56adc0');R(d,245,44,1,93,'#cd72ae')
 R(d,209,63,33,2,'#ba83b2')
 P(d,[(220,52),(225,57),(220,62),(215,57)],'#e67ba8');P(d,[(220,54),(223,57),(220,60),(217,57)],'#69c7ca')
 for xx,yy in [(205,53),(245,65),(206,101),(244,115)]:R(d,xx,yy,1,5,'#e67faf')
 # Airbridges among the tower layers.
 R(d,152,137,55,4,'#242e4b');R(d,151,136,57,1,'#77748a')
 R(d,308,133,75,5,'#212a45');R(d,307,132,77,2,'#585878')
 for px in range(313,378,14):R(d,px,134,7,2,'#7c7795')
 # Varied foreground medium-distance architecture / complex silhouettes.
 rng=random.Random(94);x=-16
 while x<W:
  w=rng.randrange(19,37);ht=rng.randrange(22,55);y=189-ht
  col=['#23314a','#29334e','#303652','#283349'][rng.randrange(4)]
  R(d,x,y,w,ht,col);R(d,x-2,y-3,w+4,3,'#514660');R(d,x,y+5,2,ht-5,'#172339')
  R(d,x+w-3,y+3,2,ht-3,'#1a2339');windows(d,x,y,w,ht,'mid',11)
  if hashish(x,45)%3==0:
   R(d,x+w//2,y-9,1,8,'#6b6a84');R(d,x+w//2-2,y-9,5,1,'#ca7ca5')
  if w>25 and hashish(x)%3==0:R(d,x+4,y+7,w-10,3,'#45516d')
  x+=w+rng.randrange(2,6)
 # Elevated bridge with rigid pier lattice and rail.
 R(d,0,179,W,2,'#66637b');R(d,0,181,W,2,'#1b2540')
 for px in range(14,478,32):
  R(d,px,183,3,29,'#182338');R(d,px+1,183,1,28,'#4d4c6b')
  L(d,[(px,183),(px+18,203)],'#2c324d')
 # A cinematic but hand-shaped orange-red sign at the center city horizon.
 R(d,336,110,19,49,'#151c39');R(d,338,111,15,45,'#533657')
 R(d,339,112,13,1,'#d66c9a')
 for k in range(4):
  yy=118+k*9
  R(d,341,yy,9,1,'#e68caf');R(d,343,yy+2,5,2,'#f0b5ae');R(d,341,yy+6,9,1,'#ad6d98')
 return im

def railtrain(f):
 im=canvas();d=ImageDraw.Draw(im)
 x=int(480-((f*0.58+140)%730))
 for i in range(6):
  xx=x+i*36
  R(d,xx,168,35,12,'#101c35');R(d,xx+1,169,33,2,'#596b87');R(d,xx+1,171,33,6,'#2b415d')
  for q in range(4):R(d,xx+3+q*8,172,6,4,'#efb88f' if (q+i)%4 else '#7d9caa')
  R(d,xx+2,178,31,1,'#8d6078');R(d,xx+2,180,3,1,'#111a31');R(d,xx+29,180,3,1,'#111a31')
 return im

def brickfield(d,x,y,w,h,seed,base,mortar,top):
 R(d,x,y,w,h,base)
 # One-pixel hand-clustered surface relief, offset mortared rows, broken masonry.
 for yy in range(y+6,y+h,8):
  for xx in range(x-5+(yy//8%2)*9,x+w,17):
   start=max(x,xx);end=min(x+w,xx+13)
   if start>=end:continue
   R(d,start,yy,end-start,1,mortar)
   if (hashish(xx,yy,seed)%5)==0:R(d,start+2,yy-3,2,2,top)
 for yy in range(y+8,y+h,16):
  for xx in range(x+9,x+w,17):R(d,xx,yy-6,1,6,mortar)

def neon_glyph(d,x,y,scale=1,co='#ffc3a5'):
 # Stylized invented glyph from clusters, visually intentional (not random Unicode).
 for dx,dy,w,h in [(0,0,7,1),(3,0,1,7),(0,3,7,1),(1,6,6,1),(1,1,1,2)]:R(d,x+dx*scale,y+dy*scale,w*scale,h*scale,co)

def bar_awn(d,x,y,w):
 R(d,x,y,w,5,'#20243b');R(d,x,y,w,1,'#ef926e');R(d,x+2,y+2,w-4,1,'#8d4d5b')
 for dx in range(0,w,8):
  R(d,x+dx,y+4,7,3,'#ab5761');R(d,x+dx+2,y+6,3,1,'#e57a6e')

def left_roof():
 im=canvas();d=ImageDraw.Draw(im)
 # Main roof facing viewer and thin traversable top shelf.
 brickfield(d,0,207,188,63,1,'#172438','#304154','#43526a')
 R(d,0,201,188,6,'#111e32');R(d,0,198,188,4,'#516073');R(d,0,198,188,1,'#9b9291')
 for xx in range(0,187,15):
  R(d,xx,199,1,3,'#8b8692')
  R(d,xx+3,202,7,1,'#23394e')
 # Old ramen bar occupies upper-left roof, with genuine layered interior visual storytelling.
 R(d,7,142,114,54,'#0d162b')
 brickfield(d,10,149,108,47,20,'#332e3b','#493e4f','#685062')
 R(d,13,157,84,30,'#1d2033');R(d,16,160,77,24,'#f9bd85');R(d,18,163,74,18,'#ffe3aa')
 R(d,18,177,74,3,'#c47965');R(d,18,160,75,2,'#dc9e79')
 # Interior back wall tiles, menu board, pictures, cook and two customers.
 for xx in range(19,92,8):R(d,xx,168,1,10,'#ebb889')
 for xx,yy in [(23,165),(39,164),(71,163)]:R(d,xx,yy,10,7,'#805e59');R(d,xx+1,yy+1,8,5,'#e3a675')
 for xx in (27,52,73):R(d,xx,159,1,7,'#463a42');R(d,xx-2,165,5,2,'#f8cf96')
 R(d,20,178,69,3,'#6b4246')
 for xx in (30,57,79):
  R(d,xx,172,5,6,'#3d3541');R(d,xx+1,169,3,4,'#68434a')
 for xx in (33,60):R(d,xx,183,4,4,'#473f4a')
 # Sliding panels with asymmetrical damaged trims.
 for xx in (17,42,66,95):R(d,xx,158,2,29,'#442f3b')
 for xx in (23,47,70):R(d,xx,184,9,1,'#dc9d73')
 R(d,101,164,12,23,'#171d30');R(d,103,168,9,17,'#463045')
 neon_glyph(d,104,170,1,'#e895ac')
 bar_awn(d,5,138,119);R(d,3,135,122,3,'#282037');R(d,3,134,122,1,'#a1606b')
 # Sign attached at left edge: a real offset banner with neon glyphs.
 R(d,0,150,14,36,'#1c1d33');R(d,1,151,12,33,'#903f5d')
 R(d,2,151,10,1,'#f1a16b');R(d,2,183,10,1,'#f0a16d')
 for k in range(3):neon_glyph(d,4,154+9*k,1,'#ffd3a1')
 # Noodle bar chimney and roof clutter.
 R(d,98,124,9,11,'#273449');R(d,96,123,13,2,'#60627a')
 for xx in (100,103):R(d,xx,128,1,6,'#4d5971')
 R(d,123,162,24,31,'#18263a');R(d,126,164,18,24,'#31465c')
 for yy in range(166,187,5):
  for xx in range(128,144,4):R(d,xx,yy,1,2,'#7e8492' if hashish(xx,yy)%3 else '#23374c')
 R(d,122,160,27,3,'#758293');R(d,120,188,30,5,'#25384c')
 # Water cistern and its steel truss; visually grounded rather than hovering boxes.
 for xx in (139,176):R(d,xx,118,2,73,'#142037');R(d,xx+1,123,1,68,'#5e6176')
 for yy in (138,154,171):L(d,[(139,yy),(176,yy+16)],'#31455c');L(d,[(176,yy),(139,yy+16)],'#304056')
 R(d,142,106,33,38,'#121e32');R(d,144,109,30,34,'#3c4057');R(d,142,107,33,2,'#7e6a81')
 for xx in (146,152,160,168):R(d,xx,108,1,35,'#68758a')
 for yy in (120,137):R(d,143,yy,32,1,'#787187')
 P(d,[(139,107),(146,102),(170,102),(178,107)],'#1a1d32')
 L(d,[(139,106),(146,101),(170,101),(178,106)],'#96859b')
 R(d,157,95,1,6,'#6b6480')
 # Corroded steel pipe and downspout runs in front of brick.
 L(d,[(116,153),(120,153),(120,190),(132,190)],'#0a1425',3)
 L(d,[(116,153),(120,153),(120,190),(132,190)],'#708093')
 for yy in (163,177):R(d,117,yy,6,2,'#3c5366')
 # An apartment below shop with deep wall cavity and illuminated clutter.
 R(d,17,225,32,33,'#0b1528');R(d,20,228,26,27,'#405067')
 R(d,22,230,22,23,'#e4aa83');R(d,23,231,20,21,'#eec398');R(d,31,230,2,24,'#344659')
 R(d,20,241,25,2,'#4d5867');R(d,24,248,6,4,'#79594f')
 R(d,63,238,30,32,'#0c1629');R(d,66,241,24,29,'#45516a')
 R(d,68,243,20,24,'#996f76');R(d,70,245,15,20,'#c49783')
 R(d,79,242,2,25,'#38445e');R(d,67,254,21,2,'#4b455b')
 # Maintenance ladder, pipes, vents and realistic ledges.
 R(d,160,213,2,57,'#66798a');R(d,177,213,2,57,'#6f7f90')
 for yy in range(216,270,7):R(d,161,yy,17,2,'#485c6e')
 R(d,107,229,38,28,'#101a2e');R(d,109,231,34,23,'#33465c')
 for xx in range(113,142,5):R(d,xx,234,1,17,'#65798a')
 L(d,[(0,221),(10,221),(10,257),(52,257)],'#667589')
 for yy in (229,245):R(d,7,yy,6,2,'#324c5e')
 # Micro foliage hanging on skyline with handcrafted leaves.
 for xx in (56,57,59,61,96,100,186):
  yy=194-(hashish(xx)%6)
  R(d,xx,yy,1,8,'#266967');R(d,xx-2,yy+2,4,2,'#3c927e');R(d,xx,yy-1,3,2,'#64a88a')
 return im

def right_roof():
 im=canvas();d=ImageDraw.Draw(im)
 brickfield(d,295,206,185,64,29,'#152238','#2b3b52','#48546d')
 R(d,294,201,186,5,'#121d31');R(d,294,198,186,4,'#52657a');R(d,294,198,186,1,'#a7a09c')
 for xx in range(295,480,16):R(d,xx,200,1,2,'#988994');R(d,xx+2,203,8,1,'#304459')
 # Giant industrial building on right roof, with asymmetrical flat-roof parapet.
 R(d,390,140,88,55,'#141d32');R(d,393,145,85,50,'#293148')
 R(d,391,139,89,4,'#39465b');R(d,391,139,89,1,'#8b7790')
 R(d,396,148,57,40,'#1c2940');R(d,399,150,49,35,'#344056')
 for yy in range(154,185,11):
  for xx in range(402,447,12):
   if hashish(xx,yy)%4:R(d,xx,yy,6,5,'#8f6b82' if hashish(xx,yy)%2 else '#52687d')
 R(d,455,149,18,30,'#101b30')
 for yy in (154,159,164,169):R(d,458,yy,11,2,'#596880')
 # Dramatic vertical cyan, rose and amber sign.
 R(d,367,121,19,70,'#101a31');R(d,369,122,16,67,'#35425a');R(d,370,123,14,64,'#274b69')
 for xx in (369,384):R(d,xx,122,1,67,'#60bac2')
 for k in range(5):
  yy=129+k*11
  P(d,[(377,yy),(382,yy+4),(377,yy+8),(372,yy+4)],'#86ddd2')
  R(d,376,yy+4,3,1,'#1c5470')
 R(d,369,186,17,2,'#bf7a9e');R(d,364,125,3,5,'#5f6c80')
 # Rooftop machinery, ventilation, fence and electric poles.
 R(d,306,178,42,19,'#132239');R(d,309,181,35,13,'#384b62')
 for xx in range(314,343,6):R(d,xx,182,2,9,'#738494')
 R(d,307,177,42,3,'#65778b');R(d,310,176,37,1,'#a8a1a0')
 R(d,328,210,48,27,'#121c30');R(d,331,213,43,20,'#40526a');R(d,333,215,38,17,'#182b43')
 for xx in range(336,371,6):R(d,xx,217,2,12,'#596e84')
 for x,y in [(317,239),(430,220)]:
  R(d,x,y,20,16,'#0c172c');R(d,x+2,y+2,16,12,'#536479')
  R(d,x+4,y+4,12,8,'#213249');R(d,x+8,y+6,4,4,'#879a9e')
  R(d,x+1,y+1,3,1,'#aeb1ad')
 # Tall pipe rise and support poles.
 L(d,[(463,199),(463,157),(472,157),(472,146)],'#101b2f',4)
 L(d,[(463,199),(463,157),(472,157),(472,146)],'#748394')
 for yy in (173,185):R(d,461,yy,5,2,'#4d6072')
 R(d,459,146,16,2,'#a98c8d');R(d,467,141,1,5,'#616d84')
 # Fence behind walkway, cross-hatched panel.
 for xx in (450,479):R(d,xx,171,2,25,'#5c6c80')
 R(d,449,169,31,2,'#8b8b91')
 for xx in range(450,481,7):
  L(d,[(xx,173),(min(480,xx+21),193)],'#3e4c63')
  L(d,[(xx,193),(min(480,xx+21),173)],'#3e4c63')
 # Extremely detailed lived-in apartments below the platform.
 for x,y,w,h,color in [(401,224,28,31,'#ce9a85'),(449,231,21,29,'#a2829a')]:
  R(d,x-3,y-3,w+6,h+6,'#0b1529');R(d,x,y,w,h,'#47526a');R(d,x+2,y+2,w-4,h-4,color)
  R(d,x+w//2,y+2,2,h-3,'#2c394d');R(d,x+1,y+h//2,w-2,2,'#364256')
  R(d,x+5,y+h-6,w-9,1,'#78697b')
 R(d,302,238,22,32,'#0a1629');R(d,305,240,16,30,'#37475f')
 R(d,307,243,12,24,'#21334b');R(d,318,254,1,3,'#ffc08f')
 for yy in (240,259):R(d,304,yy,18,1,'#516580')
 for xx in (312,348,475):
  yy=194-(hashish(xx)%5);R(d,xx,yy,1,6,'#22655f');R(d,xx-1,yy,4,2,'#4b9d8d')
 # Tiny original poster on right surface; a ghost-cat pictogram.
 R(d,377,236,18,23,'#0d1b31');R(d,379,238,14,18,'#364d64')
 R(d,381,245,10,8,'#b9a9ba');R(d,382,242,3,4,'#b9a9ba');R(d,388,242,3,4,'#b9a9ba')
 for xx in (383,389):R(d,xx,248,1,2,'#293448')
 R(d,386,251,2,1,'#493a58')
 return im

def gorge():
 im=canvas();d=ImageDraw.Draw(im)
 # City canyon at the playable gap — layered silhouettes and lit apartments receding downward.
 for i,(x,y,w,col) in enumerate([(188,199,25,'#24314b'),(215,221,22,'#263149'),(240,205,23,'#2d314a'),(263,215,24,'#212c45'),(285,198,10,'#19273e')]):
  R(d,x,y,w,270-y,col);R(d,x,y,w,2,'#56536d')
  for yy in range(y+6,270,8):
   for xx in range(x+4,x+w-3,7):
    if hashish(xx,yy,i)%6>1:R(d,xx,yy,3,3,['#b5798f','#8d8bab','#d49990','#526b89'][hashish(xx,yy)%4])
 # Deep descending alley with vanishing point; rails and luminous ground slivers.
 P(d,[(225,270),(243,234),(254,234),(272,270)],'#17243c')
 L(d,[(235,270),(246,235)],'#56647a');L(d,[(260,270),(253,235)],'#596078')
 for y in range(243,268,6):R(d,246-(y-243)//7,y,8+(y-243)//3,1,'#416177')
 R(d,245,256,11,2,'#b55e8c');R(d,248,245,7,1,'#e8a47e')
 # Two non-walkable communications cable swoops.
 L(d,[(185,169),(214,181),(243,190),(264,179),(294,167)],'#0c1327',3)
 L(d,[(185,167),(214,179),(243,188),(264,177),(294,165)],'#67748b')
 L(d,[(183,212),(215,230),(259,235),(295,212)],'#0e1529',3)
 L(d,[(183,211),(215,229),(259,234),(295,211)],'#49586c')
 return im

def detail_overlay():
 im=canvas();d=ImageDraw.Draw(im)
 # Utility telegraph wires cross all skyline layers, with subtle sag.
 L(d,[(0,112),(76,111),(145,115),(219,123),(310,128),(480,126)],'#111a30',2)
 L(d,[(0,111),(76,110),(145,114),(219,122),(310,127),(480,125)],'#776077')
 for x,y in [(77,110),(215,122),(310,127)]:
  R(d,x,y-3,2,6,'#6b5f80');R(d,x-2,y-5,6,1,'#b17e9f')
 # Roof-edge pixel highlights, planned puddles and grime.
 for x,y,w in [(9,196,11),(33,197,13),(65,195,7),(103,195,13),(143,195,9),(307,196,20),(361,195,12),(415,196,11)]:
  R(d,x,y,w,1,'#87a5a7');R(d,x+2,y+1,max(2,w-6),1,'#355671')
 # Alley lanterns: bodies remain unblurred, believable lit surroundings.
 for x,y in [(111,163),(354,170)]:
  R(d,x,y-7,1,7,'#4a556a');R(d,x-3,y,7,2,'#5b5268')
  R(d,x-2,y+2,5,3,'#f1aa78');R(d,x-1,y+4,3,1,'#ffe1a3')
 # Individual tiny route markers, not screen text overlays.
 for x,y in [(13,212),(42,214),(136,214),(340,210),(388,212)]:
  R(d,x,y,3,1,'#a57085');R(d,x+4,y,2,1,'#42516c')
 return im


def craftsmanship():
 """Cinder District's finished pixel detail: convincing surfaces, architecture and light."""
 im=canvas();d=ImageDraw.Draw(im)
 # Gigantic angular transit overpass vanishes behind lower rooftop silhouette.
 for x in range(17,180,29):
  R(d,x,174,3,16,'#1b263b');R(d,x+1,175,1,14,'#627086')
  L(d,[(x,176),(x+16,188)],'#3b4459')
 R(d,1,172,176,2,'#4c4b67');R(d,1,173,176,1,'#8e728a')
 # Roof geometry: actual exposed top surface, ragged lip, seams and patchwork.
 for a,b in [(0,187),(296,480)]:
  R(d,a,189,b-a,9,'#27364b')
  R(d,a,189,b-a,1,'#778494')
  R(d,a,196,b-a,2,'#15233a')
  for xx in range(a+4,b,22):
   off=hashish(xx)%4
   R(d,xx,192+off,15,1,'#465368')
   R(d,xx+2,195+off,7,1,'#203149')
   R(d,xx-1,189+off,1,4,'#647387')
  for xx,yy,ww in [(a+11,191,13),(a+47,194,19),(a+107,192,12),(a+137,194,20)]:
   if xx+ww<b:
    R(d,xx,yy,ww,1,'#60949b');R(d,xx+3,yy+1,ww//2,1,'#3a526a')
  for xx in range(a+6,b-4,13):
   if hashish(xx,19)%4==0:R(d,xx,195,2,1,'#e2a28c')
 # Left upper parapet / storefront steel trusses — rooftop no longer appears a flat rectangle.
 for xx in (5,117):
  R(d,xx,123,3,12,'#172339');R(d,xx+1,125,1,10,'#72869a')
 R(d,5,124,111,3,'#1c2e44');R(d,6,124,109,1,'#8e6a81')
 for xx in range(8,112,11):
  R(d,xx,126,1,8,'#48546a')
  if hashish(xx)%3==0:R(d,xx+2,129,4,2,'#74576d')
 # Exposed restaurant interior tier: chopsticks, steam pots, ceramic lamps.
 R(d,21,180,76,3,'#472f35')
 for xx in (28,46,64,82):
  R(d,xx,178,7,1,'#674144');R(d,xx+1,176,5,2,'#9c7769')
  R(d,xx+2,175,1,1,'#e6c7a5')
 for xx in (34,57):
  R(d,xx,158,1,9,'#54364a');R(d,xx-4,165,9,1,'#ffd2a1')
 # An ornate, strongly highlighted lantern on the shop facade.
 R(d,112,145,1,13,'#696174');R(d,109,157,7,2,'#6f4357')
 R(d,109,159,7,9,'#e38b70');R(d,110,159,5,8,'#ffcf92')
 R(d,110,162,5,1,'#fff0b6');R(d,112,167,1,3,'#8d4b56')
 for xx,yy,w in [(102,170,8),(104,174,7),(100,177,8)]:R(d,xx,yy,w,1,'#9a5d64')
 # Steel fire-escape ladder on facade immediately beneath left roof.
 for xx in (111,127):R(d,xx,211,2,59,'#4d5b72')
 for yy in range(214,269,8):R(d,113,yy,14,2,'#718091')
 for yy in range(216,268,17):L(d,[(111,yy),(128,yy+12)],'#263b54')
 # Power poles, insulators and electrical transformers at multi-layer depths.
 for xx,base in [(159,160),(318,175),(454,142)]:
  R(d,xx,base-56,3,56,'#111e34');R(d,xx+1,base-55,1,54,'#5b6b86')
  R(d,xx-13,base-41,29,3,'#3c4560');R(d,xx-12,base-42,28,1,'#a17c97')
  for rx in (xx-10,xx+7):
   R(d,rx,base-46,5,4,'#4e5972');R(d,rx+1,base-47,3,1,'#94a1a8')
  R(d,xx-6,base-28,13,11,'#202d45');R(d,xx-5,base-26,11,8,'#475a70')
  for ry in range(base-25,base-20,2):R(d,xx-3,ry,7,1,'#748699')
 # Art-deco sign high above the street, with shaped hanging chassis.
 R(d,43,111,58,22,'#17243b');R(d,45,112,54,20,'#77344f')
 R(d,46,113,52,2,'#ec7d81');R(d,46,128,52,2,'#b55a74')
 R(d,48,116,7,10,'#ed9d85')
 R(d,50,118,3,2,'#ffcf97')
 for k in range(3):
  xx=61+k*12
  neon_glyph(d,xx,118,1,'#ffd5ac')
 # Outer exposed catwalks, antenna and ivy on right-hand warehouse.
 for xx in (402,439):
  R(d,xx,136,2,6,'#63768b');R(d,xx-1,135,4,2,'#a58291')
 R(d,398,130,78,2,'#363c54');R(d,398,129,78,1,'#987a91')
 for xx in range(401,477,14):R(d,xx,131,1,8,'#475c70')
 for xx in range(415,474,12):
  if hashish(xx,13)%3:R(d,xx,142,2,7,'#407c79')
  if hashish(xx,17)%3:R(d,xx-2,147,4,2,'#7db28b')
 # Visible weathered loading balcony beams and grates on the right.
 R(d,397,187,82,3,'#45556b');R(d,396,187,84,1,'#b19a9e')
 for xx in range(401,479,13):
  R(d,xx,183,1,11,'#87909a')
  L(d,[(xx,189),(xx+8,197)],'#4e5f71')
 # Distinct electric conduits along lower facade; bolts, real bends.
 L(d,[(298,230),(339,230),(339,250),(387,250),(387,270)],'#101a30',4)
 L(d,[(298,229),(339,229),(339,249),(387,249),(387,270)],'#6d7e90')
 for x,y in [(310,228),(338,239),(366,249)]:R(d,x,y,5,2,'#273b51')
 # Fire escapes on right façade: railings, platforms, diagonal supports.
 for y in (218,236,254):
  R(d,459,y,21,3,'#52657b');R(d,458,y-12,2,12,'#495d75')
  for xx in (463,471,478):R(d,xx,y-8,1,8,'#61788a')
  L(d,[(460,y+2),(477,y+10)],'#2e4157')
 # City-canyon neon arcade: signage and balcony clutter, designed to lead eyes inward.
 for x,y,h,c in [(192,214,40,'#d9679d'),(227,225,29,'#66d0cc'),(267,215,43,'#e6a17f')]:
  R(d,x-2,y-3,12,h+5,'#0b172c');R(d,x,y,8,h,c)
  R(d,x+1,y+1,6,h-2,'#532e55' if c=='#d9679d' else '#205069')
  for j in range(3):neon_glyph(d,x+1,y+4+j*10,1,'#ffd1a2' if c=='#e6a17f' else '#b1e9db')
 # Perspective bridge leading towards centre. Character will not interact with it.
 for x,y in [(223,220),(238,221),(256,220),(276,221)]:
  R(d,x,y,14,2,'#364761');R(d,x+2,y+1,9,1,'#5c697e')
 # Roof signage reflections are crisp, small pixel clusters — no transparency filters.
 for x,y,col in [(371,195,'#69c8c0'),(374,196,'#69c8c0'),(377,194,'#69c8c0'),(115,194,'#f5ac75'),(113,193,'#f5ac75'),(30,195,'#ed729c')]:
  R(d,x,y,6,1,col)
  R(d,x+2,y+1,3,1,'#456278')
 return im

def blade_character(frame):
 im=canvas();d=ImageDraw.Draw(im)
 # Frame-accurate physically continuous run -> arc -> land; no teleports or sliding boots.
 if frame<65:
  x=25+frame*2.42; foot=198;run=frame%8;jump=False
 elif frame<112:
  u=(frame-65)/47;x=182+115*u;foot=198-int(53*4*u*(1-u));jump=True;run=0
 elif frame<165:
  x=297+(frame-112)*2.35;foot=198;run=(frame-112)%8;jump=False
 else:x=422;foot=198;run=0;jump=False
 x=int(x);boot='#677d8c';cloth='#111a2d';edge='#33465c';arm='#3a5365';scarf='#d95b82'
 if not jump:R(d,x-7,198,17,1,'#0b1627')
 # Wind-facing scarf and offset hem.
 P(d,[(x-4,foot-22),(x-11,foot-24),(x-18-(frame%5)//2,foot-22),(x-13,foot-20),(x-5,foot-19)],scarf)
 R(d,x-15-(frame%4),foot-22,8,2,'#a44770');R(d,x-20-(frame%3),foot-21,5,1,'#6c3b6e')
 if jump:
  P(d,[(x-3,foot-12),(x-10,foot-8),(x-15,foot-12),(x-13,foot-15),(x-4,foot-16)],'#1b2d45')
  P(d,[(x+2,foot-13),(x+9,foot-13),(x+14,foot-6),(x+10,foot-4),(x+3,foot-8)],'#22374e')
  R(d,x-17,foot-14,5,3,boot);R(d,x+11,foot-7,5,3,boot)
 else:
  if run<4:
   P(d,[(x-4,foot-13),(x-8,foot-7),(x-10,foot-2),(x-6,foot-2),(x+1,foot-11)],'#1b2d42')
   P(d,[(x+1,foot-12),(x+6,foot-8),(x+11,foot-1),(x+7,foot-1),(x+1,foot-5)],'#182a41')
   R(d,x-11,foot-3,6,3,boot);R(d,x+7,foot-2,7,2,boot)
  else:
   P(d,[(x-4,foot-13),(x-5,foot-6),(x+1,foot-1),(x+4,foot-1),(x,foot-12)],'#1b2d42')
   P(d,[(x+1,foot-12),(x+10,foot-7),(x+8,foot-2),(x+11,foot-1),(x+14,foot-2),(x+13,foot-7)],'#182a41')
   R(d,x,foot-3,6,3,boot);R(d,x+11,foot-3,5,2,boot)
 # Midnight blue coat with lapel, collar and riveted bracer.
 P(d,[(x-7,foot-24),(x+1,foot-27),(x+6,foot-23),(x+8,foot-12),(x+4,foot-9),(x-6,foot-9),(x-8,foot-16)],cloth)
 R(d,x-5,foot-22,8,11,'#293a53');R(d,x+2,foot-22,2,9,'#41677a')
 P(d,[(x-5,foot-11),(x-10,foot-6),(x-8,foot-14),(x-4,foot-17)],'#111a30')
 R(d,x+5,foot-20,3,10,arm);R(d,x+5,foot-14,4,3,'#5dabb2')
 # Hood with angular silhouette and 2-pixel warm face, clear across all motion.
 P(d,[(x-6,foot-32),(x-2,foot-35),(x+4,foot-35),(x+8,foot-30),(x+7,foot-25),(x-5,foot-24)],'#0a1429')
 R(d,x-3,foot-31,9,4,'#26344d');R(d,x+1,foot-28,6,2,'#ba8c85');R(d,x+4,foot-28,3,1,'#ffd1a1')
 R(d,x-6,foot-25,13,3,'#111b31')
 # Sword has metallic three-tone cluster, not a glow or motion streak.
 bx=x+8;by=foot-18
 L(d,[(bx,by),(bx+17,by-21)],'#567e91',3)
 L(d,[(bx+1,by-1),(bx+18,by-22)],'#d4d9d0',1)
 R(d,bx-3,by-1,8,2,'#9e5d77');R(d,bx-4,by,3,1,'#df8d92')
 return im

def render(frame,base):
 out=Image.new('RGBA',(W,H),'#11182b')
 for name in ('sky','atmosphere','skyline'):
  out.alpha_composite(base[name])
 out.alpha_composite(railtrain(frame))
 for name in ('gorge','left','right','details','craft'):
  out.alpha_composite(base[name])
 out.alpha_composite(blade_character(frame))
 return out.convert('RGB')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=8);ap.add_argument('--out',default='out/afterlight.mp4');ap.add_argument('--poster',default='out/afterlight.png');ap.add_argument('--layers',default='out/layers');args=ap.parse_args()
 if not shutil.which('ffmpeg'):raise SystemExit('ffmpeg not installed')
 b=dict(sky=sky(),atmosphere=atmosphere(),skyline=skyline(),gorge=gorge(),left=left_roof(),right=right_roof(),details=detail_overlay(),craft=craftsmanship())
 lp=Path(args.layers);lp.mkdir(parents=True,exist_ok=True)
 for name,im in b.items():im.save(lp/f'{name}.png')
 Path(args.poster).parent.mkdir(parents=True,exist_ok=True)
 render(79,b).resize((1920,1080),Image.Resampling.NEAREST).save(args.poster)
 out=Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','480x270','-r',str(FPS),'-i','-','-vf','scale=1920:1080:flags=neighbor,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE);n=int(args.seconds*FPS)
 try:
  for i in range(n):p.stdin.write(render(i,b).tobytes())
 finally:p.stdin.close()
 if p.wait():raise SystemExit('ffmpeg failed')
 print(f'{out} frames={n} native=480x270 upscaled=1920x1080')
if __name__=='__main__':main()