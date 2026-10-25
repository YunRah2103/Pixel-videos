#!/usr/bin/env python3
"""Validate real downloaded editor binaries without claiming artwork was made."""
import json,os,platform,shutil,subprocess
from pathlib import Path
from setup_pixel_art_v4 import ROOT,existing_editor
assert platform.system()=="Linux","This CI verification targets Linux"
programs={
 "pixelorama":existing_editor("pixelorama","editors/pixelorama"),
 "godot":existing_editor("godot","engines/godot"),
 "ldtk":existing_editor("ldtk","editors/ldtk"),
 "krita":shutil.which("krita")
}
report={"platform":platform.platform(),"programs":{}}
for name,path in programs.items():
 if not path:
  raise SystemExit("INSTALL_MISSING: "+name)
 p=Path(path)
 if not p.is_file():
  raise SystemExit("NOT_FILE: "+name+" "+str(path))
 report["programs"][name]={"path":str(p),"bytes":p.stat().st_size,"executable":os.access(p,os.X_OK)}
 print("EDITOR_DOWNLOADED_AND_FOUND",name,str(p),flush=True)
smoke={"godot":["--headless","--version"],"krita":["--version"],"pixelorama":["--headless","--quit"]}
for name,args in smoke.items():
 try:
  cmd=[programs[name],*args]
  if name=="krita":
   cmd=["xvfb-run","-a",*cmd]
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=35)
  report["programs"][name]["cli_exit"]=p.returncode
  report["programs"][name]["stdout"]=p.stdout[-400:]
  report["programs"][name]["stderr"]=p.stderr[-400:]
  print("EDITOR_CLI_PROBE",name,p.returncode,p.stdout[-100:],p.stderr[-100:],flush=True)
  if p.returncode!=0:
   raise SystemExit("EDITOR_CLI_FAILED: "+name)
 except subprocess.TimeoutExpired:
  raise SystemExit("EDITOR_CLI_TIMED_OUT: "+name)
report["programs"]["ldtk"]["note"]="Binary found; Electron GUI authoring still needs an interactive environment"
out=ROOT/"out"/"artist-v4";out.mkdir(parents=True,exist_ok=True)
(out/"free-editors-evidence.json").write_text(json.dumps(report,indent=2)+"\n")
print("PIXEL_V4_FREE_EDITORS_VERIFIED",list(programs))
