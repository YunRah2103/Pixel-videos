import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {renderHarborBaseLayers} from '../v4/HarborWorldV4.mjs';
import {getHarborMotionV4} from '../v4/HarborMotionV4.mjs';
import {renderHarborLifeV4} from '../v4/HarborLifeV4.mjs';
import {V5AtmospherePlane,V5AtmospherePlaneName} from './AtmosphereV5';

/**
 * Agent 2 ISOLATED 12-second proof composition. Does not modify shared Root,
 * V4 artwork, Agent 1's world or Agent 3's characters/camera.
 * Reuses the approved V4 world and story as an honest A/B comparison.
 */
const W=360,H=640;
const legacy=(content:string,clip?:'horizon')=>{
 const mask=clip?'<defs><clipPath id="v5-proof-horizon"><rect x="0" y="309" width="360" height="49"/></clipPath></defs>':'';
 const inner=clip?'<g clip-path="url(#v5-proof-horizon)">'+content+'</g>':content;
 return <svg xmlns="http://www.w3.org/2000/svg" width={W} height={H} viewBox="0 0 360 640"
   shapeRendering="crispEdges" style={{position:'absolute',left:0,top:0,imageRendering:'pixelated'}}
   dangerouslySetInnerHTML={{__html:mask+inner}}/>;
};
const layer=(name:string,scene:React.ReactNode,m:any,depth:number)=>{
 const x=(m.cameraX*depth).toFixed(3),y=(m.cameraY*depth).toFixed(3);
 const zoom=(1+(m.cameraZoom-1)*depth).toFixed(5);
 return <div key={name} style={{
   position:'absolute',left:0,top:0,width:W,height:H,overflow:'visible',
   transform:'translate('+x+'px,'+y+'px) scale('+zoom+')',
   transformOrigin:'50% 46%',imageRendering:'pixelated',pointerEvents:'none'
 }}>{scene}</div>;
};
export const AtmosphereV5Proof:React.FC=()=>{
 const frame=useCurrentFrame();
 const motion=getHarborMotionV4(frame);
 const world=renderHarborBaseLayers(frame,{...motion,cameraX:0,cameraY:0});
 const life=renderHarborLifeV4(frame,motion);
 const p=motion.parallax;
 const atmosphereMotion={
  ...motion,sunX:225,sunY:252,waterTop:353,waterBottom:535,
  drawAtmosphericBirds:false,drawAtmosphericBoatWake:false
 };
 const A=(name:V5AtmospherePlaneName)=><V5AtmospherePlane frame={frame} motion={atmosphereMotion} plane={name}/>;
 return <AbsoluteFill style={{
  width:W,height:H,backgroundColor:'#173e5b',overflow:'hidden',imageRendering:'pixelated'
 }}>
   {layer('sky',A('sky'),motion,p.sky)}
   {layer('clouds',A('clouds'),motion,p.sky*1.05)}
   {layer('birds',legacy(life.birds),motion,p.distant)}
   {layer('distant',legacy(world.distant),motion,p.distant)}
   {layer('air',A('air'),motion,p.distant)}
   {layer('water',A('water'),motion,p.water)}
   {layer('reflections',A('reflections'),motion,p.water)}
   {layer('boat-wake',legacy(life.water),motion,p.lifeFar)}
   {layer('architecture',legacy(world.architecture),motion,p.architecture)}
   {layer('quays',legacy(world.harbourStructures),motion,p.architecture)}
   {layer('lighting',A('lighting'),motion,p.architecture)}
   {layer('boat',legacy(life.boat),motion,p.lifeFar)}
   {layer('promenade',legacy(world.promenade),motion,p.promenade)}
   {layer('characters',legacy(life.characters),motion,p.lifeNear)}
   {layer('cat',legacy(life.cat),motion,p.lifeNear)}
   {layer('foreground',legacy(world.foreground),motion,p.foreground)}
   {layer('life-foreground',legacy(life.foreground),motion,p.foreground)}
 </AbsoluteFill>;
};
