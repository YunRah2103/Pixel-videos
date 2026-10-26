#!/usr/bin/env python3
"""Original 15-second non-sampled engine/gravel sound. Safe to reuse."""
import numpy as np, wave, os
sr=48000; dur=15; n=sr*dur; t=np.arange(n,dtype=float)/sr
rng=np.random.default_rng(2103)
rpm=96+44*(.5+.5*np.sin(t*1.65-.8))+15*np.sin(t*.37)
for c in [1.08,4.15,8.0,11.45]:
    rpm-=25*np.exp(-((t-c)/.19)**2)
ph=2*np.pi*np.cumsum(rpm)/sr
engine=.35*(.52*np.sin(ph)+.21*np.sin(ph*2)+.085*np.sin(ph*3)+.07*np.sin(ph*.5))
noise=rng.normal(0,1,n)
engine+=.12*np.convolve(noise,np.ones(38)/38,mode="same")+.025*noise
notes=[110.0,130.81,146.83,98.0];music=np.zeros(n)
for j,f in enumerate(notes):
    m=(t>=j*3.75)&(t<(j+1)*3.75)
    tt=t[m]-j*3.75
    music[m]+=.036*(np.sin(2*np.pi*f*tt)+.25*np.sin(2*np.pi*2*f*tt))
pops=np.zeros(n)
for loc in [.64,.86,5.52,5.77,10.46,13.26,13.48]:
    k=np.arange(int(sr*.16));start=int(loc*sr)
    pops[start:start+len(k)]+=(.22*rng.normal(0,1,len(k))+.38*np.sin(2*np.pi*78*k/sr))*np.exp(-k/(sr*.045))
left=engine+music+pops
right=np.roll(engine,28)+music+np.roll(pops,6)
pcm=(np.clip(.88*np.tanh(np.column_stack([left,right])*1.9),-1,1)*32767).astype(np.int16)
with wave.open(os.path.join(os.path.dirname(__file__),"original_audio.wav"),"wb") as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())
