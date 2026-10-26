#!/usr/bin/env python3
"""Original procedurally synthesised rally soundtrack: not a third-party recording."""
import wave, math, random, struct
from pathlib import Path
R=random.Random(14); SR=48000; D=15; TOTAL=SR*D
out=Path(__file__).resolve().parents[1]/'output'/'soundtrack.wav';out.parent.mkdir(parents=True,exist_ok=True)
flames=[(.58,1.45),(7.1,8.35),(10.7,11.5),(13.65,14.33)]
def beat(t):
 h=0
 for bt in [0,0.7,1.4,2.1,2.8,3.5,4.2,4.9,5.6,6.3,7,7.7,8.4,9.1,9.8,10.5,11.2,11.9,12.6,13.3,14]:
  dt=t-bt
  if 0<=dt<.16:h+=.19*math.exp(-dt*34)*math.sin(2*math.pi*(72-60*dt)*dt)
 return h
with wave.open(str(out),'wb') as f:
 f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR)
 chunks=[]
 for i in range(TOTAL):
  t=i/SR
  gear=math.floor((t+0.25)/2.6)
  throttle=((t+0.25)%2.6)/2.6
  rpm=72+50*throttle+10*math.sin(1.9*t)
  # Slight cubic grit / harmonic stereo engine roar, consistently sped by shared time.
  phase=2*math.pi*(75*t + 10*t*t + 0.7*math.sin(3*t))
  engine=(math.sin(phase*.81)*.28+math.sin(phase*1.62)*.14+math.sin(phase*3.24)*.06)
  engine*=.40+throttle*.35
  grit=(R.random()-.5)*(.10+.05*throttle)
  # Metallic gated pop envelope per visible exhaust event.
  pop=0
  for a,b in flames:
   if a<=t<=b:
    x=t-a
    attack=math.exp(-x*10)
    pop+=.30*attack*(R.random()-.5)+.16*math.exp(-x*22)*math.sin(2*math.pi*180*x)
  tick=beat(t)
  # Subtle driving melody built out of 12TET soft square-like harmonics.
  notes=[110,146.832,164.814,130.813,110,146.832,174.614,164.814]
  note=notes[int(t*2)%len(notes)]
  melody=.055*(math.sin(2*math.pi*note*t)+.24*math.sin(2*math.pi*note*2*t))
  fade=min(1,t/.12,(D-t)/.08)
  val=(engine+grit+pop+tick+melody)*max(0,fade)
  l=max(-1,min(1,val*.88));r=max(-1,min(1,val*.93 + math.sin(t*21)*.008))
  chunks.append(struct.pack('<hh',int(l*32767),int(r*32767)))
  if len(chunks)>20000: f.writeframesraw(b''.join(chunks));chunks=[]
 if chunks:f.writeframesraw(b''.join(chunks))
print('Generated',out, 'duration',D,'sample_rate',SR)