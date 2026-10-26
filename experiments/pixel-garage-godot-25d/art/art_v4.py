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
def wrc_rear(angle=0):
 """Original five-door rally widebody, consistently redrawn for each wheel phase."""
 im=Image.new("RGBA",(246,160));d=ImageDraw.Draw(im)
 C={"ink":"#172735","near":"#192f3b","dark":"#244653","body":"#ede7d8","white":"#fff0d6","mid":"#c0ced0","glass":"#244b5e","highglass":"#66949a","aqua":"#327977","orange":"#ef7053","amber":"#f3c47b","wheel":"#151f2d","rubber":"#222d35","rim":"#a7b7b1","lit":"#faf4dc","shadow":"#273b45"}
 def P(p,c):d.polygon(p,fill=C.get(c,c))
 def L(p,c,w=1):d.line(p,fill=C.get(c,c),width=w)
 def B(a,c):d.rectangle(a,fill=C.get(c,c))
 def E(a,c):d.ellipse(a,fill=C.get(c,c))
 E((15,120,230,147),"#10232f77")
 P([(18,81),(30,66),(46,59),(59,48),(83,34),(112,30),(147,33),(164,42),(185,61),(221,72),(237,83),(240,106),(221,119),(202,125),(50,124),(18,111)],"ink")
 P([(22,85),(40,65),(64,59),(105,54),(158,58),(219,79),(232,87),(233,108),(206,117),(48,116),(23,107)],"dark")
 P([(27,85),(42,70),(67,61),(110,55),(152,58),(213,79),(230,88),(231,106),(205,112),(46,111),(26,105)],"body")
 P([(111,89),(150,74),(207,84),(223,94),(210,111),(140,115),(97,109)],"mid")
 P([(45,68),(52,49),(76,31),(108,23),(146,27),(176,49),(170,64),(98,75)],"ink")
 P([(51,65),(59,49),(80,35),(110,28),(144,31),(167,50),(162,61),(100,70)],"mid")
 P([(55,44),(38,39),(37,33),(118,20),(170,27),(182,36),(111,29)],"ink")
 P([(47,39),(118,25),(168,31)],"amber")
 P([(116,21),(137,21),(145,28),(122,29)],"ink")
 B((122,23,137,25),"aqua")
 P([(39,74),(58,48),(81,40),(97,68),(67,78)],"ink")
 P([(45,72),(61,50),(79,44),(91,67),(65,74)],"glass")
 L([(59,52),(79,45)],"highglass",2)
 L([(47,70),(63,53)],"highglass",1)
 P([(97,40),(108,33),(140,34),(159,50),(151,63),(112,67)],"ink")
 P([(103,42),(113,37),(138,38),(153,51),(147,60),(115,63)],"glass")
 L([(111,39),(137,40)],"highglass",2)
 P([(95,41),(101,40),(117,66),(109,68)],"ink")
 P([(23,82),(39,70),(79,73),(95,85),(95,110),(46,114),(23,106)],"ink")
 P([(29,82),(41,75),(76,77),(88,86),(89,100),(44,104),(30,101)],"glass")
 L([(42,78),(76,80)],"highglass",2)
 P([(23,85),(30,82),(34,101),(24,104)],"orange")
 P([(88,88),(96,90),(97,106),(89,105)],"orange")
 B((25,91,29,97),"amber")
 B((89,93,92,100),"amber")
 P([(30,106),(95,109),(98,116),(38,119)],"near")
 B((52,107,79,113),"white")
 B((57,109,76,112),"ink")
 P([(108,77),(137,70),(173,71),(206,81),(229,91),(194,98),(152,91)],"aqua")
 P([(137,78),(174,72),(211,83),(204,95),(164,92)],"amber")
 P([(168,76),(187,77),(201,85),(190,94),(174,88)],"orange")
 P([(106,99),(149,94),(205,104),(225,102),(204,112),(105,115)],"aqua")
 L([(112,73),(149,66),(189,73),(224,86)],"white",2)
 L([(107,97),(123,104),(122,113)],"shadow")
 L([(160,80),(162,109)],"shadow")
 L([(102,114),(206,114)],"near",3)
 B((151,91,162,93),"ink")
 B((152,90,161,90),"white")
 P([(172,65),(179,58),(186,60),(187,66)],"ink")
 for x,y,rad in [(68,121,22),(178,124,18)]:
  E((x-rad-6,y-rad-6,x+rad+6,y+rad+5),"ink")
  E((x-rad-2,y-rad-2,x+rad+2,y+rad+2),"rubber")
  E((x-rad+5,y-rad+5,x+rad-5,y+rad-5),"rim")
  E((x-rad+8,y-rad+8,x+rad-8,y+rad-8),"shadow")
  for a in range(0,360,45):
   theta=math.radians(a+angle);r=rad-6
   xx=int(r*math.cos(theta));yy=int(r*math.sin(theta))
   L([(x-xx,y-yy),(x+xx,y+yy)],"rim",2)
  E((x-5,y-5,x+5,y+5),"ink")
  E((x-2,y-2,x+2,y+2),"white")
 P([(38,115),(49,117),(48,140),(36,136)],"orange")
 P([(203,120),(211,118),(213,139),(201,136)],"near")
 B((27,116,41,121),"ink")
 B((32,118,41,121),"rim")
 B((19,108,25,113),"amber")
 return im

def recolor_car(im):
 pixels=im.load()
 replacements={(211,244,107):(238,189,111),(93,148,125):(46,119,122),(237,105,87):(238,101,75),(231,245,232):(231,224,205),(244,233,208):(252,239,215)}
 for y in range(im.height):
  for x in range(im.width):
   p=pixels[x,y]
   if len(p)>3 and p[3]>0 and p[:3] in replacements:pixels[x,y]=(*replacements[p[:3]],p[3])
 return im

def refine(im,angle):
 im=recolor_car(im)
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
  for n,im,angle in [("car_side",side(p*22.5),"side"),("car_rear_34",wrc_rear(p*22.5),"rear"),("car_front_34",quarter(False,p*22.5),"front")]:
   refine(im,angle).save(out/f"{n}_{p}.png")
 for n,im,angle in [("car_side",side(),"side"),("car_rear_34",wrc_rear(),"rear"),("car_front_34",quarter(False),"front")]:
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
