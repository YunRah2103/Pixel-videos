#!/usr/bin/env python3
"""Create real editable OpenRaster (.ora) documents for Krita/Pixelorama.
The original native-pixel PNGs are first produced by Sharp from LDtk.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED,ZIP_STORED
import xml.etree.ElementTree as ET

root=Path("studio/countryside/world/sources")
root.mkdir(parents=True,exist_ok=True)
for name,width,height in [("sky",360,480),("nearTrees",960,235),("midTrees",840,265),("farTrees",720,300)]:
    source=Path(f"public/countryside/world/{name}.png")
    if not source.is_file(): raise FileNotFoundError(source)
    image=ET.Element("image",{"version":"0.0.1","w":str(width),"h":str(height),"name":"Countryside V3 "+name})
    stack=ET.SubElement(image,"stack",{"name":"Original native-pixel layers"})
    ET.SubElement(stack,"layer",{"name":name+" — hand-authored pixel clusters","src":"data/layer0.png","x":"0","y":"0","opacity":"1.0","visibility":"visible","composite-op":"svg:src-over"})
    with ZipFile(root/(name+".ora"),"w") as z:
        z.writestr("mimetype","image/openraster",compress_type=ZIP_STORED)
        z.writestr("stack.xml",ET.tostring(image,encoding="utf-8",xml_declaration=True),compress_type=ZIP_DEFLATED)
        z.write(source,"data/layer0.png",compress_type=ZIP_DEFLATED)
        z.write(source,"mergedimage.png",compress_type=ZIP_DEFLATED)
    print("EDITABLE_OPENRASTER",root/(name+".ora"))
