"""Twelve reproducible pixel environment auditions, authored natively with Pillow.
Not evidence of Pixelorama/Krita/LDtk/PixiJS execution. No external images.
Render: python3 scripts/render_style_variants.py
Config: studio/v4/style-auditions/recipes.json
Every scene uses the same small collection of reusable drawing primitives.
"""
from PIL import Image, ImageDraw, ImageFont
import random, math, json, pathlib, subprocess, hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'out/style-variants';OUT.mkdir(parents=True,exist_ok=True)
W,H=270,480
FONT=ImageFont.load_default(size=12); SMALL=ImageFont.load_default(size=8)
# sky / cloud shade+light / distant ridge / near ridge / ground shade+base+light /
# foliage shadow+base+light+highlight / bark shadow+light / road / marking
RECIPES=[
 (5,'POCKET WOODLAND','4 COLOURS / COARSE TILE GRID','block',
 ['d6e5ae','9dbb83','d6e5ae','9dbb83','638464','355b55','638464','9dbb83','355b55','638464','9dbb83','d6e5ae','355b55','638464','638464','d6e5ae'],dict(coarse=True,mono=True,detail=0,prop='cabin')),
 (6,'CLEAN ARCADE','OUTLINES / 3-TONE CANOPIES','oak',
 ['9acfe0','b0d9e5','fff6d7','719fbd','77ab91','285b50','559554','99bc69','193e44','32704b','67a557','bbd47b','394744','937651','586173','e8dfb7'],dict(outline=True,detail=1,prop='barn',recommended=True)),
 (7,'CLASSIC GROVE','STEPPED LEAF CLUSTERS / 16-BIT','oak',
 ['a0c8cf','b2c5ce','f1e6cd','7998a4','72a084','35594a','6b9257','c2be77','203e42','3e6b4d','7b9b59','d0ce84','494b41','a28b60','616568','e3d6b2'],dict(detail=2,prop='windmill',recommended=True)),
 (8,'AUTUMN BIRCH','SLENDER TRUNKS / GOLDEN CLUSTERS','birch',
 ['c9c9c5','d5c9c0','f5e4c8','a7aaa5','999f84','575e46','a19c61','d9c17c','704b49','b17743','dfaa54','f8d589','68635c','e7d9b9','706c6c','e5d1ac'],dict(detail=1,prop='cabin',petals=True)),
 (9,'ALPINE POSTCARD','TIERED PINES / ANGULAR PEAKS','pine',
 ['a2ccda','c1dae0','f4eee2','7d9aaf','779795','355754','6d997a','b8c09b','243d46','3f6a60','769883','b3cbb0','4d5655','9b9076','676c78','e5ded0'],dict(detail=1,prop='chalet',mountains=True)),
 (10,'DUSK SILHOUETTES','FLAT SHAPES / STRONG CONTRAST','willow',
 ['c5a7b2','dcb6b1','ffe1bc','a68b9d','7f7b91','353f55','646277','a49395','27384a','3d4d5b','5b6970','a9ab98','293847','6d6871','4c4d65','d5bcb0'],dict(detail=0,prop='cabin',sunset=True,recommended=True)),
 (11,'RAINY WOODLAND','COOL PALETTE / PIXEL RAIN','oak',
 ['899da9','98abb0','b6c2bc','718d97','658b85','294e50','517c6a','a2ad83','243c48','3a615a','648b70','a1b29a','394f51','8d9b86','475b69','b0bbb1'],dict(detail=1,prop='cabin',rain=True)),
 (12,'COASTAL SUMMER','PALM SILHOUETTES / WATER TILES','palm',
 ['88cadd','aedbe0','fff3d2','82b2c5','639fa0','3d7a69','7eae79','d4c48c','215751','3d805a','88b565','d0d68a','756647','c7aa72','777d85','f3e7c1'],dict(detail=1,prop='lighthouse',coast=True)),
 (13,'SNOW COUNTRY','LIMITED SHADING / SNOW CAPS','pine',
 ['b9cfdb','d0dce0','f6f1e7','95afc1','a7bec1','719495','c9d8d4','f8f0df','3d5d68','5f8287','a7c2bf','e8eee1','4c6670','b4c4c1','697e8c','f0eee0'],dict(detail=1,prop='chalet',mountains=True,snow=True)),
 (14,'DESERT EVENING','CACTUS SPRITES / MESA LAYERS','cactus',
 ['e4b3a0','efc4aa','ffe1b6','b68d95','b17f72','966e5f','c69b75','edc799','405e58','68816a','a3ad7d','d0c494','595d52','ac9d75','7e7375','e1c4a1'],dict(detail=1,prop='adobe',desert=True,sunset=True)),
 (15,'MOSAIC MEADOW','SQUARE CLUSTERS / SOFT COLOURS','block',
 ['b7c6d2','c8ced7','f5e6d2','9ba8bb','91b3aa','567d76','8fac8c','d0cf9d','436464','6f957d','a4bc93','d9dba6','5d6868','afa48b','828c98','e6debf'],dict(detail=1,prop='barn',coarse=True)),
 (16,'INK & PAPER','LIMITED INKS / ORDERED DITHER','willow',
 ['e8dfc5','c4bea9','e8dfc5','b5b3a0','8b988d','3e585b','8b988d','c4bea9','3e585b','657e77','a6ad98','e8dfc5','3e585b','8b988d','8b988d','e8dfc5'],dict(detail=0,prop='windmill',mono=True,dither=True)),
]

def poly(d,pts,c):d.polygon([(round(x),round(y)) for x,y in pts],fill=c)
def box(d,x,y,w,h,c):d.rectangle((int(x),int(y),int(x+w-1),int(y+h-1)),fill=c)
def leaf(d,x,y,rx,ry,colors,detail=1,outline=False):
 pts=[(x-rx,y-ry//3),(x-rx+3,y-ry//3),(x-rx+3,y-ry*2//3),(x-rx//2,y-ry*2//3),(x-rx//2,y-ry),(x+rx//3,y-ry),(x+rx//3,y-ry+3),(x+rx-3,y-ry+3),(x+rx-3,y-ry//3),(x+rx,y-ry//3),(x+rx,y+ry//2),(x+rx-5,y+ry//2),(x+rx-5,y+ry),(x-rx//2,y+ry),(x-rx//2,y+ry-3),(x-rx,y+ry-3)]
 poly(d,pts,colors[0]);
 # Coherent sun-facing cluster, not isolated random noise.
 pts2=[(x-rx+3,y-ry//3),(x-rx//2+2,y-ry//3),(x-rx//2+2,y-ry+3),(x+rx//3-2,y-ry+3),(x+rx//3-2,y-ry+6),(x+rx-6,y-ry+6),(x+rx-6,y),(x+3,y),(x+3,y+ry-4),(x-rx+3,y+ry-4)]
 poly(d,pts2,colors[1])
 if detail:
  poly(d,[(x-rx+5,y-ry//3),(x-rx//2+4,y-ry//3),(x-rx//2+4,y-ry+5),(x+rx//3-5,y-ry+5),(x+rx//3-5,y-ry+9),(x+rx-9,y-ry+9),(x+rx-9,y-2),(x-2,y-2),(x-2,y+3),(x-rx+5,y+3)],colors[2])
  d.line((x-rx//2+5,y-ry+5,x+rx//3-7,y-ry+5),fill=colors[3],width=2)
 if detail>1:
  for dx,dy in [(-9,-4),(0,-8),(6,-1),(-5,5),(11,-7)]:
   box(d,x+dx,y+dy,4,1,colors[3]);box(d,x+dx-1,y+dy+2,2,1,colors[2])
 if outline:d.line(pts+[pts[0]],fill=colors[0],width=1)

def make_tree(s,seed=0):
 n,title,subtitle,kind,raw,opt=s;c=['#'+x for x in raw];lc=c[8:12];bc=c[12:14]
 im=Image.new('RGBA',(100,152));d=ImageDraw.Draw(im)
 if kind=='pine':
  box(d,47,45,7,104,bc[0]);box(d,50,69,2,79,bc[1])
  for j in range(6):
   y=5+j*17;r=9+j*6
   poly(d,[(50,y),(50+r*.4,y+15),(50+r,y+32),(50+r*.5,y+29),(50+r*.65,y+37),(50,y+32),(50-r*.7,y+37),(50-r*.5,y+29),(50-r,y+32),(50-r*.4,y+15)],lc[0])
   poly(d,[(50,y+3),(50+r*.3,y+17),(50+r-6,y+29),(48,y+25),(50-r+5,y+31),(50-r*.35,y+17)],lc[1])
   d.line((49,y+8,50-r+7,y+28),fill=lc[2],width=2)
   if opt.get('snow'):
    poly(d,[(50,y+1),(50+r*.38,y+16),(50+r*.62,y+23),(50+r*.24,y+22),(50,y+17),(50-r*.7,y+26),(50-r*.35,y+15)],c[7])
 elif kind=='birch':
  for x,y in [(35,47),(60,20),(75,64)]:
   box(d,x,43,4,106,bc[1]);box(d,x+3,43,1,106,bc[0])
   d.line((x+1,84,x-12,66),fill=bc[1],width=2)
   for yy in range(65,145,16):box(d,x,yy,2,2,bc[0])
  for x,y,rx,ry in [(59,29,14,24),(43,52,17,24),(70,58,20,25),(29,72,17,24),(57,84,18,19),(78,86,15,19)]:leaf(d,x,y,rx,ry,lc,opt['detail'])
 elif kind=='palm':
  poly(d,[(44,151),(48,103),(57,68),(62,68),(54,105),(52,151)],bc[0]);d.line((47,147,51,105,59,71),fill=bc[1],width=2)
  for y in range(85,149,9):d.line((47,y,53,y-2),fill=bc[1])
  cx,cy=59,65
  for dx,dy in [(-48,14),(-42,-12),(-29,-29),(5,-37),(29,-25),(36,-2),(39,25),(-18,30)]:
   poly(d,[(cx,cy),(cx+dx*.5-2,cy+dy*.5-8),(cx+dx,cy+dy),(cx+dx*.6,cy+dy*.6+1),(cx+dx*.4,cy+dy*.5+4)],lc[0])
   d.line((cx,cy,cx+int(dx*.6),cy+int(dy*.6)-2,cx+dx,cy+dy),fill=lc[2],width=2)
  box(d,56,69,5,5,bc[0]);box(d,62,69,4,4,bc[0])
 elif kind=='cactus':
  poly(d,[(44,149),(44,37),(48,30),(54,30),(58,37),(58,149)],lc[0]);box(d,48,36,6,112,lc[1]);box(d,49,37,2,110,lc[2])
  poly(d,[(45,93),(25,93),(21,87),(21,63),(25,58),(30,61),(30,81),(45,81)],lc[0]);d.line((25,64,25,86,44,86),fill=lc[2],width=2)
  poly(d,[(56,110),(77,110),(82,104),(82,78),(77,73),(72,77),(72,98),(56,98)],lc[0]);d.line((77,79,77,102,57,104),fill=lc[1],width=2)
  for y in range(45,143,13):box(d,55,y,2,1,lc[3])
 elif kind=='willow':
  poly(d,[(44,150),(47,98),(34,65),(39,63),(52,87),(67,54),(71,57),(57,101),(60,150)],bc[0]);d.line((51,145,53,97,67,62),fill=bc[1],width=2)
  for x,y,r in [(49,30,25),(30,51,26),(68,49,26),(18,70,16),(77,72,19),(47,63,24)]:leaf(d,x,y,r,16,lc,opt['detail'])
  for j in range(13):
   x=7+j*7; y=65+int(math.sin(j*.9)*9); length=17+(j*7)%23
   box(d,x,y,3,length,lc[0]);box(d,x,y,1,length-4,lc[2] if opt['detail'] else lc[1])
 elif kind=='block':
  box(d,46,70,9,79,bc[0]);box(d,49,83,3,65,bc[1])
  for x,y,w,h in [(30,12,38,31),(15,31,38,37),(52,28,32,41),(5,59,37,31),(36,53,48,36),(25,83,40,22)]:
   box(d,x,y,w,h,lc[0]);box(d,x+3,y+3,w-7,h-9,lc[1]);box(d,x+5,y+3,w//2,5,lc[2])
 else:
  poly(d,[(42,149),(45,93),(29,71),(33,68),(49,84),(62,57),(67,59),(55,96),(60,149)],bc[0]);d.line((49,145,50,95,63,65),fill=bc[1],width=2)
  for x,y,rx,ry in [(48,25,24,19),(27,43,23,21),(70,42,22,20),(16,66,14,18),(45,61,27,25),(77,65,21,21),(33,84,23,17),(62,85,22,17)]:
   leaf(d,x,y,rx,ry,lc,opt['detail'],opt.get('outline',False))
 return im

TREES=[make_tree(s) for s in RECIPES]
def cloud(d,x,y,c,coarse=False):
 pts=[(0,11),(7,11),(7,6),(17,6),(17,1),(31,1),(31,4),(42,4),(42,9),(52,9),(52,14),(62,14),(62,21),(0,21)]
 poly(d,[(x+a,y+b) for a,b in pts],c[1]);poly(d,[(x+a,y+b-2) for a,b in pts[:-3]]+[(x+62,y+16),(x,y+16)],c[2])
def prop(d,x,y,kind,c,f):
 if kind=='windmill':
  poly(d,[(x-10,y),(x-6,y-33),(x+5,y-33),(x+10,y)],c[2]);poly(d,[(x-9,y-33),(x,y-43),(x+9,y-33)],c[12]);box(d,x-2,y-13,5,13,c[12])
  angle=f*.022
  for i in range(4):
   a=angle+i*math.pi/2;xx=x+round(23*math.cos(a));yy=y-33+round(23*math.sin(a));d.line((x,y-33,xx,yy),fill=c[12],width=2)
   poly(d,[(x+9*math.cos(a),y-33+9*math.sin(a)),(xx,yy),(xx-4*math.sin(a),yy+4*math.cos(a)),(x+9*math.cos(a)-4*math.sin(a),y-33+9*math.sin(a)+4*math.cos(a))],c[7])
 elif kind=='lighthouse':
  poly(d,[(x-7,y),(x-5,y-42),(x+4,y-42),(x+7,y)],c[2]);box(d,x-7,y-20,14,6,c[12]);box(d,x-6,y-45,12,6,c[12]);box(d,x-3,y-44,6,4,c[7]);poly(d,[(x-8,y-46),(x,y-52),(x+8,y-46)],c[12])
 else:
  box(d,x-16,y-22,33,22,c[12] if kind=='barn' else c[2]);poly(d,[(x-20,y-22),(x,y-38),(x+20,y-22)],c[12])
  if kind=='adobe':box(d,x-17,y-28,35,9,c[7])
  for xx in [x-11,x+6]:box(d,xx,y-16,6,7,c[7]);box(d,xx+2,y-16,1,7,c[12])
  box(d,x-3,y-13,6,13,c[12] if kind!='barn' else c[7])
  if kind=='chalet':d.line((x-20,y-23,x,y-38,x+20,y-23),fill=c[7],width=3)

def render(k,f):
 n,title,subtitle,kind,raw,opt=RECIPES[k];c=['#'+x for x in raw]
 im=Image.new('RGB',(W,H),c[0]);d=ImageDraw.Draw(im)
 # Restrained hard colour bands, with optional ordered ink dithering.
 if opt.get('sunset'):
  for y,col in [(142,c[1]),(207,c[2])]:box(d,0,y,W,242-y,col)
  d.ellipse((174,99,217,142),fill=c[2])
 elif not opt.get('rain'):d.ellipse((206,79,226,99),fill=c[2])
 for i,(x,y) in enumerate([(-20,75),(96,113),(217,165)]):cloud(d,int((x-f*(.13+i*.04)+75)%360)-75,y,c)
 for plane in range(2):
  pts=[(-1,301)]
  for x in range(-3,274,3):
   xx=x+f*(.04+plane*.04)
   if opt.get('mountains'):
    ridge=235+plane*26-abs(((xx+plane*43)%173)-86)*.72
   elif opt.get('desert'):
    ridge=220+plane*24-([0,12,40,40,33,4,0][int((xx+plane*30)%210)//30])
   else:ridge=235+plane*31-19*math.sin(xx*.019+plane)-9*math.sin(xx*.043+plane*2)
   pts.append((x,int(ridge)))
  pts.append((W+1,301));poly(d,pts,c[3+plane])
  if opt.get('mountains') and plane==0:
   for xx in [-173,0,173,346]:
    xx-=int(f*.04)%173;poly(d,[(xx,174),(xx+18,195),(xx+10,192),(xx+6,197),(xx-3,189),(xx-17,198)],c[2])
 box(d,0,279,W,68,c[6]);
 for y in [288,303,322]:d.line((0,y,270,y-9),fill=c[7])
 if opt.get('coast'):
  box(d,0,252,W,68,c[3]);
  for i in range(27):
   xx=int((i*41+f*.35)%300)-20;yy=258+(i*13)%56;d.line((xx,yy,xx+6+(i%3)*3,yy),fill=c[2] if i%4==0 else c[0])
  box(d,0,319,W,25,c[7])
 # Distinct distant tree line, small repeated modules.
 far=TREES[k].resize((28,43),Image.Resampling.NEAREST)
 for i in range(12):
  xx=int((i*33-f*.25+35)%396)-35;im.paste(far,(xx,255+(i%3)*3),far)
 d=ImageDraw.Draw(im);prop(d,174-int(f*.08),278,opt['prop'],c,f)
 if opt.get('dither'):
  for y in range(209,267,2):
   for x in range(y%4,270,4):
    if im.getpixel((x,y))==tuple(bytes.fromhex(raw[3])):d.point((x,y),fill=c[0])
 # Broad grassy roadside and asphalt band, continuous tiles.
 box(d,0,322,W,22,c[5]);box(d,0,326,W,9,c[6]);d.line((0,335,W,335),fill=c[7],width=2)
 box(d,0,342,W,63,c[12]);box(d,0,347,W,52,c[14]);d.line((0,349,W,349),fill=c[7]);d.line((0,397,W,397),fill=c[7])
 for x in range(-65,335,62):box(d,x-int(f*2.4)%62,372,30,2,c[15])
 if opt.get('rain'):
  for i in range(10):
   x=(i*47-int(f*2.4))%290-10;y=354+(i*11)%39
   d.line((x,y,x+13,y),fill=c[0]);d.line((x+4,y+2,x+18,y+2),fill=c[4])
 # Two larger front trees plus a cropped foreground tree.
 for i,xx in enumerate([15,218,385]):
  x=int((xx-f*.6+130)%490)-130
  tr=TREES[k];im.paste(tr,(x,185+(i%2)*5),tr)
 d=ImageDraw.Draw(im)
 # Low rail maintains readable road silhouette.
 for x in range(-40,320,40):
  x-=int(f*1.2)%40;box(d,x,318,3,23,c[12]);box(d,x+1,319,1,19,c[13])
 d.line((0,325,W,325),fill=c[13],width=2)
 box(d,0,406,W,74,c[5]);box(d,0,406,W,9,c[6])
 # Fixed repeating foreground tufts, not a different random field per frame.
 rng=random.Random(76)
 for i in range(80):
  x=int((rng.randrange(W)-f*3)%W);y=rng.randrange(412,480);h=rng.randrange(3,8);s=int(math.sin(f*.06+i)*1.4)
  d.line((x-2,y-h+2,x,y,x+s,y-h),fill=c[6] if i%3 else c[7])
  if i%13==0:box(d,x+s,y-h-1,2,2,c[2])
 # Intentional moving weather and wind details.
 if opt.get('petals'):
  for i in range(17):
   x=int((i*29+f*.65+math.sin(f*.06+i)*5)%W);y=int((i*23+f*.45)%280+100)
   box(d,x,y,2,1,c[10])
 if opt.get('snow'):
  for i in range(35):
   x=int((i*37+f*.25+math.sin(f*.04+i)*3)%W);y=int((i*47+f*.7)%H);d.point((x,y),fill=c[2])
 if opt.get('rain'):
  for i in range(70):
   x=int((i*41-f*1.1)%W);y=int((i*73+f*5)%H);d.line((x,y,x-2,y+7),fill=c[1])
 # Tiny birds change their wing pose; simple 2-frame sprite recipe.
 if not opt.get('rain') and not opt.get('snow'):
  for i in range(3):
   x=int((43+i*20+f*.38)%300)-15;y=168+i*5
   flap=1 if (f//8+i)%2 else -1;d.line((x-3,y-flap,x,y,x+3,y-flap),fill=c[12])
 if opt.get('coarse'):im=im.resize((135,240),Image.Resampling.NEAREST).resize((W,H),Image.Resampling.NEAREST)
 d=ImageDraw.Draw(im);box(d,8,10,254,49,'#172b35');d.text((16,15),f'{n:02d} / {title}',font=FONT,fill='#f1e6c9');d.text((16,34),subtitle,font=SMALL,fill='#b9d4c4')
 box(d,8,455,254,16,'#172b35');d.text((16,459),'MODULAR ART / REPRODUCIBLE RECIPE',font=SMALL,fill='#d5dfce')
 return im

def main():
 meta=[]
 for n,title,subtitle,kind,raw,opt in RECIPES:
  meta.append(dict(number=n,title=title,technique=subtitle,tree=kind,palette=['#'+x for x in raw],options=opt,native=[135,240] if opt.get('coarse') else [270,480],seconds=4,source='scripts/render_style_variants.py',licence='Original authored code/pixels; repository MIT',reproducibility='Small palette, modular sprite shapes, pure frame animation. Not benchmarked against other agents.'))
 (ROOT/'studio/v4/style-auditions/recipes.json').write_text(json.dumps(meta,indent=2)+'\n')
 proc=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','270x480','-r','30','-i','-','-vf','scale=1080:1920:flags=neighbor','-an','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'Pixel_Styles_05_to_16.mp4')],stdin=subprocess.PIPE)
 try:
  for k in range(12):
   for f in range(120):
    im=render(k,f);proc.stdin.write(im.tobytes())
    if f==50:im.save(OUT/f'{RECIPES[k][0]:02d}-native.png')
   print('Rendered',RECIPES[k][0],RECIPES[k][1],flush=True)
 finally:proc.stdin.close()
 if proc.wait():raise RuntimeError('FFmpeg failed')
 sheet=Image.new('RGB',(W*4,H*3))
 for k in range(12):sheet.paste(render(k,50),((k%4)*W,(k//4)*H))
 sheet.save(OUT/'Twelve_Style_Comparison.png')
 print('DONE',flush=True)
if __name__=='__main__':main()
