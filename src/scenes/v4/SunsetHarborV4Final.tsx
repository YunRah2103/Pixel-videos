import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {renderHarborBaseLayers} from './HarborWorldV4.mjs';
import {renderHarborFxLayers} from './HarborAtmosphereV4.mjs';
import {getHarborMotionV4} from './HarborMotionV4.mjs';
import {renderHarborLifeV4} from './HarborLifeV4.mjs';

/**
 * SUNSET HARBOR V4 — integrated 360x640 source-stage master.
 *
 * Art ownership remains clear: world paints buildings/terrain, atmosphere paints
 * clouds/sea/light, story paints the ONE travelling boat, actors, cat and birds.
 * All transforms are scene-space, continuous, and derived from Remotion's frame.
 */
const SIZE = {width:360,height:640} as const;
const svg=(raw:string, clipping?:'horizon'|'lights')=>{
  const id=clipping==='horizon'?'v4-horizon-mask':'v4-light-mask';
  const clip=clipping==='horizon'
    ? '<defs><clipPath id="'+id+'"><rect x="0" y="310" width="360" height="48"/></clipPath></defs>'
    : clipping==='lights'
      ? '<defs><clipPath id="'+id+'"><rect x="0" y="410" width="360" height="100"/></clipPath></defs>'
      : '';
  return '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640" shape-rendering="crispEdges">'+
    clip+(clipping?'<g clip-path="url(#'+id+')">'+raw+'</g>':raw)+'</svg>';
};
const layer=(key:string, content:string, motion:any, depth:number, clipping?:'horizon'|'lights')=>{
  if(!content)return null;
  const dx=(motion.cameraX*depth).toFixed(3);
  const dy=(motion.cameraY*depth).toFixed(3);
  const scale=(1+(motion.cameraZoom-1)*depth).toFixed(5);
  const style:React.CSSProperties={
    position:'absolute',left:0,top:0,width:SIZE.width,height:SIZE.height,
    transform:'translate('+dx+'px,'+dy+'px) scale('+scale+')',
    transformOrigin:'50% 46%',imageRendering:'pixelated',pointerEvents:'none'
  };
  return <div key={key} style={style} dangerouslySetInnerHTML={{__html:svg(content,clipping)}}/>;
};

export const SunsetHarborV4Final:React.FC=()=>{
  const frame=useCurrentFrame();
  const motion=getHarborMotionV4(frame);
  // World modules have a small internal camera translation from their proof.
  // Disable it here: the final camera is applied ONCE on each depth plane.
  const world=renderHarborBaseLayers(frame,{...motion,cameraX:0,cameraY:0});
  const fx=renderHarborFxLayers(frame,{
    ...motion,sunX:225,sunY:252,waterTop:353,waterBottom:535,
    drawAtmosphericBirds:false,
    drawAtmosphericBoatWake:false,
    drawLegacyFacadeHighlights:false,
  });
  const life=renderHarborLifeV4(frame,motion);
  const p=motion.parallax;
  return <AbsoluteFill style={{
    ...SIZE,backgroundColor:'#173e5b',overflow:'hidden',imageRendering:'pixelated'
  }}>
    {layer('sky',world.sky,motion,p.sky)}
    {layer('clouds',fx.clouds,motion,p.sky*1.05)}
    {layer('birds',life.birds,motion,p.distant)}
    {layer('distant',world.distant,motion,p.distant)}
    {layer('air',fx.nearAir,motion,p.distant,'horizon')}
    {layer('water',fx.water,motion,p.water)}
    {layer('reflections',fx.waterHighlights,motion,p.water)}
    {layer('wake',life.water,motion,p.lifeFar)}
    {layer('architecture',world.architecture,motion,p.architecture)}
    {layer('harbour',world.harbourStructures,motion,p.architecture)}
    {layer('lighting',fx.illumination,motion,p.architecture,'lights')}
    {layer('boat',life.boat,motion,p.lifeFar)}
    {layer('promenade',world.promenade,motion,p.promenade)}
    {layer('characters',life.characters,motion,p.lifeNear)}
    {layer('cat',life.cat,motion,p.lifeNear)}
    {layer('foreground',world.foreground,motion,p.foreground)}
    {layer('life-foreground',life.foreground,motion,p.foreground)}
  </AbsoluteFill>;
};
