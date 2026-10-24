/**
 * Agent 3 V2 — distance-led, deterministic 12-second pixel motion.
 * One authoritative road clock. NEVER animate wheels or layers independently.
 * Native pixel offsets and grounded wheel contact; body-only one-pixel springs.
 */
export const COUNTRYSIDE_FRAMES=360;
export const COUNTRYSIDE_FPS=30;
export const COUNTRYSIDE_NATIVE_WIDTH=360;
export const COUNTRYSIDE_WHEEL_CONTACT_Y=495;
export const COUNTRYSIDE_LAYER_SPEC={
  farTrees:{pixelsPerFrame:0.5,periodPx:180},
  midTrees:{pixelsPerFrame:1,periodPx:360},
  nearTrees:{pixelsPerFrame:2,periodPx:360},
  verge:{pixelsPerFrame:2.5,periodPx:180},
  road:{pixelsPerFrame:3,periodPx:360},
} as const;
export type CountrysideMovingLayer=keyof typeof COUNTRYSIDE_LAYER_SPEC;
export type CountrysideOffsets=Record<CountrysideMovingLayer,number>;
// Only a legacy fallback for standalone tests: actual authored wheel radius is 11.5.
export const DEFAULT_WHEEL_RADIUS_PX=1080/(2*Math.PI*18);
export const AUTHOR_WHEEL_RADIUS_PX=11.5;
export const AUTHOR_WHEEL_BASE_PX=85;
export type CountrysideMotion={
  frame:number;cycleFrame:number;carX:number;bobY:number;
  roadTravelPx:number;wheelRotationTurns:number;offsets:CountrysideOffsets;
  frontSpringPx:number;rearSpringPx:number;shadowOpacity:number;
};
const assertFrame=(frame:number)=>{
  if(!Number.isInteger(frame)||frame<0)throw Error('Countryside motion frame must be an integer >= 0');
};
const posmod=(value:number,mod:number)=>((value%mod)+mod)%mod;
/** Pixel positions are always integers; the distant background deliberately alternates 0/1px steps. */
export function nativeOffset(frame:number,layer:CountrysideMovingLayer):number{
  assertFrame(frame);
  return -Math.round((frame%COUNTRYSIDE_FRAMES)*COUNTRYSIDE_LAYER_SPEC[layer].pixelsPerFrame);
}
export function wrapTileOffset(offsetX:number,tileWidth:number):number{
  if(!Number.isInteger(offsetX)||!Number.isInteger(tileWidth)||tileWidth<1)
    throw Error('Tile offsets and tile width must be integer native pixels');
  return -posmod(-offsetX,tileWidth);
}
export function wheelPoseIndex(turns:number,count:number):number{
  if(!Number.isFinite(turns)||!Number.isInteger(count)||count<1)throw Error('Invalid wheel pose input');
  return posmod(Math.floor(turns*count+1e-9),count);
}
/**
 * Wheel centres are 137px (rear) and 222px (front) on the native screen.
 * Original road pixel texture has isolated tiny seams at x=109 and x=305.
 * Respond briefly to those exact surface positions as each axle crosses them.
 * A very short +1 compression and -1 rebound is intentionally NOT camera shake.
 */
export function springFromRoad(roadTravelPx:number,screenWheelX:number):number{
  if(!Number.isInteger(roadTravelPx)||!Number.isInteger(screenWheelX))
    throw Error('road travel and wheel centre must be integer pixels');
  const location=posmod(roadTravelPx+screenWheelX,360);
  for(const bumpX of [109,305]){
    const after=posmod(location-bumpX,360);
    if(after<12)return 1;          // tyre rolls across a muted road grain ridge
    if(after<21)return -1;         // very short damped return, no oscillatory wobble
  }
  return 0;
}
export function getCountrysideMotion(frame:number,wheelRadiusPx=DEFAULT_WHEEL_RADIUS_PX):CountrysideMotion{
  assertFrame(frame);
  if(!Number.isFinite(wheelRadiusPx)||wheelRadiusPx<=0)
    throw Error('wheelRadiusPx must be a finite positive measured native-pixel radius');
  const cycleFrame=frame%COUNTRYSIDE_FRAMES;
  const roadTravelPx=cycleFrame*COUNTRYSIDE_LAYER_SPEC.road.pixelsPerFrame;
  const carX=180;
  const frontSpringPx=springFromRoad(roadTravelPx,carX-78+120);
  const rearSpringPx=springFromRoad(roadTravelPx,carX-78+35);
  const bobY=Math.max(-1,Math.min(1,frontSpringPx+rearSpringPx));
  const shadowOpacity=Math.max(.22,Math.min(.34,Math.round((.27-.025*bobY)*100)/100));
  return {
    frame,cycleFrame,carX,bobY,frontSpringPx,rearSpringPx,shadowOpacity,
    roadTravelPx,wheelRotationTurns:roadTravelPx/(2*Math.PI*wheelRadiusPx),
    offsets:{
      farTrees:nativeOffset(frame,'farTrees'),midTrees:nativeOffset(frame,'midTrees'),
      nearTrees:nativeOffset(frame,'nearTrees'),verge:nativeOffset(frame,'verge'),
      road:nativeOffset(frame,'road'),
    },
  };
}
