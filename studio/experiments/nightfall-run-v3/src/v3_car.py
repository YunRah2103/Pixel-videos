#!/usr/bin/env python3
"""Hand-composed pixel-art grand-tourer, V3.2, transparent editable RGBA sprite."""
from PIL import Image,ImageDraw
from pathlib import Path
import math
AS=Path(__file__).parent/'v3_assets';AS.mkdir(exist_ok=True)
a=Image.new('RGBA',(316,143),(0,0,0,0));d=ImageDraw.Draw(a)
def p(v,c):d.polygon([(round(x),round(y)) for x,y in v],fill=c)
def r(x1,y1,x2,y2,c):d.rectangle((x1,y1,x2,y2),fill=c)
def ln(v,c,w=1):d.line(v,fill=c,width=w)
# silhouette – dramatically reduced profile, forward rake / high rear arch / long hood
p([(7,84),(14,77),(43,73),(62,69),(78,53),(102,39),(119,35),(171,36),
   (187,41),(213,69),(242,75),(278,79),(300,82),(306,90),(310,107),
   (303,114),(286,116),(35,116),(11,112),(6,106)],'#0a1626')
# rear ducktail, integrated wing with separated bracket, read clearly as tuned coupe
p([(15,70),(52,70),(61,73),(59,76),(14,76)],'#0b1b2d')
r(22,66,62,69,'#dce3d9');r(27,64,56,65,'#738b99');r(25,70,28,79,'#0a1829');r(52,70,55,76,'#0a1829')
# main metallic ivory body slabs
p([(10,86),(24,80),(68,75),(88,50),(106,41),(171,40),(186,45),(210,72),
   (236,77),(283,83),(303,88),(305,105),(297,111),(35,111),(10,107)],'#b0bdc2')
p([(18,87),(55,77),(92,48),(110,42),(167,41),(185,46),(203,70),(239,78),(279,84),
   (303,91),(304,99),(270,96),(213,92),(51,95),(14,98)],'#e5dfca')
p([(19,89),(72,78),(91,64),(211,75),(240,80),(303,91),(306,101),(277,103),(49,103),(17,100)],'#d3cab8')
# deep pearlescent shadow below glass
p([(20,100),(306,103),(303,114),(23,113)],'#42647a')
p([(22,106),(299,108),(304,112),(290,117),(28,117)],'#111d31')
r(19,114,301,118,'#0e1c2c')
# rear quarter and active side intake shapes
p([(34,80),(77,60),(83,78),(58,89),(22,94)],'#e7e0ca')
p([(17,91),(43,84),(65,84),(51,97),(17,99)],'#8199a5')
p([(45,84),(72,79),(61,88),(37,92)],'#c6d2cb')
# cab glass: back slanted + low roof + sharply raked windshield; deliberately one cabin not boxy four-door
p([(74,72),(93,47),(110,40),(171,40),(183,45),(208,74),(192,76),(84,76)],'#13283b')
p([(83,69),(99,48),(113,44),(134,43),(133,69)],'#234c60')
p([(141,43),(166,43),(177,46),(198,70),(143,69)],'#1c374c')
# glass planes, cold moon reflections
p([(89,65),(103,49),(120,46),(124,49),(108,62)],'#7aaeb5')
p([(111,48),(126,46),(131,47),(130,66),(119,65)],'#3f6571')
p([(148,46),(161,45),(176,50),(189,67),(166,58)],'#648c95')
p([(171,48),(180,54),(191,69),(186,68)],'#8aafb5')
# dark B-pillar + frameless seal
p([(131,43),(138,42),(139,74),(134,75)],'#0b293c')
# roof enamel highlight, not a plain stripe
p([(101,40),(113,36),(168,36),(186,43),(190,48),(170,40),(118,39)],'#f6efda')
r(118,39,165,39,'#f6f8e7')
p([(69,74),(209,74),(216,80),(68,79)],'#25384b')
r(78,76,205,77,'#f0edcd')
# strong black window sill and dynamic wedge shadow under A pillar
p([(204,76),(222,79),(232,83),(220,83)],'#1e3246')
# hood wedge, offset intake and designed layered highlights
p([(217,75),(253,77),(282,81),(296,86),(253,85)],'#f4ebd3')
p([(225,84),(267,83),(286,89),(238,89)],'#bfcacf')
p([(249,81),(275,83),(282,86),(258,85)],'#3f6171')
r(252,84,272,85,'#172f43')
r(260,86,273,86,'#71949b')
# two-tone motorsport stripe runs from rear into nose with taper
p([(36,92),(109,91),(211,91),(257,93),(289,98),(269,102),(33,100)],'#0e6881')
p([(38,92),(187,91),(234,92),(259,94),(202,95),(51,96)],'#1c9eae')
p([(47,101),(285,103),(279,106),(52,105)],'#e8e2bd')
# complete 2-door seam lines, sculpted rocker, door handle
ln([(140,80),(139,97),(142,109)],'#75899a',2)
ln([(202,80),(207,94),(200,107)],'#72818f',2)
ln([(140,81),(201,81)],'#ebe5cc',1)
r(158,85,171,87,'#183246');r(158,85,164,85,'#e9e1bd')
# deeper air extractor rear-wheel wake slash
for i in range(3):p([(48+i*5,97),(51+i*5,95),(54+i*5,95),(51+i*5,101)],'#0f3f55')
# accent on shoulder line, physical light/shade clusters
p([(17,81),(49,79),(77,69),(92,53),(103,48),(98,59),(75,79),(23,86)],'#faf1d7')
r(154,79,207,80,'#f1efdc')
p([(219,90),(244,92),(262,97),(223,97)],'#a5bcc1')
# headlight sliver/taillight assembly
p([(274,83),(299,85),(303,91),(294,90),(270,85)],'#112d43')
p([(276,83),(296,85),(300,89),(286,87)],'#ffe4b1')
r(298,90,307,92,'#d8a17a')
p([(8,84),(25,80),(33,80),(30,87),(10,91)],'#361f36')
p([(10,83),(28,82),(27,85),(11,88)],'#e74e68')
r(12,87,24,88,'#ffc18f')
# proper split vents and sharp front bumper air dam
p([(277,98),(307,99),(308,105),(300,108),(284,107)],'#102c3e')
r(283,102,303,103,'#2e5b66')
p([(264,110),(311,111),(313,115),(299,119),(257,116)],'#0b1929')
p([(12,107),(32,107),(38,112),(12,114)],'#132638')
# extra slim accented wheel-arch hems and actual open wheel wells
for xc in (73,243):
 rad=29
 # transparent cutouts in car body, leaving a true circular arch
 for yy in range(-rad,rad+1):
  xx=math.isqrt(max(0,rad*rad-yy*yy))
  r(xc-xx,111+yy,xc+xx,111+yy,(0,0,0,0))
 # draw outermost arch crescent 1px ONLY on above-body upper half
 for yy in range(-rad-2,-5):
  xx=math.isqrt(max(0,(rad+1)**2-yy*yy))
  for sign in (-1,1):
   xx0=xc+sign*xx;r(xx0,111+yy,xx0+1,111+yy,'#334e60')
 for sign in (-1,1):
  for xx in range(23,30,3):
   # less visible arch specks
   if xx==24: r(xc+sign*xx,88,xc+sign*xx+1,89,'#f2ecd6')
# motorsport wing top end and low diffuser guards
r(18,69,50,69,'#faf0d4')
a.save(AS/'08_coupe_body.png',optimize=True)
print('Wrote',AS/'08_coupe_body.png')