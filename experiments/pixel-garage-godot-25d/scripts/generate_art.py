#!/usr/bin/env python3
"""Original hand-composed pixel sprite shapes; NEVER pixelated Blender renders."""
from PIL import Image,ImageDraw
from pathlib import Path
from math import sin,cos,pi
import random
A=Path(__file__).resolve().parent.parent/"assets"
A.mkdir(exist_ok=True)
I="#192733";C="#e6d4ae";W="#fff0c7";S="#bcb398";T="#198b85";B="#1d4d5b";H="#6e9ca0";O="#f18a48";R="#bd403e"
def img(w,h): return Image.new("RGBA",(w,h))
def poly(d,p,c):d.polygon(p,fill=c)
def rect(d,a,c):d.rectangle(a,fill=c)
def line(d,p,c,k=1):d.line(p,fill=c,width=k)
def tire(d,x,y,phase,r=17):
 d.ellipse((x-r-2,y-r-2,x+r+2,y+r+2),fill="#14212b",outline="#334953",width=2)
 d.ellipse((x-r+5,y-r+5,x+r-5,y+r-5),fill="#a5b3aa")
 d.ellipse((x-r+8,y-r+8,x+r-8,y+r-8),fill="#334650")
 for j in range(8):
  a=2*pi*j/8+phase;line(d,(x,y,x+int(cos(a)*8),y+int(sin(a)*8)),W,2)
 d.ellipse((x-3,y-3,x+3,y+3),fill="#34c7b6")
def side(i=0):
 a=img(280,164);d=ImageDraw.Draw(a)
 poly(d,[(17,111),(20,94),(36,81),(70,69),(96,66),(111,47),(131,34),(175,29),(202,41),(229,65),(252,75),(259,92),(258,114),(51,119)],I)
 poly(d,[(23,106),(26,89),(40,80),(74,70),(98,68),(115,47),(132,38),(174,35),(196,46),(225,68),(249,77),(254,92),(252,110),(51,114)],C)
 poly(d,[(26,87),(74,74),(103,70),(215,75),(249,85),(251,89),(35,92)],W)
 poly(d,[(27,99),(93,91),(224,91),(251,97),(249,108),(42,110)],S)
 poly(d,[(99,67),(115,48),(134,40),(172,37),(196,45),(223,67)],I)
 poly(d,[(108,65),(124,48),(138,44),(153,43),(153,65)],B)
 poly(d,[(158,43),(174,41),(195,48),(212,65),(158,65)],B)
 poly(d,[(117,57),(137,46),(151,44),(146,49),(131,53)],H)
 poly(d,[(163,45),(174,43),(190,48),(195,53)],H)
 line(d,(157,40,157,67),C,4);line(d,(203,51,217,68),C,4);line(d,(113,46,97,69),W,4)
 line(d,(114,70,228,71),"#748d87",2)
 poly(d,[(230,62),(249,57),(258,61),(255,66),(231,67)],I)
 poly(d,[(232,60),(250,57),(258,59),(255,62)],O)
 poly(d,[(145,33),(164,29),(177,31),(179,36),(147,37)],I)
 rect(d,(150,32,170,33),W)
 poly(d,[(23,89),(43,83),(51,84),(43,91),(24,95)],I)
 poly(d,[(26,88),(44,84),(43,87),(27,92)],"#fff0ad")
 rect(d,(247,81,258,91),R);rect(d,(251,84,258,85),O)
 rect(d,(22,108,58,114),I);rect(d,(240,111,260,116),I)
 line(d,(100,74,99,103),"#9da99c",2);line(d,(158,75,157,104),"#9da99c",2)
 rect(d,(116,77,130,79),I);rect(d,(173,77,187,79),I)
 poly(d,[(60,84),(113,76),(144,85),(94,102),(60,101)],T)
 poly(d,[(77,83),(131,79),(152,86),(103,100),(91,98)],"#29b5a4")
 poly(d,[(131,90),(205,89),(220,103),(158,107),(116,105)],O)
 poly(d,[(140,92),(179,91),(192,100),(155,103)],"#ffc075")
 rect(d,(151,80,179,100),I);rect(d,(154,83,177,97),W)
 rect(d,(160,85,167,95),I);rect(d,(171,85,174,95),I)
 for x in (75,216):
  d.ellipse((x-23,92,x+23,137),fill=I)
  d.arc((x-24,90,x+24,138),180,360,fill=W,width=3)
  tire(d,x,115,i*pi/4)
 rect(d,(257,111,269,114),"#869997")
 for x,y in [(47,79),(92,69),(137,37),(183,38),(224,74),(47,100),(186,104)]:
  rect(d,(x,y,x+6,y+1),W)
 return a
def rear(i=0):
 a=img(280,164);d=ImageDraw.Draw(a)
 d.ellipse((29,126,257,151),fill="#152f3b")
 poly(d,[(52,99),(87,79),(154,65),(226,75),(253,97),(244,120),(190,134),(79,124)],I)
 poly(d,[(62,97),(91,82),(157,70),(225,78),(246,97),(239,114),(190,126),(82,118)],S)
 poly(d,[(95,81),(121,43),(158,29),(197,34),(225,69),(225,87),(170,98)],I)
 poly(d,[(105,78),(128,45),(158,34),(194,39),(217,69),(215,81),(167,91)],C)
 poly(d,[(132,47),(159,36),(183,39),(201,71),(170,79),(119,72)],B)
 poly(d,[(174,39),(192,44),(211,71),(201,70)],H)
 poly(d,[(200,47),(218,69),(232,95),(222,104),(204,83)],I)
 poly(d,[(204,50),(215,70),(227,90),(219,91)],B)
 poly(d,[(80,88),(149,79),(184,95),(196,121),(81,112)],C)
 poly(d,[(88,88),(151,78),(178,93),(114,103),(65,102)],W)
 poly(d,[(96,102),(167,97),(195,120),(95,116)],T)
 poly(d,[(101,105),(167,101),(188,117),(132,116)],"#2ac9b1")
 poly(d,[(162,100),(218,93),(239,98),(237,107),(195,122)],O)
 for x,y in ((95,123),(209,131)):
  d.ellipse((x-14,y-17,x+14,y+17),fill=I)
  d.ellipse((x-8,y-9,x+8,y+9),fill="#7e9998")
  for j in range(6):
   t=j*pi/3+i*pi/4;line(d,(x,y,x+int(cos(t)*7),y+int(sin(t)*7)),W,2)
 poly(d,[(189,33),(215,33),(233,47),(226,49),(209,39),(190,41)],I)
 poly(d,[(192,31),(214,31),(231,45),(226,46)],O)
 rect(d,(232,95,248,99),R);rect(d,(240,97,250,98),"#ffd07e")
 rect(d,(209,111,247,115),I)
 rect(d,(239,116,257,122),"#92a4a1");rect(d,(249,118,260,120),I)
 return a
def front(i=0):
 a=rear(i).transpose(Image.Transpose.FLIP_LEFT_RIGHT);d=ImageDraw.Draw(a)
 poly(d,[(30,100),(46,96),(64,108),(61,115),(36,112)],I)
 rect(d,(33,100,50,105),"#ffedbb");rect(d,(35,109,57,113),I)
 return a
def tree(seed):
 r=random.Random(seed);a=img(100,205);d=ImageDraw.Draw(a)
 cx=50;line(d,(cx,15,cx,198),"#263c3d",6);line(d,(cx+1,80,cx+1,190),"#82785a",2)
 for k in range(6):
  y=18+k*23;w=10+k*7-(7 if k==5 else 0)
  poly(d,[(cx,y-17),(cx-w+5,y+11),(cx-w-4,y+28),(cx,y+19),(cx+w+4,y+28),(cx+w-6,y+10)],I)
  poly(d,[(cx,y-14),(cx-w+9,y+13),(cx-w+2,y+19),(cx,y+12),(cx+w-2,y+20),(cx+w-7,y+10)],["#2e7569","#2e7263","#2b6a5c","#285e54","#24574e","#205148"][k])
  for j in range(15):
   x=cx-w+10+r.randrange(max(w,8));v=y+4+r.randrange(17)
   rect(d,(x,v,x+r.randrange(1,5),v+1),r.choice(["#4a947b","#529b80","#295a52","#67a387"]))
 return a
def mountains(near=False):
 a=img(650,185);d=ImageDraw.Draw(a);col="#476f6f" if near else "#72909a"
 p=[(x,87+int(27*sin(x*.02+1.4)+12*sin(x*.047)+9*sin(x*.08))) for x in range(-10,680,10)]
 poly(d,p+[(650,185),(0,185)],col)
 for j in range(22):
  x=j*30;y=90+int(27*sin(x*.02+1.4)+12*sin(x*.047))
  poly(d,[(x,y),(x+26,y+17),(x+12,y+9)],"#345962" if near else "#567985")
 return a
def gravel():
 r=random.Random(4301);a=Image.new("RGBA",(96,96),"#8f7e67");d=ImageDraw.Draw(a)
 for k in range(940):
  x=r.randrange(96);y=r.randrange(96);n=r.choice([1,2,2,3,4])
  rect(d,(x,y,x+n,y+r.choice([1,1,2])),r.choice(["#716956","#bba482","#9b8b71","#a89b7e","#615d54","#cdb58b"]))
 return a
def flame():
 a=img(74,46);d=ImageDraw.Draw(a)
 poly(d,[(2,18),(22,11),(39,13),(60,4),(54,17),(72,21),(47,28),(62,36),(37,32),(19,34),(2,27)],"#af462b")
 poly(d,[(2,20),(25,14),(41,16),(58,10),(46,20),(61,23),(41,28),(49,33),(26,29),(2,26)],"#ff8c37")
 poly(d,[(2,21),(27,18),(46,19),(36,23),(48,25),(26,27),(2,25)],"#ffe08f")
 poly(d,[(2,22),(20,20),(34,23),(16,25),(2,24)],"#fff8bd")
 return a
def dust():
 r=random.Random(2103);a=img(150,86);d=ImageDraw.Draw(a)
 poly(d,[(2,53),(17,41),(36,45),(45,31),(65,37),(76,20),(98,28),(114,45),(145,55),(146,69),(45,70)],"#776b64")
 for k in range(90):
  x=r.randrange(146);y=r.randrange(29,72)
  rect(d,(x,y,x+r.randrange(1,5),y+r.randrange(1,3)),r.choice(["#baa388","#8e826f","#70665d"]))
 return a

def grass():
 r=random.Random(91704)
 a=Image.new("RGBA",(128,128),"#315c4f")
 d=ImageDraw.Draw(a)
 for k in range(1250):
  x=r.randrange(128);y=r.randrange(128)
  tone=r.choice(["#2b554b","#376d55","#42775b","#254b45","#648468","#2e6051","#567861"])
  n=r.choice([1,1,2,3,4])
  rect(d,(x,y,x+n,y+r.choice([0,1,1,2])),tone)
 for k in range(35):
  x=r.randrange(128);y=r.randrange(128)
  line(d,(x,y,x+2,y-3),r.choice(["#6e8e68","#8da075","#759377"]))
 return a

if __name__=="__main__":
 for name,fn in (("side",side),("rear3q",rear),("front3q",front)):
  for j in range(8):fn(j).save(A/("car_%s_%d.png"%(name,j)))
 for j in range(7):tree(j).save(A/("pine_%d.png"%j))
 for name,im in (("mountains_far",mountains()),("mountains_near",mountains(True)),("gravel",gravel()),("grass",grass()),("flame",flame()),("dust",dust())):im.save(A/(name+".png"))
 sheet=Image.new("RGB",(840,450),"#172d3a")
 for j,(name,fn) in enumerate((("side",side),("rear3q",rear),("front3q",front),("other side",lambda i:side(i).transpose(Image.Transpose.FLIP_LEFT_RIGHT)))):
  x=j%2*420+55;y=j//2*210+22
  pic=fn(0);sheet.paste(pic,(x,y+10),pic);ImageDraw.Draw(sheet).text((x,y),name,fill="#fff0bf")
 sheet.save(A/"sprite_showcase.png")
 print("PIXEL GARAGE: Generated",len(list(A.glob("*.png"))),"native pixel-art sprites")
