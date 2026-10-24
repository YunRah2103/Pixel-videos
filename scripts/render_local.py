#!/usr/bin/env python3
"""Self-contained render validation from the exact JS artwork used by Remotion.
Requires Node, CairoSVG, FFmpeg; --music takes a user supplied licensed recording.
"""
import argparse, subprocess, io, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cairosvg
from PIL import Image

def run():
 p=argparse.ArgumentParser();p.add_argument('--frames',type=int,default=360);p.add_argument('--music');p.add_argument('--output',default='out/sunset-harbor-v2-jazz.mp4');p.add_argument('--workers',type=int,default=4);a=p.parse_args()
 src=Path('out/svg-frames'); src.mkdir(parents=True,exist_ok=True)
 subprocess.run(['node','scripts/generate_svg_frames.mjs','0',str(a.frames),str(src)],check=True)
 Path(a.output).parent.mkdir(parents=True,exist_ok=True)
 intermediate=Path('out/v2-video-only.mp4')
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','360x640','-r','30','-i','-','-vf','scale=1080:1920:flags=neighbor,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(intermediate)]
 def conv(k):
  raw=cairosvg.svg2png(url=str(src/f'frame-{k:04}.svg'))
  return Image.open(io.BytesIO(raw)).convert('RGB').tobytes()
 with subprocess.Popen(cmd,stdin=subprocess.PIPE) as proc:
  try:
   with ThreadPoolExecutor(max_workers=a.workers) as pool:
    for i,b in enumerate(pool.map(conv,range(a.frames))):
     proc.stdin.write(b)
     if i%60==59:print(f'{i+1}/{a.frames} frames',flush=True)
  finally:proc.stdin.close()
  if proc.wait()!=0:raise RuntimeError('FFmpeg video render failed')
 if a.music:
  # Music source remains user-provided, not downloaded or replaced.
  aud=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(intermediate),'-ss','0','-i',a.music,'-map','0:v:0','-map','1:a:0','-t',str(a.frames/30),'-filter:a',f'afade=t=in:st=0:d=.24,afade=t=out:st={a.frames/30-1.35}:d=1.35','-c:v','copy','-c:a','aac','-b:a','160k','-ar','44100','-movflags','+faststart','-shortest',a.output]
  subprocess.run(aud,check=True)
 else:
  from shutil import copyfile;copyfile(intermediate,a.output)
 print('Rendered',a.output)
if __name__=='__main__':run()