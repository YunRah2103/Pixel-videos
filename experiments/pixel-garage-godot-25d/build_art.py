#!/usr/bin/env python3
"""Original 2D pixel-art texture builder. No low-poly 3D or pixelation filter."""
from PIL import Image, ImageDraw
import random, math, os
rng=random.Random(2067)
OUT=os.path.join(os.path.dirname(__file__),"assets")
os.makedirs(OUT,exist_ok=True)
W,H=1800,640
def save(im,n): im.save(os.path.join(OUT,n+".png"))
def poly(d,p,c): d.polygon([(int(x),int(y)) for x,y in p],fill=c)
def rect(d,x,c): d.rectangle(tuple(map(int,x)),fill=c)
def pine(d,x,y,s,c,highlight=True):
    s=max(18,s)
    rect(d,(x-s*.03,y-s*.68,x+s*.03,y),"#384b47")
    for j in range(5):
        v=y-s*.88+j*s*.17; half=s*(.12+.105*j)
        poly(d,[(x,v-s*.22),(x-half,v+s*.22),(x-half*.65,v+s*.18),(x-half*.95,v+s*.31),(x+half*.96,v+s*.31),(x+half*.64,v+s*.18),(x+half,v+s*.22)],c)
        if highlight:
            poly(d,[(x,v-s*.21),(x-half*.8,v+s*.18),(x-half*.28,v+s*.12),(x,v+s*.06)],"#5b8b73")
            rect(d,(x-half*.4,v+s*.15,x-half*.24,v+s*.2),"#99a781")
def mountain(d,x,peak):
    poly(d,[(x-240,369),(x-42,peak+46),(x,peak),(x+100,peak+92),(x+240,369)],"#607f85")
    poly(d,[(x,peak),(x+100,peak+92),(x+241,369),(x+9,351)],"#76918d")
    poly(d,[(x-39,peak+49),(x,peak),(x+24,peak+29),(x+8,peak+24),(x-8,peak+34),(x-26,peak+27)],"#e1d3ba")
def blank():return Image.new("RGBA",(W,H),(0,0,0,0))
im=blank(); d=ImageDraw.Draw(im)
palette=["#6f939a","#7b9b9c","#8fa7a0","#a7afa0","#c3af96","#dfa98a","#efb38a","#eeb693"]
for y in range(450):rect(d,(0,y,W,y),palette[min(7,y//57)])
for r,col in [(58,"#f0b48e"),(48,"#f5bf8e"),(35,"#ffe0a1")]:d.ellipse((304-r,177-r,304+r,177+r),fill=col)
for x,y,w in [(120,109,84),(470,149,65),(820,83,101),(1500,108,81)]:
    rect(d,(x,y+12,x+w,y+27),"#e6ccae")
    rect(d,(x+15,y,x+w-14,y+24),"#f9d9ad")
for j in range(5):rect(d,(0,247+j*6,W,249+j*6),"#d4aa90")
save(im,"sky")
im=blank();d=ImageDraw.Draw(im)
for x,p in [(-80,200),(238,173),(545,222),(860,147),(1150,198),(1480,154),(1780,200)]:mountain(d,x,p)
poly(d,[(0,340),(150,307),(281,330),(435,286),(623,346),(831,303),(1004,338),(1258,289),(1487,316),(1685,294),(W,319),(W,406),(0,406)],"#6a8882")
save(im,"mountains")
im=blank();d=ImageDraw.Draw(im)
poly(d,[(0,357),(125,340),(250,352),(400,321),(590,350),(820,322),(970,351),(1180,329),(1350,351),(1580,318),(W,350),(W,435),(0,435)],"#406760")
for _ in range(150):
    x=rng.randrange(W);y=rng.randrange(360,401);s=rng.randrange(23,66)
    pine(d,x,y+s*.3,s,rng.choice(["#345d59","#3c655d","#436e62"]),False)
save(im,"farforest")
im=blank();d=ImageDraw.Draw(im)
poly(d,[(0,400),(210,395),(470,412),(720,388),(1090,406),(1360,391),(W,405),(W,445),(0,445)],"#466853")
for i in range(67):
    pine(d,int(i*29+rng.randrange(-12,15)),rng.randrange(406,449),rng.randrange(56,138),rng.choice(["#285451","#315d56","#3d665a","#31594f"]))
for _ in range(90):
    x=rng.randrange(W);y=rng.randrange(423,448)
    rect(d,(x,y,x+rng.randrange(2,7),y+rng.randrange(2,5)),rng.choice(["#b3b18e","#8ca381","#56725c"]))
save(im,"nearforest")
im=blank();d=ImageDraw.Draw(im)
rect(d,(0,436,W,548),"#635f58");rect(d,(0,436,W,445),"#988573")
rect(d,(0,445,W,454),"#797067");rect(d,(0,527,W,548),"#494d49")
for _ in range(2650):
    x=rng.randrange(W);y=rng.randrange(442,542)
    rect(d,(x,y,x+rng.choice([1,2,3,4,6]),y+rng.choice([1,1,2])),rng.choice(["#898379","#a39b83","#3c4846","#c0aa86","#67635b","#4c5350"]))
save(im,"road")
im=blank();d=ImageDraw.Draw(im)
rect(d,(0,537,W,640),"#3a6855")
for y,c in [(546,"#60835d"),(557,"#557d5b"),(590,"#2e5d52"),(610,"#254f4a")]:rect(d,(0,y,W,y+9),c)
for _ in range(1100):
    x=rng.randrange(W);y=rng.randrange(542,640);h=rng.randrange(3,16)
    d.line([(x,y),(x+rng.randint(-3,2),y-h)],fill=rng.choice(["#a1aa77","#6c9166","#90aa79","#355c51"]),width=1)
for _ in range(175):
    x=rng.randrange(W);y=rng.randrange(548,640)
    for ox,oy in [(0,-2),(-2,0),(2,0),(0,2)]:rect(d,(x+ox,y+oy,x+ox+1,y+oy+1),rng.choice(["#e7c68d","#f4d5ac","#e1a58b"]))
save(im,"foreground")
# Side-facing five-door hatchback: drawn as original clusters, never from a 3D filter.
im=Image.new("RGBA",(318,138));d=ImageDraw.Draw(im)
ink="#172938";car="#f4ecd1";teal="#1e666a"
poly(d,[(25,88),(30,59),(50,54),(69,34),(98,20),(189,17),(215,27),(242,51),(274,58),(292,67),(301,86),(294,100),(267,106),(255,105),(234,95),(98,95),(72,105),(51,107),(25,99)],ink)
poly(d,[(30,88),(37,62),(53,56),(69,36),(98,24),(190,21),(212,31),(239,55),(272,62),(292,70),(296,88),(286,96),(265,98),(249,87),(93,88),(76,99),(51,100),(32,96)],car)
poly(d,[(71,38),(97,21),(188,17),(212,26),(211,32),(184,24),(100,27),(79,43)],"#fff3df")
poly(d,[(47,42),(80,34),(93,37),(58,45)],ink)
poly(d,[(49,42),(77,36),(87,38),(60,44)],teal)
for pts in [[(63,55),(82,40),(98,29),(121,28),(118,60),(68,65)],[(123,29),(185,27),(205,33),(223,55),(119,59)]]:
    poly(d,pts,"#203746")
poly(d,[(80,44),(98,31),(115,31),(112,57),(71,60)],"#385968")
poly(d,[(130,33),(182,32),(202,37),(216,53),(127,54)],"#385968")
poly(d,[(84,43),(99,33),(106,33),(90,49)],"#638d98")
poly(d,[(137,34),(172,34),(156,44),(131,44)],"#638b93")
poly(d,[(183,34),(202,39),(210,49),(200,49)],"#8cacad")
poly(d,[(114,29),(122,28),(120,61),(113,60)],"#d3d1bd")
poly(d,[(182,27),(188,26),(211,56),(204,57)],"#d9d5bd")
d.line([(121,59),(119,89)],fill="#7a9c98")
d.line([(202,60),(204,90)],fill="#8aaba3")
poly(d,[(36,74),(105,71),(135,85),(109,90),(41,85)],teal)
poly(d,[(119,73),(192,67),(239,76),(260,86),(211,88),(169,80)],teal)
poly(d,[(138,67),(181,65),(232,71),(258,78),(224,79),(183,73)],"#ef9456")
poly(d,[(199,77),(261,83),(259,89),(220,85)],"#c9604d")
rect(d,(137,65,169,85),"#f7e7b9")
d.text((145,69),"07",fill=ink)
poly(d,[(270,66),(291,72),(293,76),(265,74)],"#fceac0")
rect(d,(289,94,305,100),"#304a4c")
rect(d,(30,69,38,83),"#dd6755")
rect(d,(24,91,41,97),ink)
rect(d,(104,92,219,98),"#203746")
poly(d,[(98,98),(224,98),(220,105),(101,105)],"#273e42")
poly(d,[(209,58),(219,54),(229,56),(224,62),(211,62)],ink)
poly(d,[(143,22),(150,13),(179,13),(184,22)],ink)
rect(d,(151,17,176,20),"#7d9a90")
rect(d,(28,104,52,108),"#73878a")
for x in (81,244):
    d.pieslice((x-24,78,x+24,126),180,360,fill=ink)
    d.pieslice((x-20,83,x+20,123),180,360,fill=(0,0,0,0))
    d.arc((x-23,80,x+23,126),180,352,fill="#49676a",width=3)
save(im,"car_body")
im=Image.new("RGBA",(51,51));d=ImageDraw.Draw(im)
for b,c in [((1,1,49,49),"#161f2a"),((4,4,46,46),"#2a3038"),((8,8,42,42),"#c9d2c8"),((11,11,39,39),"#36464a"),((15,15,35,35),"#c2cecb")]:d.ellipse(b,fill=c)
for a in range(0,360,45):
    d.line([(25,25),(25+14*math.cos(math.radians(a)),25+14*math.sin(math.radians(a)))],fill="#f4f1db",width=3)
d.ellipse((21,21,29,29),fill="#264a51")
save(im,"wheel")
for j,length in enumerate([54,77,63,39]):
    im=Image.new("RGBA",(85,37));d=ImageDraw.Draw(im);cy=18
    poly(d,[(84,8),(84-length*.35,9),(84-length*.74,13),(84-length,17),(84-length*.79,23),(84-length*.3,26),(84,25)],"#dc6248")
    poly(d,[(84,11),(84-length*.33,12),(84-length*.72,17),(84-length*.35,24),(84,22)],"#f9a350")
    poly(d,[(84,14),(84-length*.36,15),(84-length*.52,18),(84-length*.17,21),(84,20)],"#fff0a5")
    save(im,"flame_"+str(j))
print("Generated: sky, mountains, two forests, road, foreground, car body, wheel, 4 flame sprites.")
