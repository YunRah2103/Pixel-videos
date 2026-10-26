#!/usr/bin/env python3
from pathlib import Path
import wave,numpy as np
rate=48000;seconds=14;N=rate*seconds;t=np.arange(N)/rate
rng=np.random.default_rng(24252)
hz=96+18*np.sin(2*np.pi*.18*t)+10*np.sin(2*np.pi*.65*t)
phase=2*np.pi*np.cumsum(hz)/rate
engine=.20*np.sin(phase)+.12*np.sin(2*phase+.3)+.055*np.sin(3*phase+.8)
noise=rng.normal(size=N)
gravel=.065*np.convolve(noise,[.2,.6,.2],mode='same')
beat=np.exp(-((t*2.5)%1)*17)
music=.042*np.sin(2*np.pi*73.42*t)+.025*np.sin(2*np.pi*146.83*t)*beat
signal=engine+gravel+music
for when in [.42,.89,1.21,7.27,7.7,13.22,13.6]:
 start=int(when*rate);length=min(int(.21*rate),N-start)
 x=np.arange(length)/rate
 signal[start:start+length]+=(.35*np.sin(2*np.pi*(155-440*x)*x)+.12*rng.normal(size=length))*np.exp(-x*24)
signal*=np.minimum(1,t/.2)*np.minimum(1,(seconds-t)/.25)
signal=np.tanh(signal*1.45)*.86
stereo=np.stack([signal,np.roll(signal,72)*.98],axis=1)
out=Path(__file__).resolve().parent/'output'/'audio.wav';out.parent.mkdir(exist_ok=True)
with wave.open(str(out),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate)
 w.writeframes((np.clip(stereo,-1,1)*32767).astype('<i2').tobytes())
print('Original mixed audio:',out)
