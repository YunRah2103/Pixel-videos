#!/usr/bin/env python3
"""Sunset Harbor V5 original source drawing. 360x640 indexed-scale RGBA sprite planes.
All coordinates and material clusters are hand-selected for this scene; no sourced artwork.
Uses Pillow only when re-authoring the assets; exported PNGs have no runtime dependency.
"""
from PIL import Image, ImageDraw
import math, random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]/'public/v5/world'; OUT.mkdir(parents=True,exist_ok=True)
W,H=360,640
ink='#263c51'; shade='#3b5365'; cool='#5e7887'; honey='#ffe2a9'; glint='#fff0be'
pink='#eeb4a2'; lilac='#aa899d'; dusty='#ce9c99'; pale='#f8d0b0'; teal='#3c787b'
R = random.Random(1701)
imgs={k:Image.new('RGBA',(W,H),(0,0,0,0)) for k in ['far','architecture','harbor','promenade','foreground']}
d={k:ImageDraw.Draw(im) for k,im in imgs.items()}

def poly(layer, pts, fill,outline=None):
    q=[(int(round(x)),int(round(y))) for x,y in pts]; d[layer].polygon(q,fill=fill)
    if outline: d[layer].line(q+[q[0]],fill=outline,width=1)

def line(layer,pts,c,w=1): d[layer].line([(int(x),int(y)) for x,y in pts],fill=c,width=w, joint='curve')
def rect(layer,box,c): d[layer].rectangle(tuple(int(round(z)) for z in box),fill=c)
def ell(layer,box,c): d[layer].ellipse(tuple(int(round(z)) for z in box),fill=c)

def tiles(l,positions, palette):
    for i,(x,y,dx) in enumerate(positions):line(l,[(x,y),(x+dx,y)],palette[i%len(palette)])

def brush(l,x,y, color, seq):
    for dx,dy,n in seq:rect(l,(x+dx,y+dy,x+dx+n,y+dy),color)

# Five mountain silhouettes, each irregular, disappearing toward the golden opening.
# Far plane contains no sky and does not paint open water.
poly('far',[(0,321),(10,311),(19,314),(31,301),(43,305),(57,289),(69,296),(83,273),(94,277),(109,259),(122,264),(138,242),(147,247),(158,238),(177,256),(188,245),(201,258),(215,268),(229,267),(239,276),(258,280),(275,293),(288,289),(303,306),(322,300),(338,314),(360,298),(360,355),(0,355)],'#9297b1')
poly('far',[(0,335),(22,323),(35,329),(49,315),(57,315),(72,299),(84,309),(100,289),(118,302),(128,296),(140,311),(157,302),(177,318),(196,305),(212,322),(225,313),(239,327),(252,317),(273,327),(290,315),(305,326),(322,314),(338,323),(360,315),(360,362),(0,362)],'#728c9f')
poly('far',[(0,349),(20,343),(35,346),(46,338),(64,346),(85,333),(94,341),(112,338),(135,349),(147,346),(165,349),(188,341),(199,347),(221,345),(239,350),(258,344),(278,341),(292,335),(306,339),(329,327),(350,332),(360,331),(360,370),(0,370)],'#4e7d8c')
# irregular pine-and-rock headlands close to edges, leaving golden corridor unoccluded
poly('far',[(0,357),(14,351),(23,354),(37,345),(53,353),(69,348),(83,352),(93,346),(105,354),(116,355),(134,364),(144,375),(0,381)],'#315b70')
poly('far',[(272,378),(281,358),(296,358),(307,347),(321,351),(333,342),(349,348),(360,341),(360,390),(265,388)],'#315b70')
for x,y,h in [(7,348,10),(18,341,13),(29,340,12),(47,343,16),(58,346,9),(77,343,12),(89,346,10),(102,353,8),(300,348,13),(319,341,14),(338,341,16),(349,338,11)]:
    poly('far',[(x-4,y+3),(x,y-h),(x+5,y+3)],'#31586a');rect('far',(x-1,y-2,x,y+4),'#405f70')
for x,y in [(13,334),(43,332),(75,319),(139,319),(180,320),(303,325)]:
    brush('far',x,y,'#b5b2af',[(0,0,6),(6,1,3),(2,3,5)])
# Faint village nestled in distant shore, bespoke roofs
for x,y,w in [(153,344,8),(166,342,11),(178,347,6),(254,348,8),(265,345,7),(275,342,9)]:
    poly('far',[(x-2,y),(x+w//2,y-6),(x+w+2,y)],'#596a82')
    rect('far',(x,y,x+w,y+9),'#88a0a5')
    rect('far',(x+2,y+2,x+3,y+4),'#e5b9a7')

# Buildings have individual silhouettes and illustrated face construction. No repeated grid-building generator.
def crack(l,pts,color='#956f78'):line(l,pts,color)

def masonry(l,x0,y0,w,h,color1,color2,n=32,seed=1):
    rnd=random.Random(245+seed)
    for k in range(n):
        xx=x0+rnd.randrange(max(1,w)); yy=y0+rnd.randrange(max(1,h))
        length=1+rnd.randrange(1,4)
        if k%4==0:rect(l,(xx,yy,xx+1,yy+1),color1)
        elif k%4==1:line(l,[(xx,yy),(xx+length,yy)],color2)
        elif k%4==2:line(l,[(xx,yy),(xx+length,yy),(xx+length,yy+1)],color1)
        else: rect(l,(xx,yy,xx+1,yy),color2)

def round_window(l,x,y,w=9,h=13,light=True,shutters=False):
    # Actual arched stone casing plus inset and differentiated inner glass
    poly(l,[(x-2,y+3),(x,y),(x+w-1,y),(x+w+2,y+3),(x+w+2,y+h+3),(x-2,y+h+3)],'#f1c5aa')
    poly(l,[(x,y+3),(x+2,y+1),(x+w-3,y+1),(x+w-1,y+3),(x+w-1,y+h),(x,y+h)],'#3a5368')
    poly(l,[(x+1,y+4),(x+3,y+2),(x+w-4,y+2),(x+w-2,y+4),(x+w-2,y+h-2),(x+1,y+h-2)],'#fce4b2' if light else '#7094a1')
    rect(l,(x+3,y+3,x+3,y+h-1),'#8d808c')
    line(l,[(x,y+7),(x+w-1,y+7)],'#bd9b99')
    rect(l,(x-3,y+h+2,x+w+2,y+h+3),'#d39b91')
    if shutters:
        rect(l,(x-5,y+2,x-3,y+h),'#586777');rect(l,(x+w+1,y+2,x+w+3,y+h),'#576f79')
        for yy in range(y+4,y+h,3):
            line(l,[(x-5,yy),(x-3,yy)],'#bd9c90');line(l,[(x+w+1,yy),(x+w+3,yy)],'#b69591')

def slate_roof(l,points,base,highlight,seed):
    poly(l,points,ink)
    # place real polygon fascia with lowered inner contour
    poly(l,[(x,y+2) for x,y in points[:-1]]+[points[-1]],base)
    xs=[p[0] for p in points]; ys=[p[1] for p in points]; xx=min(xs); yy=min(ys)
    # hand-positioned ridge accents never tiled wall-style
    rnd=random.Random(seed)
    for i in range(24):
        x=rnd.randint(int(xx),int(max(xs))); y=rnd.randint(int(yy),int(max(ys)))
        if l=='architecture' and imgs[l].getpixel((max(0,min(359,x)),max(0,min(639,y))))[:3] == tuple(bytes.fromhex(base.lstrip('#'))):
            line(l,[(x,y),(x+rnd.choice((2,3,4)),y)],highlight)

def doorway(l,x,y,w=14,h=27):
    poly(l,[(x-2,y+h),(x-2,y+5),(x,y+1),(x+4,y-2),(x+w-5,y-2),(x+w,y+2),(x+w+2,y+5),(x+w+2,y+h)],'#e9c3a7')
    poly(l,[(x,y+h),(x,y+5),(x+3,y+1),(x+w-3,y+1),(x+w,y+5),(x+w,y+h)],'#3b5265')
    poly(l,[(x+2,y+h),(x+2,y+6),(x+4,y+4),(x+w-4,y+4),(x+w-2,y+6),(x+w-2,y+h)],'#856976')
    rect(l,(x+w-5,y+13,x+w-4,y+14),honey)
    line(l,[(x-4,y+h),(x+w+4,y+h)],'#f5c09b',2)

def balcony(l,x,y,w,flower=True):
    poly(l,[(x-3,y+1),(x+w+3,y+1),(x+w+6,y+7),(x-5,y+7)],'#e7b39b')
    line(l,[(x-5,y+7),(x+w+6,y+7)],'#4a5c6d',2)
    line(l,[(x-4,y-11),(x+w+5,y-11)],'#35465a',2)
    for xx in range(x-2,x+w+5,6):line(l,[(xx,y-9),(xx,y+7)],'#32495d',2)
    if flower:
        for xx,yy in [(x+4,y-14),(x+10,y-17),(x+17,y-14),(x+w-3,y-17)]:
            rect(l,(xx,yy,xx+5,yy+3),'#53857a');rect(l,(xx+1,yy-3,xx+3,yy-2),'#ffbfaa');rect(l,(xx+3,yy-1,xx+4,yy),'#e98fa0')

def wrought(l,x,y,w,h=14):
    line(l,[(x,y),(x+w,y)],'#e8b7a0',2)
    line(l,[(x,y+h),(x+w,y+h)],'#314d60',2)
    for xx in range(x+2,x+w,7):
        line(l,[(xx,y+1),(xx,y+h-1)],'#354e60')
        poly(l,[(xx-2,y+5),(xx,y+2),(xx+2,y+5),(xx,y+9)],'#536c7a')

def corbel(l,x,y,color='#f6c7ac'):
    poly(l,[(x,y),(x+6,y),(x+6,y+4),(x+4,y+8),(x+1,y+8)],color)
    line(l,[(x+1,y+8),(x+5,y+8)],'#9b7f82')

# Left fishmonger - stepped masonry gable, deep overhang, asymmetrical shutters, lattice door
poly('architecture',[(-12,310),(2,301),(13,309),(15,317),(29,319),(30,401),(-10,407)],'#2d4557')
poly('architecture',[(-6,315),(3,307),(16,313),(20,320),(27,321),(28,392),(0,394)],'#aaa29e')
poly('architecture',[(-7,317),(3,300),(17,316),(20,320),(4,315)],'#6d7186',ink)
poly('architecture',[(19,319),(34,319),(30,330),(18,327)],'#816879',ink)
for x,y in [(3,331),(16,355)]:round_window('architecture',x,y,8,13,True,True)
masonry('architecture',-2,328,24,58,'#d0b0a3','#71828a',25,2)
doorway('architecture',5,378,13,23)
# Hand-carved stair stepped façade to open pier
for x,y in [(0,392),(8,395),(19,396)]:rect('architecture',(x,y,x+6,y+3),'#d0a39c')

# Signature merchant house — steep Dutch stepped gable and shaped plaster façade
poly('architecture',[(24,312),(30,307),(32,291),(38,290),(38,279),(45,276),(48,267),(54,276),(58,279),(58,292),(65,298),(67,311),(67,404),(22,405)],ink)
poly('architecture',[(26,314),(32,307),(34,293),(40,292),(40,282),(46,281),(49,270),(52,280),(56,282),(56,294),(63,302),(64,314),(63,401),(25,401)],'#edbd9f')
poly('architecture',[(29,309),(40,299),(40,283),(49,273),(57,288),(57,302),(64,310)],'#925f7a')
line('architecture',[(26,313),(49,272),(64,311)],'#ffe3ad',2)
for x,y in [(29,293),(37,283),(48,275),(57,290),(64,306)]:rect('architecture',(x-1,y,x+2,y+2),'#f8d4b3')
rect('architecture',(60,316,63,399),'#8d7b83');rect('architecture',(25,318,28,401),'#fff0c9')
for x,y in [(32,320),(49,320),(33,351),(49,351)]:round_window('architecture',x,y,9,14,True,x<40)
balcony('architecture',30,372,30,True)
doorway('architecture',39,376,14,25)
masonry('architecture',27,321,35,70,'#f8ddbd','#b78b89',50,6)
# Corner restaurant awning and scalloped hanging canvas below merchant house
poly('architecture',[(23,388),(68,386),(74,392),(19,394)],'#425268')
for x in range(22,68,7):
    poly('architecture',[(x,386),(x+7,386),(x+5,394),(x+3,395),(x+1,392)],'#f5c99e' if (x//7)%2 else '#be7280')
rect('architecture',(28,397,68,400),'#c59288')

# Original clock/bell tower — faceted copper canopy, lantern, clock, grand stone arcade.
poly('architecture',[(60,263),(64,260),(63,252),(67,249),(70,245),(71,236),(74,232),(78,236),(79,245),(84,249),(88,260),(91,265),(90,405),(60,406)],ink)
poly('architecture',[(64,263),(69,253),(73,252),(73,245),(79,245),(84,255),(87,265),(87,401),(63,401)],'#c1a2a2')
poly('architecture',[(61,259),(69,252),(69,244),(75,233),(82,246),(82,252),(90,260)],'#5a6e83',ink)
poly('architecture',[(66,257),(72,249),(73,243),(75,237),(79,244),(80,253),(85,258)],'#a78b90')
rect('architecture',(72,230,78,232),'#f0c7a8');rect('architecture',(75,223,76,230),'#6a7986')
poly('architecture',[(66,266),(83,266),(85,273),(84,283),(67,283),(65,276)],'#ecbeaa')
ell('architecture',(68,269,82,282),'#536475');ell('architecture',(70,271,80,280),'#fce6b5')
line('architecture',[(75,272),(75,276),(79,278)],'#49576a',1)
for y in [292,309,326]:
    round_window('architecture',68,y,9,12,True)
rect('architecture',(64,349,87,353),'#f3c6ae')
poly('architecture',[(66,402),(66,377),(69,369),(73,365),(80,365),(85,371),(85,402)],'#f7d0aa')
poly('architecture',[(69,401),(69,378),(72,374),(79,374),(83,379),(83,401)],'#526273')
for x in [66,84]:
    for y in range(288,362,14):rect('architecture',(x,y,x+1,y+5),'#8d808b')

# Café and residences — asymmetrical cantilevered roof, recessed arch arcade, exterior steps.
poly('architecture',[(89,314),(92,300),(105,289),(129,298),(138,314),(138,398),(86,404)],ink)
poly('architecture',[(92,318),(93,306),(105,296),(125,301),(134,312),(133,397),(91,399)],'#d69d96')
poly('architecture',[(86,316),(104,286),(132,297),(141,317),(127,311),(106,296),(96,316)],'#685a72',ink)
poly('architecture',[(104,289),(130,297),(132,302),(108,295)],'#bc7a87')
line('architecture',[(90,319),(105,291),(132,302)],'#eeb6a1',2)
poly('architecture',[(134,309),(148,318),(147,392),(133,398)],'#796f7c')
# Wooden eave outriggers placed along the actual roof slope
for x,y in [(93,317),(105,294),(122,299),(132,307)]:line('architecture',[(x-2,y),(x+3,y+3)],'#ebbd9e',2)
for x,y in [(97,330),(117,333),(97,356),(117,355)]:round_window('architecture',x,y,9,12,True,x==97)
balcony('architecture',97,371,32,True)
# Ground floor bespoke arcade with separated stone columns
for x in [94,110,125]:
    poly('architecture',[(x,393),(x,380),(x+3,375),(x+9,375),(x+12,380),(x+12,393)],'#f0bc9f')
    poly('architecture',[(x+2,393),(x+2,381),(x+5,378),(x+7,378),(x+10,381),(x+10,393)],'#42566a')
    rect('architecture',(x+4,381,x+7,386),'#f7daab')
line('architecture',[(90,396),(136,396)],'#e6b69e',2)
masonry('architecture',94,315,40,72,'#f7cbb1','#ac7e80',35,7)
# Destination waterfront coffee house to right of café, readable sign and ornamental roof
poly('architecture',[(139,353),(145,345),(152,351),(156,366),(156,402),(136,399)],ink)
poly('architecture',[(140,362),(145,350),(152,355),(153,398),(138,398)],'#b9a2a4')
poly('architecture',[(138,359),(145,345),(154,352),(159,361)],'#ac7583')
rect('architecture',(141,366,152,371),'#374c5d');rect('architecture',(143,367,151,369),honey)
rect('architecture',(143,375,152,394),'#4c6871');rect('architecture',(146,377,149,385),honey)
poly('architecture',[(105,384),(151,381),(155,389),(101,394)],'#3d5265')
for ix,x in enumerate(range(103,153,7)):
    poly('architecture',[(x,382),(x+7,382),(x+6,391),(x+3,393),(x,390)],'#f2d6ae' if ix%2 else '#b86f7e')

# Right headland fishing houses: layered alley, curving roofline and a lilac fish-market hotel
poly('architecture',[(264,343),(275,339),(278,323),(288,321),(303,334),(309,354),(313,399),(265,401)],ink)
poly('architecture',[(269,346),(276,341),(279,326),(289,324),(300,336),(304,349),(308,395),(267,399)],'#aeb4a8')
poly('architecture',[(264,341),(273,334),(277,318),(285,313),(296,321),(308,344),(294,338),(288,326),(281,323),(276,343)],'#5e7182',ink)
line('architecture',[(273,334),(285,317),(306,341)],'#e5c0a4',2)
for x,y in [(276,349),(291,351),(278,371),(293,374)]:round_window('architecture',x,y,8,12,True,False)
rect('architecture',(268,388,307,394),'#cba69c')
masonry('architecture',272,345,31,44,'#e2c6ac','#6d8a86',25,10)
# Large right hotel with shaped Normandy hip roof and overhanging balcony
poly('architecture',[(301,311),(308,301),(324,300),(328,286),(335,285),(340,273),(347,283),(352,286),(356,305),(365,316),(365,412),(298,409)],ink)
poly('architecture',[(304,315),(312,304),(326,303),(333,288),(341,278),(351,288),(356,309),(356,404),(302,402)],'#d6aba7')
poly('architecture',[(300,314),(310,295),(328,295),(339,267),(352,296),(365,313),(350,306),(338,278),(331,303),(313,306)],'#5a5d75',ink)
poly('architecture',[(314,295),(326,295),(331,304),(312,304)],'#9d728a')
line('architecture',[(339,270),(339,262)],'#445b6e',2);rect('architecture',(334,261,345,263),honey)
# round tower bay and mansard dormers
poly('architecture',[(314,316),(317,311),(329,307),(338,312),(340,316),(338,401),(314,400)],'#b3919c')
for x,y in [(310,322),(325,320),(344,321),(311,351),(327,349),(345,351)]:round_window('architecture',x,y,8,13,True,x==345)
balcony('architecture',310,372,41,True)
doorway('architecture',338,376,14,28)
masonry('architecture',304,316,53,75,'#ffe0b7','#9c7981',60,15)
for x,y in [(308,299),(348,294)]:
    poly('architecture',[(x-3,y+7),(x+4,y-4),(x+12,y+7)],'#35485f')
    poly('architecture',[(x,y+5),(x+4,y),(x+9,y+5)],'#b28190')
    rect('architecture',(x+3,y+7,x+7,y+12),honey)
# Non-uniform signage, ropes and hanging textiles
rect('architecture',(133,349,135,369),'#334f60');rect('architecture',(129,350,140,358),'#3b5365')
rect('architecture',(131,352,139,356),'#f1cda9');rect('architecture',(133,353,134,355),'#a26c77')
line('architecture',[(2,341),(25,339)],'#e5bba8')
for x,c in [(4,'#f6d3ac'),(12,'#98b5b0'),(21,'#bb799a')]:
    poly('architecture',[(x,341),(x+6,341),(x+7,351),(x+4,354),(x,352)],c)
# Curved blue vines climb masonry, with exactly composed coral flowers
for x,y in [(359,315),(355,323),(357,332),(351,337),(354,345),(352,354),(359,360),(352,369),(355,378),(347,388),(352,397)]:
    poly('architecture',[(x,y),(x-4,y-3),(x-8,y-2),(x-6,y+1),(x-2,y+2)],'#548577')
for x,y in [(354,324),(351,348),(356,373),(346,389)]:rect('architecture',(x,y,x+2,y+2),'#ffa6ab')

# Fishing quay: physical material edge, carved arch stones, asymmetrical timber piers.
poly('harbor',[(0,397),(146,393),(151,414),(113,433),(0,425)],'#263e51')
poly('harbor',[(0,394),(142,390),(148,397),(0,407)],'#e8bda6')
poly('harbor',[(0,407),(143,402),(135,421),(0,421)],'#627984')
poly('harbor',[(279,402),(360,389),(360,433),(304,428)],'#2b495b')
poly('harbor',[(280,397),(360,384),(360,393),(282,409)],'#f3c6aa')
for x,y in [(0,405),(27,405),(54,405),(83,404),(111,401),(294,402),(321,396),(343,390)]:
    poly('harbor',[(x,y+6),(x,y-7),(x+2,y-12),(x+10,y-12),(x+12,y-7),(x+12,y+6)],'#395368')
    poly('harbor',[(x+2,y+4),(x+2,y-6),(x+5,y-9),(x+8,y-9),(x+10,y-6),(x+10,y+4)],'#ddad94')
    rect('harbor',(x+4,y-3,x+7,y+3),'#ffe7b5')
for j,y in enumerate([409,415,422]):
    for k,x in enumerate(range(-12,361,22)):
        if (k*3+j)%4==0:line('harbor',[(x+4+j*6,y),(x+13+j*6,y)],'#879396')
        else:line('harbor',[(x,y),(x+10,y)],'#596d7b')
# one broad authentic fishing jetty with converging boards, perspective shapes
poly('harbor',[(0,428),(80,421),(127,447),(38,469),(0,457)],'#304657')
poly('harbor',[(0,426),(80,420),(127,445),(37,462),(0,450)],'#a27b78')
poly('harbor',[(0,427),(79,423),(118,445),(37,457),(0,448)],'#bd9682')
for x0,y0,x1,y1 in [(7,427,41,456),(21,426,52,454),(35,425,66,452),(50,423,82,449),(66,423,99,447),(81,422,117,443)]:
    line('harbor',[(x0,y0),(x1,y1)],'#644f61')
for x,y,h in [(7,442,42),(30,450,39),(56,449,38),(82,447,35),(112,447,32)]:
    rect('harbor',(x,y,x+5,y+h),'#2c4356');rect('harbor',(x+1,y+3,x+1,y+13),'#a4867f')
for x,y in [(13,420),(41,422),(74,422),(109,429),(327,405),(349,399)]:
    rect('harbor',(x,y-16,x+4,y+9),'#2e4a5a')
    rect('harbor',(x-1,y-16,x+5,y-13),'#ffd4a3')
    line('harbor',[(x+5,y-2),(x+10,y+1),(x+17,y+1)],'#c0a18e')
# individually placed crates/net floats & net textures
for x,y,sz in [(18,442,12),(44,455,10),(64,453,10),(108,422,9)]:
    poly('harbor',[(x,y),(x+sz,y-2),(x+sz+1,y+sz-2),(x,y+sz)],'#625d68')
    poly('harbor',[(x+1,y+1),(x+sz-1,y),(x+sz-1,y+sz-3),(x+1,y+sz-1)],'#aa7e72')
    for z in range(2,sz,4):line('harbor',[(x+z,y),(x+z,y+sz)],'#34495c')
for x,y in [(17,450),(51,463),(67,463)]:
    for dy in range(0,6,2):line('harbor',[(x,y+dy),(x+8,y+dy)],'#b2a090')
# Old tiled stairway from tavern down to quay, tapered at the bottom
for i in range(7):
    x=130+i*2;y=394+i*7
    poly('harbor',[(x,y),(x+24-i*2,y),(x+22-i*2,y+3),(x-2,y+3)],'#d3a99a')
    line('harbor',[(x-1,y+4),(x+23-i*2,y+4)],'#536a79')
line('harbor',[(130,398),(150,438)],'#304b5c',2)
# Right narrow jetty points into frame, no moving boats (agent 3 owns story)
poly('harbor',[(331,420),(360,414),(360,427),(331,439),(307,430)],'#3a5366')
poly('harbor',[(330,415),(360,409),(360,422),(331,433),(308,424)],'#bc8f81')
for x,y in [(323,428),(345,425)]:rect('harbor',(x,y,x+4,y+31),'#2d4656')

# Promenade: hand-laid cobbles in perspective, bright quay curb, asymmetric path layout
poly('promenade',[(0,506),(360,517),(360,640),(0,640)],'#2d4557')
poly('promenade',[(0,510),(360,526),(360,540),(0,525)],'#bda39b')
poly('promenade',[(0,522),(360,538),(360,552),(0,535)],'#687b82')
poly('promenade',[(0,536),(360,549),(360,640),(0,640)],'#486473')
poly('promenade',[(0,541),(360,555),(360,559),(0,545)],'#344e61')
# Perspective courses authored in staggered, nonrepeating lengths
for row,y in enumerate([554,564,575,587,600,615,630]):
    line('promenade',[(0,y),(360,y+int(row*.55))],'#82908e')
    xs=[];x=-26 + (row%3)*7
    rnd=random.Random(500+row)
    while x<365:
        seg=rnd.choice([18,22,26,29,34,40]);xs.append((x,y,seg));x+=seg
    for i,(x,yy,w) in enumerate(xs):
        v=7+row*2
        line('promenade',[(x,yy+1),(x,yy+v)],'#2b4c5d')
        if i%3==0:line('promenade',[(x+5,yy+3),(x+11,yy+3)],'#9caaa1')
        if i%5==2:rect('promenade',(x+9,yy+7,x+12,yy+8),'#707c85')
# A separate inviting curved step stage for characters (open around x176-270)
poly('promenade',[(65,548),(95,546),(129,551),(143,560),(64,561)],'#78868b')
line('promenade',[(65,548),(95,546),(129,551),(143,560)],'#dab59c',2)
# Antique promenade balustrade follows shoreline but gaps around front-story stage
line('promenade',[(0,505),(89,508),(136,510)],'#ead0b0',2)
line('promenade',[(264,514),(360,519)],'#ead0b0',2)
for x in list(range(4,140,14))+list(range(270,361,15)):
    y=int(503+x*.044)
    rect('promenade',(x,y,x+3,y+25),'#375367');rect('promenade',(x+1,y+4,x+1,y+21),'#87989b')
    poly('promenade',[(x-2,y-3),(x+6,y-3),(x+6,y),(x-2,y)],'#e1b9a1')
    rect('promenade',(x-1,y-6,x+5,y-4),'#34495b')
line('promenade',[(0,522),(141,529)],'#354e5e',2)
line('promenade',[(266,534),(360,539)],'#354e5e',2)
# Real solid cast iron bench silhouette, hand-shaped legs and wood slats
for y,c in [(553,'#e7b69c'),(558,'#c38c7d'),(565,'#a57571')]:
    poly('promenade',[(81,y),(143,y-1),(148,y+3),(84,y+5)],c)
for x in [87,138]:
    line('promenade',[(x,561),(x-2,579)],'#2d4659',3)
    line('promenade',[(x,573),(x+9,575)],'#2d4659',2)
for x in range(90,143,10):rect('promenade',(x,552,x+2,562),'#ffe0b4')
# boutique outdoor café environment on right, imperfect round parasol and table
poly('promenade',[(267,562),(274,551),(286,546),(302,548),(313,554),(323,565),(317,562),(300,557),(283,557)],'#bb8391')
poly('promenade',[(275,560),(280,551),(290,549),(306,553),(317,561)],'#eab59e')
line('promenade',[(295,556),(295,589)],'#42596c',2)
ell('promenade',(277,566,315,572),'#e2b59d');line('promenade',[(278,572),(312,572)],'#987b7c',2)
rect('promenade',(292,573,296,593),'#344f60')
for x in [285,308]:
    line('promenade',[(x,583),(x+2,599)],'#334c5e',2)
rect('promenade',(284,562,289,567),'#fbdbba');rect('promenade',(306,563,311,566),'#f5c8ad')
for x in [286,309]:line('promenade',[(x,557),(x+2,557)],'#d8a28f')
# Some narrow cobbled flower beds at extreme frame edge not busy at centre
poly('promenade',[(0,588),(29,590),(35,640),(0,640)],'#3b625c')
poly('promenade',[(329,600),(360,584),(360,640),(321,640)],'#3b625c')
for x,y in [(7,602),(17,611),(26,628),(344,605),(333,618),(347,630)]:
    line('promenade',[(x,y+12),(x,y)],'#64967e');rect('promenade',(x-1,y-2,x+2,y),'#ed9fa0')

# Foreground artist-authored flowering terraces, iron lamp silhouettes and trellised foliage

def gas_lamp(x,y,scale=1):
    # native integer-only for crisp edges
    def rr(x1,y1,x2,y2,c):rect('foreground',(x+x1*scale,y+y1*scale,x+x2*scale,y+y2*scale),c)
    def po(points,c):poly('foreground',[(x+a*scale,y+b*scale) for a,b in points],c)
    rr(-2,13,2,121,ink);rr(-1,21,0,98,'#957d7e');rr(-6,115,6,119,ink)
    po([(-9,1),(-5,-7),(-1,-14),(3,-13),(9,-5),(10,1)],'#283d50')
    po([(-6,4),(-5,-3),(4,-3),(7,4),(5,18),(-6,18)],'#425a6b')
    rr(-4,3,4,13,'#ffe1aa');rr(-3,4,3,8,'#fff1c2');rr(-9,17,10,19,'#d6a48d');rr(-7,19,8,21,ink)
    rr(-4,26,4,28,'#cb9f8a');rr(-6,118,6,122,ink)

gas_lamp(22,453,1)
gas_lamp(343,472,.8)
# Hand-sculpted planters and cascading botanical leaves (no identical repeated shrubs)
poly('foreground',[(0,592),(31,585),(36,614),(29,640),(0,640)],'#254b56')
poly('foreground',[(323,592),(350,583),(360,584),(360,640),(329,640)],'#294b59')
# Left forged flower urn, generous irregular plants with varied leaf forms
poly('foreground',[(1,597),(25,596),(22,625),(5,627)],'#8c6a73')
poly('foreground',[(0,596),(27,594),(29,601),(0,602)],'#edb399')
for x,y,w,h,cc in [(4,585,11,9,'#4f8876'),(10,576,13,8,'#649581'),(19,570,9,10,'#3a766b'),(0,567,8,9,'#8ba88d'),(16,589,16,7,'#789b7f'),(25,580,8,10,'#508a73'),(2,578,7,6,'#9caa85')]:
    poly('foreground',[(x,y+h),(x-2,y+3),(x+2,y),(x+w,y-2),(x+w+2,y+2),(x+w-1,y+h)],cc)
for x,y,c in [(6,571,'#ffd5b1'),(14,579,'#e99da5'),(24,576,'#ffc2a8'),(10,586,'#ffdea9'),(30,586,'#eea2a5'),(3,591,'#e99298')]:
    rect('foreground',(x,y,x+3,y+2),c);rect('foreground',(x+1,y-2,x+2,y+4),'#f3b8b0')
# Right terracotta tall planter and olive branches
poly('foreground',[(338,592),(360,589),(360,628),(347,625)],'#9c6e73')
poly('foreground',[(337,589),(360,586),(360,598),(335,598)],'#e9ae91')
line('foreground',[(346,590),(348,565),(353,548)],'#345b60',2)
line('foreground',[(348,577),(333,555)],'#345b60',2)
for x,y,w,cc in [(326,553,8,'#679985'),(330,550,9,'#47796f'),(349,547,12,'#88a58f'),(342,569,10,'#3c7368'),(353,557,7,'#79a18d'),(327,566,10,'#55917b'),(339,543,7,'#538772')]:
    poly('foreground',[(x,y),(x+w,y-4),(x+w-1,y+2),(x+3,y+4)],cc)
for x,y in [(331,554),(349,546),(356,563),(339,570)]:rect('foreground',(x,y,x+2,y+2),'#ffb7a5')
# Sculpted hanging wisteria threaded over frame corner, copper trellis
line('foreground',[(0,632),(12,630),(22,626)],'#614e60',2)
for x,y in [(1,622),(5,612),(14,619),(17,628),(24,624)]:
    poly('foreground',[(x-3,y),(x+3,y-4),(x+7,y),(x+2,y+3)],'#487b70')
    rect('foreground',(x,y,x+2,y+3),'#b9a1b8')
# Hand-laid scenic stone detail in foreground, restrained
for x,y,w in [(42,619,10),(59,624,7),(170,627,13),(205,632,8),(266,624,11),(295,638,9)]:
    line('foreground',[(x,y),(x+w,y)],'#97a19d')
    line('foreground',[(x+3,y+1),(x+8,y+1)],'#3c5967')

for name,img in imgs.items():
    img.save(OUT/f'{name}.png',optimize=True)
    print(name,(OUT/f'{name}.png').stat().st_size, 'pixels=',sum(1 for p in img.getdata() if p[3]>0))

# Simplified layered contact preview against existing V4 still supplied only as local QA aid;
# source layers stay transparent and separate on disk.
base=Path(__file__).resolve().parent/'v4/v4-final-qa/frame-090.png'
if base.exists():
    v4=Image.open(base).convert('RGBA').resize((360,640),Image.Resampling.NEAREST)
    # show full V5 planes independently against existing V4 shot, will not represent full final composite
    for name in imgs:
        v4=Image.alpha_composite(v4,imgs[name])
    v4.resize((1080,1920),Image.Resampling.NEAREST).convert('RGB').save(Path(__file__).resolve().parent/'preview-overlay.png')
# Source plane composite for inspection on neutral blue (no reuse of old architecture)
can=Image.new('RGBA',(360,640),'#25465c')
for img in imgs.values():can=Image.alpha_composite(can,img)
can.resize((1080,1920),Image.Resampling.NEAREST).convert('RGB').save(Path(__file__).resolve().parent/'preview-planes.png')
# Rebuild the git-bundled indexed-colour atlas in identical native coordinates.
atlas=Image.new('RGBA',(W,H*5),(0,0,0,0))
for i,layer_name in enumerate(['far','architecture','harbor','promenade','foreground']):
    atlas.alpha_composite(imgs[layer_name],(0,i*H))
atlas.quantize(colors=128,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE).save(OUT/'world-v5-atlas.png',optimize=True)
print('Atlas ready:',OUT/'world-v5-atlas.png')
