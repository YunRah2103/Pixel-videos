#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
p=Path(sys.argv[1]); assert p.exists() and p.stat().st_size>100000,(p,p.stat().st_size if p.exists() else 'MISSING')
r=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
v=next(x for x in r['streams'] if x['codec_type']=='video')
a=next(x for x in r['streams'] if x['codec_type']=='audio')
frames=int(v.get('nb_frames') or 0)
assert v['width']==1080 and v['height']==1920,v
assert v['r_frame_rate']=='30/1',v['r_frame_rate']
assert 14.95<=float(r['format']['duration'])<=15.1,r['format']['duration']
assert frames>=449,frames
assert a['codec_name']=='aac',a
print(json.dumps({'file':str(p),'width':v['width'],'height':v['height'],'fps':v['r_frame_rate'],'frames':frames,'duration':r['format']['duration'],'audio':a['codec_name'],'bytes':p.stat().st_size},indent=2))