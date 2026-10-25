#!/usr/bin/env python3
"""Safe importer for legally obtained editable artist asset ZIP files."""
import argparse,hashlib,json,shutil,stat,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
STORE=ROOT/'.tools'/'licensed-art'
ART={'.png','.aseprite','.ase','.psd','.kra','.pxo'}
ALLOW=ART|{'.txt','.md','.json'}
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--archive',required=True,type=Path)
 p.add_argument('--asset-id',required=True)
 p.add_argument('--source-url',required=True)
 p.add_argument('--author',required=True)
 p.add_argument('--license',required=True,choices=['CC0-1.0','CC-BY-3.0','MIT','PROPRIETARY-PERMITTED'])
 a=p.parse_args()
 if not a.asset_id.replace('-','').replace('_','').isalnum() or len(a.asset_id)>70:p.error('Invalid asset-id')
 if not a.source_url.startswith('https://'):p.error('HTTPS source URL required')
 if not a.author.strip():p.error('Author required')
 if not a.archive.is_file() or not zipfile.is_zipfile(a.archive):p.error('Valid ZIP required')
 dest=STORE/a.asset_id
 if dest.exists():p.error('Destination already exists')
 with zipfile.ZipFile(a.archive) as z:
  selected=[]; total=0
  for item in z.infolist():
   if item.is_dir():continue
   n=Path(item.filename)
   total+=item.file_size
   if total>150*1024*1024 or item.file_size>70*1024*1024:p.error('Archive exceeds safe size')
   if n.is_absolute() or '..' in n.parts or len(n.parts)>12:p.error('Unsafe ZIP pathname')
   if stat.S_ISLNK(item.external_attr>>16):p.error('Symlinks forbidden')
   if n.suffix.lower() in ALLOW:selected.append((item,n))
  count=sum(n.suffix.lower() in ART for _,n in selected)
  if not count:p.error('No editable art / PNG in pack')
  try:
   for item,n in selected:
    output=dest/n;output.parent.mkdir(parents=True,exist_ok=True)
    with z.open(item) as source,output.open('xb') as sink:shutil.copyfileobj(source,sink)
  except BaseException:
   shutil.rmtree(dest,ignore_errors=True)
   raise
 manifest={'asset_id':a.asset_id,'source_url':a.source_url,'author':a.author,
 'declared_license':a.license,'archive_sha256':hashlib.sha256(a.archive.read_bytes()).hexdigest(),
 'file_count':count,'audio_excluded':True,'license_verification':'User/agent must check original bundled notices and publishing terms'}
 (dest/'ASSET_PROVENANCE.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('PIXEL_ART_IMPORT_OK',json.dumps({'location':str(dest),'art_files':count}))
if __name__=='__main__':main()
