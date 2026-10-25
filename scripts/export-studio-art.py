#!/usr/bin/env python3
"""Practical editor-to-Remotion asset adapters (no re-licensing).

Example:
 python3 scripts/export-studio-art.py pixelorama studio/original/hero.pxo public/toolkit/imports/hero.png
 python3 scripts/export-studio-art.py krita studio/original/sky.kra public/toolkit/imports/sky.png
 python3 scripts/export-studio-art.py inspect-ldtk studio/original/town.ldtk
 python3 scripts/export-studio-art.py godot studio/godot/world out/godot-scene.png --frames 90
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
TOOLS=ROOT/'.tools'

def binary(name,location):
    direct=shutil.which(name)
    if direct:
        return direct
    if location.exists():
        files=[p for p in location.rglob('*') if p.is_file() and name.lower() in p.name.lower()
               and (p.suffix.lower() not in ('.pck','.so','.dll','.png','.md','.txt') and (os.access(p,os.X_OK) or p.suffix.lower() in ('.appimage','.exe','.x86_64')))]
        if files:
            return str(sorted(files,key=lambda p:len(str(p)))[0])
    raise RuntimeError(name+' unavailable; run python3 scripts/install_studio_v2.py --'+name.lower())

def run(parts):
    print('>', ' '.join(map(str,parts)))
    subprocess.run(list(map(str,parts)),cwd=ROOT,check=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('tool',choices=['pixelorama','krita','godot','inspect-ldtk'])
    ap.add_argument('source')
    ap.add_argument('output',nargs='?')
    ap.add_argument('--frames',type=int,default=90)
    ap.add_argument('--fps',type=int,default=30)
    args=ap.parse_args()
    src=Path(args.source).resolve()
    if not src.exists():
        ap.error('Source not found: '+str(src))
    if args.tool=='inspect-ldtk':
        data=json.loads(src.read_text(encoding='utf8'))
        print(json.dumps({'world':str(src),'levels':[{'identifier':x.get('identifier'),'iid':x.get('iid'),'worldX':x.get('worldX'),'worldY':x.get('worldY'),'layerCount':len(x.get('layerInstances') or [])} for x in data.get('levels',[])]},indent=2))
        return
    if not args.output:
        ap.error('Output path required')
    dst=Path(args.output).resolve()
    dst.parent.mkdir(parents=True,exist_ok=True)
    if args.tool=='pixelorama':
        tool=binary('Pixelorama',TOOLS/'editors'/'pixelorama')
        run([tool,'--headless','--quit','--','--export','--spritesheet','--output',dst,src])
    elif args.tool=='krita':
        tool=binary('krita',TOOLS/'editors'/'krita')
        display=[tool,str(src),'--export','--export-filename',str(dst)]
        if sys.platform.startswith('linux') and not os.environ.get('DISPLAY') and shutil.which('xvfb-run'):
            display=['xvfb-run','-a',*display]
        run(display)
    elif args.tool=='godot':
        if args.frames<1 or args.fps<1:
            ap.error('frames and fps must be positive')
        tool=binary('godot',TOOLS/'engines'/'godot')
        # Godot infers PNG sequence when --write-movie points at PNG.
        cmd=[tool,'--path',src,'--write-movie',dst,'--fixed-fps',args.fps,'--quit-after',args.frames]
        if sys.platform.startswith('linux') and not os.environ.get('DISPLAY') and shutil.which('xvfb-run'):
            cmd=['xvfb-run','-a',*cmd]
        run(cmd)
    if args.tool!='godot' and not dst.exists():
        raise RuntimeError('Editor completed but output is missing: '+str(dst))
    print('Exported',dst)

if __name__=='__main__':
    main()
