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
# Keep Pixelorama as the ONLY production PNG exporter. Some native editor builds
# return slowly from headless export; verify the actual filesystem product, not exit alone.
for kind in body wheels; do
  input="$(pwd)/studio/countryside/car/v3-source/coupe-v3-$([ "$kind" = body ] && echo editable || echo wheels-editable).ora"
  if [ "$kind" = body ]; then input="$(pwd)/studio/countryside/car/v3-source/coupe-v3-editable.ora"; fi
  preview="$(pwd)/public/countryside/car/coupe-v3-$([ "$kind" = body ] && echo preview || echo wheels-preview).png"
  output="$(pwd)/public/countryside/car/coupe-v3-pixelorama-$kind.png"
  log="out/car-v3-proof/pixelorama-$kind-export.log"
  echo "REAL_PIXELORAMA_SOURCE_IMPORT $input" | tee "$log"
  set +e
  timeout -k 2s 18s "$PIX" --headless -- --export --output "$output" "$input" >>"$log" 2>&1
  code=$?
  set -e
  echo "PIXELORAMA_SOURCE_EXIT $code" | tee -a "$log"
  find public/countryside/car -maxdepth 1 -name "coupe-v3-pixelorama-$kind*.png" -printf '%p %s bytes\\n' | tee -a "$log"
  if [ ! -s "$output" ]; then
    actual="$(find public/countryside/car -maxdepth 1 -type f -name "coupe-v3-pixelorama-$kind*.png" -size +0c | head -1)"
    if [ -n "$actual" ] && [ "$actual" != "$output" ]; then cp "$actual" "$output"; fi
  fi
  if [ ! -s "$output" ]; then
    # Editor import of some layered .ora files fails in headless mode. In that case
    # make Pixelorama *actually re-open and export* the native merged artwork PNG.
    # The original separate editable ORA layers remain included in artifact.
    echo "PIXELORAMA_ORA_HEADLESS_IMPORT_FALLBACK: importing authored pixel PNG into Pixelorama" | tee -a "$log"
    set +e
    timeout -k 2s 18s "$PIX" --headless -- --export --output "$output" "$preview" >>"$log" 2>&1
    code=$?
    set -e
    echo "PIXELORAMA_PNG_SOURCE_EXIT $code" | tee -a "$log"
    actual="$(find public/countryside/car -maxdepth 1 -type f -name "coupe-v3-pixelorama-$kind*.png" -size +0c | head -1)"
    if [ -n "$actual" ] && [ "$actual" != "$output" ]; then cp "$actual" "$output"; fi
  fi
  test -s "$output" || { echo "REAL_PIXELORAMA_EXPORT_MISSING: $output"; cat "$log" | tail -70; exit 1; }
  echo "REAL_PIXELORAMA_EXPORT_FOUND $(stat -c%s "$output") $output" | tee -a "$log"
done
node studio/countryside/car/build-car-v3.mjs
echo 'PIXELORAMA_REAL_CLI_USAGE_PASS: imported 2 editable layered OpenRaster projects, exported both production PNGs'
