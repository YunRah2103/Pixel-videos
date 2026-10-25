#!/usr/bin/env python3
import json,subprocess,sys,pathlib
target=pathlib.Path(sys.argv[1])
info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(target)],text=True))
video=next((s for s in info['streams'] if s['codec_type']=='video'),None)
audio=next((s for s in info['streams'] if s['codec_type']=='audio'),None)
assert video and audio, 'Video or audio missing'
assert (video['width'],video['height'])==(1080,1920), 'TikTok dimensions incorrect'
assert video['r_frame_rate']=='30/1', 'Not 30fps'
frames=int(video.get('nb_read_frames',video.get('nb_frames',-1)))
assert 417<=frames<=420, 'Unexpected frame count '+str(frames)
duration=float(info['format']['duration'])
assert 13.9<=duration<=14.1,'Duration not 14 seconds'
results={'file':target.name,'width':1080,'height':1920,'fps':30,'frames':frames,'duration_seconds':duration,'video_codec':video['codec_name'],'audio_codec':audio['codec_name'],'size_bytes':target.stat().st_size}
(target.parent/'verification.json').write_text(json.dumps(results,indent=2))
print('VERIFIED:',json.dumps(results,indent=2))
