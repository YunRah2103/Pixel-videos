import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {renderHarborWorld} from '../v3/HarborWorld.mjs';
import {getHarborMotionV4} from './HarborMotionV4.mjs';
import {renderHarborLifeV4} from './HarborLifeV4.mjs';

/**
 * Agent 3's standalone proof. Intentional production boundary:
 * - V3 world is ONLY a temporary painted backdrop.
 * - Agent 1's V4 layers replace it during integration, not in this branch.
 * - Agent 2's V4 light/water slots will replace V3 light/water during integration.
 * - All action belongs to independent sky, water, actor and foreground planes.
 * - No text, transitions, artificial camera shake or global animated CSS.
 */
const WIDTH=360,HEIGHT=640;
const makeSvg=(contents:string)=>'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640" shape-rendering="crispEdges">'+contents+'</svg>';
const inner=(html:string)=>({__html:html});
const layerStyle=(m:any,depth:number):React.CSSProperties=>({
  position:'absolute',left:0,top:0,width:WIDTH,height:HEIGHT,
  transform:'translate('+Number(m.cameraX*depth).toFixed(4)+'px,'+
    Number(m.cameraY*depth).toFixed(4)+'px) scale('+
    Number(1+(m.cameraZoom-1)*depth).toFixed(5)+')',
  transformOrigin:'50% 46%',imageRendering:'pixelated',
  pointerEvents:'none'
});
export const HarborStoryProof:React.FC=()=>{
 const frame=useCurrentFrame();
 const m=getHarborMotionV4(frame);
 const v3=renderHarborWorld(frame,{
   cameraX:m.cameraX*0.25,cameraY:m.cameraY*0.16,
   cameraZoom:1+(m.cameraZoom-1)*0.18,
   cloudDrift:m.cloudDrift,waterMotion:m.waterMotion,
   foliage:m.foliageSway*0.18,lightIntensity:m.lightIntensity
 });
 const life=renderHarborLifeV4(frame,m);
 return <AbsoluteFill style={{width:WIDTH,height:HEIGHT,
     backgroundColor:'#183e56',overflow:'hidden',imageRendering:'pixelated'}}>
   <div style={layerStyle(m,0.55)} dangerouslySetInnerHTML={inner(v3)}/>
   <div style={layerStyle(m,m.parallax.sky)} dangerouslySetInnerHTML={inner(makeSvg(life.birds))}/>
   <div style={layerStyle(m,m.parallax.water)} dangerouslySetInnerHTML={inner(makeSvg(life.water))}/>
   <div style={layerStyle(m,m.parallax.lifeFar)} dangerouslySetInnerHTML={inner(makeSvg(life.boat))}/>
   <div style={layerStyle(m,m.parallax.lifeNear)} dangerouslySetInnerHTML={inner(makeSvg(life.characters))}/>
   <div style={layerStyle(m,m.parallax.lifeNear)} dangerouslySetInnerHTML={inner(makeSvg(life.cat))}/>
   <div style={layerStyle(m,m.parallax.foreground)} dangerouslySetInnerHTML={inner(makeSvg(life.foreground))}/>
 </AbsoluteFill>;
};
