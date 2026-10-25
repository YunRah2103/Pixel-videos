/**
 * Real PixiJS world choreography, using the 6 original layered sprite PNGs.
 * Strong depth, accelerated road, near-camera shrub parallax, dappled road
 * shade and restrained leaf particles. Every vertex is integer pixel snapped.
 */
import type {CinematicMotion} from './DrivingMotionV3';
export const PIXI_WORLD_LAYERS=[
 {name:'sky',path:'sky.png',width:360,height:480,y:0},
 {name:'farTrees',path:'farTrees.png',width:720,height:300,y:180},
 {name:'midTrees',path:'midTrees.png',width:840,height:265,y:215},
 {name:'nearTrees',path:'nearTrees.png',width:960,height:235,y:245},
 {name:'road',path:'road.png',width:384,height:160,y:480},
 {name:'verge',path:'verge.png',width:384,height:160,y:480},
] as const;
export type PixiWorldLayer=typeof PIXI_WORLD_LAYERS[number]['name'];
const mod=(n:number,m:number)=>((n%m)+m)%m;
const snapped=(n:number)=>Math.round(n);
export type PixiWorldPlan={
 frame:number;
 layers:ReadonlyArray<{name:PixiWorldLayer;tileX:number;y:number}>;
 shrubs:ReadonlyArray<{x:number;y:number;size:number;tint:number}>;
 shadeBands:ReadonlyArray<{x:number;width:number;alpha:number}>;
 lightPixels:ReadonlyArray<{x:number;y:number;alpha:number;color:number}>;
 leafMotes:ReadonlyArray<{x:number;y:number;size:number;color:number}>;
 roadSpecks:ReadonlyArray<{x:number;y:number;width:number;color:number}>;
 dust:ReadonlyArray<{x:number;y:number;size:number;opacity:number}>;
 contactShadow:{x:number;y:number;width:number;alpha:number};
};
/** Drawing instructions are deterministic for any seek/reverse order. */
export function planPixiWorld(frame:number,m:CinematicMotion):PixiWorldPlan{
 if(!Number.isInteger(frame)||frame<0||m.frame!==frame)throw Error('Stale world/motion frame');
 const layers=PIXI_WORLD_LAYERS.map(l=>({
  name:l.name,
  // Clouds now move SLOWLY across the skyline, independent from the trees.
  tileX:l.name==='sky'?-snapped(frame*.22):m.offsets[l.name],
  y:l.y,
 }));
 const shrubBases=[-45,4,56,103,163,217,274,339,391,445,497,553];
 const shrubs=shrubBases.map((x,i)=>({
  x:mod(x-m.foregroundTravelPx,598)-65,
  y:466+(i%3)*3,
  size:[14,25,18,30,20,24,16,32,22,19,28,16][i],
  tint:i%4,
 })).filter(s=>s.x>-70&&s.x<380);
 // Wide stepped shade falls across the actual road surface below passing trees.
 const shadeBases=[0,112,253,379,516,640,799];
 const shadeBands=shadeBases.map((x,i)=>({
  x:mod(x-snapped(m.roadTravelPx*.79),886)-130,
  width:[17,29,21,35,24,38,25][i],
  alpha:[.13,.19,.15,.23,.17,.20,.15][i]
 })).filter(s=>s.x>-70&&s.x<360);
 const leafBases=[17,42,67,105,130,174,217,246,285,312,351,384,429,475,508,552];
 const leafMotes=leafBases.map((x,i)=>({
  x:mod(x-snapped(m.foregroundTravelPx*.72)+i*13,617)-55,
  y:360+(i*23)%112+snapped(Math.sin(frame*.09+i*2)*3),
  size:i%3===0?3:2,
  color:[0xB1C87C,0xE1C87E,0x8AAC67,0xC9D77C][i%4],
 })).filter(p=>p.x>=0&&p.x<358);
 const glintBases=[25,63,111,158,203,251,291,330,373,413,472,511,566];
 const lightPixels=glintBases.map((x,i)=>({
  x:mod(x+ m.offsets.nearTrees,960),
  y:364+(i*31)%81,
  alpha:[.18,.3,.23][(i+Math.floor(frame/14))%3],
  color:i%2?0xD1D58B:0x9BBC69,
 })).filter(p=>p.x>=0&&p.x<357);
 const roadSpecks=Array.from({length:28},(_,i)=>({
   x:mod(31+i*53-m.roadTravelPx,523)-9,
   y:[513,531,546,566][i%4],
   width:[2,4,7,3][i%4],
   color:i%5===0?0xBBC2A1:0x777C75,
 })).filter(s=>s.x>0&&s.x<355);
 // Dust wakes behind the rear tyre only at higher speed; never a fog screen.
 const dust=Array.from({length:5},(_,i)=>{
  const age=mod(frame*2+i*13,51);
  return {x:snapped(m.carX-57-age*.62),y:493+snapped(age*.09)+(i%2)*2,
   size:i%3===0?3:2,opacity:(m.velocityPx>=5? .25:.07)*(1-age/52)};
 }).filter(p=>p.x>0&&p.y<512);
 return {
  frame,layers,shrubs,shadeBands,lightPixels,leafMotes,roadSpecks,dust,
  contactShadow:{x:snapped(m.carX-73),y:494,width:146,alpha:m.shadowOpacity},
 };
}
