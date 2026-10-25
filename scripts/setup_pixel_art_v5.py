#!/usr/bin/env python3
"""Pixel Videos V5 — fully free editor and licensed pixel-art source downloader.

Does not download paid trials, AI APIs, or falsely claim GUI editing happened.
Linux x86_64 runner supported; downloaded binaries stay in ignored .tools.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import sys
import tarfile
import time
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parent.parent
TOOLS=ROOT/'.tools'/'pixel-v5'
BIN=TOOLS/'bin'
PACKS=TOOLS/'assets'
OUTPUT=ROOT/'out'/'pixel-v5'
USER_AGENT='PixelVideosFreeStudioV5/1.0'
UA={'User-Agent':USER_AGENT,'Accept':'application/vnd.github+json'}
KENNEY='https://kenney.nl/media/pages/assets/tiny-city/357bf73846-1791720771/kenney_tiny-city.zip'
ANSIMUZ='https://opengameart.org/sites/default/files/cyberpunk-street-files.zip'
LOSPEC='https://lospec.com/palette-list/apollo.json'
SPOOKY_BRANCH='SpookyGhost-master-linux-gcc'
SPOOKY_REPO='SpookyGhost2D/SpookyGhost-artifacts'

def request(url,json_body=False):
    headers=dict(UA)
    if os.getenv('GITHUB_TOKEN') and 'api.github.com' in url:
        headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
    req=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(req,timeout=50) as r:
        contents=r.read()
    return json.loads(contents) if json_body else contents

def download(url,dest,kind):
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.is_file() and dest.stat().st_size>1000:
        print('CACHED',kind,dest.stat().st_size,flush=True)
        return dest
    for attempt in range(3):
        try:
            payload=request(url)
            if len(payload)<100:
                raise RuntimeError('Unexpected tiny response (possible paywall)')
            tmp=dest.with_name(dest.name+'.part')
            tmp.write_bytes(payload)
            if kind=='zip' and not zipfile.is_zipfile(tmp):
                raise RuntimeError('Server did not return a valid free ZIP: '+url)
            if kind=='appimage' and not payload.startswith(b'\x7fELF'):
                raise RuntimeError('Not a valid Linux AppImage/ELF: '+url)
            if kind=='tar.gz' and not tarfile.is_tarfile(tmp):
                raise RuntimeError('Not a valid tar archive')
            tmp.replace(dest)
            print('DOWNLOADED',dest.name,len(payload),'sha256',hashlib.sha256(payload).hexdigest(),flush=True)
            return dest
        except Exception as e:
            print('DOWNLOAD_RETRY',url,'attempt',attempt+1,str(e),flush=True)
            if attempt==2:raise
            time.sleep(2+attempt*2)

def safe_extract(path,dest):
    dest.mkdir(parents=True,exist_ok=True)
    base=dest.resolve()
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                target=(dest/member.filename).resolve()
                if not target.is_relative_to(base):raise RuntimeError('ZIP path traversal')
                if stat.S_ISLNK(member.external_attr>>16):raise RuntimeError('Symlink in ZIP')
                if member.file_size>200_000_000:raise RuntimeError('Too-large ZIP member')
            archive.extractall(dest)
    elif tarfile.is_tarfile(path):
        with tarfile.open(path) as archive:
            members=[]
            skipped=0
            for member in archive.getmembers():
                target=(dest/member.name).resolve()
                if not target.is_relative_to(base):
                    raise RuntimeError('Unsafe tar path')
                if member.issym() or member.islnk():
                    skipped+=1
                    continue  # No symlink/hardlink extraction into our build runner.
                if not (member.isfile() or member.isdir()):
                    skipped+=1
                    continue
                if member.size>200_000_000:raise RuntimeError('Too-large tar member')
                members.append(member)
            archive.extractall(dest,members=members,filter='data')
            print('TAR_EXTRACTED',len(members),'SKIPPED_LINKS_OR_SPECIAL_FILES',skipped,flush=True)
    else:raise RuntimeError('Unknown archive '+str(path))

def release_appimage(repo,tag,keyword):
    endpoint='https://api.github.com/repos/'+repo+'/releases/'+('latest' if tag is None else 'tags/'+tag)
    data=request(endpoint,True)
    found=[a for a in data.get('assets',[]) if keyword.lower() in a['name'].lower() and a['name'].lower().endswith('.appimage')]
    if not found:raise RuntimeError('No Linux AppImage for '+repo+' '+str(tag))
    found.sort(key=lambda a:a['size'])
    return found[0]['browser_download_url'],found[0]['name'],data['tag_name']

def binary_install():
    if platform.system()!='Linux' or platform.machine().lower() not in ('x86_64','amd64'):
        raise RuntimeError('V5 automatic native editor downloader supports Linux x86_64 only; use project docs for other platforms')
    BIN.mkdir(parents=True,exist_ok=True)
    wanted=[
      ('tiled','mapeditor/tiled',None,'linux_x86_64'),
      ('libresprite','LibreSprite/LibreSprite',None,'linux-x86_64'),
      # Linux AppImage absent in 1.14.0, so use latest Linux-capable stable 1.13.1
      ('laigter','azagaya/laigter','1.13.1','x86_64')
    ]
    report={}
    for key,repo,tag,pattern in wanted:
        url,name,version=release_appimage(repo,tag,pattern)
        dest=BIN/(key+'.AppImage')
        download(url,dest,'appimage')
        dest.chmod(dest.stat().st_mode|0o111)
        report[key]={'source_repo':repo,'tag':version,'filename':name,'path':str(dest),
                     'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                     'downloaded':True,'used_for_art':False}
    # Official freely published binary artifacts from SpookyGhost2D.
    index='https://api.github.com/repos/'+SPOOKY_REPO+'/contents?ref='+SPOOKY_BRANCH
    files=request(index,True)
    tarballs=[x for x in files if x.get('name','').lower().endswith('.tar.gz') and 'linux' in x['name'].lower()]
    if not tarballs:raise RuntimeError('No free Linux SpookyGhost binary in artifact branch')
    info=tarballs[0]
    src=info.get('download_url')
    if not src:raise RuntimeError('No official SpookyGhost artifact URL')
    path=TOOLS/'downloads'/info['name']
    download(src,path,'tar.gz')
    safe_extract(path,TOOLS/'spookyghost')
    exes=[p for p in (TOOLS/'spookyghost').rglob('*') if p.is_file() and (
          p.name.lower() in ('spookyghost','spookyghost.bin') or
          p.name.lower().endswith('.x86_64'))]
    for p in exes:p.chmod(p.stat().st_mode|0o111)
    report['spookyghost']={'source_repo':SPOOKY_REPO,'branch':SPOOKY_BRANCH,
                            'filename':info['name'],'executable_candidates':[str(p) for p in exes],
                            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                            'downloaded':True,'used_for_art':False}
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/'tool-install-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print('V5_FREE_BINARIES_READY',json.dumps({k:v['filename'] for k,v in report.items()}),flush=True)

def download_assets():
    PACKS.mkdir(parents=True,exist_ok=True)
    records=[]
    sources=[
      ('kenney-tiny-city',KENNEY,'CC0-1.0','Kenney','https://kenney.nl/assets/tiny-city'),
      ('ansimuz-cyberpunk-street',ANSIMUZ,'CC-BY-3.0','Ansimuz','https://opengameart.org/content/cyberpunk-street-environment')
    ]
    for name,url,license,author,page in sources:
        archive=TOOLS/'downloads'/(name+'.zip')
        download(url,archive,'zip')
        extracted=PACKS/name
        safe_extract(archive,extracted)
        files=[str(p.relative_to(extracted)) for p in extracted.rglob('*') if p.is_file()]
        imagefiles=[str(p.relative_to(extracted)) for p in extracted.rglob('*') if p.is_file() and p.suffix.lower() in ('.png','.aseprite','.psd','.ase','.kra')]
        record={'name':name,'author':author,'license':license,'source':page,'actual_archive_url':url,
                'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'asset_count':len(imagefiles),
                'sample_images':imagefiles[:45],'file_count':len(files)}
        records.append(record)
        if not imagefiles:raise RuntimeError('Artist pack contained no artwork: '+name)
        print('V5_LICENSED_ART_READY',name,len(imagefiles),'sample',imagefiles[:14],flush=True)
    palette=request(LOSPEC,True)
    colors=palette.get('colors',[])
    if not (16<=len(colors)<=128 and all(len(c) in (6,7) for c in colors)):
        raise RuntimeError('Invalid Lospec palette')
    (PACKS/'apollo-lospec.json').write_text(json.dumps({'name':palette.get('name'),'author':palette.get('author'),
         'colors':colors,'source':LOSPEC,'note':'Palette metadata retrieved from the free Lospec API; no exclusive rights claimed'},indent=2)+'\n')
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/'free-asset-provenance.json').write_text(json.dumps(records,indent=2)+'\n')
    print('V5_ALL_ASSETS_DOWNLOADED',len(records),'palette',palette.get('name'),len(colors),flush=True)
    print('ANSiMUZ_ATTRIBUTION_REQUIRED: Cyberpunk Street Environment by Ansimuz, CC BY 3.0 — '+sources[1][4],flush=True)

def check():
    report={'linux':platform.system()=='Linux','v5_tools':{},'v5_art':{},'v5_palette':(PACKS/'apollo-lospec.json').exists()}
    for name in ('tiled','libresprite','laigter'):
        f=BIN/(name+'.AppImage')
        report['v5_tools'][name]={'exists':f.is_file(),'size':f.stat().st_size if f.exists() else None}
    spooky=list((TOOLS/'spookyghost').rglob('*')) if (TOOLS/'spookyghost').exists() else []
    report['v5_tools']['spookyghost']={'exists':any(p.is_file() and 'spookyghost' in p.name.lower() for p in spooky)}
    for name in ('kenney-tiny-city','ansimuz-cyberpunk-street'):
        root=PACKS/name
        report['v5_art'][name]={'exists':root.exists(),'image_files':len(list(root.rglob('*.png'))) if root.exists() else 0}
    print(json.dumps(report,indent=2),flush=True)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tools',action='store_true')
    parser.add_argument('--assets',action='store_true')
    parser.add_argument('--all',action='store_true')
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.all or args.tools:binary_install()
    if args.all or args.assets:download_assets()
    check()

if __name__=='__main__':main()
