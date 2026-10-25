"""Original pixel-cluster artwork. Four style auditions, not the V4 production pipeline.
Run: python3 scripts/render_style_audition.py
No external art, AI images, fonts or textures. Pillow pixels + FFmpeg only.
"""
from PIL import Image, ImageDraw, ImageFont
import math, random, subprocess, pathlib, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'out/style-audition'; OUT.mkdir(parents=True,exist_ok=True)
W,H=270,480
STYLES=[
 dict(name='01  /  BOLD 8-BIT',sub='CHUNKY PIXELS / BRIGHT & SIMPLE',sky=['#426acb','#7396e0','#b5d4ec'],cloud=['#e2effa','#ffffff'],hill=['#5278ac','#50947b','#71b86c'],leaf=['#184d49','#28764a','#48a446','#83c956'],bark=['#423c42','#816348'],grass=['#285947','#488648','#7cac4c'],road=['#333f59','#515d72','#7e8796'],flower=['#ffd26e','#f9f5bb'],coarse=True),
 dict(name='02  /  LUSH 16-BIT',sub='RICH CLUSTERS / CLASSIC GAME WORLD',sky=['#4b83aa','#90b9c4','#e3dac0'],cloud=['#a3b9c4','#e9e6d5'],hill=['#6c8f9b','#538879','#63966b'],leaf=['#183e43','#285d4a','#438052','#74a15c','#a7bd75'],bark=['#3e4140','#7b6750','#a58a62'],grass=['#2b5546','#4b7951','#7b9b58'],road=['#484b54','#666667','#8d8980'],flower=['#f1c96e','#d9dfb0'],coarse=False),
 dict(name='03  /  SOFT PASTEL',sub='WARM LIGHT / COZY STORYBOOK PIXELS',sky=['#aaa8ce','#dfc4d0','#f5dbca'],cloud=['#d7b8c8','#fff0db'],hill=['#a7abc1','#91aea5','#9dbd97'],leaf=['#986c94','#bb83a4','#dca3bb','#edc1cc','#ffe6da'],bark=['#786b7c','#ac8d83','#d3aa93'],grass=['#7b988f','#a2b497','#c5ca9b'],road=['#8b8090','#aaa0a5','#c8b9b1'],flower=['#edabb6','#fff1ca'],coarse=False),
 dict(name='04  /  MOONLIT PIXEL',sub='DEEP COLOURS / QUIET NIGHT',sky=['#111a39','#273556','#59617e'],cloud=['#414c6d','#68728a'],hill=['#354b69','#2c5261','#2f615f'],leaf=['#112a3b','#1b4049','#2d5b57','#4c7c6d','#7fa28c'],bark=['#162c3b','#3d5358','#6b7870'],grass=['#183c46','#2d5a58','#5b8270'],road=['#242e43','#3c495b','#617181'],flower=['#8cc9b1','#d5e1b2'],coarse=False),
]
font=ImageFont.load_default(size=10)
small=ImageFont.load_default(size=7)
def poly(d,pts,c): d.polygon([(int(x),int(y)) for x,y in pts],fill=c)
def cloud(im,x,y,s,p):
 d=ImageDraw.Draw(im)
 pts=[(0,13),(8,13),(8,7),(17,7),(17,3),(30,3),(30,0),(43,0),(43,5),(53,5),(53,10),(65,10),(65,16),(77,16),(77,22),(0,22)]
 poly(d,[(x+a*s,y+b*s) for a,b in pts],p[0]);
 poly(d,[(x+a*s,y+b*s) for a,b in pts[:-2]]+[(x+77*s,y+17*s),(x,y+17*s)],p[1])
def tree(p,seed,size=1):
 # Layered asymmetric hand-designed crown masses, each shaded with stepped clusters.
 im=Image.new('RGBA',(102,158));d=ImageDraw.Draw(im);rng=random.Random(seed)
 b=p['bark']; l=p['leaf']
 if 'MOONLIT' in p['name']:
  poly(d,[(46,154),(47,33),(53,33),(56,154)],b[0]);d.line((51,62,52,153),fill=b[1],width=2)
  for tier in range(7):
   y=10+tier*15;rx=8+tier*6;cx=51
   poly(d,[(cx,y),(cx+4,y+10),(cx+rx,y+29),(cx+rx-10,y+26),(cx+rx-5,y+34),(cx-3,y+30),(cx-rx,y+34),(cx-rx+5,y+27),(cx-rx,y+29),(cx-4,y+9)],l[0])
   poly(d,[(cx,y+3),(cx+3,y+13),(cx+rx-6,y+26),(cx+4,y+23),(cx-3,y+26),(cx-rx+6,y+29)],l[1])
   d.line((cx-2,y+11,cx-rx+7,y+27),fill=l[3],width=2)
   d.line((cx+2,y+17,cx+rx-6,y+28),fill=l[2])
  if size!=1: im=im.resize((round(102*size),round(158*size)),Image.Resampling.NEAREST)
  return im
 poly(d,[(43,153),(46,91),(34,71),(39,66),(51,88),(58,56),(64,58),(57,100),(61,153)],b[0])
 poly(d,[(49,151),(51,96),(55,93),(55,151)],b[1]);d.line((53,103,73,77),fill=b[1],width=3)
 masses=[(46,20,29,22),(28,40,27,26),(70,40,28,25),(16,63,18,22),(45,62,32,27),(78,66,23,24),(35,84,26,19),(65,86,25,20)]
 for cx,cy,rx,ry in masses:
  cx+=rng.randrange(-2,3);cy+=rng.randrange(-2,3)
  if 'PASTEL' in p['name']: cy=int(cy*.72)+10;rx+=3;ry=max(12,ry-4)
  shape=[(-1,-1)]
  pts=[(cx-rx,cy-ry//3),(cx-rx+4,cy-ry*2//3),(cx-rx//2,cy-ry*2//3),(cx-rx//2,cy-ry),(cx+rx//3,cy-ry),(cx+rx//3,cy-ry+4),(cx+rx-4,cy-ry//2),(cx+rx,cy),(cx+rx-3,cy+ry//2),(cx+rx//2,cy+ry//2),(cx+rx//2,cy+ry),(cx-rx//3,cy+ry),(cx-rx//3,cy+ry-4),(cx-rx+2,cy+ry//2)]
  poly(d,pts,l[0]);poly(d,[(x,y-3) for x,y in pts[:-4]]+[(cx-rx+5,cy+ry//2-2)],l[1])
  poly(d,[(cx-rx+5,cy-3),(cx-rx+8,cy-ry//2),(cx-6,cy-ry//2),(cx-6,cy-ry+4),(cx+rx//3-3,cy-ry+4),(cx+rx//3-3,cy-ry//2),(cx+rx-8,cy-ry//2),(cx+rx-8,cy),(cx+4,cy),(cx+4,cy+5),(cx-rx+5,cy+5)],l[2])
  hi=l[-1]
  for j in range(5 if p['coarse'] else 13):
   xx=cx+rng.randrange(-rx+6,max(-rx+7,rx-5)); yy=cy+rng.randrange(-ry+5,max(-ry+6,ry//3))
   col=hi if j%4==0 else l[-2]
   d.rectangle((xx,yy,xx+rng.randrange(2,6),yy+1),fill=col)
   if 'PASTEL' in p['name'] and j%3==0:
    d.point((xx+1,yy-1),fill=l[-1]);d.point((xx+1,yy+2),fill=l[-1])
 if size!=1: im=im.resize((round(102*size),round(158*size)),Image.Resampling.NEAREST)
 return im
TREES=[[tree(p,seed) for seed in (11,47,83)] for p in STYLES]
def frame(k,f):
 p=STYLES[k]; im=Image.new('RGB',(W,H));d=ImageDraw.Draw(im)
 for y in range(H):d.line((0,y,W,y),fill=p['sky'][min(2,y//93)])
 if k==3:
  r=random.Random(93)
  for i in range(55):
   x,y=r.randrange(W),r.randrange(22,200); c='#cbd9d6' if (i+f//15)%7 else '#738dab';d.point((x,y),fill=c)
  d.ellipse((204,64,226,86),fill='#e4e6c5');d.ellipse((209,62,231,82),fill=p['sky'][0])
 else:
  d.ellipse((207,93,229,115),fill='#f7e5b7' if k!=0 else '#ffe9a8')
 for i,(x,y,s) in enumerate([(-30,112,.7),(110,75,.9),(238,143,.55)]):
  cloud(im,int((x-f*.12*(i+1))%350)-50,y,s,p['cloud'])
 d=ImageDraw.Draw(im)
 # Three distant ridge silhouettes and meadows.
 for idx,(base,amp) in enumerate([(245,52),(270,40),(289,23)]):
  pts=[(-1,H)]
  for x in range(-2,W+4,3): pts.append((x,base-int(amp*(.55+.30*math.sin(x*.025+idx*2)+.2*math.sin(x*.061+idx)))))
  pts.extend([(W+2,H)]);poly(d,pts,p['hill'][idx])
 # Tiny farmhouse and rows at consistent visual anchor.
 d.rectangle((162,249,184,268),fill='#c7bca1' if k!=3 else '#5c7273')
 poly(d,[(158,250),(173,239),(188,250)],'#6b6264' if k!=3 else '#304354')
 d.rectangle((166,255,170,260),fill=p['flower'][1]);d.rectangle((177,255,181,260),fill=p['flower'][1]);d.rectangle((172,259,176,268),fill=p['bark'][0])
 d.rectangle((0,279,W,332),fill=p['grass'][1])
 for y in [284,295,311]:
  d.line((0,y,W,y-7),fill=p['grass'][2],width=1)
 # Hedge row.
 for i in range(22):
  x=i*16-int(f*.25)%16
  poly(d,[(x,291),(x,282),(x+4,282),(x+4,277),(x+12,277),(x+12,282),(x+17,282),(x+17,291)],p['leaf'][1])
  d.line((x+5,280,x+11,280),fill=p['leaf'][3])
 # Midground trees visibly pass the landscape.
 for i,x in enumerate([-55,54,211,346]):
  xx=int((x-f*.5+130)%470)-130
  tr=TREES[k][i%3]; im.paste(tr,(xx,162),tr)
 d=ImageDraw.Draw(im)
 # Verge and road with clear articulated shoulders.
 d.rectangle((0,315,W,336),fill=p['grass'][0]);d.line((0,327,W,327),fill=p['grass'][2],width=2)
 d.rectangle((0,336,W,403),fill=p['road'][0]);d.rectangle((0,341,W,397),fill=p['road'][1]);d.line((0,343,W,343),fill=p['road'][2]);d.line((0,394,W,394),fill=p['road'][2])
 for x in range(-70,350,61):
  xx=x-int(f*2.5)%61; d.rectangle((xx,368,xx+29,370),fill='#d4d2b6' if k!=3 else '#96a9a5')
 # Deliberate small road chips, attached to moving road clock.
 rng=random.Random(721)
 for i in range(60 if not p['coarse'] else 12):
  x=(rng.randrange(270)-int(f*2.5))%270;y=rng.randrange(345,393)
  d.line((x,y,x+2,y),fill=p['road'][0] if i%3 else p['road'][2])
 d.rectangle((0,404,W,H),fill=p['grass'][0]);d.rectangle((0,405,W,416),fill=p['grass'][1])
 # Fence moving independently of back trees.
 off=int(f*1.6)%43
 for x in range(-43,W+44,43):
  x-=off;d.rectangle((x,303,x+3,330),fill=p['bark'][0]);d.line((x+1,304,x+1,326),fill=p['bark'][-1])
 d.line((0,311,W,311),fill=p['bark'][1],width=2);d.line((0,320,W,320),fill=p['bark'][0],width=2)
 # Foreground grass: arranged blades and flower heads, restrained texture.
 rng=random.Random(892)
 for i in range(130 if not p['coarse'] else 45):
  x=(rng.randrange(W)-int(f*3))%W;y=rng.randrange(411,479);h=rng.randrange(3,10);sway=int(math.sin(f*.08+i)*1.7)
  d.line((x,y,x+sway,y-h),fill=p['grass'][1],width=1)
  d.line((x,y,x-3+sway,y-h+2),fill=p['grass'][2],width=1)
  if i%7==0:
   d.rectangle((x+sway-1,y-h-1,x+sway+1,y-h+1),fill=p['flower'][i%2])
 if k==2:
  for i in range(14):
   x=int((i*31+f*.6+math.sin(f*.07+i)*4)%W); y=int((i*23+f*.32)%285+120)
   d.line((x,y,x+1,y),fill=p['leaf'][-1])
 # Large near-frame canopy helps depth; leaf rows sway by whole pixels.
 tr=TREES[k][2];tr=tr.resize((153,237),Image.Resampling.NEAREST)
 shift=int(math.sin(f*.045)*2)
 im.paste(tr,(-104+shift,149),tr)
 if k==3:
  d=ImageDraw.Draw(im)
  for i in range(9):
   x=int((i*39+math.sin(f*.045+i)*11)%W);y=int(289+math.sin(f*.035+i*3)*20)
   d.point((x,y),fill=p['flower'][0] if (f//12+i)%3 else p['flower'][1])
 # 8-bit is a genuinely coarser source grid, not a blur filter.
 if p['coarse']: im=im.resize((135,240),Image.Resampling.NEAREST).resize((270,480),Image.Resampling.NEAREST)
 d=ImageDraw.Draw(im);d.rectangle((10,12,260,48),fill='#142833')
 d.text((18,18),p['name'],font=font,fill='#f6e7c6');d.text((18,34),p['sub'],font=small,fill='#a8c9bf')
 d.rectangle((10,459,260,470),fill='#142833');d.text((18,461),'SAME SCENE  /  DIFFERENT PIXEL LANGUAGE',font=small,fill='#e2d9be')
 return im

def main():
 cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','270x480','-r','30','-i','-','-vf','scale=1080:1920:flags=neighbor','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'Countryside_Pixel_Style_Montage.mp4')]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for k in range(4):
   for f in range(150):
    im=frame(k,f);proc.stdin.write(im.tobytes())
    if f==65:im.save(OUT/f'style-{k+1}-native.png')
   print('Rendered style',k+1,flush=True)
 finally:proc.stdin.close()
 if proc.wait()!=0:raise RuntimeError('FFmpeg encode failed')
 sheet=Image.new('RGB',(540,960))
 for k in range(4):sheet.paste(frame(k,65),((k%2)*270,(k//2)*480))
 sheet.resize((1080,1920),Image.Resampling.NEAREST).save(OUT/'Style_Comparison.png')
 print(OUT/'Countryside_Pixel_Style_Montage.mp4')
if __name__=='__main__':main()
