import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {renderHarborWorld} from '../v3/HarborWorld.mjs';
import {getHarborMotion} from '../v3/HarborMotion.mjs';
import {harborLifeSvg} from '../v3/HarborLife.mjs';
import {renderHarborFxLayers} from './HarborAtmosphereV4.mjs';

/**
 * V4 Agent 2 isolated proof. V3 is a *temporary* backdrop: Agent 1's eventual
 * scene should insert the raw FX strings in proper painter's order instead.
 * Does not change Root, any other agent's source or the established soundtrack.
 */
const makeSvg=(body:string,clip?:string,id='v4GenericMask')=>'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640" shape-rendering="crispEdges">'+(clip?'<defs><clipPath id="'+id+'">'+clip+'</clipPath></defs><g clip-path="url(#'+id+')">'+body+'</g>':body)+'</svg>';
const skyMask='<rect x="0" y="0" width="360" height="234"/>';
const waterMask='<rect x="0" y="353" width="360" height="182"/>';
const shoreMask='<rect x="0" y="490" width="360" height="150"/><rect x="0" y="235" width="152" height="206"/><rect x="270" y="251" width="90" height="182"/>';
const stripRoot=(svg:string)=>svg.replace(/^<svg[^>]*>/,'').replace(/<\/svg>\s*$/,'');
const layerStyle:React.CSSProperties={position:'absolute',inset:0,width:360,height:640,imageRendering:'pixelated'};
const SvgLayer:React.FC<{svg:string}>=({svg})=><div style={layerStyle} dangerouslySetInnerHTML={{__html:svg}}/>;

export const HarborAtmosphereProof:React.FC=()=>{
 const f=useCurrentFrame();
 const m=getHarborMotion(f);
 const art=renderHarborWorld(f,{
  cameraX:m.cameraX*.6,cameraY:m.cameraY*.6,
  cameraZoom:1+(m.cameraZoom-1)*.35,
  cloudDrift:m.cloudDrift,waterMotion:Math.sin(m.waterPhase*.55)*.2,
  foliage:m.foliageSway*.16,lightIntensity:.96+(m.lightIntensity-.82)*.45,
 });
 const fx=renderHarborFxLayers(f,m);
 const transform='translate('+m.cameraX.toFixed(3)+'px,'+m.cameraY.toFixed(3)+'px) scale('+m.cameraZoom.toFixed(5)+')';
 const clouds=makeSvg(fx.clouds,skyMask,'v4SkyMask');
 const water=makeSvg(fx.water+fx.waterHighlights,waterMask,'v4SeaMask');
 // Restore the original foreground, buildings and dock furniture over the new
 // sky/sea, because V3 exports a flattened SVG instead of independent layers.
 const shore=makeSvg(stripRoot(art),shoreMask,'v4ShoreMask');
 const atmosphere=makeSvg(fx.nearAir);
 const light=makeSvg(fx.illumination);
 return <AbsoluteFill style={{width:360,height:640,background:'#123e55',overflow:'hidden'}}>
  <div style={{...layerStyle,transform,transformOrigin:'50% 48%'}}>
   <SvgLayer svg={art}/>
   <SvgLayer svg={clouds}/>
   <SvgLayer svg={water}/>
   <SvgLayer svg={shore}/>
   <SvgLayer svg={atmosphere}/>
   <SvgLayer svg={harborLifeSvg(m)}/>
   <SvgLayer svg={light}/>
  </div>
 </AbsoluteFill>;
};
