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



# === V2 NEW ART ASSETS ===
# Original 3/4-view rally sprite + independently placed scenery.
# Earlier side-view assets above are generated but NOT used by V2.
def new_v2(w,h):return Image.new("RGBA",(w,h),(0,0,0,0))
def L(d,a,b,c,w=1):d.line([a,b],fill=c,width=w)
N="#1b303b";T="#287883";WHT="#f4edd5";OR="#f69b5e"
def draw_rally_v2(frame):
    im=new_v2(270,208);d=ImageDraw.Draw(im)
    d.ellipse((24,164,255,190),fill=(27,40,40,75))
    for x,y,r in [(65,153,17),(129,166,23),(224,169,20)]:
        d.ellipse((x-r,y-r,x+r,y+r),fill=N)
    poly(d,[(33,126),(43,84),(72,64),(127,70),(174,80),(210,103),(240,113),(249,144),(242,157),(215,167),(145,165),(97,157),(42,148)],N)
    poly(d,[(123,83),(159,81),(203,104),(232,112),(242,130),(237,146),(211,153),(164,139),(121,131)],WHT)
    poly(d,[(124,130),(164,137),(197,145),(235,143),(227,158),(190,152),(153,147),(124,143)],T)
    poly(d,[(40,94),(67,78),(126,83),(129,135),(113,146),(52,139),(35,126)],"#d7d4b7")
    poly(d,[(45,96),(66,87),(119,92),(122,129),(114,137),(51,131),(43,126)],WHT)
    # The angled hatchback roof, rear glass and side glass are authored at consistent camera angle.
    poly(d,[(50,86),(69,50),(104,39),(160,43),(208,78),(215,104),(126,92)],N)
    poly(d,[(59,85),(77,54),(107,45),(158,48),(200,77),(207,100),(127,87)],WHT)
    poly(d,[(72,54),(106,42),(159,45),(202,76),(192,79),(158,53),(109,49),(74,62)],"#fff5d9")
    poly(d,[(62,81),(82,55),(109,52),(126,58),(124,92),(55,89)],N)
    poly(d,[(68,78),(83,61),(109,58),(118,63),(119,85),(61,84)],"#254b5a")
    poly(d,[(84,59),(107,59),(93,70),(72,72)],"#68949d")
    poly(d,[(131,60),(156,56),(197,80),(205,101),(143,90),(126,86)],N)
    poly(d,[(138,64),(156,61),(180,76),(170,88),(136,82)],"#315969")
    poly(d,[(161,62),(197,81),(199,94),(175,87),(184,78)],"#628f94")
    poly(d,[(150,62),(157,63),(180,90),(172,88)],WHT)
    poly(d,[(183,74),(188,77),(197,97),(191,95)],"#d3d3b9")
    # Motorsport livery carries around rear and side (no generic boxy panel).
    poly(d,[(145,98),(178,103),(209,112),(233,125),(230,134),(194,125),(162,117),(137,112)],T)
    poly(d,[(148,103),(176,106),(217,119),(230,126),(216,126),(176,114)],"#5aa393")
    poly(d,[(164,113),(192,113),(217,125),(208,135),(186,125)],OR)
    poly(d,[(187,119),(220,128),(213,135),(199,131)],"#eac074")
    poly(d,[(156,122),(182,127),(184,143),(156,139)],WHT)
    d.text((162,127),"7",fill=N)
    L(d,(152,92),(151,142),"#90a89e",2);L(d,(184,103),(189,144),"#a9ada1",1)
    rect(d,(153,108,165,111),N);rect(d,(191,116,204,119),N)
    poly(d,[(46,110),(116,120),(120,128),(49,124)],"#315b62")
    rect(d,(43,106,54,119),"#d65c50");rect(d,(43,109,52,112),"#ffbca1")
    poly(d,[(109,117),(123,119),(122,135),(110,132)],"#db6257")
    poly(d,[(52,127),(118,136),(111,147),(47,138)],T)
    poly(d,[(65,137),(102,143),(98,148),(65,142)],N)
    rect(d,(40,146,66,152),N);rect(d,(46,149,60,153),"#b2b4ac")
    poly(d,[(72,130),(97,133),(97,140),(70,136)],WHT)
    d.text((79,131),"RX",fill=N)
    # Wheel arches cut a physical opening for the near-side rotating wheel sprites.
    for x,y,r in [(129,166,23),(225,170,20)]:
        d.ellipse((x-r-3,y-r-4,x+r+3,y+r+2),fill=N)
        d.ellipse((x-r,y-r,x+r,y+r),fill="#172a32")
        d.ellipse((x-r+4,y-r+4,x+r-4,y+r-4),fill="#abbdb5")
        d.ellipse((x-r+7,y-r+7,x+r-7,y+r-7),fill="#28424a")
        for j in range(6):
            a=frame*math.pi/4+j*math.pi/3
            L(d,(x,y),(int(x+(r-9)*math.cos(a)),int(y+(r-9)*math.sin(a))),"#f6f1d8",2)
        d.ellipse((x-4,y-4,x+4,y+4),fill="#38565b")
    # Wide rear spoiler, roof scoop and black side mirror.
    poly(d,[(38,60),(123,64),(133,71),(38,67)],N)
    poly(d,[(48,55),(120,59),(124,65),(47,61)],"#345b68")
    rect(d,(53,63,59,80),N);rect(d,(115,65,121,81),N)
    poly(d,[(129,45),(143,36),(164,36),(176,47)],N)
    poly(d,[(141,41),(165,41),(171,46),(139,45)],"#577a7d")
    poly(d,[(136,92),(151,91),(154,95),(149,102),(139,101)],N)
    save(im,"rally_"+str(frame))
for k in range(8):draw_rally_v2(k)
# Sprite3D pine illustrations. Each is a separately textured card at a real world Z.
for idx in range(5):
    rr=random.Random(317+idx);im=new_v2(120,230);d=ImageDraw.Draw(im)
    tx=58+rr.randint(-6,6)
    rect(d,(tx-7,105,tx+8,229),"#4b4c40")
    rect(d,(tx-4,118,tx+1,219),"#997d58")
    pal=[("#1b4a4a","#286960","#538774","#9eac89"),("#204d4c","#2b6d5e","#579479","#c1bb87"),("#235353","#357368","#679479","#a5b67b"),("#1a474a","#285d55","#478071","#91a98b"),("#20494c","#387363","#679480","#b6be91")][idx]
    for j in range(6):
        y=18+j*25+rr.randint(-4,5);wide=14+j*8+rr.randint(-4,4)
        poly(d,[(tx,y-12),(tx-wide,y+40),(tx+wide*.14,y+33),(tx+wide,y+40)],pal[0])
        poly(d,[(tx,y-10),(tx-wide*.75,y+34),(tx-wide*.43,y+30),(tx+wide*.07,y+36)],pal[1])
        for _ in range(10):
            xx=tx+rr.randint(-wide+8,max(1,wide//2))
            yy=y+rr.randint(13,38)
            rect(d,(xx,yy,xx+rr.randint(2,7),yy+rr.randint(2,4)),rr.choice(pal[1:]))
    save(im,"pine_"+str(idx))
for idx in range(4):
    rr=random.Random(81+idx);im=new_v2(130,64);d=ImageDraw.Draw(im)
    for _ in range(14):
        x=rr.randrange(5,126);y=rr.randrange(21,54);r=rr.randrange(7,19)
        poly(d,[(x-r,y+r//2),(x-r//2,y-r//2),(x,y-r),(x+r//2,y-r//2),(x+r,y+r//2),(x,y+r)],rr.choice(["#305f59","#3e7766","#698d74","#a2ad83"]))
    for _ in range(14):
        x=rr.randrange(6,120);y=rr.randrange(14,49)
        rect(d,(x,y,x+3,y+2),rr.choice(["#f6c38d","#f9e0a1","#c4c595"]))
    save(im,"shrub_"+str(idx))
for idx in range(4):
    im=new_v2(80,55);d=ImageDraw.Draw(im)
    poly(d,[(4,42),(11,23),(27,8),(49,11),(71,32),(67,47),(22,49)],"#273d44")
    poly(d,[(12,27),(29,10),(47,14),(38,31),(19,38)],"#83938b")
    poly(d,[(49,13),(70,33),(65,43),(38,37)],"#486163")
    save(im,"rock_"+str(idx))
# Continuous road and grass tile textures for real perspective ground.
rr=random.Random(654)
im=Image.new("RGB",(256,256),"#7e7569");d=ImageDraw.Draw(im)
for _ in range(4200):
    x=rr.randrange(256);y=rr.randrange(256)
    rect(d,(x,y,x+rr.choice([1,2,3,4]),y+rr.choice([1,1,2])),rr.choice(["#aa9980","#555c58","#736c60","#d0b18b","#606960","#9c8c79"]))
for x0 in (75,186):
    for y in range(0,256,3):
        xx=x0+int(5*math.sin(y*.035))
        rect(d,(xx-12,y,xx+11,y+1),"#6a665b")
save(im,"gravel")
im=Image.new("RGB",(256,256),"#4b745d");d=ImageDraw.Draw(im)
for _ in range(1600):
    x=rr.randrange(256);y=rr.randrange(256)
    d.line([(x,y+3),(x+rr.randint(-2,2),y-rr.randint(2,9))],fill=rr.choice(["#3e6a5b","#60836b","#9aab74","#c4b88e"]),width=1)
save(im,"grass")
# Distant mountains painted as a 2D backdrop, behind all perspective objects.
im=Image.new("RGB",(360,640));d=ImageDraw.Draw(im)
cs=["#344d64","#486a7b","#6c8587","#9b9691","#c7a18f","#e9b391","#f4c6a4"]
for y in range(640):d.line([(0,y),(359,y)],fill=cs[min(6,max(0,int((y-35)/66)))])
for rad,col in [(53,"#d8ac8c"),(40,"#e9ba93"),(29,"#ffe0ab")]:
    d.ellipse((258-rad,154-rad,258+rad,154+rad),fill=col)
poly(d,[(0,318),(41,266),(68,302),(115,231),(152,287),(198,237),(240,308),(295,253),(360,313),(360,395),(0,395)],"#6c8986")
poly(d,[(113,233),(90,259),(108,252),(119,260),(126,246)],"#eee1c7")
poly(d,[(295,254),(280,276),(293,269),(301,276),(311,270)],"#e7dec5")
poly(d,[(0,350),(65,304),(113,323),(178,290),(225,334),(278,304),(360,341),(360,431),(0,431)],"#456b68")
save(im,"sky")
for k in range(4):
    im=new_v2(126,56);d=ImageDraw.Draw(im);r2=random.Random(k+551)
    for _ in range(21):
        x=r2.randrange(6,114);y=r2.randrange(10,47);rad=r2.randrange(3,13)
        d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=r2.choice(["#8b8a7c","#b6a792","#a9b0a0"]))
    im.putalpha(im.getchannel("A").point(lambda a:min(95,a)))
    save(im,"dust_"+str(k))
print("Original 3/4 sprite, trees, grass, rock, dust, sky and gravel for V2 complete")


# FINAL hand-illustrated perspective refinement. Compress the receding nose
# of every same-source sprite, not the 3D engine's output.
for k in range(8):
    pth=os.path.join(OUT,"rally_%d.png" % k)
    src=Image.open(pth).convert("RGBA")
    dest=Image.new("RGBA",src.size,(0,0,0,0))
    inp=src.load();out=dest.load()
    for y in range(src.height):
        for x in range(src.width):
            color=inp[x,y]
            if color[3]==0:continue
            if x<120:
                xx=x+19; yy=y
            else:
                xx=139+round((x-120)*.64)
                yy=y-round((x-120)*.28)
            if 0<=xx<src.width and 0<=yy<src.height:out[xx,yy]=color
    dest.save(pth)


# V2's distinct final palette: blue rally hatch and autumn roadside, no copy
# of the earlier cream/teal car or pine mountain scene.
replacements = {
    (244,237,212):(119,186,215), (255,242,217):(189,224,226),
    (215,213,185):(77,139,163), (40,121,130):(38,70,115),
    (49,95,103):(35,71,103), (62,155,146):(58,122,163),
    (255,152,90):(246,192,74)
}
for k in range(8):
    p=os.path.join(OUT,"rally_%d.png" % k)
    im=Image.open(p).convert("RGBA");px=im.load()
    for yy in range(im.height):
        for xx in range(im.width):
            r,g,b,a=px[xx,yy]
            if (r,g,b) in replacements:px[xx,yy]=(*replacements[r,g,b],a)
    im.save(p)
for idx in range(5):
    rr=random.Random(404+idx)
    im=Image.new("RGBA",(120,230),(0,0,0,0))
    d=ImageDraw.Draw(im);bx=58+rr.randrange(-6,7)
    rect(d,(bx-6,107,bx+7,228),"#624b3a")
    rect(d,(bx-4,114,bx,222),"#ad8555")
    for sx,sy in [(-23,108),(29,112),(-11,84),(12,70)]:
        d.line((bx,151,bx+sx,sy),fill="#715f46",width=5)
    pal=[
    ["#456c56","#698760","#9fa370","#e2b66d"],
    ["#526b4f","#82905b","#b4a05f","#e1ac58"],
    ["#465c52","#688668","#ac9c6c","#deb067"],
    ["#4c6553","#708960","#af9d61","#e4b46c"],
    ["#3c6b5f","#678a6f","#a8ad79","#ddba6f"]
    ][idx]
    for cx,cy,rx,ry in [(bx,56,31,37),(bx-25,91,31,35),(bx+22,91,30,36),(bx,115,35,27)]:
        poly(d,[(cx-rx,cy),(cx-rx+6,cy-ry//2),(cx-17,cy-ry),(cx+16,cy-ry),(cx+rx,cy-ry//3),(cx+rx+3,cy+ry//3),(cx+rx//2,cy+ry),(cx-rx//2,cy+ry)],pal[0])
        for j in range(48):
            xx=cx+rr.randrange(-rx+4,rx-2);yy=cy+rr.randrange(-ry+4,ry-1)
            if abs(xx-cx)+abs(yy-cy)>rx+ry//2:continue
            rect(d,(xx,yy,xx+rr.randrange(2,7),yy+rr.randrange(2,5)),rr.choice(pal[1:]))
    save(im,"pine_"+str(idx))
im=Image.new("RGB",(360,640));d=ImageDraw.Draw(im)
sky=["#344f6d","#456b7d","#688e91","#96a9a0","#c2b6a0","#e6c7a5","#edcfad"]
for y in range(640):
    d.line((0,y,360,y),fill=sky[min(6,max(0,int((y-30)/75)))])
for rad,c in [(25,"#dfc69c"),(17,"#f0d8a7"),(10,"#fff0bc")]:
    d.ellipse((290-rad,160-rad,290+rad,160+rad),fill=c)
poly(d,[(0,355),(35,325),(77,341),(132,301),(182,342),(244,320),(299,344),(360,314),(360,640),(0,640)],"#668e87")
poly(d,[(0,381),(57,344),(98,366),(148,340),(221,372),(287,345),(360,370),(360,640),(0,640)],"#6d9180")
for j in range(60):
    x=rng.randrange(360);y=rng.randrange(361,430)
    rect(d,(x,y,x+rng.randrange(2,5),y+rng.randrange(1,3)),rng.choice(["#b7b493","#a39d76","#6c8c6e"]))
save(im,"sky")
print("V2 distinct autumn countryside and blue angled sprite assets built")


# Correct exact generated car palette values from this branch (distinct from
# the local exploratory draft), so the final film actually has blue bodywork.
exact_colours = {
    (244,237,213):(119,186,215),
    (255,245,217):(189,224,226),
    (215,212,183):(77,139,163),
    (40,120,131):(38,70,115),
    (49,91,98):(35,71,103),
    (90,163,147):(58,122,163),
    (246,155,94):(246,192,74),
}
for k in range(8):
    path=os.path.join(OUT,"rally_%d.png" % k)
    im=Image.open(path).convert("RGBA");pixels=im.load()
    for yy in range(im.height):
        for xx in range(im.width):
            r,g,b,a=pixels[xx,yy]
            new_rgb=exact_colours.get((r,g,b))
            if new_rgb is not None:pixels[xx,yy]=(*new_rgb,a)
    im.save(path)
