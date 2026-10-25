#!/usr/bin/env python3
"""Install/check the official Pixel Videos V2 authoring tools.

Default check never implies binaries are installed. External desktop editors
are downloaded on demand and are not vendored into git.
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
TARGET=ROOT/'.tools'
UA={'User-Agent':'pixel-videos-v2-toolkit','Accept':'application/vnd.github+json'}

def run(*args):
    print('>', ' '.join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),cwd=ROOT,check=True)

def find_executable(name,root):
    binary=shutil.which(name)
    if binary:
        return binary
    if root.is_dir():
        matches=[p for p in root.rglob('*') if p.is_file() and
                 name.lower() in p.name.lower() and
                 p.name.lower().endswith(('.x86_64','.arm64','.appimage','.exe')) and
                 os.access(p,os.X_OK)]
        if matches:
            return str(sorted(matches,key=lambda p:len(str(p)))[0])
    return None

def install_ldtk():
    if platform.system()!='Linux' or platform.machine().lower() not in ('x86_64','amd64'):
        raise RuntimeError('Automatic LDtk installer currently supports Linux x64 only; see https://ldtk.io')
    api='https://api.github.com/repos/deepnight/ldtk/releases/latest'
    req=urllib.request.Request(api,headers=UA)
    with urllib.request.urlopen(req,timeout=30) as response:
        release=json.load(response)
    assets=release.get('assets',[])
    matches=[a for a in assets if a.get('name','').lower() in ('ubuntu-distribution.zip','ldtk-linux.zip')
             or ('linux' in a.get('name','').lower() and a['name'].lower().endswith('.zip'))]
    if not matches:
        raise RuntimeError('No official Linux LDtk ZIP in latest release; install manually from https://ldtk.io')
    matches.sort(key=lambda a: (a['name'].lower()=='ubuntu-distribution.zip',a.get('size',0)),reverse=True)
    asset=matches[0]
    dest=TARGET/'editors'/'ldtk'
    dest.mkdir(parents=True,exist_ok=True)
    archive=TARGET/'downloads'/asset['name']
    archive.parent.mkdir(parents=True,exist_ok=True)
    if not archive.is_file() or archive.stat().st_size!=asset.get('size'):
        req=urllib.request.Request(asset['browser_download_url'],headers=UA)
        with urllib.request.urlopen(req,timeout=240) as src,archive.open('wb') as dst:
            shutil.copyfileobj(src,dst)
    with zipfile.ZipFile(archive) as z:
        for i in z.infolist():
            path=(dest/i.filename).resolve()
            if not path.is_relative_to(dest.resolve()):
                raise RuntimeError('Unsafe LDtk archive member: '+i.filename)
            if (i.external_attr>>16)&0o170000==0o120000:
                raise RuntimeError('Refusing symlink from release archive')
        z.extractall(dest)
    for p in dest.rglob('*'):
        if p.is_file() and (p.suffix.lower() in ('.appimage','.sh') or p.name.lower() in ('ldtk','ldtk-linux64')):
            p.chmod(p.stat().st_mode|0o111)
    print('LDtk installed to',dest)

def install_krita():
    if shutil.which('krita'):
        print('Krita already installed')
        return
    if platform.system()!='Linux' or not shutil.which('apt-get'):
        raise RuntimeError('Automatic Krita install needs apt on Linux; install Krita from https://krita.org')
    prefix=[] if os.geteuid()==0 else ['sudo']
    if prefix and not shutil.which('sudo'):
        raise RuntimeError('Need sudo permissions to install Krita')
    run(*prefix,'apt-get','update','-y')
    run(*prefix,'apt-get','install','-y','krita','xvfb')

def check():
    status={}
    for name in ('node','npm','ffmpeg','ffprobe','python3','git','krita','godot','pixelorama','LDtk'):
        part=name.lower()
        directory=(TARGET/'editors'/part) if part in ('pixelorama','ldtk') else TARGET/'engines'/'godot'
        status[name]=find_executable(name,directory)
    status['pixijs_node_modules']=(ROOT/'node_modules'/'pixi.js').exists()
    status['sharp_node_modules']=(ROOT/'node_modules'/'sharp').exists()
    status['ldtk_download']=(TARGET/'editors'/'ldtk').exists()
    status['pixelorama_download']=(TARGET/'editors'/'pixelorama').exists()
    status['godot_download']=(TARGET/'engines'/'godot').exists()
    print(json.dumps(status,indent=2))
    print('External tools are optional: npm run assets:verify requires only npm, sharp, FFmpeg.')
    return status

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for a in ('all','check','npm','pixelorama','godot','ldtk','krita'):
        ap.add_argument('--'+a,action='store_true')
    args=ap.parse_args()
    if args.check or not any(vars(args).values()):
        check()
        return
    if args.all or args.npm:
        run('npm','install','--no-audit','--no-fund')
    if args.all or args.pixelorama:
        run(sys.executable,'scripts/install_tools.py','--pixelorama')
    if args.all or args.godot:
        run(sys.executable,'scripts/install_tools.py','--godot')
    if args.all or args.ldtk:
        install_ldtk()
    if args.all or args.krita:
        install_krita()
    check()

if __name__=='__main__':
    main()
