#!/usr/bin/env python3
"""Procedurally generated original engine, gravel and flame-pops soundtrack."""
import wave
from pathlib import Path
import numpy as np
rate=48000
N=rate*14
t=np.arange(N)/rate
rng=np.random.default_rng(2103)
rpm=105+12*np.sin(2*np.pi*.15*t)+6*np.sin(2*np.pi*.43*t)
for shift in (3.85,8.60,11.30):
    rpm-=18*np.exp(-.5*((t-shift)/.25)**2)
phase=2*np.pi*np.cumsum(rpm)/rate
motor=.14*np.sin(phase)+.11*np.sin(phase*2+.14)+.08*np.sin(phase*3+.3)+.036*np.sin(phase*4.9)
noise=rng.normal(size=N)
noise=np.convolve(noise,[.16,.22,.24,.22,.16],mode='same')
gravel=.048*noise*(.75+.25*np.sin(2*np.pi*1.8*t))
music=.031*(np.sin(2*np.pi*73.42*t)+.65*np.sin(2*np.pi*110*t))
beat=((t*2.4)%1.0)
music+=.027*np.sin(2*np.pi*146.8*t)*np.exp(-beat*13)
base=motor+gravel+music
for event,amount in [(0.45,1.0),(.87,.8),(1.25,1.1),(7.36,.86),(7.67,.70),(12.84,1.0),(13.18,.8),(13.54,1.2)]:
    k=int(event*rate)
    length=int(.34*rate)
    st=np.arange(length)/rate
    low=np.sin(2*np.pi*(100-64*st/.34)*st)
    crack=rng.normal(size=length)
    y=amount*(.28*low+.13*crack)*np.exp(-st*22)
    base[k:min(k+length,N)]+=y[:min(length,N-k)]
base*=np.minimum(1,t/.22)*np.minimum(1,(14-t)/.33)
base=np.tanh(base*1.6)*.74
stereo=np.stack([base,np.roll(base,int(rate*.0013))*.985],axis=1)
out=Path(__file__).resolve().parent/'output'/'original-engine-audio.wav'
out.parent.mkdir(parents=True,exist_ok=True)
with wave.open(str(out),'wb') as f:
    f.setnchannels(2)
    f.setsampwidth(2)
    f.setframerate(rate)
    f.writeframes((np.clip(stereo,-1,1)*32767).astype('<i2').tobytes())
print('AUDIO:',out,'14.0 sec, 48kHz, stereo')
