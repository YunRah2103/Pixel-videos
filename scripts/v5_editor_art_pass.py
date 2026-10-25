#!/usr/bin/env python3
"""V5 experimental native editor round-trip.

Produces ORIGINAL transparent, pixel-native car detail layers as an editable
OpenRaster stack, sends the art through Krita's real exporter and LibreSprite's
real batch export, and adopts LibreSprite's *actual* exported sprite atlas for
the film. No fake editor screenshots or claims of brush/stylus GUI painting.

Usage:
 python3 scripts/v5_editor_art_pass.py prepare
 xvfb-run -a krita out/pixel-v5-portrait/car-detail-source.ora --export --export-filename out/pixel-v5-portrait/car-detail-krita.png
 APPIMAGE_EXTRACT_AND_RUN=1 xvfb-run -a .tools/pixel-v5/editors/libresprite.AppImage -b out/pixel-v5-portrait/car-detail-krita.png --save-as out/pixel-v5-portrait/car-detail-libresprite.png
 python3 scripts/v5_editor_art_pass.py cels
 APPIMAGE_EXTRACT_AND_RUN=1 xvfb-run -a .tools/pixel-v5/editors/libresprite.AppImage -b out/pixel-v5-portrait/editor-cels/car-cel-*.png --sheet-type horizontal --sheet out/pixel-v5-portrait/car-editor-atlas.png --data out/pixel-v5-portrait/car-editor-atlas.json
 python3 scripts/v5_editor_art_pass.py adopt
"""
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from PIL import Image, ImageDraw
from v5_sports_car import car_cel

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'out/pixel-v5-portrait'
CELDIR=OUT/'editor-cels'
W,H=164,66
N=24

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def png_bytes(image):
    dst=io.BytesIO()
    image.save(dst,format='PNG')
    return dst.getvalue()

def specular_layers():
    # Deliberately clustered paint/rain highlights in three manually specified
    # layers: not a noise function and not vector smoothing.
    body=Image.new('RGBA',(W,H))
    d=ImageDraw.Draw(body,'RGBA')
    # Sloping canopy ridge/side shoulder specular; clustered paint ramps.
    d.line((59,29,72,17),fill=(132,218,212,220),width=1)
    d.line((73,16,88,16),fill=(244,178,165,240),width=1)
    d.line((98,16,108,16),fill=(119,204,202,170),width=1)
    d.line((48,37,67,37),fill=(171,224,204,150),width=1)
    d.line((77,37,92,37),fill=(79,213,213,205),width=1)
    d.line((103,38,114,38),fill=(85,197,209,150),width=1)
    d.line((125,35,139,37),fill=(245,136,174,220),width=1)
    d.line((142,39,149,40),fill=(245,192,148,230),width=1)
    d.line((18,42,26,42),fill=(230,99,142,170),width=1)
    d.line((55,45,86,45),fill=(81,193,187,110),width=1)
    d.line((98,45,118,45),fill=(57,196,208,135),width=1)
    for p,c in [((29,36),(242,185,166,220)),((31,36),(255,215,158,230)),
                ((47,41),(255,126,167,190)),((51,42),(146,226,210,180)),
                ((64,33),(126,214,224,160)),((76,15),(255,200,172,205)),
                ((91,33),(235,127,151,190)),((120,35),(170,226,213,180)),
                ((145,43),(118,238,213,190)),((151,42),(255,212,159,210))]:
        d.point(p,fill=c)

    material=Image.new('RGBA',(W,H))
    m=ImageDraw.Draw(material,'RGBA')
    # Small deliberately asymmetrical hand-clustered water/runoff on paint.
    for x,y in ((25,39),(46,41),(63,38),(83,40),(117,42),(138,42)):
        m.point((x,y),fill=(166,235,221,155))
        m.point((x+1,y),fill=(103,212,210,100))
    m.line((10,47,15,47),fill=(221,101,127,150),width=1)
    m.line((55,49,74,49),fill=(22,63,87,195),width=1)
    m.line((99,49,113,49),fill=(16,66,80,200),width=1)
    for x,y in ((34,35),(42,34),(109,35),(119,37)):
        m.point((x,y),fill=(250,157,157,180))
    return [('Neon reflections — drawn pixel clusters',body),
            ('Paint material breaks',material)]

def prepare():
    OUT.mkdir(parents=True,exist_ok=True)
    layers=specular_layers()
    flattened=Image.new('RGBA',(W,H))
    for _,layer in reversed(layers):
        flattened.alpha_composite(layer)
    xml=Element('image',{'w':str(W),'h':str(H),'name':'V5 GT neon body detail','version':'0.0.1'})
    stack=SubElement(xml,'stack')
    ora=OUT/'car-detail-source.ora'
    with zipfile.ZipFile(ora,'w') as archive:
        archive.writestr('mimetype','image/openraster',compress_type=zipfile.ZIP_STORED)
        archive.writestr('mergedimage.png',png_bytes(flattened))
        for i,(name,layer) in enumerate(layers):
            src=f'data/layer{i}.png'
            archive.writestr(src,png_bytes(layer))
            SubElement(stack,'layer',{'name':name,'src':src,'opacity':'1.0',
                                      'visibility':'visible','composite-op':'svg:src-over',
                                      'x':'0','y':'0'})
        archive.writestr('stack.xml',tostring(xml,encoding='utf-8',xml_declaration=True))
    flattened.save(OUT/'car-detail-source-reference.png')
    print('EDITOR_SOURCE_PREPARED',ora,'layers',len(layers))

def make_cels():
    source=OUT/'car-detail-libresprite.png'
    if not source.is_file():raise FileNotFoundError('LibreSprite processed overlay missing')
    overlay=Image.open(source).convert('RGBA')
    assert overlay.size==(W,H),overlay.size
    assert len(set(overlay.getdata()))>6,'Editor exported a blank/flat result'
    CELDIR.mkdir(parents=True,exist_ok=True)
    for i in range(N):
        im=car_cel(i)
        im.alpha_composite(overlay)
        im.save(CELDIR/f'car-cel-{i:02d}.png')
    print('EDITOR_CELS_PREPARED',len(list(CELDIR.glob('car-cel-*.png'))),'from',source)

def adopt():
    atlas=OUT/'car-editor-atlas.png'
    if not atlas.is_file():raise FileNotFoundError('LibreSprite sprite atlas was not exported')
    sheet=Image.open(atlas).convert('RGBA')
    # LibreSprite's --sheet-type horizontal, with 24 unique same-size source cels
    # and default 0px padding, must fit this exact continuous atlas.
    if sheet.size not in ((W*N,H),(W,H*N)):
        raise AssertionError(f'Unexpected LibreSprite sprite atlas geometry: {sheet.size}')
    observed=[]
    for i in range(N):
        if sheet.size==(W*N,H):
            cel=sheet.crop((i*W,0,(i+1)*W,H))
        else:
            cel=sheet.crop((0,i*H,W,(i+1)*H))
        expected=Image.open(CELDIR/f'car-cel-{i:02d}.png').convert('RGBA')
        if cel.tobytes()!=expected.tobytes():
            raise AssertionError(f'LibreSprite exported mismatch/order at cel {i}')
        path=OUT/f'car-cel-{i}.png'
        cel.save(path)
        observed.append(hashlib.sha256(cel.tobytes()).hexdigest())
    assert len(set(observed))>=12,'Insufficient actual animation cel diversity'
    meta={'workflow':'Original layered OpenRaster authored in Pixel Videos -> real Krita export -> real LibreSprite batch export and sprite atlas -> film',
          'no_gui_brush_authoring_claim':True,
          'original_layers':2,
          'krita_export_sha256':digest(OUT/'car-detail-krita.png'),
          'libresprite_export_sha256':digest(OUT/'car-detail-libresprite.png'),
          'libresprite_atlas_sha256':digest(atlas),
          'actual_editor_atlas_used_to_derive_final_cels':True,
          'car_cels':N,'unique_exported_car_cels':len(set(observed)),
          'atlas_size':list(sheet.size)}
    (OUT/'real-editor-evidence.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('KRITA_LIBRESPRITE_EDITOR_PIPELINE_VERIFIED',json.dumps(meta))

if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit(__doc__)
    {'prepare':prepare,'cels':make_cels,'adopt':adopt}[sys.argv[1]]()
