#!/usr/bin/env python3
"""Build a real editable Pixelorama v1.2 PXO (ZIP v8) from original Sharp RGBA art.
PXO is the official project format: data.json + RGBA cel pixels + preview.
See Pixelorama OpenSave.gd::save_pxo_file / Project.deserialize.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json
import subprocess

src=Path('public/countryside/world/nearTrees.png')
dst=Path('studio/countryside/world/sources/nearTrees.pxo')
dst.parent.mkdir(parents=True,exist_ok=True)
raw=Path('out/editor-evidence/nearTrees.raw')
raw.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(['node','-e',"""
const sharp=require('sharp');
sharp(process.argv[1]).ensureAlpha().raw().toFile(process.argv[2])
 .catch(e=>{console.error(e); process.exitCode=1;});
""",str(src),str(raw)],check=True)
width,height=960,235
pixels=raw.read_bytes()
if len(pixels)!=width*height*4:raise ValueError('Invalid RGBA Sharp pixels')
project={
 'pixelorama_version':'1.2.3','pxo_version':8,
 'size_x':width,'size_y':height,'color_mode':5,
 'layers':[{'name':'Original Countryside Pixel Tree Sprites','type':0,
            'new_cels_linked':False,'visible':True,'locked':False,
            'blend_mode':0,'clipping_mask':False,'opacity':1.0,'parent':-1,'effects':[]}],
 'frames':[{'cels':[{'opacity':1.0,'z_index':0,
                      'image_size':f'Vector2i({width}, {height})'}],
            'duration':1.0}],
 'current_frame':0,'current_layer':0,'fps':12,
 'tags':[],'guides':[],'brushes':[],'palettes':[],
 'project_current_palette_name':'','reference_images':[],
 'tilesets':[],'include_blended_images':True
}
with ZipFile(dst,'w',ZIP_DEFLATED) as z:
 z.writestr('mimetype','application/x-pixelorama')
 z.writestr('data.json',json.dumps(project,separators=(',',':')))
 z.writestr('image_data/frames/1/layer_1',pixels)
 z.writestr('image_data/final_images/1',pixels)
 z.write(src,'preview.png')
print('PIXELORAMA_EDITABLE_PXO_BUILT',dst,'native sprite',width,height, 'bytes',dst.stat().st_size)
