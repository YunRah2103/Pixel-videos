/**
 * Sunset Harbor V3 — one deterministic 360-frame cinematic camera and acting score.
 * Frame-in/frame-out, 30fps. No wall-clock state, RNG, CSS animation or timers.
 * Agent 1's HarborWorld can consume this plain parameter object unchanged.
 */
export const HARBOR_FPS = 30;
export const HARBOR_FRAMES = 360;
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const smooth=t=>{t=clamp(t);return t*t*(3-2*t)};
const mix=(a,b,t)=>a+(b-a)*t;
const ramp=(f,start,end)=>smooth((f-start)/(end-start));
const pulse=(f,start,peak,end)=>ramp(f,start,peak)*(1-ramp(f,peak,end));
const sin=(f,period,phase=0)=>Math.sin((f/period)*Math.PI*2+phase);

/** The camera is quiet: one long breath, small pan, then a deliberate settle. */
export function getHarborMotion(frame){
  const f=clamp(Math.floor(Number.isFinite(frame)?frame:0),0,HARBOR_FRAMES-1);
  const reveal=ramp(f,0,92);
  const drift=ramp(f,55,252);
  const settle=ramp(f,253,359);
  const cameraX=mix(-1.1,1.05,drift)-0.38*settle+sin(f,310)*0.12;
  const cameraY=-0.58*reveal-0.55*drift+0.27*settle;
  const cameraZoom=1.014+0.014*reveal+0.013*drift-0.003*settle;
  const cloudDrift=f*0.028;
  const waterPhase=f*0.087;
  const boatX=276-f*0.105;
  const foliageSway=sin(f,149)*1.7+sin(f,67,0.8)*0.5;
  const lightIntensity=0.82+0.11*ramp(f,94,250)+0.05*sin(f,163);
  const waveStrength=0.60+0.15*sin(f,122,-0.5);
  const catX=195+48*ramp(f,132,278);
  const catStep= Math.floor(f/6)%4;
  const characterBeat=f<72?'opening':f<166?'watching':f<252?'noticing':f<312?'together':'stillness';
  const glance=pulse(f,127,182,244);
  const wave=pulse(f,174,205,242);
  const handhold=ramp(f,236,307);
  const catSit=ramp(f,281,319);
  const boatBob=sin(f,48,0.4)*1.2;
  const gullWing=Math.floor(f/7)%4;
  return {
    frame:f,seconds:f/HARBOR_FPS,progress:f/(HARBOR_FRAMES-1),
    cameraX,cameraY,cameraZoom,
    cloudDrift,waterPhase,boatX,boatBob,foliageSway,lightIntensity,
    waveStrength,catX,catStep,catSit,characterBeat,glance,wave,handhold,
    gullWing,endingEase:settle,
    // Independent parallax planes: sky, skyline, water, promenade, nearby foliage.
    parallax:{sky:0.13,far:0.30,mid:0.58,water:0.75,near:1.0,foreground:1.35},
  };
}
