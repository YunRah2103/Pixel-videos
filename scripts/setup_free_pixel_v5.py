#!/usr/bin/env python3
"""Pixel Videos V5. No API fees, free trials, paid export, or extra AI providers.
Download official open-source editor binaries and CC0 art into gitignored .tools/.
Use --check to inspect honestly; use --all for actual installations.
"""
import argparse,hashlib,json,os,platform,shutil,stat,subprocess,sys,tarfile,urllib.request,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
DEST=ROOT/'.tools'/'pixel-v5'
UA={"User-Agent":"PixelVideos-FreeArtStudio/5.0","Accept":"application/vnd.github+json"}
URLS={
 "libresprite":"https://github.com/LibreSprite/LibreSprite/releases/download/v1.3/libresprite-v1.3-linux-x86_64.AppImage",
 "tiled":"https://github.com/mapeditor/tiled/releases/download/v1.12.2/Tiled-1.12.2_Linux_x86_64.AppImage",
 "spookyghost":"https://raw.githubusercontent.com/SpookyGhost2D/SpookyGhost-artifacts/SpookyGhost-master-linux-gcc/SpookyGhost-2026.10.r1-187a90d-Linux-GCC.tar.gz",
 "spookyghost_manifest":"https://raw.githubusercontent.com/SpookyGhost2D/SpookyGhost-artifacts/SpookyGhost-master-linux-gcc/manifest.json",
 "kenney_tiny_city":"https://kenney.nl/media/pages/assets/tiny-city/357bf73846-1791720771/kenney_tiny-city.zip",
 "ansimuz_industrial":"https://opengameart.org/sites/default/files/parallax-industrial-pack_0.zip",
 "lospec_greyt_bit":"https://lospec.com/palette-list/greyt-bit.json",
}
LICENSES={
 "kenney_tiny_city":{"author":"Kenney","license":"CC0-1.0","source":"https://kenney.nl/assets/tiny-city"},
 "ansimuz_industrial":{"author":"Luis Zuno / ansimuz","license":"CC0-1.0","source":"https://opengameart.org/content/industrial-parallax-background"}
}
def fetch(url,dst,maxbytes=120_000_000):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists() and dst.stat().st_size>64:
  print("EXISTING_DOWNLOAD",dst,dst.stat().st_size)
  return dst
 request=urllib.request.Request(url,headers=UA)
 with urllib.request.urlopen(request,timeout=75) as resp,dst.open("wb") as out:
  size=0
  while True:
   b=resp.read(1024*1024)
   if not b:break
   size+=len(b)
   if size>maxbytes:
    out.close();dst.unlink(missing_ok=True)
    raise ValueError("Download over safety limit "+url)
   out.write(b)
 print("DOWNLOADED",str(dst),size)
 return dst
def sha(path):
 h=hashlib.sha256()
 with open(path,"rb") as f:
  for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
 return h.hexdigest()
def safe_extract(src,outdir):
 outdir.mkdir(parents=True,exist_ok=True)
 total=0;count=0
 if zipfile.is_zipfile(src):
  with zipfile.ZipFile(src) as z:
   for item in z.infolist():
    if item.is_dir():continue
    p=Path(item.filename)
    if p.is_absolute() or ".." in p.parts or stat.S_ISLNK(item.external_attr>>16):raise ValueError("Unsafe ZIP entry "+str(p))
    total+=item.file_size;count+=1
    if total>350_000_000 or count>10000:raise ValueError("Archive too large")
   z.extractall(outdir)
 else:
  with tarfile.open(src) as tar:
   for item in tar.getmembers():
    p=Path(item.name)
    if p.is_absolute() or ".." in p.parts or item.issym() or item.islnk():raise ValueError("Unsafe TAR entry "+str(p))
    total+=item.size;count+=1
    if total>350_000_000 or count>10000:raise ValueError("Archive too large")
   tar.extractall(outdir,filter="data")
 return count
def run(command,env=None,timeout=180):
 print("RUN",*map(str,command),flush=True)
 p=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
 print(p.stdout[-2500:])
 if p.returncode!=0:raise RuntimeError("Command failed: "+str(command)+" exit="+str(p.returncode))
 return p.stdout
def download_editor(name):
 if name in ("tiled","libresprite"):
  file=DEST/"editors"/(name+".AppImage")
  fetch(URLS[name],file)
  with file.open("rb") as fd:
   if fd.read(4)!=b"\x7fELF":raise RuntimeError("Not a Linux executable: "+str(file))
  file.chmod(file.stat().st_mode|0o111)
  return file
 if name=="spookyghost":
  target=DEST/"editors"/"spookyghost"
  archive=fetch(URLS[name],DEST/"downloads"/"spookyghost.tar.gz")
  manifest=fetch(URLS["spookyghost_manifest"],DEST/"downloads"/"spookyghost-manifest.json")
  expected=json.loads(manifest.read_text()).get("sha256")
  if not expected or expected!=sha(archive):raise RuntimeError("SpookyGhost vendor manifest SHA-256 mismatch")
  if not (target/".installed").exists():
   safe_extract(archive,target)
   (target/".installed").write_text(sha(archive))
  executables=[p for p in target.rglob("*") if p.is_file() and p.name.lower()=="spookyghost"]
  if executables:
   for p in executables:p.chmod(p.stat().st_mode|0o111)
  print("SPOOKYGHOST_BINARY",executables[:2])
  if not executables:raise RuntimeError("No SpookyGhost executable in verified official archive")
  return executables[0]
 if name=="laigter":
  source=DEST/"sources"/"laigter"
  if not (source/".git").exists():
   source.parent.mkdir(parents=True,exist_ok=True)
   run(["git","clone","--depth","1","--branch","1.14.0","https://github.com/azagaya/laigter.git",source],timeout=120)
  if not (source/"laigter.pro").is_file():raise RuntimeError("Laigter source missing qmake project")
  qmake=shutil.which("qmake")
  if not qmake:
   print("LAIGTER_SOURCE_READY but qmake absent. Install qtbase5-dev qt5-qmake libqt5opengl5-dev for free source build.")
   return source
  binary=DEST/"build"/"laigter"/"laigter"
  if not binary.is_file():
   folder=binary.parent;folder.mkdir(parents=True,exist_ok=True)
   run(["qmake",str(source/"laigter.pro")],env=None,timeout=90) if False else None
   subprocess.run(["qmake",str(source/"laigter.pro")],cwd=folder,check=True,timeout=90)
   jobs=min(4,os.cpu_count() or 2)
   subprocess.run(["make","-j",str(jobs)],cwd=folder,check=True,timeout=420)
  if not binary.is_file():
   binaries=[p for p in (DEST/"build"/"laigter").rglob("laigter") if p.is_file() and os.access(p,os.X_OK)]
   if not binaries:raise RuntimeError("Laigter source compiled but no executable found")
   binary=binaries[0]
  print("LAIGTER_EXECUTABLE",binary)
  return binary
 raise ValueError(name)
def fetch_art(name):
 archive=fetch(URLS[name],DEST/"downloads"/(name+".zip"),maxbytes=65_000_000)
 if not zipfile.is_zipfile(archive):raise RuntimeError("Not a ZIP: "+name)
 dest=DEST/"art"/name
 if not (dest/"ASSET_PROVENANCE.json").is_file():
  safe_extract(archive,dest)
  art=[str(p.relative_to(dest)) for p in dest.rglob("*.png")]
  if not art:raise RuntimeError("No PNG artwork in "+name)
  meta={**LICENSES[name],"archive_sha256":sha(archive),"artist_created":True,"files":len(art),
   "notice":"Use official supplied licence and attribution notices; files remain in ignored .tools/ and are not sold."}
  (dest/"ASSET_PROVENANCE.json").write_text(json.dumps(meta,indent=2)+"\n")
 print("CC0_ART_READY",name,"PNG",len(list(dest.rglob("*.png"))))
def fetch_palette():
 path=fetch(URLS["lospec_greyt_bit"],DEST/"palettes"/"greyt-bit.json",maxbytes=250_000)
 data=json.loads(path.read_text())
 if not isinstance(data.get("colors"),list) or not 2<=len(data["colors"])<=256:raise ValueError("Palette API returned malformed data")
 print("LOSPEC_PALETTE_READY",data.get("name"),len(data["colors"]),"creator",data.get("author"))
def check():
 reports={"tools":{},"assets":{},"no_extra_ai_payments":True}
 for name in ("tiled","libresprite","spookyghost","laigter"):
  if name in ("tiled","libresprite"):p=DEST/"editors"/(name+".AppImage")
  elif name=="spookyghost":p=DEST/"editors"/"spookyghost"/".installed"
  else:p=DEST/"sources"/"laigter"/"laigter.pro"
  reports["tools"][name]={"available":p.exists(),"location":str(p)}
 for name in LICENSES:
  p=DEST/"art"/name/"ASSET_PROVENANCE.json"
  reports["assets"][name]={"downloaded":p.exists(),"path":str(p)}
 p=DEST/"palettes"/"greyt-bit.json"
 reports["palette"]={"downloaded":p.exists(),"path":str(p)}
 out=ROOT/"out"/"pixel-v5";out.mkdir(parents=True,exist_ok=True)
 (out/"tool-readiness.json").write_text(json.dumps(reports,indent=2)+"\n")
 print("PIXEL_V5_READINESS",json.dumps(reports))
 return reports
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--check",action="store_true")
 ap.add_argument("--all",action="store_true",help="Get genuinely free editors, 2 CC0 packs and palette")
 ap.add_argument("--editors",action="store_true")
 ap.add_argument("--art",action="store_true")
 ap.add_argument("--palette",action="store_true")
 args=ap.parse_args()
 if not (args.all or args.editors or args.art or args.palette):check();return
 if platform.system()!="Linux" or platform.machine().lower() not in ("x86_64","amd64"):
  raise RuntimeError("V5 automated binaries currently Linux x64 only; use upstream downloads on other platforms")
 if args.all or args.editors:
  for name in ("libresprite","tiled","spookyghost","laigter"):download_editor(name)
 if args.all or args.art:
  for name in LICENSES:fetch_art(name)
 if args.all or args.palette:fetch_palette()
 check()
if __name__=="__main__":
 main()
