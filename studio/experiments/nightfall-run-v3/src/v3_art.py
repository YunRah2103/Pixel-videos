#!/usr/bin/env python3
"""Pixel Garage V3: original native 360px art, multi-layer pixel assets.
Art is structured as discrete editable scene layers and car components.
Deliberately uses visible pixel blocks and hand-keyed silhouettes. No blur/no upscale filtering.
"""
from PIL import Image, ImageDraw
from pathlib import Path
import math, random
ROOT=Path(__file__).resolve().parent
AS=ROOT/'v3_assets';AS.mkdir(exist_ok=True)
W,H=960,640
TRAN=(0,0,0,0)

def canvas(w=W,h=H):return Image.new('RGBA',(w,h),TRAN)
def rect(d,box,c):d.rectangle(tuple(map(int,box)),fill=c)
def poly(d,pts,c):d.polygon([(round(x),round(y)) for x,y in pts],fill=c)
def line(d,pts,c,wd=1):d.line(pts,fill=c,width=wd,joint='curve')
def stripe(d,x,y,w,c):rect(d,(x,y,x+w,y+1),c)
def save(a,n):a.save(AS/(n+'.png'),optimize=True)
# Color system: storm-indigo cobalt / moon-ivory / copper and flame maple / racing cyan
SKY=['#0c172e','#101b36','#15223d','#1d2d4a','#28334d','#333c58','#494361','#66506a','#835a70','#a96c70','#c38274','#d59a7d']
# SKY BACKDROP - authored color stations and long sharp-edged wind clouds.
a=canvas();d=ImageDraw.Draw(a)
for i,c in enumerate(SKY):rect(d,(0,i*30,959,i*30+31),c)
rect(d,(0,359,959,639),'#d9a37f')
# horizon has its own deeper bands
rect(d,(0,365,959,395),'#bb8b82')
rect(d,(0,393,959,443),'#81697e')
# moon and stepped corona manually ringed, blocked against sky
for rad,col in [(44,'#66546f'),(39,'#94717e'),(33,'#c4a09a'),(29,'#f3c5a0'),(23,'#ffe3b8')]:
 for yy in range(-rad,rad+1,2):
  xx=int(math.sqrt(max(0,rad*rad-yy*yy)))
  if xx:rect(d,(755-xx,220+yy,755+xx,220+yy+1),col)
# moon surface etched blocks
for x,y,l in [(748,210,7),(762,228,6),(742,230,4),(757,203,6)]:rect(d,(x,y,x+l,y+2),'#f7cfab')
# hand shaped cloud silhouettes (not procedural elliptical puffs)
clouds=[(36,100,171,0),(296,145,197,1),(548,79,151,2),(760,127,183,3),(121,257,131,1),(510,276,172,2)]
for x,y,w,k in clouds:
 dark=['#1b2946','#303651','#222d49','#252c4a'][k]
 rim=['#3c3d58','#58506a','#3d4462','#49485e'][k]
 pts=[(x,y+15),(x+9,y+15),(x+9,y+8),(x+22,y+8),(x+22,y+4),(x+40,y+4),(x+40,y),
       (x+w-50,y),(x+w-50,y+4),(x+w-22,y+4),(x+w-22,y+9),(x+w-4,y+9),
       (x+w-4,y+15),(x+w+8,y+15),(x+w+8,y+22),(x+w-28,y+22),(x+w-28,y+25),
       (x+19,y+25),(x+19,y+21),(x,y+21)]
 poly(d,pts,dark)
 rect(d,(x+16,y+17,x+w-21,y+18),rim)
 for xx,ww in [(x+32,18),(x+61,9),(x+w-77,26)]:rect(d,(xx,y+3,xx+ww,y+4),rim)
# pure pixel stars - fewer near sun
for x,y in [(81,44),(212,89),(441,51),(627,39),(902,61),(15,159),(231,190),(408,115),(580,209),(878,254),
            (52,231),(303,46),(729,53),(344,227),(931,197),(159,32),(492,198)]:
 rect(d,(x,y,x+1,y+1),'#b1b0b2')
 if x%3==0:rect(d,(x-2,y+1,x+3,y+1),'#777b94')
# wind streaks
for x,y,ww in [(8,302,62),(162,325,43),(357,315,79),(520,354,42),(807,339,66),(917,308,32)]:
 rect(d,(x,y,x+ww,y+2),'#e5a484');rect(d,(x+16,y-3,x+39,y-2),'#a76c77')
save(a,'01_sky')

# DISTANT CLIFFS – angular mountain geometry and a pale capped ridge
a=canvas();d=ImageDraw.Draw(a)
# mountain chains with large nonrepeating key silhouettes
poly(d,[(0,393),(44,333),(71,357),(128,268),(156,309),(199,245),(250,325),(291,292),(338,345),(388,257),(436,321),(489,267),(530,326),(574,273),(621,344),(655,285),(693,325),(729,246),(770,298),(823,268),(875,319),(921,274),(960,332),(960,459),(0,459)],'#3c465c')
poly(d,[(0,400),(79,333),(126,366),(186,293),(238,356),(301,307),(360,385),(445,314),(493,360),(540,310),(602,383),(687,314),(731,358),(780,290),(833,370),(898,321),(960,367),(960,472),(0,472)],'#323b57')
# physical snow key facets on cliff peaks (no glow)
for pts in [ [(108,294),(128,268),(143,292),(129,286),(119,301)],[(184,263),(199,245),(211,271),(201,262)],
[(374,281),(388,257),(407,286),(391,278)],[(716,270),(729,246),(746,278),(729,269)],[(767,309),(780,290),(798,320),(781,310)] ]:
 poly(d,pts,'#a5a5a9')
for pts in [[(210,300),(238,356),(253,335),(235,322)],[(572,272),(602,383),(618,359),(597,302)],[(820,299),(833,370),(851,354),(833,320)]]:poly(d,pts,'#62617a')
# distant village cut against cliff, repeat architectural language but not clone
for x,y,w,h in [(32,404,24,16),(69,409,13,11),(234,404,21,16),(270,413,16,10),(451,403,29,19),(484,415,15,11),(616,406,22,17),(840,402,18,15),(900,409,26,17)]:
 rect(d,(x,y,x+w,y+h),'#30344e');poly(d,[(x-4,y),(x+w//2,y-8),(x+w+4,y)],'#55435a')
 for wx in range(x+4,x+w-2,8):rect(d,(wx,y+5,wx+2,y+8),'#e8ad80')
# taller tower landmark
rect(d,(575,385,581,427),'#2f3653');rect(d,(565,383,592,387),'#42445e');rect(d,(576,375,579,385),'#554a63')
# high lake, distinctive horizontal shimmer at edge of horizon
poly(d,[(0,452),(77,447),(127,450),(197,444),(262,447),(323,443),(395,449),(460,446),(526,449),(587,443),(655,450),(715,443),(780,450),(832,444),(907,451),(960,445),(960,505),(0,505)],'#214358')
rect(d,(0,459,960,461),'#336078')
for i,(x,y,ww) in enumerate([(4,475,38),(64,488,24),(127,471,59),(202,492,18),(289,471,43),(356,493,29),(431,478,41),(509,466,43),(562,484,66),(643,479,36),(735,469,39),(817,490,62),(914,474,28)]):
 rect(d,(x,y,x+ww,y+1),['#427287','#5a788d','#365d71'][i%3])
for x,y in [(720,477),(741,489),(758,470),(774,483),(797,464)]:rect(d,(x,y,x+16,y+2),'#967988')
save(a,'02_mountains_lake')

# FIR TREE with distinctive branch angles not a repeated triangle, actual bark and bough groups.
def pine(d,x,b,h,style=0,phase=0):
 trunk='#202e43' if style==0 else '#172d3b'; needles=['#224255','#255164','#234a5a'] if style==0 else ['#164b52','#20575b','#1c434e']
 dark=needles[0]
 rect(d,(x-3,b-h+21,x+2,b+3),trunk)
 poly(d,[(x,b-h-7),(x-3,b-h+13),(x+4,b-h+13)],needles[1])
 for q in range(5):
  yy=b-h+23+q*(h-34)/5;wide=int(h*(.12+q*.056));dir1=((q*7+phase*13)%9)-4
  # each tier organically asymmetrical
  p=[(x+1,yy-11),(x-wide//2,yy+5),(x-wide+dir1,yy+13),(x-wide//2,yy+14),(x-wide//2-6,yy+19),
     (x+wide//3,yy+18),(x+wide+dir1//2,yy+20),(x+wide//2+1,yy+6)]
  poly(d,p,needles[(q+style)%3])
  poly(d,[(x-3,yy-8),(x-wide//2,yy+5),(x-wide+8+dir1,yy+11),(x-4,yy+11),(x+wide-8,yy+17),(x+wide//2,yy+6)],'#31667a' if style==0 else '#397c75')
  # branch voids and edge bits
  if q>0:
   rect(d,(x-wide//2-6,yy+14,x-wide//2-1,yy+16),trunk)
   rect(d,(x+wide//2+1,yy+13,x+wide//2+7,yy+15),needles[0])
  if q%2==0:rect(d,(x+3,yy+7,x+12,yy+9),'#7b9d93' if style else '#5f8994')
 # bark geometry
 rect(d,(x-2,b-18,x+1,b),'#334252')
 rect(d,(x+1,b-13,x+2,b),'#4b5358')

# maple canopy authored from asymmetrical jagged silhouette polygons, not stacked circles
MAPLE_SHAPES=[
[(-57,-7),(-55,-23),(-43,-31),(-38,-42),(-23,-43),(-17,-57),(3,-54),(13,-46),(29,-50),(41,-34),(54,-31),(60,-14),(54,-3),(37,7),(17,10),(-3,15),(-24,10),(-40,7)],
[(-49,0),(-55,-16),(-40,-30),(-31,-32),(-27,-49),(-7,-57),(9,-49),(20,-45),(32,-53),(46,-41),(43,-25),(57,-13),(48,2),(31,8),(19,4),(2,13),(-17,7),(-32,13)],
[(-59,-2),(-50,-18),(-55,-30),(-39,-34),(-35,-49),(-19,-43),(-4,-61),(13,-57),(21,-43),(40,-50),(48,-34),(62,-25),(55,-7),(35,-2),(28,11),(5,7),(-11,17),(-26,9),(-46,12)]
]
MAPLE_PAL=[['#763b57','#a54c5c','#c76462','#ec9068','#ffc184'],['#69445d','#a24c56','#d26d5e','#f1a073','#ffd08c'],['#593f59','#974a61','#d07368','#eb9e79','#ffd49a']]
def maple(d,x,b,s,typ=0):
 scale=s/100; pal=MAPLE_PAL[typ%3]
 # slender dark trunk with very explicit branch angles
 rect(d,(x-4,b-100*scale,x+3,b),'#26323e')
 line(d,[(x,b-58*scale),(x-27*scale,b-82*scale),(x-40*scale,b-92*scale)],'#243142',max(2,round(6*scale)))
 line(d,[(x,b-49*scale),(x+19*scale,b-86*scale),(x+34*scale,b-93*scale)],'#303041',max(2,round(5*scale)))
 line(d,[(x,b-76*scale),(x+3*scale,b-112*scale)],'#303340',3)
 top=b-s*0.92;shape=MAPLE_SHAPES[typ%3]
 def pp(points):return [(x+dx*scale,top+dy*scale) for dx,dy in points]
 poly(d,pp(shape),pal[0]);
 # asymmetric interior clusters, explicit art marks that break up mass
 patches=[([(-49,-8),(-42,-28),(-26,-39),(-9,-33),(-19,-17),(-27,-2)],1),
 ([(-21,-39),(-17,-54),(2,-54),(15,-38),(11,-20),(-1,-28)],2),
 ([(15,-35),(38,-44),(48,-22),(36,-8),(18,-10)],2),
 ([(-46,-22),(-37,-33),(-27,-25),(-31,-17)],3),
 ([(-11,-50),(4,-51),(16,-38),(1,-38),(-14,-41)],3),
 ([(29,-40),(41,-33),(46,-26),(31,-25)],4),
 ([(8,-23),(23,-16),(15,-8),(-8,-13)],1),
 ([(-52,-7),(-41,-2),(-29,3),(-45,7)],2)]
 for p,col in patches:poly(d,pp(p),pal[col])
 # tiny foliage chips distributed as composed left-to-right groups, not noise
 for ox,oy,l,c in [(-45,-19,7,3),(-36,-35,5,4),(-19,-34,10,4),(0,-47,9,4),(22,-38,12,3),(35,-16,6,4),(-1,-8,8,3),(-33,-2,8,2)]:
  rect(d,(x+ox*scale,top+oy*scale,x+(ox+l)*scale,top+(oy+3)*scale),pal[c])
 # gaps where darkness can breathe
 for ox,oy,ww in [(-20,-18,7),(17,-14,9),(5,-34,6)]:rect(d,(x+ox*scale,top+oy*scale,x+(ox+ww)*scale,top+(oy+2)*scale),pal[0])

# MID FOREST - graphic triangular pines and individually varied deciduous silhouette groups
a=canvas();d=ImageDraw.Draw(a)
poly(d,[(0,489),(57,483),(113,490),(194,479),(250,487),(330,473),(401,489),(480,477),(539,488),(632,471),(700,489),(792,475),(864,490),(941,478),(960,481),(960,539),(0,539)],'#1d3548')
for i,(x,h,b,style) in enumerate([(17,100,482,0),(90,137,490,1),(162,107,488,0),(246,160,488,0),(323,101,480,1),(382,136,484,0),(491,109,482,1),(548,143,489,0),(657,112,478,1),(734,158,488,0),(829,124,489,1),(909,148,487,0)]):pine(d,x,b,h,style,i)
for i,(x,b,s,t) in enumerate([(60,488,75,0),(204,481,83,2),(439,491,89,1),(612,480,80,2),(784,483,84,0),(952,488,82,1)]): maple(d,x,b,s,t)
# edge highlight along lake bank
rect(d,(0,499,960,502),'#2d4b59')
for x,ww in [(13,30),(113,44),(268,22),(353,31),(515,53),(680,34),(843,60)]:rect(d,(x,497,x+ww,498),'#5d716d')
save(a,'03_mid_forest')

# NEAR VEGETATION – more detailed pine / maple group, bold separated silhouettes
# preserve visual space above road for car, layer ends near wheel upper bnd
a=canvas();d=ImageDraw.Draw(a)
poly(d,[(0,503),(41,496),(90,502),(157,490),(209,501),(260,489),(308,500),(361,490),(422,504),(487,494),(556,502),(618,486),(702,501),(780,490),(839,499),(960,491),(960,535),(0,535)],'#142e3e')
for i,(x,b,h) in enumerate([(39,507,137),(174,500,118),(303,507,148),(508,501,133),(682,504,159),(879,501,142)]):pine(d,x,b,h,1,i+25)
for i,(x,b,s) in enumerate([(119,508,93),(409,506,114),(595,504,92),(782,506,111),(950,500,99)]):maple(d,x,b,s,(i+1)%3)
# mossy stone wall under trees
rect(d,(0,506,960,517),'#1e3543')
for x,w in [(14,38),(70,27),(132,19),(216,52),(299,34),(375,48),(485,33),(568,43),(654,25),(749,50),(872,31),(910,39)]:
 rect(d,(x,510,x+w,512),'#32505a')
 rect(d,(x+3,514,x+int(w*.7),515),'#1c2839')
save(a,'04_near_forest')

# BARRIER: exterior road furniture independently animated, discrete gold edge guides
a=canvas();d=ImageDraw.Draw(a)
rect(d,(0,517,959,527),'#24384b')
rect(d,(0,515,959,516),'#92b2a5')
rect(d,(0,519,959,521),'#506b72')
rect(d,(0,526,959,528),'#1a2a39')
for x in range(0,960,96):
 rect(d,(x+16,512,x+20,532),'#182734');rect(d,(x+17,518,x+18,525),'#5d6b67')
 rect(d,(x+22,517,x+36,518),'#d9bb8b')
save(a,'05_guardrail')

# Highway asphalt & markings, stronger directional motion and proper restrained specular breakup
a=canvas();d=ImageDraw.Draw(a)
rect(d,(0,526,959,639),'#101f31')
rect(d,(0,530,959,537),'#192c3f')
rect(d,(0,538,959,550),'#142338')
rect(d,(0,551,959,634),'#112035')
rect(d,(0,632,959,639),'#0d1829')
# embossed paving seams, two pairs of gold lane lines
rect(d,(0,577,959,578),'#2a3a4d')
for x in range(0,960,136):
 poly(d,[(x+10,574),(x+76,574),(x+71,578),(x+7,578)],'#e9bb78')
 rect(d,(x+13,573,x+50,573),'#fff0b0')
for x in range(0,960,171):
 rect(d,(x+33,546,x+89,547),'#263951')
 rect(d,(x+18,555,x+51,556),'#2e3c53')
 rect(d,(x+66,602,x+113,603),'#29384d')
 rect(d,(x+112,614,x+131,616),'#213049')
 rect(d,(x+94,588,x+106,589),'#496072')
# wet strip glints: block-locked not glow particles
for x,y,ww in [(17,542,25),(123,546,20),(237,557,14),(359,542,35),(484,569,20),(568,551,29),(690,542,23),(804,548,18),(908,562,29)]:
 rect(d,(x,y,x+ww,y+1),'#366177')
save(a,'06_road')

# FOREGROUND: visible motion due to near-field speed, avoid blocking the hero car.
a=canvas();d=ImageDraw.Draw(a)
# layered rock/grassy bank appears at very bottom of frame
poly(d,[(0,631),(24,619),(54,628),(84,615),(122,624),(156,619),(201,633),(241,618),(298,627),(331,612),(382,634),(425,622),(473,634),(516,615),(568,628),(616,620),(676,637),(735,620),(790,634),(853,620),(915,632),(960,621),(960,640),(0,640)],'#162f34')
poly(d,[(0,637),(44,629),(92,639),(136,631),(185,637),(215,629),(263,639),(302,631),(363,639),(406,629),(460,640),(522,629),(570,639),(619,628),(680,639),(730,633),(789,640),(836,632),(895,639),(960,631),(960,640),(0,640)],'#284f49')
for x in range(12,950,38):
 y=[626,629,632,625,631][(x//38)%5]; col=['#45765e','#629172','#315e54'][x//38%3]
 line(d,[(x,y+7),(x,y-5)],col,2)
 line(d,[(x,y+4),(x-5,y)],col,2)
 line(d,[(x,y+1),(x+5,y-3)],col,2)
# two roadside fluted hazard reflectors; travel fast and cross frame
for x in range(48,960,260):
 rect(d,(x,568,x+4,625),'#132d38')
 rect(d,(x-4,564,x+8,575),'#e6bc84')
 rect(d,(x-3,575,x+7,579),'#466778')
 rect(d,(x-2,579,x+5,582),'#eaaa73')
 rect(d,(x+1,594,x+3,602),'#b07d63')
save(a,'07_verge')

# bespoke low-slung grand tourer with shaped greenhouse, hand-layered glazing, tire voids.
CW,CH=316,139
a=canvas(CW,CH);d=ImageDraw.Draw(a)
# rear glass shadow and body silhouette, outlined one-by-one (front points right)
body=[(10,80),(15,73),(43,68),(58,50),(78,31),(103,21),(180,18),(205,23),(236,51),
      (251,56),(284,63),(296,69),(305,78),(307,98),(299,108),(280,111),(40,111),(13,106),(6,99),(6,88)]
poly(d,body,'#0c263e')
# upper gloss / side skirt, angular sections
poly(d,[(13,77),(46,70),(77,33),(101,25),(176,22),(203,26),(233,56),(249,62),(288,67),(302,80),(301,99),(285,102),(40,102),(13,99)],'#04637e')
poly(d,[(14,79),(56,73),(81,43),(99,31),(172,29),(200,32),(226,59),(248,68),(285,71),(300,83),(286,86),(252,82),(240,76),(65,77),(32,87)],'#168daa')
poly(d,[(14,83),(34,82),(60,77),(235,78),(249,83),(300,86),(301,95),(289,103),(18,103)],'#0e6f90')
# hard-edged dark rocker and front splitter
poly(d,[(18,102),(296,101),(304,104),(310,107),(305,112),(12,112),(11,108)],'#103045')
poly(d,[(28,108),(284,108),(278,114),(32,114)],'#07192c')
poly(d,[(257,112),(311,112),(313,114),(260,115)],'#142d44')
# coupe glass roof line slopes down to hood, narrow A pillar and C pillar geometry
poly(d,[(75,43),(96,26),(171,25),(197,31),(222,59),(189,59),(81,61)],'#061e32')
poly(d,[(84,43),(101,31),(170,29),(189,34),(207,54),(164,54),(145,53),(90,56)],'#183b53')
# rear triangular privacy glass shape, rear pillar turns into quarter
poly(d,[(83,45),(102,34),(125,31),(120,55),(87,57)],'#36637b')
poly(d,[(93,43),(106,35),(116,34),(111,45),(92,52)],'#6eacc0')
# tinted front window and rear reflection segments
poly(d,[(131,31),(166,31),(184,36),(202,53),(129,53)],'#21475d')
poly(d,[(155,32),(171,33),(185,39),(193,49),(175,46)],'#2a6176')
poly(d,[(135,33),(149,31),(151,49),(136,52)],'#537d8e')
rect(d,(122,31,126,60),'#052139')
# bright window-line, single clean graphic shape
poly(d,[(81,59),(202,58),(211,62),(83,63)],'#6cb5bb')
poly(d,[(79,61),(205,62),(210,66),(77,65)],'#092a42')
# roof highlight and unique pixel ramps rather than neon lines
poly(d,[(99,22),(174,19),(193,24),(200,29),(184,27),(170,23),(106,25),(91,29)],'#b5d4c4')
rect(d,(108,25,171,26),'#6bafb4')
# aerodynamic bonnet contour and wing flares
poly(d,[(230,57),(255,61),(284,65),(295,69),(246,68)],'#76c1c2')
poly(d,[(238,69),(285,72),(295,76),(261,75)],'#269aaf')
# doors with convincing panel detailing
line(d,[(124,66),(122,94),(126,105)],'#114c6a',2)
line(d,[(203,66),(202,95),(198,107)],'#0f4f6b',2)
rect(d,(150,69,162,71),'#0b2f43')
rect(d,(149,69,158,69),'#b5d2bc')
# rear quarter gill (three displaced notches)
for j in range(3):rect(d,(42+j*5,85,45+j*5,91),'#0d4b63')
# multi-block reflections intentionally sparse and physical
poly(d,[(64,75),(114,73),(127,76),(93,81),(50,83)],'#43b1b7')
rect(d,(133,76,199,78),'#2a9cae')
poly(d,[(213,76),(247,76),(267,81),(220,80)],'#73c4bf')
rect(d,(29,95,53,97),'#2b9da7')
rect(d,(179,92,214,94),'#2ba5b1')
# precise rear lamp assembly / tiny bright road accents
poly(d,[(9,78),(31,76),(33,82),(11,87)],'#341e38')
poly(d,[(11,79),(29,78),(29,81),(11,84)],'#ee736c')
rect(d,(10,83,21,84),'#ffb383')
# graphic headlight wedge (thin not super high)
poly(d,[(278,69),(296,72),(302,78),(293,80),(270,73)],'#143d54')
poly(d,[(279,70),(294,73),(298,77),(289,76)],'#ffe3b0')
rect(d,(295,76,302,78),'#eab97f')
# front lip and rear diffuser
rect(d,(298,96,309,99),'#0a293c')
rect(d,(8,99,28,101),'#071829')
poly(d,[(14,103),(51,104),(56,108),(15,108)],'#18374c')
# race-style side stripe tapered, not a slab
poly(d,[(44,95),(218,94),(260,99),(45,99)],'#153d54')
poly(d,[(65,97),(213,97),(224,98),(59,98)],'#66adb3')
# intentionally cut two wheel wells out as actual transparency; wheel sprites live below body
for xc in (75,243):
 rr=27
 for yy in range(-rr,rr+1):
  xx=int(math.sqrt(max(0,rr*rr-yy*yy)))
  rect(d,(xc-xx,111+yy,xc+xx,111+yy),TRAN)
# elegant dark arch edges built as exposed outer crescent, not wheel occluder
for xc in (75,243):
 for rad,color in [(29,'#072238'),(28,'#123449'),(27,'#264c62')]:
  for yy in range(-rad,8):
   if rad*rad-yy*yy<0:continue
   xx=int(math.sqrt(rad*rad-yy*yy))
   # edge pixel lines only around top of wheel well
   for sx in (-1,1):
    x=xc+sx*xx
    rect(d,(x,111+yy,x+1,112+yy),color)
# fender highlight C-shaped pixel ramp
for xc in (75,243):
 line(d,[(xc-31,90),(xc-23,80),(xc-8,77),(xc+12,79),(xc+27,86)],'#53b0b4',2)
save(a,'08_coupe_body')

# detachable five twin spoke magnesium sports wheel
WH=65;a=canvas(WH,WH);d=ImageDraw.Draw(a);xc=cy=32
for rad,c in [(31,'#071422'),(29,'#142338'),(26,'#2a3141'),(23,'#0b1d2a'),(19,'#9cb6af'),(17,'#19344b')]:
 d.ellipse((xc-rad,cy-rad,xc+rad,cy+rad),fill=c)
# radial tire details are physically rotated with sprite
for i in range(16):
 theta=i*math.pi/8
 x1=xc+round(27*math.cos(theta));y1=cy+round(27*math.sin(theta))
 x2=xc+round(30*math.cos(theta));y2=cy+round(30*math.sin(theta))
 line(d,[(x1,y1),(x2,y2)],'#4a5263',2)
for i in range(5):
 th=(i*2*math.pi/5)-math.pi/2
 dx,dy=math.cos(th),math.sin(th)
 # twin-spoke forged alloy blades
 for ang in [-.10,.10]:
  ux,uy=math.cos(th+ang),math.sin(th+ang)
  poly(d,[(xc+ux*5-uy*2,cy+uy*5+ux*2),(xc+ux*16-uy*2,cy+uy*16+ux*2),
           (xc+ux*18+uy*2,cy+uy*18-ux*2),(xc+ux*6+uy*2,cy+uy*6-ux*2)],'#d6dbcb')
  rect(d,(xc+ux*15,cy+uy*15,xc+ux*15+1,cy+uy*15+1),'#f7dca9')
# lug hubs
d.ellipse((27,27,37,37),fill='#718e96')
d.ellipse((29,29,35,35),fill='#20394b')
for th in range(0,360,72):
 xx=xc+round(math.cos(math.radians(th))*8);yy=cy+round(math.sin(math.radians(th))*8)
 rect(d,(xx,yy,xx+1,yy+1),'#e0d8bd')
save(a,'09_wheel')
# accessory: translucent light and tire shadow component

print('Built V3',len(list(AS.glob('*.png'))),'layered PNGs in',AS)