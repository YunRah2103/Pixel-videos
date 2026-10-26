import subprocess,json,pathlib,re,sys
p=pathlib.Path(sys.argv[1]);assert p.is_file() and p.stat().st_size>100000
v=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_format','-show_streams','-of','json',str(p)]))
video=next((s for s in v['streams'] if s['codec_type']=='video'),None)
audio=next((s for s in v['streams'] if s['codec_type']=='audio'),None)
assert video and audio,'Missing video or audio stream'
assert (video['width'],video['height'])==(1080,1920)
assert video['r_frame_rate']=='30/1'
frames=int(video.get('nb_read_frames',video.get('nb_frames',-1)))
assert frames==420,f'Expected 420 frames; got {frames}'
assert 13.9<=float(v['format']['duration'])<=14.1
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True)
x=re.search(r'max_volume:\s*(-?[0-9.]+) dB',r.stderr)
assert x and float(x.group(1))>-45., 'Silent audio track'
report=dict(frames=frames,width=1080,height=1920,fps=30,duration=v['format']['duration'],peak_db=x.group(1),size=p.stat().st_size,codec=video['codec_name'],audio=audio['codec_name'])
(p.parent/'verification.json').write_text(json.dumps(report,indent=2))
print('2.5D VIDEO VERIFIED:',json.dumps(report,indent=2))
