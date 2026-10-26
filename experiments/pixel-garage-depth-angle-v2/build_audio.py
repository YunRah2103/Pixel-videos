#!/usr/bin/env python3
import numpy as np, wave, os
sr=48000;n=sr*8;t=np.arange(n,dtype=float)/sr;r=np.random.default_rng(32)
freq=73+29*np.sin(t*1.8)+24*t/8
phase=2*np.pi*np.cumsum(freq)/sr
engine=.24*np.sin(phase)+.12*np.sin(phase*2)+.06*np.sin(phase*.5)
s=engine+.05*r.normal(size=n)
for p in (.58,4.72,7.1):
    at=int(p*sr);q=min(int(.15*sr),n-at);v=np.arange(q)/sr
    s[at:at+q]+=.4*r.normal(size=q)*np.exp(-v/.031)
s=np.clip(s,-.85,.85)
pcm=(np.column_stack([s,np.roll(s,18)])*32767).astype(np.int16)
with wave.open(os.path.join(os.path.dirname(__file__),"sound.wav"),"wb") as f:
    f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr);f.writeframes(pcm.tobytes())
