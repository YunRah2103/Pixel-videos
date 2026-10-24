import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {V5WorldPlane,WorldPlane} from './WorldV5';
import {renderHarborBaseLayers} from '../v4/HarborWorldV4.mjs';
import {renderHarborFxLayers} from '../v4/HarborAtmosphereV4.mjs';
import {renderHarborLifeV4} from '../v4/HarborLifeV4.mjs';
import {getHarborMotionV4} from '../v4/HarborMotionV4.mjs';

// Isolated film-quality proof: same V4 sky, ocean, lighting, life and camera;
// the five V4 world planes are completely REPLACED by the V5 illustrated atlas.
const SIZE={width:360,height:640};
const rawSvg=(raw:string,clipping?:'horizon'|'lights')=>{
  const id=clipping==='horizon'?'v5-air-clip':'v5-lamp-clip';
  const defs=clipping?'<defs><clipPath id="'+id+'"><rect x="0" y="'+(clipping==='horizon'?'310':'410')+'" width="360" height="'+(clipping==='horizon'?'48':'100')+'"/></clipPath></defs>':'';
  return '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640" shape-rendering="crispEdges">'+defs+(clipping?'<g clip-path="url(#'+id+')">'+raw+'</g>':raw)+'</svg>';
};
const cameraStyle=(m:any,depth:number):React.CSSProperties=>({
  position:'absolute',left:0,top:0,width:360,height:640,
  transform:'translate('+(m.cameraX*depth).toFixed(3)+'px,'+(m.cameraY*depth).toFixed(3)+'px) scale('+(1+(m.cameraZoom-1)*depth).toFixed(5)+')',
  transformOrigin:'50% 46%',imageRendering:'pixelated',pointerEvents:'none'
});
const fxPlane=(key:string,raw:string,m:any,depth:number,clip?:'horizon'|'lights')=>
  raw?<div key={key} style={cameraStyle(m,depth)} dangerouslySetInnerHTML={{__html:rawSvg(raw,clip)}}/>:null;
const artPlane=(key:WorldPlane,m:any,depth:number,frame:number)=>
  <div key={'v5-'+key} style={cameraStyle(m,depth)}>
    <V5WorldPlane plane={key} frame={frame} motion={{...m,disableWorldParallax:true}}/>
  </div>;
export const WorldV5Proof:React.FC=()=>{
  const frame=useCurrentFrame();
  const m=getHarborMotionV4(frame);
  const p=m.parallax;
  const world=renderHarborBaseLayers(frame,{...m,cameraX:0,cameraY:0});
  const fx=renderHarborFxLayers(frame,{...m,sunX:225,sunY:252,waterTop:353,waterBottom:535,
    drawAtmosphericBirds:false,drawAtmosphericBoatWake:false,drawLegacyFacadeHighlights:false});
  const life=renderHarborLifeV4(frame,m);
  return <AbsoluteFill style={{...SIZE,backgroundColor:'#173e5b',overflow:'hidden',imageRendering:'pixelated'}}>
    {fxPlane('sky',world.sky,m,p.sky)}
    {fxPlane('clouds',fx.clouds,m,p.sky*1.05)}
    {fxPlane('birds',life.birds,m,p.distant)}
    {artPlane('far',m,p.distant,frame)}
    {fxPlane('air',fx.nearAir,m,p.distant,'horizon')}
    {fxPlane('water',fx.water,m,p.water)}
    {fxPlane('reflections',fx.waterHighlights,m,p.water)}
    {fxPlane('wake',life.water,m,p.lifeFar)}
    {artPlane('architecture',m,p.architecture,frame)}
    {artPlane('harbor',m,p.architecture,frame)}
    {fxPlane('lighting',fx.illumination,m,p.architecture,'lights')}
    {fxPlane('boat',life.boat,m,p.lifeFar)}
    {artPlane('promenade',m,p.promenade,frame)}
    {fxPlane('characters',life.characters,m,p.lifeNear)}
    {fxPlane('cat',life.cat,m,p.lifeNear)}
    {artPlane('foreground',m,p.foreground,frame)}
    {fxPlane('life-foreground',life.foreground,m,p.foreground)}
  </AbsoluteFill>;
};