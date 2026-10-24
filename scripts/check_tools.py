#!/usr/bin/env python3
"""Detect tools; does not imply anything has been downloaded."""
import shutil
import subprocess
from pathlib import Path
for name in ['node','npm','ffmpeg','ffprobe','git','python3','cargo','godot','pixelorama']:
    present=shutil.which(name)
    print(f'{name:<12} {present if present else "not installed / not on PATH"}')
for path in [Path('node_modules/remotion'),Path('node_modules/pixi.js'),Path('.tools/sources/parallax-scene-editor'),Path('.tools/sources/pixelgen'),Path('.tools/engines/godot'),Path('.tools/editors/pixelorama')]:
    print(f'{str(path):<45} {"present" if path.exists() else "not downloaded"}')
