#!/usr/bin/env python3
"""VERDANT DRIVE / standalone hand-authored pixel-scene and 300-frame animation.
Original art. Drawn natively at 360x640; no antialiasing, sprites filtered NEAREST.
Requires Pillow and ffmpeg. Run: python render.py --still, or python render.py --render.
"""
from PIL import Image, ImageDraw
import argparse, math, random, subprocess, os
from pathlib import Path

W,H=360,640
HERE=Path(__file__).resolve().parent
OUT=HERE/'output'; OUT.mkdir(exist_ok=True)
R=random.Random(316)
P={
 'sky0':'#a4d8cf','sky1':'#b3ded1','sky2':'#c9e7c9','sky3':'#dce9c1',
 'cream':'#fff0cd','cloudShade':'#d9dfb6','sun':'#fce7a2',
 'hillFar':'#9abdb0','hillFarHi':'#bdd6b1','hillMid':'#709f83','hillDark':'#548c76',
 'meadow':'#8bb879','meadowLight':'#bdd18a','meadowDark':'#6b9c69',
 'firDark':'#3f725f','oakDark':'#275b50','oakMid':'#3c8062','oakLight':'#6cab75',
 'oakBright':'#94c97e','oakSun':'#b8d98a','branch':'#503f3a',
 'verge':'#4e8767','vergeDeep':'#2d624f','vergeLight':'#8eb67b',
 'asphalt':'#46505e','asphalt2':'#3d4654','asphaltLight':'#66707a',
 'mark':'#f0da9b','roadEdge':'#c0bba0','edgeShadow':'#2b4a4c',
 'paintDark':'#8a5648','paintShadow':'#b8754d','paintBase':'#e8ac68',
 'paintHi':'#f9d18b','paintSun':'#ffe1a1','outline':'#283d44',
 'glass':'#2f6670','glassDeep':'#1d4254','glassHi':'#8dc6bb','glassSpark':'#d5e7c5',
 'rubber':'#24323e','rubberHi':'#4e5661','rim':'#d8dfd0','rimDark':'#7d9a9a'
}

def poly(d, points, fill): d.polygon([(int(x),int(y)) for x,y in points], fill=fill)
def rect(d,box,fill): d.rectangle(tuple(map(int,box)),fill=fill)
def line(d, pts, fill, width=1): d.line([(int(x),int(y)) for x,y in pts],fill=fill,width=width,joint='curve')

def cloud_sprite():
 im=Image.new('RGBA',(122,53)); d=ImageDraw.Draw(im)
 poly(d,[(5,35),(14,35),(14,27),(28,27),(28,20),(46,20),(46,13),(58,13),(58,6),(72,6),(72,10),(80,10),(80,18),(94,18),(94,25),(110,25),(110,34),(119,34),(119,43),(5,43)],P['cream'])
 rect(d,(5,41,119,45),P['cloudShade']);rect(d,(15,45,106,46),'#ecdfb9')
 rect(d,(34,24,55,25),'#fff8df');rect(d,(62,12,70,14),'#fff8df')
 return im
CLOUD=cloud_sprite()

def fir_sprite():
 im=Image.new('RGBA',(47,86));d=ImageDraw.Draw(im)
 rect(d,(21,56,24,85),'#695642')
 poly(d,[(24,3),(18,20),(21,20),(12,35),(17,35),(6,50),(12,50),(3,64),(14,64),(10,72),(38,72),(32,63),(43,63),(32,47),(37,47),(28,33),(32,33),(26,17),(27,17)],'#3b7060')
 poly(d,[(23,12),(17,31),(21,31),(11,52),(17,52),(12,65),(23,64),(22,42),(28,41)],'#538f6a')
 for a,b in [((15,40),(20,42)),((11,55),(19,55)),((23,27),(26,29)),((20,62),(31,63))]: line(d,[a,b],'#80ad79',2)
 return im
FIR=fir_sprite()

def oak_sprite(variant=0):
 """Two asymmetrical, manually shaped oak canopies, with individually placed cluster paths."""
 im=Image.new('RGBA',(164,204));d=ImageDraw.Draw(im)
 # sharply shaped roots and irregular trunk behind foliage
 poly(d,[(75,195),(76,130),(67,116),(53,99),(51,92),(57,90),(81,120),(87,141),(91,112),(106,92),(112,95),(97,123),(92,148),(93,194)],'#594638')
 poly(d,[(82,193),(81,129),(77,123),(76,184)],'#80664b')
 poly(d,[(86,137),(92,120),(102,108),(94,122)],'#8a704d')
 poly(d,[(78,193),(73,197),(61,197),(62,200),(96,200),(103,196),(95,194)],'#4b493a')
 if variant==0:
  crown=[(17,102),(9,97),(10,83),(3,82),(6,63),(16,60),(17,48),(30,44),(35,31),(49,29),(52,22),(68,22),(71,13),(87,15),(93,23),(112,20),(122,29),(132,29),(137,40),(150,45),(151,56),(158,63),(155,81),(161,88),(154,101),(145,101),(143,111),(129,114),(125,123),(108,121),(103,134),(87,133),(81,139),(68,132),(55,135),(49,126),(34,122),(31,114),(19,114)]
 else:
  crown=[(3,83),(7,69),(17,64),(14,50),(27,46),(30,32),(45,26),(52,26),(61,17),(80,18),(89,11),(99,20),(117,19),(124,30),(139,30),(146,41),(151,53),(160,55),(157,72),(161,79),(153,93),(158,105),(146,114),(131,112),(128,126),(111,130),(98,128),(88,140),(70,135),(64,128),(49,133),(36,121),(22,119),(20,106),(7,101)]
 poly(d,crown,P['oakDark'])
 # main facets are hand-drawn shapes rather than cloned circles or noisy stipples
 facets=[
 ([(13,72),(22,60),(22,50),(39,46),(46,34),(62,31),(76,37),(69,48),(52,52),(47,64),(28,65),(27,76)],'oakMid'),
 ([(75,33),(86,24),(101,30),(112,27),(123,36),(124,46),(143,48),(147,59),(130,63),(123,75),(103,67),(92,77),(76,65)],'oakMid'),
 ([(24,81),(43,76),(53,68),(73,72),(76,84),(89,77),(106,81),(119,74),(137,81),(148,86),(142,99),(127,94),(116,108),(99,103),(87,117),(75,110),(59,119),(51,107),(36,107),(29,99),(15,96)],'oakMid'),
 ([(27,55),(32,45),(48,43),(52,32),(62,32),(70,40),(55,46),(52,54),(44,55),(40,66),(27,66)],'oakLight'),
 ([(85,32),(92,25),(102,36),(115,34),(128,48),(115,49),(112,55),(93,53),(86,62),(74,58),(78,42)],'oakLight'),
 ([(9,76),(19,66),(27,67),(30,76),(43,72),(46,87),(30,89),(23,99),(13,93)],'oakLight'),
 ([(55,71),(72,62),(85,75),(81,86),(98,84),(111,92),(108,106),(89,107),(83,120),(67,114),(64,103),(51,99)],'oakLight'),
 ([(119,66),(135,62),(145,67),(151,79),(138,82),(145,91),(134,100),(125,93),(113,92),(113,81)],'oakLight'),
 ([(38,38),(44,33),(58,33),(57,39),(49,39),(44,49),(33,52)],'oakBright'),
 ([(94,30),(103,29),(104,37),(116,38),(119,46),(105,45),(99,51),(90,47)],'oakBright'),
 ([(20,70),(29,65),(36,68),(30,79),(15,81)],'oakBright'),
 ([(58,80),(67,74),(77,76),(76,86),(63,92),(52,88)],'oakBright'),
 ([(111,78),(124,69),(137,74),(134,83),(120,86)],'oakBright'),
 ([(39,35),(49,31),(56,33),(52,38),(42,41)],'oakSun'),
 ([(97,31),(105,32),(112,39),(102,40)],'oakSun'),
 ([(22,72),(29,69),(32,70),(27,76)],'oakSun'),
 ([(63,80),(70,76),(76,79),(70,86),(62,85)],'oakSun'),
 ([(125,74),(133,74),(137,78),(130,81)],'oakSun'),
 # negative gaps and shadow pockets add internal structure
 ([(35,90),(42,85),(48,88),(43,96),(37,98)],'oakDark'),
 ([(89,94),(96,88),(103,91),(100,97)],'oakDark'),
 ([(117,105),(121,98),(127,98),(128,106)],'oakDark'),
 ([(62,120),(66,110),(72,111),(75,124)],'oakDark'),
 ]
 for pts,key in facets:poly(d,pts,P[key])
 # small intentional leaf clusters (not random scatter), mostly sun-facing upper left
 for x,y in [(45,34),(66,38),(24,70),(17,84),(58,76),(75,53),(92,36),(114,45),(132,71),(102,82),(42,75),(56,95),(72,108),(109,105),(139,88)]:
  rect(d,(x,y,x+4,y+2),P['oakBright'])
  rect(d,(x+1,y+3,x+5,y+4),P['oakLight'])
 if variant==1:
  poly(d,[(108,114),(118,115),(122,121),(114,129),(103,124)],P['oakLight'])
  rect(d,(20,85,32,88),P['oakBright'])
 return im
OAKS=[oak_sprite(0),oak_sprite(1)]

def bush_sprite(variant=0):
 im=Image.new('RGBA',(84,43));d=ImageDraw.Draw(im)
 poly(d,[(0,38),(3,29),(11,27),(12,18),(22,16),(26,8),(36,12),(42,5),(52,8),(58,16),(70,12),(77,19),(82,26),(84,42),(0,42)],P['oakDark'])
 poly(d,[(7,34),(17,29),(17,21),(28,20),(32,14),(43,17),(47,10),(56,18),(71,19),(75,30),(64,30),(56,35),(40,32),(30,38)],P['oakMid'])
 for x,y in [(14,27),(22,20),(31,22),(42,15),(57,21),(67,24),(34,30),(49,26)]:
  poly(d,[(x,y),(x+7,y-2),(x+10,y+3),(x+4,y+5)],P['oakLight'])
  rect(d,(x+2,y,x+5,y+1),P['oakBright'])
 return im
BUSH=bush_sprite()

def wheel(draw,cx,cy,a):
 # tire silhouette, dark cavity, faceted tyre edge
 draw.ellipse((cx-23,cy-23,cx+23,cy+23),fill='#23313a')
 draw.ellipse((cx-20,cy-20,cx+20,cy+20),fill=P['rubber'])
 for n in range(12):
  t=n*math.tau/12
  px=cx+int(20.5*math.cos(t));py=cy+int(20.5*math.sin(t))
  rect(draw,(px-2,py-1,px+1,py+1),'#38444c')
 draw.ellipse((cx-15,cy-15,cx+15,cy+15),fill=P['rimDark'])
 draw.ellipse((cx-13,cy-13,cx+13,cy+13),fill=P['rim'])
 draw.ellipse((cx-10,cy-10,cx+10,cy+10),fill='#9cbbb4')
 for k in range(6):
  a1=a+math.tau*k/6
  x1=cx+int(5*math.cos(a1));y1=cy+int(5*math.sin(a1))
  x2=cx+int(11*math.cos(a1));y2=cy+int(11*math.sin(a1))
  line(draw,[(x1,y1),(x2,y2)],'#e3e6d5',3)
  rect(draw,(x2-1,y2-1,x2+1,y2+1),'#f0e9d2')
 draw.ellipse((cx-4,cy-4,cx+4,cy+4),fill='#394e54')
 draw.ellipse((cx-2,cy-2,cx+2,cy+2),fill='#e4dbb9')

def car_sprite(a=0.):
 """Drawn as a unique side-profile hot hatch with faceted metal/glazing."""
 im=Image.new('RGBA',(274,132)); d=ImageDraw.Draw(im)
 # ground cast shadow: offset dark teal
 d.ellipse((6,105,267,130),fill=(28,53,52,78))
 # body black silhouette, including rear hatch, roof and front bonnet
 poly(d,[(7,72),(14,64),(28,62),(48,31),(61,23),(149,20),(162,23),(188,56),(208,68),(240,70),(254,77),(260,89),(263,106),(253,110),(18,111),(7,106)],P['outline'])
 # rear boot/hatch step, greenhouse and primary painted profile
 poly(d,[(13,76),(20,67),(32,66),(53,34),(63,28),(149,25),(159,27),(183,61),(204,72),(240,75),(252,82),(255,102),(246,106),(23,107),(13,102)],P['paintBase'])
 # underside cool shadow and lower sill
 poly(d,[(19,93),(39,96),(180,94),(251,96),(253,103),(243,109),(27,110),(16,102)],P['paintShadow'])
 poly(d,[(22,101),(38,100),(236,101),(252,99),(248,107),(24,109)],P['paintDark'])
 # scalloped fender contour / wheel wells, drawn before tires
 for cx in (63,207):
  d.ellipse((cx-27,83,cx+27,134),fill=P['outline'])
 # body top extended past arch like pressed fenders
 poly(d,[(16,75),(25,69),(41,68),(55,35),(63,28),(146,26),(159,28),(181,61),(196,69),(237,75),(252,81),(255,88),(199,84),(178,76),(44,79),(15,83)],P['paintBase'])
 # broad golden sunlight across top roof + bonnet
 poly(d,[(53,34),(62,27),(149,25),(157,29),(157,33),(62,33),(49,49)],P['paintSun'])
 poly(d,[(189,71),(220,75),(244,78),(250,82),(214,81)],P['paintHi'])
 # upper greenhouse in dark paint, side windows individual irregular polygons
 poly(d,[(48,64),(62,35),(149,32),(158,35),(177,63),(175,69),(46,69)],P['outline'])
 # hatch quarter-light
 poly(d,[(54,61),(65,38),(90,37),(90,63),(53,64)],P['glassDeep'])
 poly(d,[(94,37),(145,36),(153,40),(168,62),(94,63)],P['glass'])
 # slanted windshield, subtle angled forward pillars
 poly(d,[(153,35),(161,41),(176,62),(183,65),(165,36)],P['glassDeep'])
 # warm window reflection drawn as intentionally stepped angular streaks
 poly(d,[(63,41),(72,39),(70,61),(57,61)],P['glassHi'])
 poly(d,[(99,38),(112,37),(97,61),(94,61)],'#589ba0')
 poly(d,[(135,37),(147,37),(159,55),(158,59),(143,47)],'#8dbdb2')
 poly(d,[(160,41),(167,51),(172,62),(169,61)],P['glassHi'])
 rect(d,(56,62,86,64),'#b9dbc4')
 # window lower chrome lip and B-pillar
 rect(d,(48,69,179,71),P['outline'])
 rect(d,(92,35,95,68),P['outline'])
 # actual panel separation: front and rear door arches / door hinge
 line(d,[(99,73),(97,98)],P['paintDark'],2)
 line(d,[(176,73),(175,98)],P['paintDark'],2)
 # door highlights: careful horizontal curves in pixel-cluster form
 line(d,[(33,79),(85,77),(156,78),(190,83),(233,86)],P['paintHi'],3)
 line(d,[(104,91),(169,92)],'#f4c181',2)
 line(d,[(108,96),(163,96)],'#c58952',1)
 rect(d,(106,77,121,80),P['outline']);rect(d,(109,77,119,78),P['paintSun'])
 rect(d,(59,76,74,79),P['outline']);rect(d,(61,76,72,77),P['paintSun'])
 # mirror sticking out of leading edge of driver window
 poly(d,[(177,65),(192,66),(197,71),(196,76),(183,74)],P['outline'])
 poly(d,[(183,66),(191,67),(194,70),(184,70)],P['paintHi'])
 # rear light cluster and front headlight both shaped not blocks
 poly(d,[(12,77),(20,70),(29,70),(26,83),(14,84)],'#a74b46')
 poly(d,[(14,77),(24,73),(23,78),(14,81)],'#f2a17b')
 poly(d,[(240,80),(250,83),(255,90),(245,91),(236,87)],'#f9e6b0')
 poly(d,[(242,82),(250,84),(251,87),(244,86)],'#ffffff')
 rect(d,(247,94,260,97),P['outline'])
 rect(d,(248,99,257,102),'#536770')
 # grille detail and bumper highlights
 line(d,[(231,93),(247,94)],P['paintDark'],2)
 line(d,[(39,88),(73,88)],'#e9b470',1)
 rect(d,(15,95,20,101),'#f1c48a')
 rect(d,(26,111,244,113),'#283c3c')
 # arch surfaces with thin clipped crescent fender highlights
 for cx in (63,207):
  d.arc((cx-27,82,cx+27,134),183,357,fill=P['paintHi'],width=3)
  d.arc((cx-25,84,cx+25,132),183,357,fill=P['paintDark'],width=2)
 wheel(d,63,105,a);wheel(d,207,105,a)
 # visible wheel top shadow and tiny rivet
 rect(d,(44,83,47,85),P['paintHi']);rect(d,(226,86,229,88),P['paintHi'])
 return im

def sky(draw,t):
 rect(draw,(0,0,W,H),P['sky0'])
 poly(draw,[(0,75),(60,74),(60,71),(200,71),(200,77),(360,74),(360,225),(0,225)],P['sky1'])
 poly(draw,[(0,154),(47,154),(47,150),(146,150),(146,156),(274,156),(274,153),(360,153),(360,240),(0,240)],P['sky2'])
 poly(draw,[(0,211),(160,212),(160,207),(288,207),(288,212),(360,212),(360,268),(0,268)],P['sky3'])
 # sun diffused cream circle at right edge; flat pixel steps, no gradient
 draw.ellipse((252,99,311,158),fill='#f2e9b5')
 draw.ellipse((259,106,305,152),fill=P['sun'])
 # soft block stepped rim fragments, kept minimal
 for x, y,scale in [(30,61,0.8),(233,39,0.55),(410,113,0.7),(122,109,0.50)]:
  px=int((x-t*0.2)%(W+165))-90
  if -115<px<W+2:
   cloud=CLOUD.resize((int(122*scale),int(53*scale)),resample=Image.Resampling.NEAREST)
   # compositing clouds elsewhere (Image.paste required) 
   yield (cloud,px,y)

def mountain(draw,t):
 dx=t*.25
 # two mountain horizons handmade stepped slopes; mirrored landscape strips shift slowly
 for k in range(-2,5):
  x=int(k*264-dx)-35
  high=8 if k%3==0 else -8 if k%3==1 else 2
  poly(draw,[(x,298),(x,281),(x+24,276),(x+32,265),(x+47,262),(x+58,247+high),(x+68,242+high),(x+77,242+high),(x+90,251+high),(x+105,267),(x+127,263),(x+143,273),(x+175,279),(x+191,292),(x+237,304),(x+264,304)],P['hillFar'])
  poly(draw,[(x+34,269),(x+50,260),(x+60,253+high),(x+70,247+high),(x+77,247+high),(x+89,262),(x+107,268),(x+70,262)],P['hillFarHi'])
 rect(draw,(0,298,360,331),P['hillMid'])
 for k in range(-2,6):
  x=int(k*166-t*.44)
  poly(draw,[(x-9,324),(x+8,313),(x+24,309),(x+32,294),(x+47,292),(x+64,306),(x+84,303),(x+111,318),(x+137,333)],'#649b7e')
  poly(draw,[(x+20,322),(x+38,315),(x+54,314),(x+67,327)],'#80ad82')
 rect(draw,(0,328,W,437),P['meadow'])
 poly(draw,[(0,333),(35,332),(40,338),(108,337),(108,331),(183,334),(220,330),(286,336),(360,330),(360,357),(0,357)],P['meadowLight'])
 poly(draw,[(0,359),(56,353),(112,367),(165,355),(226,363),(300,350),(360,364),(360,407),(0,407)],'#8fb77a')
 # hand spaced harvest-field furrows, with perspective and parallax
 for i in range(-1,11):
  x=int((i*47-t*.60)%490)-65
  poly(draw,[(x,337),(x+13,337),(x+21,340),(x+48,338),(x+52,342),(x+13,343)],'#bed18a')
 for i in range(-2,30):
  x=int((i*19-t*.9)%430)-32
  y=375+((i*17)%45)
  rect(draw,(x,y,x+6,y+1),'#74a16e')
  if i%5==0:rect(draw,(x+7,y-4,x+9,y-2),'#e4db9a')

def distant_grove(img,t):
 # intentional alternating silhouette rhythm at different depths
 for i in range(-3,14):
  x=int(i*48-t*.72)%650-120
  sprite=FIR.resize((25,49),Image.Resampling.NEAREST)
  img.paste(sprite,(x,335+(i%3)*4),sprite)
 for i in range(-2,12):
  x=int(i*81+16-t*.98)%820-130
  sprite=OAKS[i%2].resize((60,76),Image.Resampling.NEAREST)
  img.paste(sprite,(x,367+(i%3)*5),sprite)

def large_trees(img,t):
 # world positions give visible passage of multiple unique canopies over ten seconds
 for i in range(-2,9):
  world=i*205+(36 if i%3==1 else -11 if i%3==2 else 0)
  x=int(world-t*1.57)
  if x<-175 or x>W+12:continue
  ys=265+((i*7)%3)*8
  oak=OAKS[i%2]
  if i%4==2:oak=oak.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
  img.paste(oak,(x,ys),oak)
 # tonal ground behind carriageway, bright grass popping over trunks
 d=ImageDraw.Draw(img)
 rect(d,(0,438,W,459),P['verge'])
 poly(d,[(0,444),(18,442),(30,447),(55,441),(84,447),(130,443),(172,449),(219,442),(254,446),(301,441),(360,445),(360,457),(0,457)],P['vergeLight'])
 for i in range(-8,60):
  x=int((i*17-t*2)%420)-25
  y=448+(i*13)%9
  line(d,[(x,y+2),(x+1,y-5),(x+3,y+2)],'#337259',1)
  if i%4==0:rect(d,(x+4,y-3,x+5,y-2),'#e8d797')

def road(d,t):
 rect(d,(0,459,W,570),P['asphalt'])
 rect(d,(0,459,W,463),P['roadEdge'])
 rect(d,(0,463,W,467),'#71806f')
 rect(d,(0,468,W,471),P['asphalt2'])
 rect(d,(0,565,W,571),'#454b4e')
 rect(d,(0,570,W,577),P['roadEdge'])
 rect(d,(0,576,W,580),'#a19f88')
 # road wear and chips move with ground, not with camera
 for i in range(-6,135):
  x=int((i*27-t*2.86)%470)-70
  y=479+((i*137)%78)
  if i%6==0:rect(d,(x,y,x+15,y+2),'#606977')
  elif i%3==0:rect(d,(x,y,x+6,y+1),'#57606e')
  elif i%4==0:rect(d,(x,y,x+3,y+1),'#35424e')
 for i in range(-2,6):
  x=int(i*145-(t*2.86)%145)
  poly(d,[(x,527),(x+62,527),(x+65,532),(x+1,532)],P['mark'])
  rect(d,(x+6,529,x+57,529),'#fbebbb')
 # verge wear lines
 for i in range(-3,70):
  x=int(i*24-t*2.86)%450-40
  if i%3==0:rect(d,(x,463,x+6,463),'#ddd0a8')
  if i%4==0:rect(d,(x,571,x+4,572),'#ece0b0')

def foreground(d,t):
 rect(d,(0,580,W,H),P['vergeDeep'])
 poly(d,[(0,591),(17,588),(28,593),(40,588),(59,590),(76,584),(100,590),(126,586),(143,591),(159,585),(188,590),(219,585),(240,591),(273,584),(297,589),(318,586),(342,592),(360,587),(360,638),(0,638)],'#468268')
 poly(d,[(0,609),(18,606),(33,613),(57,607),(94,614),(118,604),(136,612),(169,608),(195,614),(218,606),(251,611),(278,607),(309,614),(339,605),(360,611),(360,640),(0,640)],'#37775d')
 # beautifully clustered native verge grasses and flower stems on moving ground
 for i in range(-4,88):
  x=int(i*14-t*3.1)%420-26
  y=590+(i*31)%52
  c=['#649f74','#6baa78','#96bc7b','#315b50'][i%4]
  poly(d,[(x-4,y),(x-2,y-8),(x,y-2),(x+1,y-12),(x+3,y-3),(x+6,y-9),(x+5,y)],c)
  if i%7==1:
   rect(d,(x,y-13,x+1,y-4),'#6b9874')
   rect(d,(x-3,y-16,x+3,y-13),'#f4d88a')
   rect(d,(x-1,y-18,x+1,y-15),'#fff0ba')
  if i%11==4:
   rect(d,(x+2,y-11,x+3,y-2),'#6d9271')
   rect(d,(x,y-13,x+5,y-11),'#f8e7ca')
   rect(d,(x+2,y-14,x+3,y-12),'#f3bd8e')

# car at y=365 and shadow/wheels make contact with road at 465-470

def draw_frame(frame):
 t=frame
 im=Image.new('RGB',(W,H));d=ImageDraw.Draw(im)
 clouds=list(sky(d,t))
 for c,x,y in clouds:im.paste(c,(x,y),c)
 d=ImageDraw.Draw(im)
 mountain(d,t)
 distant_grove(im,t)
 large_trees(im,t)
 d=ImageDraw.Draw(im)
 road(d,t)
 # moving car: pitch + suspension. Wheel rotation linked to horizontal world travel 2.86 logical px/frame
 bounce=round(1.3*math.sin(frame*math.tau/27)+.55*math.sin(frame*math.tau/11))
 car=car_sprite(frame*2.86/21.0)
 x=43+round(2.2*math.sin(frame*math.tau/175))
 y=357+bounce
 im.paste(car,(x,y),car)
 d=ImageDraw.Draw(im)
 foreground(d,t)
 return im

def render():
 # pipe low-res original pixel frames into FFmpeg; ffmpeg performs exact 3x integer nearest-neighbour upscale
 final=OUT/'Verdant_Drive_10s_1080x1920.mp4'
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','360x640','-r','30','-i','-','-vf','scale=1080:1920:flags=neighbor,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','18','-profile:v','high','-movflags','+faststart','-r','30','-frames:v','300',str(final)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for k in range(300):
  frame=draw_frame(k)
  p.stdin.write(frame.tobytes())
  if k in (0,150,299):frame.save(OUT/f'frame_{k:03d}_native.png')
 p.stdin.close()
 result=p.wait()
 if result:raise RuntimeError('FFmpeg failed '+str(result))
 print('WROTE',final,final.stat().st_size)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--still',action='store_true');parser.add_argument('--render',action='store_true')
 args=parser.parse_args()
 if args.still:
  f=draw_frame(74);f.save(OUT/'artwork_native_360x640.png');f.resize((1080,1920),Image.Resampling.NEAREST).save(OUT/'artwork_upscaled_1080x1920.png');print('Still created')
 if args.render:render()
