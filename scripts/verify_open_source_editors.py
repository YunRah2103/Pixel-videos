#!/usr/bin/env python3
"""Check editor installations by finding executables and actually running supported CLIs.

Pixelorama and Godot have headless CLI; Krita has --version.
LDtk is an Electron GUI with no documented headless CLI, so for LDtk we
only verify its installed executable, and explicitly record that limit.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parent.parent
TOOLS=ROOT/'.tools'
OUT=ROOT/'out'/'editor-toolchain'
OUT.mkdir(parents=True,exist_ok=True)

def executable(folder, rule):
    if not folder.exists():
        raise RuntimeError('Missing editor directory: '+str(folder))
    files=[p for p in folder.rglob('*') if p.is_file() and rule(p.name.lower()) and os.access(p,os.X_OK)]
    files.sort(key=lambda f:(len(f.parts),len(str(f))))
    if not files:
        raise RuntimeError('No executable found in '+str(folder))
    return files[0]

def run_version(path, args):
    env=dict(os.environ)
    if Path(str(path)).name.lower() == 'krita':
        env['QT_QPA_PLATFORM']='offscreen'
    proc=subprocess.run([str(path),*args],cwd=ROOT,capture_output=True,
                        text=True,errors='replace',timeout=65,env=env)
    output=(proc.stdout+'\n'+proc.stderr).strip()
    if proc.returncode!=0:
        raise RuntimeError(str(path)+' exited '+str(proc.returncode)+': '+output[-1400:])
    return output[-1600:]

pixelorama=executable(TOOLS/'editors'/'pixelorama',lambda n:n.startswith('pixelorama') and (n.endswith('.x86_64') or n.endswith('.arm64')))
godot=executable(TOOLS/'engines'/'godot',lambda n:n.startswith('godot') and (n.endswith('.x86_64') or n.endswith('.arm64')))
ldtk=executable(TOOLS/'editors'/'ldtk',lambda n:n in ('ldtk','ldtk-linux64','ldtk-linux') or (n.startswith('ldtk') and n.endswith('.appimage')))
krita=shutil.which('krita')
if not krita:raise RuntimeError('Krita is not installed')

results={
 'pixelorama':{'path':str(pixelorama.relative_to(ROOT)),'version_output':run_version(pixelorama,['--headless','--quit','--','--version']),'cli_executed':True},
 'godot':{'path':str(godot.relative_to(ROOT)),'version_output':run_version(godot,['--headless','--version']),'cli_executed':True},
 'krita':{'path':krita,'version_output':run_version(krita,['--version']),'cli_executed':True},
 'ldtk':{'path':str(ldtk.relative_to(ROOT)),'downloaded_official_installer_and_executable':True,
         'cli_executed':False,
         'note':'The upstream Ubuntu ZIP currently contains an LDtk AppImage installer. This verifies its download and executable permission, not a completed GUI installation, launch or exported map.'},
 'limitations':['No sprite artwork was authored in these apps by this smoke test.',
                'PixelLab MCP is a separate remote authenticated service; PixelOver paid version not included.',
                'Editor binaries installed on this runner only and are not committed or distributed in this artifact.']
}
(OUT/'verification.json').write_text(json.dumps({'verified_installations':True,'editors':results},indent=2)+'\n')
for name,value in results.items():
 if isinstance(value,dict):
  print('EDITOR_INSTALL_CHECK',name,json.dumps(value))
print('EDITOR_TOOLCHAIN_PROOF_PASS')
