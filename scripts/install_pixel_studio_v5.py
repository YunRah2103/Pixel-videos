#!/usr/bin/env python3
"""Zero-cost Pixel Studio V5 installers. No paid tiers, accounts, or AI credits."""
import argparse,hashlib,json,os,platform,shutil,stat,tarfile,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
BASE=ROOT/'.tools'/'v5-free'
SOURCES={
 'spookyghost':('https://raw.githubusercontent.com/SpookyGhost2D/SpookyGhost-artifacts/SpookyGhost-master-linux-gcc/SpookyGhost-2026.10.r1-187a90d-Linux-GCC.tar.gz','MIT','tar','https://github.com/SpookyGhost2D/SpookyGhost-artifacts'),
 'libresprite':('https://github.com/LibreSprite/LibreSprite/releases/download/v1.3/libresprite-v1.3-linux-x86_64.AppImage','GPL-2.0','bin','https://github.com/LibreSprite/LibreSprite/releases/tag/v1.3'),
 'tiled':('https://github.com/mapeditor/tiled/releases/download/v1.12.2/Tiled-1.12.2_Linux_x86_64.AppImage','GPL-2.0+','bin','https://github.com/mapeditor/tiled/releases/tag/v1.12.2'),
 'laigter':('https://github.com/azagaya/laigter/releases/download/1.13.1/Laigter-x86_64.AppImage','GPL-3.0+','bin','https://github.com/azagaya/laigter/releases/tag/1.13.1'),
 'kenney_tiny_city':('https://kenney.nl/media/pages/assets/tiny-city/357bf73846-1791720771/kenney_tiny-city.zip','CC0-1.0','zip','https://kenney.nl/assets/tiny-city'),
 'ansimuz_street':('https://opengameart.org/sites/default/files/cyberpunk-street-files.zip','CC-BY-3.0','zip','https://opengameart.org/content/cyberpunk-street-environment'),
 'lospec_palette':('https://lospec.com/palette-list/endesga-32.json','author-credit-to-check','json','https://lospec.com/palette-list/endesga-32')
}
def get(url,out):
 if out.is_file() and out.stat().st_size>100:return
 out.parent.mkdir(parents=True,exist_ok=True)
 req=urllib.request.Request(url,headers={'User-Agent':'PixelStudioV5/5.0'})
 with urllib.request.urlopen(req,timeout=120) as src,out.open('wb') as dest:
  n=0
  while True:
   buf=src.read(1048576)
   if not buf:break
   n+=len(buf)
   if n>150*1024*1024:raise RuntimeError('Oversize '+url)
   dest.write(buf)
 if out.stat().st_size<100:raise RuntimeError('Missing/empty '+url)
def unpack(source,target,kind):
 if target.is_dir() and any(target.iterdir()):return
 target.mkdir(parents=True,exist_ok=True)
 if kind=='zip':
  with zipfile.ZipFile(source) as z:
   members=z.infolist()
   if sum(x.file_size for x in members)>350*1024*1024:raise RuntimeError('ZIP expansion excessive')
   for x in members:
    if not (target/x.filename).resolve().is_relative_to(target.resolve()) or stat.S_ISLNK(x.external_attr>>16):
     raise RuntimeError('Unsafe ZIP')
   z.extractall(target)
 elif kind=='tar':
  with tarfile.open(source,'r:gz') as t:
   members=t.getmembers()
   if sum(x.size for x in members)>350*1024*1024:raise RuntimeError('TAR expansion excessive')
   for x in members:
    if not (target/x.name).resolve().is_relative_to(target.resolve()):
     raise RuntimeError('Unsafe TAR path')
   for x in members:
    if x.isdir():
     (target/x.name).mkdir(parents=True,exist_ok=True)
    elif x.isfile():
     dst=target/x.name
     dst.parent.mkdir(parents=True,exist_ok=True)
     with t.extractfile(x) as inp,dst.open('wb') as out:
      shutil.copyfileobj(inp,out)
    else:
     print('SKIPPED_UNTRUSTED_TAR_ENTRY',x.name,x.type,flush=True)
 for x in target.rglob('*'):
  if x.is_file() and (x.name in ('spookyghost','launch.sh') or x.suffix.lower() in ('.appimage','.x86_64')):
   x.chmod(x.stat().st_mode|0o111)
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--all',action='store_true')
 p.add_argument('--inspect',action='store_true')
 p.add_argument('--only',choices=SOURCES)
 args=p.parse_args()
 if (args.all or args.only) and (platform.system()!='Linux' or platform.machine().lower() not in ('x86_64','amd64')):
  p.error('Automatic downloadable binaries currently target Linux x64')
 records=[]
 if args.all or args.only:
  for key in (SOURCES if args.all else [args.only]):
   url,license,kind,source=SOURCES[key]
   archive=BASE/'downloads'/key/Path(url).name
   get(url,archive)
   folder=BASE/('apps' if key in ['spookyghost','libresprite','tiled','laigter'] else 'art')/key
   if kind in ('tar','zip'):unpack(archive,folder,kind)
   else:
    folder.mkdir(parents=True,exist_ok=True)
    to=folder/archive.name
    if not to.exists():shutil.copyfile(archive,to)
    if kind=='bin':to.chmod(to.stat().st_mode|0o111)
   rec={'name':key,'url':url,'publisher':source,'license':license,'bytes':archive.stat().st_size,
        'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'location':str(folder.relative_to(ROOT))}
   records.append(rec)
   print('V5_DOWNLOADED',key,rec['bytes'],flush=True)
 report={'platform':platform.platform(),'cost':'0 GBP','extra_ai_services':False,'downloads':records,'inventory':{}}
 for key in SOURCES:
  folder=BASE/('apps' if key in ['spookyghost','libresprite','tiled','laigter'] else 'art')/key
  files=[x for x in folder.rglob('*') if x.is_file()] if folder.exists() else []
  report['inventory'][key]={'found':bool(files),'file_count':len(files),
                            'png_count':sum(x.suffix.lower()=='.png' for x in files),
                            'file_examples':[str(x.relative_to(folder)) for x in files[:30]]}
  print('V5_INSTALLED',key,len(files),flush=True)
 out=ROOT/'out'/'studio-v5'
 out.mkdir(parents=True,exist_ok=True)
 (out/'free-tools.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__':main()
