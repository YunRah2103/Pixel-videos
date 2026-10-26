#!/usr/bin/env python3
"""Original, reproducible, pixel-cluster illustration toolkit for Pixel Garage 2.5D.
No external sprite or game artwork is sampled. All shapes are drawn at native pixel resolution.
"""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import random,math
R=random.Random(20261026)
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'godot'/'assets'; OUT.mkdir(parents=True,exist_ok=True)
C={'outline':'#182132','deep':'#26364b','metal':'#e7f5e8','white':'#f4e9d0','shade':'#a5bac1','cyan':'#71c4c7','window':'#183948','glass':'#376b75','lime':'#d3f46b','green':'#5d947d','red':'#ed6957','gold':'#fbbd67','wheel':'#151c29','tire':'#26323a','rim':'#90a8b2','shine':'#fff6ce','shadow':'#17232f'}
def rgb(k):return C.get(k,k)
def P(d,pts,c): d.polygon(pts,fill=rgb(c))
def L(d,pts,c,w=1):d.line(pts,fill=rgb(c),width=w,joint='curve')
def E(d,bb,c,w=1):d.ellipse(bb,fill=rgb(c),width=w)
def rect(d,bb,c):d.rectangle(bb,fill=rgb(c))
def save(im, n):im.save(OUT/n)
def spoke_wheel(d,x,y,r=19,phase=0):
 E(d,(x-r-2,y-r-2,x+r+2,y+r+2),'outline');E(d,(x-r,y-r,x+r,y+r),'wheel')
 for a in [phase,45+phase,90+phase,135+phase]:
  th=math.radians(a); dx=int((r-4)*math.cos(th));dy=int((r-4)*math.sin(th))
  L(d,[(x-dx,y-dy),(x+dx,y+dy)],'rim',3)
 E(d,(x-r+5,y-r+5,x+r-5,y+r-5),'tire');E(d,(x-7,y-7,x+7,y+7),'rim');E(d,(x-3,y-3,x+3,y+3),'deep')
 for j in range(9):
  a=math.radians(j*40);px=x+int((r-1)*math.cos(a));py=y+int((r-1)*math.sin(a));rect(d,(px,py,px+2,py+2),'shadow')

def accents(d,pts):
 P(d,pts,'red')

def side(phase=0):
 im=Image.new('RGBA',(238,136));d=ImageDraw.Draw(im)
 E(d,(20,109,221,128),'#111c2955')
 # Roof, hatch, bonnet, bumpers; asymmetrical crafted silhouette
 P(d,[(19,80),(31,73),(68,68),(89,44),(103,31),(153,28),(173,35),(191,57),(214,68),(223,76),(220,98),(207,103),(33,103),(18,97)],'outline')
 P(d,[(24,80),(37,74),(70,72),(92,46),(105,35),(150,33),(171,38),(187,60),(207,69),(219,78),(215,96),(28,96)],'metal')
 P(d,[(33,81),(76,75),(91,49),(103,37),(152,35),(168,42),(181,64),(193,74)],'shade')
 # dark canopy with outlined pillars
 P(d,[(89,68),(104,38),(147,36),(165,44),(183,67)],'outline')
 P(d,[(94,66),(107,41),(126,39),(126,67)],'window');P(d,[(130,40),(148,39),(163,46),(177,66),(130,67)],'glass')
 L(d,[(109,43),(125,42)],'cyan',2);L(d,[(137,43),(158,48)],'cyan',2)
 P(d,[(127,39),(133,39),(133,67),(127,67)],'outline')
 P(d,[(189,71),(217,79),(216,90),(193,88)],'deep')
 # livery triangles deliberately punchy
 P(d,[(31,80),(92,79),(113,86),(64,96),(32,95)],'green')
 P(d,[(83,75),(152,72),(178,88),(126,88)],'lime')
 P(d,[(143,74),(174,69),(190,84),(165,89)],'red')
 P(d,[(30,80),(56,77),(44,92),(28,91)],'cyan')
 L(d,[(32,73),(72,69),(92,44),(111,36),(155,36)],'shine',2)
 L(d,[(40,97),(211,97)],'deep',3)
 # spoiler and air scoop
 P(d,[(166,28),(203,31),(204,36),(169,35)],'outline');P(d,[(173,30),(199,32)],'lime')
 P(d,[(131,27),(151,26),(156,31),(134,31)],'outline')
 # door lines / handles
 L(d,[(128,70),(127,94)],'deep');L(d,[(173,71),(174,95)],'deep')
 rect(d,(144,72,156,75),'outline');rect(d,(144,72,154,72),'shine')
 P(d,[(93,58),(83,54),(79,61),(90,67)],'outline');P(d,[(85,57),(79,59),(87,62)],'green')
 # wheel arches lower body, wheels on top
 for x in (67,182):
  E(d,(x-26,76,x+26,125),'outline');E(d,(x-22,81,x+22,126),'deep');spoke_wheel(d,x,105,18,phase)
 # fenders and body chrome
 L(d,[(18,86),(32,83)],'red',4);rect(d,(209,79,221,86),'shine')
 P(d,[(22,95),(41,100),(44,105),(22,103)],'deep');P(d,[(207,100),(222,95),(220,104),(204,106)],'deep')
 # number placard and decals
 rect(d,(114,78,142,93),'white');rect(d,(116,80,140,91),'outline')
 d.text((123,80),'07',fill=rgb('lime'))
 rect(d,(150,83,161,85),'white');rect(d,(47,88,55,89),'gold')
 return im

def quarter(rear=True,phase=0):
 im=Image.new('RGBA',(228,154));d=ImageDraw.Draw(im)
 # rear near left, narrowing in perspective toward distant nose at right
 E(d,(21,121,213,139),'#111c29')
 if rear:
  P(d,[(18,79),(43,61),(97,48),(155,52),(202,70),(216,86),(210,112),(145,124),(43,116),(18,103)],'outline')
  P(d,[(23,82),(47,65),(96,53),(152,57),(199,73),(211,89),(205,107),(143,117),(42,111),(23,101)],'metal')
  # curved roofline hatchback, roof scoop, tall upright back
  P(d,[(43,66),(67,39),(98,29),(142,31),(173,54),(153,65),(86,73)],'outline')
  P(d,[(49,65),(71,42),(101,34),(140,36),(163,55),(148,63),(83,70)],'shade')
  P(d,[(46,72),(70,44),(100,36),(106,65)],'window')
  P(d,[(111,37),(137,39),(158,55),(118,66)],'glass')
  L(d,[(71,46),(95,39)],'cyan',2);L(d,[(121,40),(138,42)],'cyan',2)
  P(d,[(42,60),(34,58),(37,49),(116,31),(149,35),(155,42),(79,53)],'outline')
  P(d,[(39,55),(117,35),(145,38)],'lime')
  P(d,[(106,29),(122,27),(130,32),(113,34)],'outline')
  # rear window/hatch + tall angular rear lights
  P(d,[(24,81),(44,70),(91,75),(98,104),(42,107),(24,102)],'deep')
  P(d,[(35,78),(45,74),(88,78),(92,93),(43,96)],'glass')
  L(d,[(43,79),(84,82)],'cyan',2)
  P(d,[(24,83),(31,80),(35,98),(24,100)],'red');P(d,[(91,82),(98,83),(104,104),(96,105)],'red')
  rect(d,(50,99,78,107),'white');rect(d,(53,101,76,106),'outline')
  # strong diagonal side livery
  P(d,[(104,78),(162,66),(195,77),(160,96),(115,103)],'lime')
  P(d,[(103,103),(148,94),(192,96),(166,111),(101,113)],'green')
  P(d,[(161,66),(192,73),(195,81),(174,84)],'red')
  L(d,[(113,70),(152,63),(191,75)],'shine',2)
  # side glass door frame and mirror
  L(d,[(115,69),(130,96)],'outline');rect(d,(150,91,160,94),'outline')
  P(d,[(156,64),(159,56),(167,59),(170,66)],'deep')
  # wheels perspective
  E(d,(36,97,90,141),'outline');E(d,(134,105,176,141),'outline')
  spoke_wheel(d,65,119,18,phase);spoke_wheel(d,155,120,15,phase)
  P(d,[(26,109),(104,115),(107,121),(31,117)],'deep')
  rect(d,(36,107,45,112),'red');rect(d,(96,108,110,112),'gold')
  rect(d,(28,110,43,116),'outline');rect(d,(37,113,49,117),'deep') # exhaust
 else:
  # front three-quarter uses consistent colour / geometry with opposing nose
  P(d,[(17,90),(48,71),(108,58),(166,56),(206,72),(219,91),(212,108),(150,121),(42,119),(17,105)],'outline')
  P(d,[(22,91),(51,76),(108,63),(163,61),(201,77),(214,92),(207,104),(150,115),(43,113),(22,103)],'metal')
  P(d,[(51,76),(75,43),(108,30),(150,32),(178,54),(164,72),(96,78)],'outline')
  P(d,[(57,74),(79,46),(110,35),(148,37),(170,55),(158,67),(99,74)],'shade')
  P(d,[(77,49),(108,39),(113,67),(62,74)],'glass');P(d,[(116,38),(147,41),(164,56),(160,68),(120,66)],'window')
  L(d,[(79,50),(106,41)],'cyan',2);L(d,[(126,42),(150,45)],'cyan',2)
  P(d,[(32,79),(49,70),(94,66),(100,95),(40,102)],'white')
  P(d,[(26,85),(45,80),(92,79),(101,100),(32,102)],'deep')
  P(d,[(31,85),(47,81),(56,88),(33,92)],'shine');P(d,[(83,85),(95,81),(100,94),(90,93)],'shine')
  P(d,[(40,95),(92,92),(87,100),(42,101)],'outline')
  # racing stripes continuing onto nose and side
  P(d,[(105,80),(174,65),(205,80),(179,93),(121,100)],'lime')
  P(d,[(109,98),(168,89),(205,98),(177,111),(116,113)],'green')
  P(d,[(160,70),(179,67),(196,77),(168,83)],'red')
  P(d,[(139,30),(153,30),(160,35),(145,35)],'outline')
  P(d,[(151,45),(180,45),(196,52),(184,56)],'outline')
  for x,y,r in [(62,119,18),(167,119,15)]:
   E(d,(x-r-7,y-r-18,x+r+7,y+r+4),'outline');spoke_wheel(d,x,y,r,phase)
  rect(d,(31,106,93,111),'deep');rect(d,(100,80,113,85),'outline')
  rect(d,(157,92,170,95),'outline')
 return im

def face(rear=True):
 im=Image.new('RGBA',(198,154));d=ImageDraw.Draw(im)
 P(d,[(16,77),(33,60),(56,39),(140,39),(166,60),(182,77),(181,115),(17,115)],'outline')
 P(d,[(21,79),(37,64),(61,44),(137,44),(160,65),(177,80),(174,108),(24,108)],'metal')
 P(d,[(48,69),(60,45),(136,45),(149,69)],'deep')
 P(d,[(54,64),(65,48),(133,48),(143,64)],'glass')
 L(d,[(64,50),(123,50)],'cyan',2)
 P(d,[(18,112),(39,112),(43,126),(18,126)],'wheel');P(d,[(156,112),(180,112),(180,126),(153,126)],'wheel')
 if rear:
  P(d,[(27,80),(171,80),(170,109),(29,109)],'deep')
  P(d,[(33,82),(47,82),(50,105),(33,105)],'red');P(d,[(149,82),(165,82),(165,105),(146,105)],'red')
  rect(d,(73,100,123,108),'white');rect(d,(78,102,118,106),'outline')
  P(d,[(29,113),(168,113),(166,120),(32,120)],'outline');rect(d,(140,117,154,122),'deep')
 else:
  P(d,[(25,80),(173,80),(168,107),(29,107)],'deep')
  P(d,[(28,82),(59,82),(70,93),(31,96)],'shine');P(d,[(139,82),(170,82),(166,96),(129,93)],'shine')
  P(d,[(66,95),(133,95),(125,106),(74,106)],'outline')
  for k in range(5):L(d,[(75,98+k*2),(125,98+k*2)],'shade')
  P(d,[(88,57),(110,57),(107,78),(91,78)],'lime')
 P(d,[(59,42),(62,33),(85,30),(118,30),(138,34),(141,42)],'outline')
 P(d,[(83,31),(112,31),(115,35),(81,35)],'lime')
 L(d,[(32,77),(55,52),(142,52),(166,77)],'shine',2)
 return im

def draw_tree(seed=0):
 r=random.Random(200+seed);im=Image.new('RGBA',(112,192));d=ImageDraw.Draw(im)
 cx=56+r.randint(-3,3);trunk=r.randint(18,26);h=r.randint(151,174)
 rect(d,(cx-5,180-trunk,cx+5,190),'#4b4f49')
 depths=[('#193f4b',67,153),('#265a5b',62,126),('#346c61',55,103),('#4e8365',48,78),('#76a17b',38,54)]
 for k,(color,half,level) in enumerate(depths):
  ybase=180-k*18; peak=max(9,187-h+k*9)
  for tier in range(3):
   ht=peak+tier*18; spread=int(half*(0.54+tier*0.19))
   P(d,[(cx,ht),(cx-spread, ybase-17+tier*7),(cx-spread+8,ybase-18+tier*7),(cx-spread-4,ybase-6+tier*7),(cx+spread+4,ybase-6+tier*7),(cx+spread-10,ybase-18+tier*7)],color)
  # left pixel cluster boughs
  for m in range(12):
   y=r.randint(peak+15,min(ybase,186));wid=max(5,int((y-peak)/max(1,ybase-peak)*half))
   x=cx+r.randint(-wid,wid)
   if r.random()<0.72:rect(d,(x,y,x+r.randint(3,8),y+2),r.choice(['#679984','#8cba8c','#306a66']))
 # pixel highlights, trunk shards
 rect(d,(cx-1,154,cx+1,176),'#755e51')
 return im

def bush(seed):
 r=random.Random(seed);im=Image.new('RGBA',(88,54));d=ImageDraw.Draw(im)
 for j in range(21):
  x=r.randint(5,80);y=r.randint(14,37);rr=r.randint(5,13)
  E(d,(x-rr,y-rr,x+rr,y+rr),r.choice(['#254f50','#306d59','#417d5e','#71966b']))
 for j in range(35):
  x=r.randint(8,80);y=r.randint(10,35);rect(d,(x,y,x+3,y+2),r.choice(['#aec288','#dbe3a5','#5e996a']))
 for j in range(4):
  x=r.randint(5,80);y=r.randint(24,45);rect(d,(x,y,x+2,y+3),r.choice(['#efc785','#fcf0ba','#ee9c7d']))
 return im

def mountains():
 im=Image.new('RGBA',(720,240));d=ImageDraw.Draw(im)
 # handcrafted layered hill silhouettes that can billboard far behind actual trees
 P(d,[(0,160),(45,135),(80,146),(135,79),(164,100),(205,64),(259,121),(320,86),(368,105),(410,62),(457,112),(505,80),(553,121),(609,73),(661,123),(720,88),(720,240),(0,240)],'#658b90')
 P(d,[(0,160),(49,142),(80,153),(135,93),(160,110),(205,80),(260,139),(319,107),(364,124),(410,83),(456,127),(508,95),(554,137),(612,87),(660,142),(720,106),(720,240),(0,240)],'#789e96')
 P(d,[(0,201),(61,163),(95,173),(153,145),(213,171),(282,137),(346,173),(400,141),(475,179),(542,146),(607,163),(673,138),(720,171),(720,240),(0,240)],'#3f7775')
 P(d,[(0,211),(80,180),(120,186),(194,170),(244,187),(302,167),(376,194),(437,171),(501,194),(571,173),(642,187),(720,158),(720,240),(0,240)],'#376c69')
 for i in range(145):
  x=R.randrange(720);y=R.randrange(132,228)
  if im.getpixel((x,y))[3]:rect(d,(x,y,x+R.randrange(2,9),y+1),R.choice(['#4f8880','#9db3a0','#4e7772']))
 return im

def road():
 im=Image.new('RGBA',(256,512),'#83786b');d=ImageDraw.Draw(im)
 # Gravel is dense curated aggregates rather than post-process grain
 for i in range(5200):
  x=R.randrange(256);y=R.randrange(512);s=R.choices([1,2,3,4],[0.5,0.35,.12,.03])[0]
  color=R.choice(['#a3a091','#b9af90','#766c61','#5d6260','#a29580','#d0be99'])
  rect(d,(x,y,x+s,y+(1 if s<4 else 2)),color)
 for i in range(23):
  y=R.randrange(512)
  L(d,[(28,y),(29,y+R.randrange(8,24))],'#68645d',1)
  L(d,[(223,y),(224,y+R.randrange(8,24))],'#66645a',1)
 return im

def flame():
 im=Image.new('RGBA',(80,43));d=ImageDraw.Draw(im)
 P(d,[(72,20),(50,11),(59,5),(33,12),(18,10),(4,19),(26,23),(18,31),(43,29),(58,38),(51,26)],'#ed6949')
 P(d,[(61,20),(47,17),(48,12),(31,16),(20,15),(10,20),(30,23),(23,28),(41,25),(49,29),(46,24)],'#ffd06e')
 P(d,[(47,20),(31,18),(13,20),(32,23),(42,24)],'#fff4b4')
 for i in range(12):
  x=R.randrange(18,79);y=R.randrange(2,38);rect(d,(x,y,x+R.randrange(1,4),y+1),R.choice(['#ffbd5c','#fc7553','#ffebaa']))
 return im

def terrain():
 im=Image.new('RGBA',(128,128),'#345d54');d=ImageDraw.Draw(im)
 for i in range(900):
  x=R.randrange(128);y=R.randrange(128)
  col=R.choice(['#3e7059','#406854','#42775c','#638065','#54765d','#345452'])
  rect(d,(x,y,x+R.randrange(1,4),y+R.randrange(1,4)),col)
 return im

def title_text(txt):
 im=Image.new('RGBA',(345,36));d=ImageDraw.Draw(im)
 font=ImageFont.load_default()
 # thin deliberate dark backing / 2-tone text pixel edges
 d.text((9,9),txt,fill='#1a2c38',font=font,stroke_width=2,stroke_fill='#1a2c38')
 d.text((9,9),txt,fill='#f5f3da',font=font)
 return im

def main():
 for n,f in [('car_side.png',side()),('car_rear_34.png',quarter(True)),('car_front_34.png',quarter(False)),('car_rear.png',face(True)),('car_front.png',face(False))]:save(f,n)
 for phase in range(4):
  spin=phase*22.5
  save(side(spin),f'car_side_{phase}.png')
  save(quarter(True,spin),f'car_rear_34_{phase}.png')
  save(quarter(False,spin),f'car_front_34_{phase}.png')
 for i in range(6):save(draw_tree(i),f'pine_{i}.png')
 for i in range(5):save(bush(700+i),f'bush_{i}.png')
 for name,obj in [('mountains.png',mountains()),('road.png',road()),('flame.png',flame()),('ground.png',terrain()),('caption_flame.png',title_text('UNBURNED FUEL + HOT EXHAUST + OXYGEN')),('caption_antilag.png',title_text('ANTI-LAG CAN ADD MORE FUEL'))]:save(obj,name)
 from art_v4 import upgrade
 upgrade(OUT, side, quarter, face)
 # alpha transparent strip will be used as sprite-board flipbook too
 print('Created',len(list(OUT.glob('*.png'))),'original nearest-neighbour pixel-art assets in',OUT)
if __name__=='__main__':main()