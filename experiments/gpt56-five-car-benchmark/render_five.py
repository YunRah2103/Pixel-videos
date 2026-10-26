#!/usr/bin/env python3
import json, math, os, random, struct, subprocess, wave
from pathlib import Path
from PIL import Image, ImageDraw

W, H, FPS, DUR = 270, 480, 30, 8
FRAMES = FPS * DUR
OUT = Path("out/gpt56-five-car-benchmark")
OUT.mkdir(parents=True, exist_ok=True)

def clamp(v,a,b): return max(a,min(b,v))
def lerp(a,b,t): return a+(b-a)*t
def ease(t):
    t=clamp(t,0,1)
    return t*t*(3-2*t)

def rect(d, box, fill):
    d.rectangle(tuple(int(x) for x in box), fill=fill)

def poly(d, pts, fill):
    d.polygon([(int(x),int(y)) for x,y in pts], fill=fill)

def line(d, pts, fill, width=1):
    d.line([(int(x),int(y)) for x,y in pts], fill=fill, width=width)

def circle(d, cx, cy, r, fill):
    d.ellipse((int(cx-r),int(cy-r),int(cx+r),int(cy+r)), fill=fill)

def banded_sky(img, top, bottom, horizon=300, bands=12):
    d=ImageDraw.Draw(img)
    def hx(c): return tuple(int(c[i:i+2],16) for i in (1,3,5))
    a,b=hx(top),hx(bottom)
    for i in range(bands):
        t=i/max(1,bands-1)
        c=tuple(int(lerp(a[j],b[j],t)) for j in range(3))
        y0=int(horizon*i/bands); y1=int(horizon*(i+1)/bands)+1
        d.rectangle((0,y0,W,y1),fill=c)

def draw_wheel(d,cx,cy,r,phase,tyre="#121318",rim="#aeb4bd",hub="#30343a",accent=None):
    circle(d,cx,cy,r,tyre)
    circle(d,cx,cy,r-3,"#2c3037")
    circle(d,cx,cy,r-6,rim)
    circle(d,cx,cy,r-9,"#20242b")
    spokes=6
    for k in range(spokes):
        a=phase + k*math.tau/spokes
        x2=cx+math.cos(a)*(r-7); y2=cy+math.sin(a)*(r-7)
        line(d,[(cx,cy),(x2,y2)],rim,2)
    circle(d,cx,cy,3,accent or hub)
    rect(d,(cx-r+2,cy-r+4,cx-r+4,cy-r+9),"#414750")
    rect(d,(cx-r+4,cy+r-2,cx+r-4,cy+r),"#090a0c")

def draw_shadow(d,x,y,w,h,alpha_like="#15151a"):
    poly(d,[(x-w*.52,y),(x+w*.52,y),(x+w*.42,y+h),(x-w*.42,y+h)],alpha_like)

def moving_hash(seed, frame, count):
    rng=random.Random(seed*1000003 + frame*97)
    return [(rng.randrange(W),rng.randrange(H),rng.random()) for _ in range(count)]

def render_rally(f):
    img=Image.new("RGB",(W,H),"#89b6d6"); d=ImageDraw.Draw(img)
    banded_sky(img,"#8fd0f0","#e6d1a0",260,14)
    off=(f*0.25)%W
    for base, col, amp, step in [(250,"#607a67",24,42),(278,"#405f4d",32,36)]:
        pts=[(-20,base)]
        for x in range(-20,W+60,step):
            xx=x-off%step
            yy=base-int((math.sin((x+20)*.09)+1)*amp*.45)
            pts.append((xx,yy))
        pts += [(W+20,base+70),(-20,base+70)]
        poly(d,pts,col)
    for layer,(speed,base,col,trunk) in enumerate([(0.8,320,"#2f513a","#4d3a2b"),(1.6,350,"#1f3d2e","#3b2b24")]):
        spacing=30 if layer==0 else 24
        shift=int((f*speed)%spacing)
        for i in range(-2,14):
            x=i*spacing-shift
            h=48+(i*17+layer*13)%35
            rect(d,(x+7,base-h+20,x+10,base),trunk)
            poly(d,[(x,base-h+28),(x+9,base-h),(x+18,base-h+28)],col)
            poly(d,[(x-4,base-h+42),(x+9,base-h+13),(x+22,base-h+42)],col)
    rect(d,(0,340,W,H),"#615849")
    rect(d,(0,340,W,348),"#877b63")
    rect(d,(0,410,W,H),"#4f493f")
    for x,y,q in moving_hash(9,f,55):
        yy=350 + (y%120)
        xx=(x-int(f*5.2))%W
        c="#817562" if q>.55 else "#514a40"
        rect(d,(xx,yy,xx+2+(q>.8),yy+1),c)
    if f>25:
        for i in range(26):
            age=(f*6+i*19)%170
            x=122-age*1.15
            y=381+(i*13%35)-age*.08
            r=max(1,int(5-age/45))
            if r>0 and x>-15: circle(d,x,y,r,"#9b8a6a")
    t=f/FPS
    jump=max(0,1-abs(t-4.1)/0.55)
    jump=ease(jump)
    body_y=362 - 14*jump + math.sin(f*.42)*1.2
    x=139 + math.sin(f*.035)*3
    draw_shadow(d,x,404,97*(1-.28*jump),7,"#302d28")
    phase=f*.62
    rear=(x-54,body_y+29); front=(x+48,body_y+29)
    draw_wheel(d,*rear,16,phase,accent="#d84b3f")
    draw_wheel(d,*front,16,phase,accent="#d84b3f")
    poly(d,[(x-69,body_y+24),(x-62,body_y+5),(x-35,body_y-12),(x+20,body_y-14),
            (x+49,body_y-2),(x+65,body_y+12),(x+62,body_y+28),(x+45,body_y+31),
            (x-52,body_y+31)],"#d9e0e2")
    poly(d,[(x-60,body_y+7),(x-34,body_y-10),(x-24,body_y-32),(x+16,body_y-31),
            (x+35,body_y-15),(x+20,body_y-12),(x-35,body_y-12)],"#f2f4f0")
    poly(d,[(x-25,body_y-28),(x-4,body_y-29),(x-4,body_y-13),(x-31,body_y-13)],"#2b4050")
    poly(d,[(x,body_y-29),(x+14,body_y-28),(x+31,body_y-15),(x,body_y-14)],"#314d60")
    poly(d,[(x-55,body_y+4),(x-4,body_y+5),(x+15,body_y+24),(x-50,body_y+24)],"#315b91")
    poly(d,[(x+15,body_y+7),(x+57,body_y+9),(x+51,body_y+24),(x+26,body_y+24)],"#d64c3f")
    rect(d,(x-14,body_y-8,x+3,body_y+9),"#f3e8d3")
    rect(d,(x-9,body_y-5,x-2,body_y+4),"#1d2631")
    rect(d,(x+53,body_y+5,x+64,body_y+10),"#f3d384")
    rect(d,(x-68,body_y+10,x-59,body_y+14),"#bb2631")
    rect(d,(x-55,body_y+28,x+50,body_y+31),"#20242b")
    rect(d,(x-29,body_y-35,x+8,body_y-32),"#252a2f")
    poly(d,[(x-66,body_y+4),(x-53,body_y+1),(x-53,body_y-4),(x-70,body_y-1)],"#2c3238")
    for i in range(8):
        a=(f*11+i*29)%80
        px=x-57-a*.9; py=body_y+39+(i%4)*3-a*.12
        if px>0: rect(d,(px,py,px+2,py+2),"#b7a178")
    shift=int((f*7.5)%190)
    for bx in (-30+shift,160+shift):
        bx%=380; bx-=60
        rect(d,(bx,245,bx+8,H),"#2a2723")
        poly(d,[(bx-35,285),(bx+4,215),(bx+43,285)],"#173525")
    rect(d,(12,16,112,31),"#10161b")
    d.text((17,19),"RALLY / FOREST",fill="#e8f1ef")
    return img

def draw_coupe(d,x,y,phase,body="#672aa3",highlight="#bd69df"):
    draw_shadow(d,x,y+39,103,7,"#0f1018")
    draw_wheel(d,x-51,y+27,16,phase,accent="#cf7cf2")
    draw_wheel(d,x+48,y+27,17,phase,accent="#cf7cf2")
    poly(d,[(x-72,y+23),(x-64,y+4),(x-31,y-8),(x-12,y-29),(x+24,y-30),
            (x+47,y-14),(x+69,y-4),(x+74,y+19),(x+57,y+29),(x-58,y+29)],body)
    poly(d,[(x-31,y-7),(x-10,y-27),(x+20,y-27),(x+42,y-11),(x+15,y-9)],"#172637")
    poly(d,[(x-61,y+5),(x+52,y+1),(x+42,y+8),(x-57,y+11)],highlight)
    rect(d,(x+60,y+3,x+72,y+10),"#76f2ff")
    rect(d,(x-70,y+8,x-62,y+14),"#ff4f93")
    rect(d,(x-49,y+25,x+47,y+29),"#1c1825")
    rect(d,(x-3,y-31,x+22,y-29),"#d994ef")
    return (x-69,y+11)

def render_neon(f):
    img=Image.new("RGB",(W,H),"#0d1020"); d=ImageDraw.Draw(img)
    banded_sky(img,"#070918","#171229",270,12)
    for i in range(12):
        x=i*29-int(f*.18)%29
        h=80+(i*41)%100
        col="#171a2c" if i%2 else "#121526"
        rect(d,(x,275-h,x+24,275),col)
        for wy in range(285-h,260,13):
            for wx in range(x+4,x+21,7):
                if ((wx+wy+i*3)//7)%4==0: rect(d,(wx,wy,wx+2,wy+3),"#5e4d7e")
    rect(d,(0,270,W,350),"#12131d")
    for i in range(7):
        x=i*46-int(f*.75)%46
        rect(d,(x,290,x+36,344),"#1e1f2c")
        neon=["#ff3ca6","#55e5ff","#b26cff"][i%3]
        rect(d,(x+4,297,x+32,301),neon)
        rect(d,(x+7,311,x+29,339),"#202d3c")
    rect(d,(0,350,W,H),"#171922")
    for i in range(9):
        y=360+i*14
        rect(d,(0,y,W,y+1),"#282938")
    colors=["#ff3ca6","#55e5ff","#8c56ff"]
    for i in range(20):
        x=(i*41-int(f*3.3))%300-15
        c=colors[i%3]
        rect(d,(x,372+(i*17)%80,x+3+(i%5),392+(i*11)%60),c)
    for i in range(45):
        x=(i*37+f*5)%300-10
        y=(i*53+f*13)%500-20
        line(d,[(x,y),(x-2,y+9)],"#44506b",1)
    x=136+math.sin(f*.045)*4; y=368+math.sin(f*.33)*1.2
    flame_anchor=draw_coupe(d,x,y,f*.7)
    rect(d,(x-47,y-2,x+17,y+1),"#63dcff")
    rect(d,(x-22,y+15,x+41,y+17),"#f23ca7")
    if 3.25 < f/FPS < 3.65:
        ex,ey=flame_anchor
        poly(d,[(ex,ey),(ex-10,ey-3),(ex-22,ey+1),(ex-10,ey+4)],"#ff8a25")
        poly(d,[(ex-2,ey),(ex-10,ey-2),(ex-15,ey+1),(ex-8,ey+2)],"#ffe36e")
    shift=int(f*4.7)%170
    for px in (55-shift,225-shift):
        px%=340; px-=35
        rect(d,(px,235,px+5,H),"#090b12")
        rect(d,(px-8,244,px+28,249),"#090b12")
    rect(d,(12,16,114,31),"#090b12")
    d.text((17,19),"NEON / STREET",fill="#f36bc4")
    return img

def render_touge(f):
    img=Image.new("RGB",(W,H),"#9ab6ce"); d=ImageDraw.Draw(img)
    banded_sky(img,"#62799b","#e8c19c",240,14)
    for base,col,amp,spd in [(250,"#5f6d76",70,.18),(295,"#394d50",90,.38)]:
        pts=[(-20,base)]
        off=(f*spd)%70
        for i in range(-2,8):
            x=i*70-off
            peak=base-amp-(i*17%28)
            pts.extend([(x,base),(x+35,peak),(x+70,base)])
        pts += [(W+20,340),(-20,340)]
        poly(d,pts,col)
    shift=int(f*1.7)%33
    for i in range(-2,12):
        x=i*33-shift; base=335
        poly(d,[(x,base),(x+11,base-48-(i%4)*9),(x+22,base)],"#1e3b33")
        rect(d,(x+10,base-5,x+12,base+8),"#3a3228")
    rect(d,(0,336,W,H),"#41454c")
    for i in range(11):
        x=(i*42-int(f*4.8))%460-90
        poly(d,[(x,414),(x+18,414),(x+35,480),(x+5,480)],"#d5d1bb")
    rect(d,(0,346,W,351),"#bfc2c0")
    for i in range(12):
        x=(i*30-int(f*5.5))%360-40
        rect(d,(x,319,x+4,354),"#686d70")
        rect(d,(x-2,323,x+20,328),"#d6d8d5")
    t=f/FPS
    roll=math.sin(clamp((t-2.2)/2.2,0,1)*math.pi)*3.2
    x=138+math.sin(f*.04)*3
    y=372+roll*.25
    phase=f*.64
    draw_shadow(d,x,412,99,7,"#24262a")
    draw_wheel(d,x-49,y+28,15,phase,accent="#d64040")
    draw_wheel(d,x+45,y+28,15,phase,accent="#d64040")
    poly(d,[(x-68,y+24),(x-60,y+3),(x-26,y-7),(x-10,y-27),(x+18,y-28),
            (x+42,y-11),(x+63,y-3),(x+69,y+18),(x+55,y+28),(x-55,y+28)],"#e7e6df")
    poly(d,[(x-27,y-7),(x-9,y-24),(x+15,y-24),(x+37,y-10),(x+8,y-9)],"#263641")
    poly(d,[(x-57,y+6),(x+47,y+4),(x+54,y+9),(x-60,y+11)],"#d74848")
    rect(d,(x-66,y+9,x-58,y+14),"#ffb55c")
    rect(d,(x+56,y+5,x+67,y+11),"#f5e28b")
    rect(d,(x-47,y+24,x+46,y+28),"#25282e")
    if 3.0<t<5.0:
        strength=math.sin((t-3)/2*math.pi)
        for i in range(22):
            age=(f*5+i*17)%80
            px=x-55-age*1.05
            py=y+37-(i%5)*2-age*.06
            r=max(1,int(4*strength-age/32))
            if r>0: circle(d,px,py,r,"#c9c9c2")
    if 2.0<t<3.2: rect(d,(x-67,y+8,x-61,y+14),"#ff3946")
    for i in range(12):
        px=(i*31-f*8)%330-30
        py=280+(i*19)%170
        rect(d,(px,py,px+3,py+2),"#142e29")
    rect(d,(12,16,111,31),"#171b20")
    d.text((17,19),"TOUGE / DRIFT",fill="#eee9da")
    return img

def render_supercar(f):
    img=Image.new("RGB",(W,H),"#f2a45f"); d=ImageDraw.Draw(img)
    banded_sky(img,"#6f5a8d","#f6b05e",260,16)
    circle(d,220,122,28,"#ffd98a")
    for col,base,amp,spd in [("#625b6a",278,42,.25),("#3c4b50",320,34,.55)]:
        pts=[(-20,base)]
        for i in range(-2,7):
            x=i*80-(f*spd)%80
            pts.extend([(x,base),(x+40,base-amp-(i*11%15)),(x+80,base)])
        pts += [(W+20,350),(-20,350)]
        poly(d,pts,col)
    rect(d,(0,338,W,H),"#4c4c4c")
    rect(d,(0,338,W,346),"#84715f")
    for i in range(8):
        x=(i*55-int(f*6.0))%500-90
        poly(d,[(x,415),(x+24,415),(x+46,480),(x+11,480)],"#f0e9d5")
    shift=int(f*3.3)%90
    for i in range(-2,6):
        x=i*90-shift
        rect(d,(x,220,x+4,343),"#3b3434")
        line(d,[(x+2,229),(x+44,236)],"#453f46",1)
    for i in range(18):
        x=(i*27-int(f*4.1))%340-30
        h=8+(i*7)%18
        rect(d,(x,338-h,x+13,338),"#384d3f")
    t=f/FPS
    push=ease(clamp((t-1.5)/5.0,0,1))
    scale=1+0.13*push
    x=138; y=369-6*push
    s=scale
    def P(px,py): return (x+(px)*s, y+(py)*s)
    draw_shadow(d,x,y+42*s,108*s,7*s,"#2a2929")
    draw_wheel(d,*P(-52,28),17*s,f*.72,accent="#e2642c")
    draw_wheel(d,*P(50,28),18*s,f*.72,accent="#e2642c")
    poly(d,[P(-75,23),P(-66,5),P(-30,-4),P(-3,-31),P(30,-32),P(52,-17),
            P(72,-8),P(78,18),P(61,29),P(-61,29)],"#e86b2d")
    poly(d,[P(-31,-4),P(-4,-28),P(25,-29),P(46,-15),P(10,-10)],"#24323a")
    poly(d,[P(-61,5),P(8,-4),P(57,-7),P(42,3),P(-57,12)],"#ff9b49")
    poly(d,[P(-58,13),P(35,8),P(54,16),P(-54,21)],"#c94726")
    rect(d,(*P(63,-3),*P(76,6)),"#e7f6d8")
    rect(d,(*P(-75,8),*P(-66,14)),"#b83435")
    rect(d,(*P(-50,25),*P(50,29)),"#222327")
    poly(d,[P(17,-7),P(45,-10),P(35,7),P(14,4)],"#40252a")
    rect(d,(*P(-12,-26),*P(13,-23)),"#ffd19a")
    rect(d,(*P(-50,1),*P(-16,3)),"#ffb870")
    for i in range(16):
        px=(i*37-f*7)%360-40
        line(d,[(px,441),(px-7,462)],"#2c3830",2)
    rect(d,(12,16,132,31),"#302b35")
    d.text((17,19),"SUPERCAR / SPRINT",fill="#ffd59b")
    return img

def render_rain_gt(f):
    img=Image.new("RGB",(W,H),"#09101a"); d=ImageDraw.Draw(img)
    banded_sky(img,"#070b12","#182839",270,12)
    for i in range(17):
        x=i*21-int(f*.28)%21
        h=20+(i*17)%75
        rect(d,(x,295-h,x+16,295),"#111b27")
        if i%3==0: rect(d,(x+4,281-h//2,x+6,284-h//2),"#d1a96a")
    rect(d,(0,312,W,H),"#171b22")
    rect(d,(0,333,W,337),"#5b6570")
    for i in range(8):
        x=(i*57-int(f*6.4))%520-100
        poly(d,[(x,407),(x+22,407),(x+48,480),(x+9,480)],"#aab4b7")
    for i in range(13):
        x=(i*43-int(f*4.5))%360-40
        c="#d74d57" if i%2 else "#e0b269"
        rect(d,(x,351+(i*9)%80,x+2,389+(i*13)%76),c)
    shift=int(f*5.2)%46
    for i in range(-2,10):
        x=i*46-shift
        rect(d,(x,302,x+4,350),"#3d464e")
        rect(d,(x-2,310,x+31,315),"#879097")
    for i in range(70):
        x=(i*29+f*(5+i%3))%310-20
        y=(i*47+f*(10+i%4))%520-30
        ln=6+(i%4)*3
        line(d,[(x,y),(x-3,y+ln)],"#334659",1)
    x=139+math.sin(f*.04)*3; y=370+math.sin(f*.28)*1
    draw_shadow(d,x,416,110,8,"#0b0d10")
    draw_wheel(d,x-51,y+28,17,f*.7,accent="#7ea0b8")
    draw_wheel(d,x+47,y+28,18,f*.7,accent="#7ea0b8")
    poly(d,[(x-73,y+23),(x-65,y+3),(x-30,y-7),(x-12,y-29),(x+18,y-30),
            (x+46,y-14),(x+67,y-5),(x+75,y+17),(x+58,y+29),(x-60,y+29)],"#203d5a")
    poly(d,[(x-29,y-7),(x-10,y-26),(x+14,y-27),(x+40,y-12),(x+10,y-9)],"#111e2a")
    poly(d,[(x-59,y+4),(x+51,y+2),(x+43,y+7),(x-55,y+11)],"#315f81")
    rect(d,(x-72,y+7,x-61,y+13),"#ff3045")
    rect(d,(x-68,y+8,x-64,y+11),"#ff9a9f")
    rect(d,(x+59,y+4,x+72,y+10),"#c7e9ff")
    rect(d,(x-49,y+24,x+45,y+29),"#12171d")
    for i in range(30):
        age=(f*6+i*11)%115
        px=x-55-age*1.05
        py=y+38+(i%5)*3-age*.10
        r=max(1,int(5-age/31))
        if r>0 and px>-15: circle(d,px,py,r,"#53697a")
    if (f//15)%2==0:
        line(d,[(x-9,y-22),(x+13,y-13)],"#4a6b80",1)
    rect(d,(12,16,100,31),"#080b10")
    d.text((17,19),"RAIN / GT",fill="#a8c4d9")
    return img

SCENES = [
    ("01-rally-forest", render_rally, 96.0, "gravel"),
    ("02-neon-street", render_neon, 78.0, "city"),
    ("03-touge-drift", render_touge, 88.0, "tyre"),
    ("04-supercar-sprint", render_supercar, 106.0, "open"),
    ("05-rainy-gt", render_rain_gt, 82.0, "rain"),
]

def make_audio(path, base_hz, mode):
    sr=22050
    rng=random.Random(7701+int(base_hz))
    with wave.open(str(path),"wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr)
        frames=bytearray()
        for n in range(sr*DUR):
            t=n/sr
            accel=.85 + .35*math.sin(t*.62) + .18*(t/DUR)
            hz=base_hz*accel
            engine=(math.sin(2*math.pi*hz*t)+.46*math.sin(2*math.pi*hz*2.02*t)+.22*math.sin(2*math.pi*hz*3.01*t))
            noise=(rng.random()*2-1)
            extra=0
            if mode=="rain": extra=noise*.42
            elif mode=="gravel": extra=noise*(.14+.20*(math.sin(t*9)**8))
            elif mode=="tyre": extra=noise*(.22 if 3.0<t<5.0 else .04)
            elif mode=="city": extra=noise*.04 + .06*math.sin(2*math.pi*43*t)
            else: extra=noise*.03
            val=int(clamp((engine*.11+extra*.10)*32767,-32000,32000))
            frames += struct.pack("<h",val)
        wf.writeframes(frames)

def encode_scene(name, renderer, hz, mode):
    wav=OUT/f"{name}.wav"
    mp4=OUT/f"{name}.mp4"
    make_audio(wav,hz,mode)
    cmd=[
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-i",str(wav),
        "-vf","scale=1080:1920:flags=neighbor",
        "-c:v","libx264","-preset","medium","-crf","16","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","128k","-shortest",str(mp4)
    ]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    captures=[]
    capture_ids={0,60,120,180,239}
    for f in range(FRAMES):
        im=renderer(f)
        if f in capture_ids: captures.append(im.copy())
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    rc=proc.wait()
    if rc: raise SystemExit(f"ffmpeg failed for {name}: {rc}")
    sheet=Image.new("RGB",(W*3,H*2),"#000000")
    for i,im in enumerate(captures):
        sheet.paste(im,((i%3)*W,(i//3)*H))
    sheet.save(OUT/f"{name}-contact.png")
    wav.unlink(missing_ok=True)
    return mp4

def verify(mp4):
    probe=subprocess.check_output([
        "ffprobe","-v","error","-count_frames","-select_streams","v:0",
        "-show_entries","stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_read_frames",
        "-show_entries","format=duration","-of","json",str(mp4)
    ], text=True)
    data=json.loads(probe)
    subprocess.check_call(["ffmpeg","-v","error","-xerror","-i",str(mp4),"-f","null","-"])
    st=data["streams"][0]
    ok=(st["codec_name"]=="h264" and int(st["width"])==1080 and int(st["height"])==1920
        and st["pix_fmt"]=="yuv420p" and st["r_frame_rate"]=="30/1"
        and int(st.get("nb_read_frames",0))==FRAMES)
    if not ok: raise SystemExit(f"QA mismatch: {mp4}: {data}")
    return data

def main():
    qa={}
    for name,renderer,hz,mode in SCENES:
        print("Rendering",name,flush=True)
        mp4=encode_scene(name,renderer,hz,mode)
        qa[name]=verify(mp4)
        print("PASS",name,mp4.stat().st_size,flush=True)
    (OUT/"qa.json").write_text(json.dumps(qa,indent=2))
    print("All five videos rendered and verified.")

if __name__=="__main__":
    main()
