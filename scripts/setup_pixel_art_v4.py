#!/usr/bin/env python3
"""Install/check Pixel Videos' source-authoring stack. All downloaded tools live outside Git.
Paid or account-bound apps require the owner's own authorised access.
"""
import argparse
import json
import os
import platform
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
TOOL_HOME = ROOT / ".tools"
SNAPPER = TOOL_HOME / "pixel-art-v4" / "bin" / ("spritefusion-pixel-snapper.exe" if os.name == "nt" else "spritefusion-pixel-snapper")

def run(args):
    print("> " + " ".join(map(str, args)), flush=True)
    subprocess.run([str(x) for x in args], cwd=ROOT, check=True)

def executable(names):
    for name in names:
        p = shutil.which(name)
        if p:
            return p
    return None

def existing_editor(name, subdir):
    direct = executable([name])
    if direct:
        return direct
    root=TOOL_HOME / subdir
    if not root.is_dir():
        return None
    allowed = ('.x86_64', '.arm64', '.appimage', '.exe')
    matches=[p for p in root.rglob("*") if p.is_file() and name.lower() in p.name.lower() and
             p.name.lower().endswith(allowed) and os.access(p,os.X_OK)]
    return str(sorted(matches,key=lambda x:len(str(x)))[0]) if matches else None

def check():
    snapper = str(SNAPPER) if SNAPPER.is_file() else executable(["spritefusion-pixel-snapper"])
    report = {
      "platform": {"os": platform.system(), "architecture": platform.machine()},
      "open_source_local": {
        "pixel_snapper": snapper,
        "pixelorama": existing_editor("pixelorama","editors/pixelorama"),
        "krita": executable(["krita"]),
        "godot": existing_editor("godot","engines/godot"),
        "ldtk": existing_editor("ldtk","editors/ldtk"),
        "ffmpeg": executable(["ffmpeg"]), "ffprobe": executable(["ffprobe"]),
        "cargo": executable(["cargo"]),
      },
      "external_account_or_gui": {
        "pixellab_mcp_endpoint": "https://api.pixellab.ai/mcp",
        "pixellab_token_present": bool(os.environ.get("PIXELLAB_SECRET") or os.environ.get("PIXELLAB_API_TOKEN")),
        "sprite_fusion_web": "https://www.spritefusion.com/",
        "pixelover_demo": "https://deakcor.itch.io/pixelover",
        "artist_pack": "https://ansimuz.itch.io/cyberpunk-street-environment",
      },
      "artist_pack_imported": (TOOL_HOME / "licensed-art").exists(),
      "notes": [
        "A URL or token-present flag does NOT certify a connected or used external tool.",
        "PixelLab uses a remote authenticated MCP endpoint; it is NOT downloaded as an offline executable.",
        "PixelOver paid export is NOT included; its demo cannot export.",
        "Sprite Fusion's free edition is browser-hosted, not a redistributable local package.",
        "Native GUI tools require interactive/system environments and are installed on demand."
      ],
    }
    print(json.dumps(report,indent=2))
    return report

def install_snapper():
    if SNAPPER.exists():
        print("Pixel Snapper already installed:",SNAPPER)
        run([SNAPPER,"--help"])
        return
    cargo=executable(["cargo"])
    if not cargo:
        raise RuntimeError("Rust Cargo is required: https://rustup.rs/ . No fake installation.")
    root=SNAPPER.parent.parent
    root.mkdir(parents=True,exist_ok=True)
    # Versioned, reproducible, MIT-licensed tool. No sudo and no writes outside .tools.
    run([cargo,"install","spritefusion-pixel-snapper","--version","1.0.0","--locked","--root",root])
    if not SNAPPER.is_file():
        raise RuntimeError("Pixel Snapper installer exited successfully but binary is missing")
    run([SNAPPER,"--help"])
    print("Installed Pixel Snapper at",SNAPPER)

def install_free_editors():
    script=ROOT/"scripts/install_studio_v2.py"
    if platform.system()=="Linux":
        run([sys.executable,script,"--pixelorama"])
        run([sys.executable,script,"--godot"])
        run([sys.executable,script,"--ldtk"])
        # Krita may require root or sudo. Explicit flag permits the system package installation.
        run([sys.executable,script,"--krita"])
    else:
        raise RuntimeError("Install Pixelorama/Krita/Godot/LDtk manually on this OS using links in docs/PIXEL_ART_V4.md")

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--snapper",action="store_true")
    parser.add_argument("--free-editors",action="store_true")
    parser.add_argument("--all-free",action="store_true",help="Install snapper and existing open-source desktop editor stack")
    args=parser.parse_args()
    if args.check or not (args.snapper or args.free_editors or args.all_free):
        check()
        return
    if args.snapper or args.all_free:
        install_snapper()
    if args.free_editors or args.all_free:
        install_free_editors()
    check()

if __name__=="__main__":
    main()
