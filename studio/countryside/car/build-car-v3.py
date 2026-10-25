#!/usr/bin/env python3
"""Original layered 16-bit GT sprite for Pixelorama editing/export. Native 192x80, no filters/vector assets."""
from PIL import Image,ImageDraw
from zipfile import ZipFile,ZIP_DEFLATED
from xml.etree.ElementTree import Element,SubElement,tostring
from io import BytesIO
from pathlib import Path
import math,hashlib,json
P=Path('studio/countryside/car/v3-source');P.mkdir(parents=True,exist_ok=True)
Q=Path('public/countryside/car');Q.mkdir(parents=True,exist_ok=True)
W,H=192,80
C={'outline':'#1b2732','seam':'#313244','shadow':'#56263a','low':'#8b2940','base':'#c7444a','mid':'#e45854','light':'#f17b61','sun':'#ffb77d','cream':'#ffe6a9','dark':'#a43340','glass0':'#102735','glass1':'#24465b','glass2':'#3b7280','glass3':'#93ced0','trim':'#374855','chrome':'#bbd3cc','fog':'#f8e5ae','lamp':'#db3550','wheel':'#1f2933','tyre':'#232d36','tyre0':'#131e2a','tyre1':'#3c454b','metal':'#b2baba','metal1':'#f5f1d9'}
def im(w=W,h=H):return Image.new('RGBA',(w,h),(0,0,0,0))
def ora(path,layers,w,h):
 root=Element('image',{'w':str(w),'h':str(h),'name':'Original 16-bit coupe','version':'0.0.1'})
 stack=SubElement(root,'stack');merged=im(w,h)
 with ZipFile(path,'w',ZIP_DEFLATED) as z:
  z.writestr('mimetype','image/openraster',compress_type=0)
  for _,pic in layers:merged.alpha_composite(pic)
  b=BytesIO();merged.save(b,format='PNG');z.writestr('mergedimage.png',b.getvalue())
  for i in reversed(range(len(layers))):
   name,pic=layers[i];dst='data/layer%d.png'%i;b=BytesIO();pic.save(b,format='PNG')
   z.writestr(dst,b.getvalue())
   SubElement(stack,'layer',{'name':name,'src':dst,'opacity':'1.0','visibility':'visible','composite-op':'svg:src-over','x':'0','y':'0'})
  z.writestr('stack.xml',tostring(root,encoding='utf-8',xml_declaration=True))
 return merged
body=im();d=ImageDraw.Draw(body)
d.polygon([(4,55),(8,50),(23,47),(37,39),(48,32),(59,25),(72,19),(107,17),(121,20),(135,30),(145,37),(171,41),(184,45),(190,49),(190,62),(187,67),(171,69),(159,68),(142,69),(62,69),(54,70),(28,70),(13,68),(7,65)],fill=C['outline'])
d.polygon([(7,54),(15,50),(38,44),(51,33),(61,27),(74,21),(106,20),(117,22),(135,36),(148,40),(175,44),(188,50),(187,63),(182,65),(13,65),(8,62)],fill=C['low'])
d.polygon([(8,53),(25,49),(54,40),(65,31),(77,25),(107,24),(118,28),(139,39),(168,43),(184,46),(188,50),(180,52),(24,56),(8,56)],fill=C['base'])
d.polygon([(13,54),(36,50),(55,40),(67,30),(78,25),(106,24),(116,28),(133,38),(166,43),(181,46),(166,46),(137,42),(42,53)],fill=C['mid'])
d.polygon([(10,63),(187,63),(184,68),(21,69),(11,66)],fill=C['shadow'])
d.line([(17,64),(180,64)],fill=C['dark'],width=2)
gloss=im();s=ImageDraw.Draw(gloss)
s.polygon([(25,48),(49,38),(66,28),(78,24),(104,23),(111,25),(98,26),(75,28),(58,37),(39,46)],fill=C['sun'])
s.line([(22,50),(41,45),(51,41)],fill=C['cream'])
s.polygon([(136,39),(169,44),(183,47),(159,45),(138,42)],fill=C['light'])
s.line([(111,25),(115,26),(119,30)],fill=C['cream'])
s.line([(20,57),(179,54)],fill=C['light'])
s.line([(20,58),(179,55)],fill=C['dark'])
s.polygon([(69,57),(115,56),(135,57),(118,58)],fill=C['sun'])
s.line([(16,62),(28,62)],fill=C['sun'])
s.line([(165,62),(185,61)],fill=C['sun'])
s.polygon([(26,52),(33,48),(45,45),(40,48)],fill=C['light'])
windows=im();g=ImageDraw.Draw(windows)
g.polygon([(57,38),(70,24),(80,21),(108,21),(119,25),(137,40),(111,41),(59,41)],fill=C['outline'])
g.polygon([(61,37),(72,26),(80,24),(103,24),(104,38),(62,38)],fill=C['glass1'])
g.polygon([(108,24),(117,28),(132,39),(109,39)],fill=C['glass0'])
g.polygon([(73,27),(81,25),(88,25),(68,37),(63,37)],fill=C['glass3'])
g.polygon([(90,25),(99,25),(88,38),(80,38)],fill=C['glass2'])
g.polygon([(112,26),(116,29),(126,38),(116,38)],fill=C['glass2'])
g.line([(106,24),(106,40)],fill=C['outline'],width=3)
g.line([(60,41),(136,41)],fill=C['seam'])
g.line([(61,42),(136,42)],fill=C['sun'])
g.polygon([(126,40),(132,38),(137,39),(137,43),(132,44),(126,42)],fill=C['outline'])
g.rectangle((130,39,136,40),fill=C['glass3'])
g.line([(108,43),(108,61)],fill=C['dark'])
g.line([(110,44),(110,59)],fill=C['mid'])
g.line([(112,48),(122,48)],fill=C['outline'],width=2)
g.line([(114,48),(120,48)],fill=C['chrome'])
detail=im();f=ImageDraw.Draw(detail)
f.polygon([(178,47),(187,48),(189,51),(187,54),(176,52)],fill=C['outline'])
f.polygon([(179,48),(187,49),(187,51),(178,50)],fill=C['fog'])
f.line([(179,48),(186,48)],fill=C['cream'])
f.polygon([(7,53),(13,51),(17,53),(16,58),(8,57)],fill=C['outline'])
f.rectangle((9,53,14,55),fill=C['lamp'])
f.line([(186,56),(189,55),(189,61),(185,63)],fill=C['outline'],width=2)
f.rectangle((172,59,184,60),fill=C['glass0'])
f.line([(173,58),(183,58)],fill=C['trim'])
f.line([(75,65),(122,65)],fill=C['sun'])
f.rectangle((6,61,11,63),fill=C['trim'])
f.polygon([(8,49),(9,46),(23,46),(24,48),(12,49)],fill=C['outline'])
f.line([(11,47),(22,47)],fill=C['light'])
# Wheel openings cut out from ALL body layers, exposing animated tyre sprites behind paint.
layers=[('Paint silhouette and belly',body),('Hand placed specular paint',gloss),('Window pillars and glass reflection',windows),('Lights panels and arch lips',detail)]
for name,pic in layers:
 p=pic.load()
 for cx in (43,151):
  for y in range(45,80):
   for x in range(cx-20,cx+21):
    if math.hypot(x-cx,y-64)<17.8:p[x,y]=(0,0,0,0)
f=ImageDraw.Draw(detail)
for cx in (43,151):
 for deg in range(201,341,8):
  a=math.radians(deg);x=round(cx+19*math.cos(a));y=round(64+19*math.sin(a))
  if 43<=y<=64:f.point((x,y),fill=C['light'] if deg<270 else C['dark'])
merged=ora(P/'coupe-v3-editable.ora',layers,W,H)
merged.save(Q/'coupe-v3-preview.png')
# Eight distinct native-pixel wheel frames in three independently editable Pixelorama layers.
rubber=im(256,32);r=ImageDraw.Draw(rubber)
spokes=im(256,32);s=ImageDraw.Draw(spokes)
finish=im(256,32);t=ImageDraw.Draw(finish)
for frame in range(8):
 ox=frame*32
 for y in range(32):
  for x in range(32):
   dist=math.hypot(x-15.5,y-15.5)
   if dist<=15.45:
    color=C['tyre0'] if dist>14.5 else C['tyre'] if dist>12.2 else C['tyre1'] if dist>11.35 else C['outline'] if dist>10 else C['metal'] if dist>8.6 else C['wheel']
    r.point((ox+x,y),fill=color)
 for k in range(16):
  a=2*math.pi*k/16;x=round(15.5+14*math.cos(a));y=round(15.5+14*math.sin(a))
  if 0<=x<32 and 0<=y<32:t.point((ox+x,y),fill=C['tyre1'] if k%2==0 else C['tyre0'])
 for spoke in range(5):
  angle=frame*math.pi/4+spoke*2*math.pi/5
  for radius in range(4,10):
   x=round(15.5+radius*math.cos(angle));y=round(15.5+radius*math.sin(angle))
   s.point((ox+x,y),fill=C['metal1'] if radius<7 else C['metal'])
   if 5<=radius<=8 and x+1<32:s.point((ox+x+1,y),fill=C['metal'])
 t.ellipse((ox+12,12,ox+19,19),fill=C['outline'])
 t.ellipse((ox+14,14,ox+17,17),fill=C['metal1'])
 t.point((ox+15,14),fill=C['glass3'])
strip=ora(P/'coupe-v3-wheels-editable.ora',[('Tire carcass',rubber),('Rotating forged five spokes',spokes),('Tread and hubs',finish)],256,32)
strip.save(Q/'coupe-v3-wheels-preview.png')
assert len({strip.crop((i*32,0,(i+1)*32,32)).tobytes() for i in range(8)})==8
(P/'manifest.json').write_text(json.dumps({'bodySize':[W,H],'wheelSheetSize':[256,32],'wheelFrames':8,'bodyLayers':[n for n,_ in layers],'source':'original native-pixel editable OpenRaster','preview_sha256':hashlib.sha256(merged.tobytes()).hexdigest()},indent=2)+'\n')
print('CAR_V3_EDITABLE_OK 192x80 body, layered ORA, eight 32x32 animated wheels')
