import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {renderHarborBaseLayers} from '../v4/HarborWorldV4.mjs';
import {renderHarborFxLayers} from '../v4/HarborAtmosphereV4.mjs';
import {getV5Motion} from './MotionV5.mjs';
import {V5StoryPlane,type V5StoryPlaneName} from './StoryV5';

/**
 * Isolated proof: V4 finished environment + V4 atmosphere + NEW V5 story.
 * Shared Root.tsx remains untouched. Agent 4 can substitute V5 world/fx.
 */
const W=360,H=640;
const wrap=(raw:string,clip?:'horizon'|'lights')=>{
 const id=clip==='horizon'?'v5-air-mask':'v5-light-mask';
 const mask=clip==='horizon'
  ?'<defs><clipPath id="'+id+'"><rect x="0" y="310" width="360" height="48"/></clipPath></defs>'
  :clip==='lights'
    ?'<defs><clipPath id="'+id+'"><rect x="0" y="410" width="360" height="100"/></clipPath></defs>':'';
 return '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640" shape-rendering="crispEdges">'+mask+
 (clip?'<g clip-path="url(#'+id+')">'+raw+'</g>':raw)+'</svg>';
};
const position=(m:any,d:number):React.CSSProperties=>({
 position:'absolute',left:0,top:0,width:W,height:H,
 transform:'translate('+Number(m.cameraX*d).toFixed(3)+'px,'+
 Number(m.cameraY*d).toFixed(3)+'px) scale('+
 Number(1+(m.cameraZoom-1)*d).toFixed(5)+')',
 transformOrigin:'50% 46%',pointerEvents:'none',imageRendering:'pixelated'
});
const sceneLayer=(id:string,content:string,m:any,d:number,clip?:'horizon'|'lights')=>
 content?<div key={id} style={position(m,d)} dangerouslySetInnerHTML={{__html:wrap(content,clip)}}/>:null;
const actorLayer=(id:V5StoryPlaneName,f:number,m:any,d:number)=>
 <div key={id} style={position(m,d)}>
  <V5StoryPlane frame={f} motion={m} plane={id}/>
 </div>;
export const SunsetHarborV5StoryProof:React.FC=()=>{
 const f=useCurrentFrame(),m=getV5Motion(f),p=m.parallax;
 const base=renderHarborBaseLayers(f,{...m,cameraX:0,cameraY:0});
 const fx=renderHarborFxLayers(f,{...m,sunX:225,sunY:252,
  waterTop:353,waterBottom:535,drawAtmosphericBirds:false,
  drawAtmosphericBoatWake:false,drawLegacyFacadeHighlights:false});
 return <AbsoluteFill style={{width:W,height:H,backgroundColor:'#193f59',overflow:'hidden',imageRendering:'pixelated'}}>
  {sceneLayer('sky',base.sky,m,p.sky)}
  {sceneLayer('clouds',fx.clouds,m,p.sky*1.05)}
  {actorLayer('birds',f,m,p.distant)}
  {sceneLayer('distant',base.distant,m,p.distant)}
  {sceneLayer('air',fx.nearAir,m,p.distant,'horizon')}
  {sceneLayer('water',fx.water,m,p.water)}
  {sceneLayer('reflections',fx.waterHighlights,m,p.water)}
  {actorLayer('waterInteraction',f,m,p.lifeFar)}
  {sceneLayer('architecture',base.architecture,m,p.architecture)}
  {sceneLayer('harbour',base.harbourStructures,m,p.architecture)}
  {sceneLayer('lighting',fx.illumination,m,p.architecture,'lights')}
  {actorLayer('boat',f,m,p.lifeFar)}
  {sceneLayer('promenade',base.promenade,m,p.promenade)}
  {actorLayer('characters',f,m,p.lifeNear)}
  {actorLayer('cat',f,m,p.lifeNear)}
  {sceneLayer('foreground',base.foreground,m,p.foreground)}
  {actorLayer('foregroundLife',f,m,p.foreground)}
 </AbsoluteFill>;
};
