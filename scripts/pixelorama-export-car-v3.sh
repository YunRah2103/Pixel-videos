#!/usr/bin/env bash
# Genuine Pixelorama CLI export; no fallback to ImageMagick, Pillow or Sharp allowed.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .tools/editors/pixelorama out/car-v3-proof public/countryside/car
python3 - <<'PY'
import json,urllib.request,tarfile,pathlib,shutil
url='https://api.github.com/repos/Orama-Interactive/Pixelorama/releases/tags/v1.2.3'
req=urllib.request.Request(url,headers={'User-Agent':'pixel-videos-agent2','Accept':'application/vnd.github+json'})
with urllib.request.urlopen(req,timeout=60) as r:release=json.load(r)
matches=[a for a in release['assets'] if 'linux-64bit' in a['name'].lower() and a['name'].endswith('.tar.gz')]
if len(matches)!=1:raise RuntimeError('Pixelorama official Linux x64 release asset was not found')
asset=matches[0];dest=pathlib.Path('.tools/editors/pixelorama')
archive=dest/'pixelorama-official.tar.gz'
if not archive.exists():
 req=urllib.request.Request(asset['browser_download_url'],headers={'User-Agent':'pixel-videos-agent2'})
 with urllib.request.urlopen(req,timeout=180) as src,archive.open('wb') as out:shutil.copyfileobj(src,out)
with tarfile.open(archive) as t:
 for item in t.getmembers():
  target=(dest/item.name).resolve()
  if not target.is_relative_to(dest.resolve()) or item.issym() or item.islnk():raise RuntimeError('Unsafe release archive')
 t.extractall(dest,filter='data')
print('PIXELORAMA_OFFICIAL_RELEASE',release['tag_name'],'asset',asset['name'],'bytes',archive.stat().st_size)
PY
PIX="$(find .tools/editors/pixelorama -type f \( -name 'Pixelorama.x86_64' -o -name 'Pixelorama*.x86_64' -o -name 'Pixelorama' \) | head -1)"
if [ -z "$PIX" ]; then echo 'Pixelorama release binary missing'; exit 1; fi
chmod +x "$PIX"
timeout 30s "$PIX" --headless --quit -- --version 2>&1 | tee out/car-v3-proof/pixelorama-version.log
set -o pipefail
timeout 60s "$PIX" --headless -- --export --output "$(pwd)/public/countryside/car/coupe-v3-pixelorama-body.png" "$(pwd)/studio/countryside/car/v3-source/coupe-v3-editable.ora" 2>&1 | tee out/car-v3-proof/pixelorama-body-export.log
timeout 60s "$PIX" --headless -- --export --output "$(pwd)/public/countryside/car/coupe-v3-pixelorama-wheels.png" "$(pwd)/studio/countryside/car/v3-source/coupe-v3-wheels-editable.ora" 2>&1 | tee out/car-v3-proof/pixelorama-wheels-export.log
# Pixelorama may name a single exported frame with an _0001 suffix.
for kind in body wheels; do
  expected="public/countryside/car/coupe-v3-pixelorama-$kind.png"
  if [ ! -s "$expected" ]; then
    echo "Checking real Pixelorama export filenames for $kind"
    find public/countryside/car -maxdepth 1 -name "coupe-v3-pixelorama-$kind*.png" -printf '%p %s bytes\n'
    actual="$(find public/countryside/car -maxdepth 1 -type f -name "coupe-v3-pixelorama-$kind*.png" -size +0c | head -1)"
    if [ -n "$actual" ] && [ "$actual" != "$expected" ]; then cp "$actual" "$expected"; fi
  fi
  test -s "$expected" || { echo "PIXELORAMA_EXPORT_NOT_FOUND: $expected"; exit 1; }
done
# The production sprite builder will also reject the wrong dimensions/invalid wheel animation.
node studio/countryside/car/build-car-v3.mjs
echo 'PIXELORAMA_REAL_CLI_USAGE_PASS: imported 2 editable layered OpenRaster projects, exported both production PNGs'
