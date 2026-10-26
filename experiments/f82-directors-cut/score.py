"""Original 10-second restrained electronic cue. No sampled/licensed audio."""
from pathlib import Path
import numpy as np,wave
from scipy.signal import butter,sosfilt
P=Path(__file__).resolve().parent;SR=48000;N=SR*10;t=np.arange(N)/SR
rng=np.random.default_rng(82);L=np.zeros(N);R=np.zeros(N)
def add(sound,at,gain=1,pan=0):
 i=round(at*SR);n=min(len(sound),N-i)
 if n>0:L[i:i+n]+=sound[:n]*gain*(1-pan*.35);R[i:i+n]+=sound[:n]*gain*(1+pan*.35)
def note(freq,duration,pluck=False):
 x=np.arange(int(duration*SR))/SR
 if pluck:env=(1-np.exp(-x*100))*np.exp(-x*4)
 else:env=np.minimum(1,x/.18)*np.minimum(1,np.maximum(0,(duration-x)/.4))*.55
 return (np.sin(2*np.pi*freq*x)+.2*np.sin(2*np.pi*freq*2*x)+.07*np.sin(2*np.pi*freq*3*x))*env
# low, spacious harmony
for start,chord in [(0,[146.83,174.61,220]),(2,[116.54,146.83,174.61]),(5.5,[130.81,164.81,196]),(7.8,[146.83,174.61,220])]:
 for j,f in enumerate(chord):add(note(f,2.4),start,.055,(j-1)*.8)
for i in range(16):
 at=2+i*.35
 if at>=7.7:break
 add(note([293.66,440,349.23,523.25][i%4],.75,True),at,.065,(-1 if i%2 else 1)*.65)
for at in [0,.85,2,3.1,4.2,5.5,6.6,7.8]:
 x=np.arange(int(.38*SR))/SR;phase=2*np.pi*(42*x+60*.035*(1-np.exp(-x/.035)));kick=np.sin(phase)*np.exp(-x*12);add(kick,at,.18)
for at in np.arange(2.25,7.7,.55):
 x=np.arange(int(.08*SR))/SR;noise=rng.normal(0,1,len(x));noise=sosfilt(butter(2,6500,fs=SR,btype='high',output='sos'),noise);add(noise*np.exp(-x*70),at,.018,.4)
# gentle tactile road bed, not presented as an engine recording
noise=rng.normal(0,1,N);road=sosfilt(butter(2,[140,1200],fs=SR,btype='band',output='sos'),noise)
vel=np.clip((t-1.8)/1,0,1)*np.clip((8-t)/.35,0,1);L+=road*.012*vel;R+=road*.011*vel
fade=np.minimum(1,t/.025)*np.minimum(1,(10-t)/.16);out=np.stack([L,R],1)*fade[:,None];out=np.tanh(out*1.5);out*=.72/max(.72,np.max(np.abs(out)))
with wave.open(str(P/'Original_Score.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype('<i2').tobytes())
print('Original score: stereo, 48000 Hz, 10s, peak',float(abs(out).max()))
