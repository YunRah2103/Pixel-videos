#!/usr/bin/env python3
"""Optional external tool downloader. Third-party tools remain upstream-owned.

Usage: python3 scripts/install_tools.py --all
       python3 scripts/install_tools.py --godot --pixelorama

Requires internet. Places downloads under .tools/ (gitignored).
Tool licenses and resource requirements are those of their upstream projects.
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / '.tools'
UA = {'User-Agent': 'pixel-videos-studio-installer/0.1', 'Accept': 'application/vnd.github+json'}


def run(*argv, cwd=ROOT):
    print('>', ' '.join(str(p) for p in argv), flush=True)
    subprocess.run(list(map(str, argv)), cwd=cwd, check=True)


def latest_release(repo):
    url = f'https://api.github.com/repos/{repo}/releases/latest'
    request = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(request, timeout=30) as res:
        return json.load(res)


def choice(assets, kind):
    """Pick the official binary for this architecture; project filename conventions differ."""
    system = platform.system().lower()
    arch = platform.machine().lower()
    x64 = arch in ('x86_64','amd64')
    arm64 = arch in ('arm64','aarch64')
    if not (x64 or arm64):
        raise RuntimeError(f'Unsupported CPU architecture: {arch}')
    def valid(a):
        name = a['name'].lower()
        if kind == 'pixelorama':
            if system == 'linux':
                return name == ('pixelorama-linux-64bit.tar.gz' if x64 else 'pixelorama-linux-arm64.tar.gz')
            if system == 'windows':
                return name == ('pixelorama-windows-64bit.zip' if x64 else 'pixelorama-windows-arm64.zip')
            return False
        if kind == 'godot':
            if system == 'linux':
                return name.endswith(('_linux.x86_64.zip' if x64 else '_linux.arm64.zip')) and not 'mono' in name
            if system == 'windows':
                return name.endswith('_win64.exe.zip') if x64 else name.endswith('_windows_arm64.exe.zip')
            if system == 'darwin':
                return name.endswith('_macos.universal.zip') and not 'mono' in name
        return False
    matches = [a for a in assets if valid(a)]
    if not matches:
        raise RuntimeError(f'No official {kind} download compatible with {system}/{arch}')
    matches.sort(key=lambda a: a.get('size',0))
    return matches[0]


def safe_extract(archive, destination):
    destination.mkdir(parents=True, exist_ok=True)
    dest_resolved = destination.resolve()
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                p = (destination / item.filename).resolve()
                if not p.is_relative_to(dest_resolved):
                    raise ValueError('Refusing archive path traversal')
                if (item.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError('Refusing archive symlink')
            z.extractall(destination)
    else:
        with tarfile.open(archive) as t:
            for item in t.getmembers():
                p = (destination / item.name).resolve()
                if not p.is_relative_to(dest_resolved) or item.issym() or item.islnk():
                    raise ValueError('Refusing unsafe tar archive member')
            t.extractall(destination, filter='data')
    for path in destination.rglob('*'):
        if path.is_file() and (path.name.startswith(('Godot','Pixelorama')) or path.suffix.lower() in ('.x86_64','.sh')):
            try: path.chmod(path.stat().st_mode | 0o111)
            except PermissionError: pass


def binary_tool(repo, kind, target):
    data = latest_release(repo)
    asset = choice(data['assets'], kind)
    target.mkdir(parents=True, exist_ok=True)
    archive = TOOLS/'downloads'/asset['name']
    archive.parent.mkdir(parents=True, exist_ok=True)
    if not archive.exists() or archive.stat().st_size != asset.get('size'):
        print('Downloading', asset['name'], '(official GitHub release)', flush=True)
        request = urllib.request.Request(asset['browser_download_url'], headers=UA)
        with urllib.request.urlopen(request, timeout=240) as src, archive.open('wb') as out:
            shutil.copyfileobj(src, out)
    safe_extract(archive,target)
    print(f'Installed {kind} under {target.relative_to(ROOT)} from {asset["name"]}')


def clone(repo, name):
    target = TOOLS/'sources'/name
    target.parent.mkdir(parents=True, exist_ok=True)
    if (target/'.git').exists():
        print('Already cloned:',target)
        return target
    run('git','clone','--depth','1',f'https://github.com/{repo}.git',str(target))
    return target


def install_pixelgen():
    source = clone('jmelahman/pixelgen', 'pixelgen')
    if not shutil.which('cargo'):
        print('pixelgen source downloaded, but Rust/Cargo is not installed. Install Rust then run:')
        print(f'  cargo install --path {source / "crates/pixelgen-cli"} --root {TOOLS}')
        return
    run('cargo','install','--path',str(source/'crates/pixelgen-cli'),'--root',str(TOOLS))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for flag in ('all','npm','parallax','pixelgen','godot','pixelorama'):
        ap.add_argument('--'+flag,action='store_true')
    a = ap.parse_args()
    if not any(vars(a).values()):
        ap.print_help()
        return 0
    jobs=[]
    if a.all or a.npm: jobs.append(('npm',lambda: run('npm','install','--no-audit','--no-fund')))
    if a.all or a.parallax: jobs.append(('parallax',lambda: clone('christt105/parallax-scene-editor','parallax-scene-editor')))
    if a.all or a.pixelgen: jobs.append(('pixelgen',install_pixelgen))
    if a.all or a.godot: jobs.append(('godot',lambda:binary_tool('godotengine/godot','godot',TOOLS/'engines'/'godot')))
    if a.all or a.pixelorama: jobs.append(('pixelorama',lambda:binary_tool('Orama-Interactive/Pixelorama','pixelorama',TOOLS/'editors'/'pixelorama')))
    failed=[]
    for name, fn in jobs:
        try:
            fn()
        except Exception as exc:
            print(f'ERROR installing {name}: {exc}',file=sys.stderr)
            failed.append(name)
    if failed:
        print('These tools require a retry or manual install:',', '.join(failed),file=sys.stderr)
        return 1
    print('Selected tools installed successfully. Run: npm run check')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
