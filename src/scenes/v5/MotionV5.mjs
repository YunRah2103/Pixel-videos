/**
 * SUNSET HARBOR V5 / AGENT 3 — deterministic 360x640 director's timeline.
 * 360 frames, 30fps. Neither camera nor actor animation uses mutable state.
 * Contract: every V5StoryPlane takes one returned motion object.
 */
export const V5_FPS=30;
export const V5_FRAMES=360;
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x));
const ease=t=>{t=clamp(t);return t*t*(3-2*t)};
const blend=(f,a,b)=>ease((f-a)/(b-a));
const lerp=(a,b,t)=>a+(b-a)*t;
const wave=(f,p,phase=0)=>Math.sin((f/p)*Math.PI*2+phase);
const pulse=(f,a,b,c)=>blend(f,a,b)*(1-blend(f,b,c));
/**
 * One foot swings at a time; the OTHER stays at an absolute world x coordinate.
 * No faux treadmill sliding: walking progress advances on six discrete planted
 * steps; the swing phase has a 4px clearance and lands at zero clearance.
 */
export function walkingFeet(frame){
 const f=clamp(frame,0,359),phase=clamp((f-100)/105);
 const targets=[187,193,198,203,208,215],initial=[177,188];
 const u=phase*6;
 const active=Math.min(5,Math.floor(Math.min(5.999999,u)));
 const local=u-active;
 const placed=[...initial];
 for(let j=0;j<active;j++)placed[j%2]=targets[j];
 if(phase>0&&phase<1)placed[active%2]=lerp(placed[active%2],targets[active],ease(local));
 if(phase>=1){placed[0]=targets[4];placed[1]=targets[5]}
 const lift=phase>0&&phase<1?Math.round(4*Math.sin(Math.PI*ease(local))):0;
 return {
  leftX:placed[0],rightX:placed[1],
  leftY:550-(active%2===0?lift:0),
  rightY:550-(active%2===1?lift:0),
  walk:phase>0&&phase<1,phase:local
 };
}
export function getV5Motion(frame=0){
 const f=clamp(Math.floor(Number.isFinite(frame)?frame:0),0,359);
 const intro=blend(f,0,84),boatView=blend(f,84,153);
 const meet=blend(f,153,243),settle=blend(f,255,359);
 // A three-phrase crane / lateral-track / soft-release, not one 12s zoom.
 // Smooth velocity between phrases; pan foreground more than sky.
 const cameraX=lerp(2,5,intro)-9*boatView-9*meet+6*settle;
 const cameraY=-2+2*intro-3*boatView-5*meet+2*settle;
 const cameraZoom=1.012+.005*intro+.033*boatView+.078*meet-.018*settle;
 const wind=.62*wave(f,113,.8)+.28*wave(f,59,1.7)+.1*wave(f,223,.1);
 const actorWalk=blend(f,100,205);
 const actorX=181+30*actorWalk;
 const actorLook=blend(f,164,194);
 const partnerLook=blend(f,173,209);
 const reach=blend(f,197,229),handsJoined=blend(f,227,239);
 const breathe=wave(f,149,.3);
 const catProgress=blend(f,113,253),catSit=blend(f,255,286);
 const boatProgress=blend(f,1,329);
 const boatX=lerp(369,110,boatProgress);
 const boatY=413+.7*wave(f,79,.8)+.9*wave(f,37,.3);
 const boatHeel=.6*wave(f,98,.7)+.3*wave(f,49,.4);
 const story={
  actorX,actorFeet:walkingFeet(f),actorWalk,actorLook,
  partnerX:244-4*blend(f,195,248),partnerLook,
  reach,handsJoined,quietSmile:blend(f,224,258),
  scarfWind:wind*(.65+.35*blend(f,90,150)),breathe,
  blinkA:([75,76,211,212,329,330].includes(f)),
  blinkB:([129,130,229,230,341,342].includes(f)),
  catX:174+30*catProgress,catY:567,
  catWalk:catProgress,catSit,catStride:(f-113)/9,
  catLook:blend(f,201,232),catTail:wave(f,97,.4),
  boatX,boatY,boatHeel,boatProgress,
  boatReveal:blend(f,0,51),boatWake:blend(f,29,89),
  sailFlutter:wave(f,81,.8)*1.6+wind*.8,
  birdsTravel:f*.21,birdWing:wave(f,19,.3),
  finalGlint:pulse(f,266,320,359),eveningHold:settle
 };
 return {
  frame:f,seconds:f/30,progress:f/359,
  act:f<90?'wonder':f<246?'meeting':'afterglow',
  cameraX,cameraY,cameraZoom,
  cloudDrift:f*.052+.18*wave(f,203),
  waterPhase:f*.079,waterMotion:wave(f,131)*.12,
  lightIntensity:.92+.12*blend(f,94,305)+.008*wave(f,173),
  foliageSway:wind*1.7,wind,
  parallax:{sky:.13,distant:.28,architecture:.51,water:.69,promenade:.96,
    foreground:1.19,lifeFar:.61,lifeNear:1.02},
  ...story
 };
}
