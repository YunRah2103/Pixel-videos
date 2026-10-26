"""V4 art pass: original hand authored pixel art, no 3D pixel filter."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import random, math
def box(d,x,c): d.rectangle(x,fill=c)
def poly(d,p,c): d.polygon(p,fill=c)
def pine(n):
 r=random.Random(871+n); im=Image.new("RGBA",(132,230)); d=ImageDraw.Draw(im)
 cx=66+r.randint(-7,7); top=r.randint(11,34)
 box(d,(cx-4,149,cx+5,224),"#64493e")
 for j in range(11,0,-1):
  y=top+j*15;w=max(6,int((y-top)*r.randint(40,58)/206));x=cx+r.randint(-4,4)
  poly(d,[(x,y-25),(x-w//2,y-5),(x-w-4,y+11),(x-w+10,y+7),(x+w-10,y+7),(x+w+5,y+12),(x+w//2,y-6)],r.choice(["#123740","#16454a","#1d4d4c"]))
  poly(d,[(x,y-26),(x-w//2,y-7),(x-w+5,y+4),(x-w+16,y+5),(x,y-10),(x+w//2,y+3),(x+w-4,y+5)],r.choice(["#2f6c60","#457f6b","#346f64"]))
  for k in range(9):
   xx=x+r.randint(-w,w);yy=y+r.randint(-6,10)
   box(d,(xx,yy,xx+r.randint(2,7),yy+2),r.choice(["#9aa989","#5b9476","#31635d","#bcb38c","#789d81"]))
 return im
def shrub(n,kind):
 r=random.Random(900+n); im=Image.new("RGBA",(94,56) if kind=="bush" else (66,44));d=ImageDraw.Draw(im)
 if kind=="rock":
  poly(d,[(5,37),(19,19),(36,12),(55,23),(63,40),(9,42)],"#1a343c")
  poly(d,[(10,35),(19,21),(36,16),(54,26),(49,37),(22,40)],"#7d8981")
  poly(d,[(19,21),(36,16),(30,29),(12,34)],"#c7b9a1")
 elif kind=="flowers":
  for i in range(24):
   x=r.randint(2,63);y=r.randint(12,32)
   d.line([(x,42),(x+r.randint(-3,3),y)],fill=r.choice(["#538369","#6e9d78"]),width=1)
   if i%2==0:box(d,(x-2,y-2,x+3,y+2),r.choice(["#f8dba2","#da9177","#f1b37f"]))
 else:
  for i in range(27):
   x=r.randint(9,85);y=r.randint(13,40);w=r.randint(6,13)
   poly(d,[(x-w,y+3),(x-7,y-7),(x,y-w),(x+w,y+2),(x+3,y+8)],r.choice(["#244d4c","#356e57","#498263","#1b4549"]))
  for i in range(48):
   x=r.randint(9,85);y=r.randint(12,44)
   box(d,(x,y,x+r.randint(2,4),y+2),r.choice(["#c3b58d","#88a77e","#4b8b65"]))
 return im
def mountain():
 r=random.Random(87);im=Image.new("RGBA",(900,300));d=ImageDraw.Draw(im)
 poly(d,[(0,215),(65,161),(96,183),(166,94),(215,150),(292,66),(348,127),(423,57),(466,119),(520,70),(592,148),(633,90),(697,139),(754,72),(818,135),(873,94),(900,124),(900,300),(0,300)],"#536e7f")
 poly(d,[(0,217),(65,175),(96,194),(166,113),(215,163),(292,87),(348,150),(423,80),(466,141),(520,97),(592,166),(633,109),(697,155),(754,93),(818,155),(873,111),(900,140),(900,300),(0,300)],"#829797")
 for x,y in [(166,113),(292,87),(423,80),(520,97),(754,93)]:
  poly(d,[(x,y),(x-14,y+30),(x+1,y+24),(x+14,y+34),(x+7,y+13)],"#e5b99a")
 poly(d,[(0,245),(65,221),(109,228),(153,188),(234,226),(296,194),(361,226),(412,198),(474,218),(552,183),(626,223),(689,194),(757,224),(819,181),(900,216),(900,300),(0,300)],"#264e56")
 poly(d,[(0,283),(70,239),(130,260),(189,228),(252,263),(314,234),(374,269),(429,229),(481,263),(552,222),(625,261),(691,226),(751,260),(822,230),(900,249),(900,300),(0,300)],"#193e47")
 for i in range(240):
  x=r.randrange(900);y=r.randrange(238,298)
  box(d,(x,y,x+r.randint(3,8),y+1),r.choice(["#3b6966","#658780","#203e45"]))
 return im
def gravel():
 r=random.Random(400);im=Image.new("RGB",(256,512),"#5a514b");d=ImageDraw.Draw(im)
 for i in range(12000):
  x=r.randrange(256);y=r.randrange(512);w=r.choice([1,1,2,2,3,4])
  box(d,(x,y,x+w,y+(w//3)),r.choice(["#978774","#b3a080","#70695f","#41494b","#d4bb95","#7e7164"]))
 for x in [34,37,40,210,213,216]:
  d.line([(x,0),(x,511)],fill="#595047",width=1)
 return im
def meadow():
 r=random.Random(310);im=Image.new("RGB",(256,256),"#25504e");d=ImageDraw.Draw(im)
 for i in range(3500):
  x=r.randrange(256);y=r.randrange(256)
  box(d,(x,y,x+r.randint(2,11),y+r.randint(1,3)),r.choice(["#204648","#2b5d51","#416e5b","#608463","#55755e"]))
 return im
def flames(n):
 r=random.Random(61+n);im=Image.new("RGBA",(126,68));d=ImageDraw.Draw(im)
 poly(d,[(3,29),(31,17),(49,13),(59,4),(77,19),(98,5),(83,27),(124,33),(85,40),(105,59),(61,46),(46,54),(26,40)],"#de694c")
 poly(d,[(3,29),(32,20),(51,19),(68,13),(64,24),(99,32),(65,36),(82,48),(48,39),(30,44)],"#f3a359")
 poly(d,[(2,30),(34,25),(49,25),(67,29),(76,32),(44,34),(26,37)],"#ffdb8a")
 poly(d,[(2,31),(22,27),(36,29),(52,31),(25,34)],"#8bdad4")
 for i in range(22):
  x=r.randint(40,122);y=r.randint(3,63)
  box(d,(x,y,x+r.randint(1,5),y+r.randint(1,3)),r.choice(["#ffba73","#f17f5e","#ffe7b4"]))
 return im
def dusk_cloud():
 r=random.Random(29);im=Image.new("RGBA",(512,208));d=ImageDraw.Draw(im)
 for x,y in [(71,92),(236,119),(412,77)]:
  for i in range(32):
   xx=x+r.randint(-70,70);yy=y+r.randint(-14,12)
   box(d,(xx,yy,xx+r.randint(11,47),yy+r.randint(4,11)),r.choice(["#3f5264","#627080","#2f4457","#887b80"]))
  for i in range(10):
   xx=x+r.randint(-65,65);yy=y+r.randint(-13,-1)
   box(d,(xx,yy,xx+r.randint(11,32),yy+2),r.choice(["#e5b085","#bd8f82"]))
 return im
def sun():
 im=Image.new("RGBA",(128,128));d=ImageDraw.Draw(im)
 for rad,col in [(57,"#c68f79"),(46,"#e7b185"),(35,"#ffda92")]:
  d.ellipse((64-rad,64-rad,64+rad,64+rad),fill=col)
 for i in range(7):
  y=73+i*6;box(d,(18+i*3,y,110-i*3,y+2),"#d49b7e")
 return im
def dust(n):
 r=random.Random(n+44);im=Image.new("RGBA",(116,56));d=ImageDraw.Draw(im)
 for i in range(25):
  x=r.randint(4,111);y=r.randint(8,49)
  box(d,(x,y,x+r.randint(5,20),y+r.randint(2,5)),r.choice(["#b6a08588","#d2b49877","#86786e88"]))
 return im
def label(t):
 im=Image.new("RGBA",(348,46));d=ImageDraw.Draw(im)
 try:f=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",13)
 except OSError:f=ImageFont.load_default()
 d.text((5,10),t,font=f,fill="#f8e6c8",stroke_width=2,stroke_fill="#172833")
 return im
def refine(im,angle):
 d=ImageDraw.Draw(im)
 if angle=="side":
  d.line([(35,75),(78,69)],fill="#fcf1d8",width=2)
  d.line([(103,35),(149,33)],fill="#f4f0d6",width=1)
  d.line([(42,100),(212,100)],fill="#152936",width=3)
  for x in [43,51,104,114,146,172,201]:
   box(d,(x,88,x+4,89),"#c9d9c2")
  d.line([(110,92),(150,87)],fill="#e6b994",width=2)
 elif angle=="rear":
  d.line([(31,83),(34,99)],fill="#f7a085",width=3)
  d.line([(93,84),(100,103)],fill="#f7a085",width=3)
  d.line([(47,104),(90,106)],fill="#c1d7cb",width=1)
  d.line([(105,113),(191,106)],fill="#112734",width=3)
  d.line([(123,79),(165,69)],fill="#e2e4ce",width=2)
 else:
  d.line([(31,94),(84,95)],fill="#bdddd3",width=2)
  d.line([(101,112),(191,103)],fill="#162936",width=3)
  d.line([(124,78),(172,69)],fill="#e5ead3",width=2)
 return im
def upgrade(out,side,quarter,face):
 for p in range(4):
  for n,im,angle in [("car_side",side(p*22.5),"side"),("car_rear_34",quarter(True,p*22.5),"rear"),("car_front_34",quarter(False,p*22.5),"front")]:
   refine(im,angle).save(out/f"{n}_{p}.png")
 for n,im,angle in [("car_side",side(),"side"),("car_rear_34",quarter(True),"rear"),("car_front_34",quarter(False),"front")]:
  refine(im,angle).save(out/f"{n}.png")
 for i in range(9):pine(i).save(out/f"pine_{i}.png")
 for i in range(7):shrub(i,"bush").save(out/f"bush_{i}.png")
 for i in range(6):shrub(i,"rock").save(out/f"rock_{i}.png")
 for i in range(8):shrub(i,"flowers").save(out/f"flowers_{i}.png")
 for i in range(4):dust(i).save(out/f"dust_{i}.png")
 for i in range(3):flames(i).save(out/f"flame_{i}.png")
 flames(0).save(out/"flame.png")
 gravel().save(out/"road.png")
 meadow().save(out/"ground.png")
 mountain().save(out/"mountains.png")
 dusk_cloud().save(out/"clouds.png")
 sun().save(out/"sun.png")
 label("WHY DO RALLY CARS SPIT FIRE?").save(out/"opening_title.png")
 label("FUEL + OXYGEN + HOT EXHAUST").save(out/"caption_flame.png")
 label("ANTI-LAG KEEPS TURBO SPINNING").save(out/"caption_antilag.png")
 label("EVERY SPARK HAS A STORY").save(out/"final_title.png")
 print("V4 hand-drawn upgrade",len(list(out.glob("*.png"))),"sprites")
