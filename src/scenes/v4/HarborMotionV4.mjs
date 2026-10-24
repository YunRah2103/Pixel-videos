/**
 * Sunset Harbor V4 — Agent 3 film direction score.
 * All channels are frame-derived. No timers, random numbers, mutable state or CSS keyframes.
 * Art-space = 360 x 640; output = 360 frames at 30fps.
 * Designed to be consumed by HarborWorldV4 + HarborAtmosphereV4 without importing them.
 */
export const HARBOR_V4_FPS = 30;
export const HARBOR_V4_FRAMES = 360;
const clamp = (v,a=0,b=1) => Math.min(b,Math.max(a,v));
const ease = t => { t=clamp(t); return t*t*t*(t*(t*6-15)+10); };
const span = (f,a,b) => ease((f-a)/(b-a));
const lerp = (a,b,t) => a+(b-a)*t;
const sin = (f,period,phase=0) => Math.sin(f*Math.PI*2/period+phase);
const bell = (f,a,b,c) => span(f,a,b)*(1-span(f,b,c));
export function getHarborMotionV4(frame=0) {
  const f=clamp(Math.floor(Number.isFinite(frame)?frame:0),0,HARBOR_V4_FRAMES-1);
  const reveal=span(f,0,90), inhabit=span(f,90,260), rest=span(f,266,359);
  const opening=(1-reveal), stillness=span(f,275,355);
  // Single continuous move: observe the sun, drift towards the people, finish at rest.
  // The near plane moves ~4x as far as the sky, but scenery never clips the sun.
  const cameraX=2.7-4.2*reveal-13.4*inhabit+2.5*rest;
  const cameraY=1.3-1.8*reveal-4.5*inhabit+1.1*rest;
  const cameraZoom=1.018+0.026*reveal+0.073*inhabit-0.009*rest;
  const clock=f/HARBOR_V4_FPS;
  const breeze=0.68*sin(f,137,0.4)+0.34*sin(f,61,1.3);
  // Each plane has its own deterministic displacement measured in native pixels.
  const parallax={sky:0.14,distant:0.28,architecture:0.55,water:0.73,
    promenade:1.0,foreground:1.28,lifeFar:0.62,lifeNear:1.08};
  const boatReveal=span(f,48,74);
  const boatTravel=span(f,65,321);
  const boatX=lerp(369,123,boatTravel);
  const boatY=421+1.3*sin(f,51,0.5)+0.45*sin(f,23,1);
  const boatHeel=0.7*sin(f,63,0.3);
  const boatWake=boatReveal*(0.6+0.4*span(f,85,144));
  const sailFlutter=sin(f,77,0.15)*1.25;
  const firstStep=bell(f,97,142,194);
  const nextStep=bell(f,113,159,202);
  const meet=span(f,150,212);
  const glance=bell(f,139,178,245);
  const handhold=span(f,170,232);
  const quietSmile=span(f,185,245);
  const coatBreeze=breeze*(0.5+0.5*span(f,80,140))*(1-0.5*stillness);
  const blinking=(!((f+9)%137<4)||f<20)?0:1;
  const catTravel=span(f,87,251);
  // Walk beside the couple, away from the cafe umbrella and chairs.\n  const catX=lerp(190,174,catTravel);
  const catSit=span(f,248,295);
  const catStep=(f-85)*0.19;
  const catTail=sin(f,69,1.2)*(1-0.72*catSit);
  const birdsTravel=span(f,38,280);
  const gullWing=sin(f,25,0.6);
  const cloudDrift=f*0.046 + 0.18*sin(f,224);
  const waterPhase=f*0.073;
  const foliageSway=breeze*1.8;
  const lightIntensity=0.91+0.105*span(f,120,312)+0.012*sin(f,188);
  const finalGlint=bell(f,290,331,359);
  return {
    frame:f, fps:HARBOR_V4_FPS, seconds:clock, progress:f/(HARBOR_V4_FRAMES-1),
    act:f<90?'wonder':f<270?'belonging':'afterglow',
    cameraX,cameraY,cameraZoom,parallax,cloudDrift,waterPhase,
    waterMotion:sin(f,95)*0.16,foliageSway,lightIntensity,
    waveStrength:0.62+0.08*sin(f,91),finalGlint,
    boatX,boatY,boatHeel,boatReveal,boatTravel,boatWake,sailFlutter,
    firstStep,nextStep,meet,glance,handhold,quietSmile,coatBreeze,blinking,
    catX,catSit,catTravel,catStep,catTail,birdsTravel,gullWing,
    endingEase:rest,stillness,opening
  };
}
// Explicitly stable compatibility aliases for V3 integrator wiring.
export const getHarborMotion = getHarborMotionV4;
