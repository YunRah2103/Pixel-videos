#!/usr/bin/env python3
"""Hand-keyed pine overhang – strong foreground framing at top of vertical film."""
from PIL import Image,ImageDraw
from pathlib import Path
p=Path(__file__).parent/'v3_assets'/'01a_canopy.png'
a=Image.new('RGBA',(960,640),(0,0,0,0));d=ImageDraw.Draw(a)
def poly(pts,c):d.polygon(pts,fill=c)
def ln(pts,c,w):d.line(pts,fill=c,width=w)
def r(box,c):d.rectangle(box,fill=c)
# first piece enters from upper-left as a compositional hand-painted graphic, not a particle effect.
poly([(540,0),(691,0),(681,12),(665,27),(645,38),(625,45),(600,52),(562,74),(538,72)],'#11273a')
poly([(548,0),(674,0),(657,14),(630,24),(607,41),(577,48),(546,60)],'#223c4c')
# large branch forks, with explicit weight
ln([(548,4),(591,37),(633,55),(673,59)],'#172c3b',8)
ln([(595,39),(598,68),(619,83)],'#192e3e',5)
ln([(642,54),(667,85),(694,97)],'#1b3441',5)
# large irregular needle tufts at different heights and opening holes
bundles=[([(562,17),(604,24),(627,44),(614,57),(575,40)],'#173e49'),
         ([(586,26),(631,14),(655,33),(645,48),(606,49)],'#21505a'),
         ([(633,31),(670,21),(699,46),(686,60),(654,48)],'#173f49'),
         ([(592,58),(620,53),(641,80),(631,93),(601,81)],'#204650'),
         ([(655,65),(696,56),(713,80),(690,96),(674,83)],'#204b4f'),
         ([(673,91),(716,75),(736,100),(725,114),(688,107)],'#1a4850')]
for shape,color in bundles:poly(shape,color)
for box,c in [((584,29,613,32),'#447478'),((622,40,652,42),'#548581'),((663,57,693,60),'#527b75'),
              ((603,74,624,76),'#527d79'),((695,98,720,100),'#608a7b')]:r(box,c)
# edge tassels with 3-5 pixel torn fronds and broken negative spaces
for x,y in [(600,40),(635,48),(682,67),(705,92),(615,79),(664,40)]:
 poly([(x-8,y),(x+3,y+2),(x+10,y+17),(x+5,y+13),(x-4,y+7)],'#163747')
# right-hand smaller tree hanging above another bend
ln([(942,0),(928,20),(898,29)],'#183441',6)
poly([(854,10),(906,0),(960,0),(943,23),(918,33),(883,25)],'#193b49')
poly([(897,19),(935,10),(960,19),(955,38),(929,36)],'#24606a')
r((893,17,923,19),'#4a7c77')
a.save(p,optimize=True)
print(p)