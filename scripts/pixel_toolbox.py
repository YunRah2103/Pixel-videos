#!/usr/bin/env python3
"""Read the 49-tool catalog, pick suitable tools, and report REAL availability.

No silent downloads and no fictional editor invocation. All commands are local.
"""
import argparse
import importlib.util
import json
import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "studio" / "toolbox" / "catalog.json"
STAGES = ["sprites", "levels", "motion", "lighting", "processing", "audio", "reference"]

def catalog():
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    rows = data["tools"]
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicated tool id")
    if len(rows) < 20:
        raise ValueError("Tool catalog accidentally shrank")
    return rows

def available(tool):
    mode, probe = tool["interface"], tool["probe"]
    if mode == "web":
        return "web (not locally installed)"
    if mode == "python":
        try:
            return "ready" if importlib.util.find_spec(probe) else "missing"
        except (ImportError, ModuleNotFoundError, ValueError):
            return "missing"
    if mode == "npm":
        path = ROOT / "node_modules" / probe
        return "ready" if path.exists() else "missing"
    paths = [ROOT / ".tools"]
    if probe and shutil.which(probe):
        return "ready"
    if tool["id"] == "pixelorama" and (ROOT / ".tools" / "editors" / "pixelorama").exists():
        return "downloaded (locate binary)"
    if tool["id"] == "godot" and (ROOT / ".tools" / "engines" / "godot").exists():
        return "downloaded (locate binary)"
    return "missing"

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list", help="List every free toolkit option")
    ls.add_argument("--stage", choices=STAGES)
    ls.add_argument("--json", action="store_true")
    doctor = sub.add_parser("doctor", help="Check tools actually installed in THIS runtime")
    doctor.add_argument("--json", action="store_true")
    rec = sub.add_parser("recommend", help="Pick tools for a job without pretending GUI is usable headlessly")
    rec.add_argument("stage", choices=STAGES)
    rec.add_argument("--headless", action="store_true")
    rec.add_argument("--limit", type=int, default=10)
    guide = sub.add_parser("how", help="Show official source and setup for one tool id")
    guide.add_argument("id")
    a = ap.parse_args()
    rows = catalog()
    if a.cmd == "how":
        x = next((r for r in rows if r["id"] == a.id), None)
        if not x:
            ap.error("unknown tool id; run list")
        for k in ("name", "purpose", "source", "interface", "setup"):
            print(f"{k}: {x[k]}")
        print("runtime:", available(x))
        return
    if a.cmd == "recommend":
        rows = [r for r in rows if r["stage"] == a.stage]
        if a.headless:
            rows = [r for r in rows if r["interface"] in {"cli", "python", "npm"}]
        rows = sorted(rows, key=lambda r: (available(r) != "ready", r["interface"] in {"gui", "web"}, r["name"].lower()))
        rows = rows[:max(1, a.limit)]
    elif a.cmd == "list" and a.stage:
        rows = [r for r in rows if r["stage"] == a.stage]
    if getattr(a, "json", False):
        print(json.dumps([{**r, "runtime": available(r)} for r in rows], indent=2))
        return
    print(f"Found {len(rows)} catalog entries; availability checked on this machine only.")
    for row in rows:
        status = available(row)
        print(f"{row['id']:<22} {row['stage']:<11} {row['interface']:<7} {status:<27} {row['purpose']}")
    if a.cmd == "doctor":
        print("\nMissing != unavailable forever. Use 'how <id>' for setup; see docs/PIXEL_TOOLBOX_2026.md.")
if __name__ == "__main__":
    main()
