import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {renderHarborWorld} from './HarborWorld.mjs';
/** Isolated preview: Agent 2's existing animated scene is left alone. */
export const HarborEnvironmentProof:React.FC=()=>{
 const frame=useCurrentFrame(),t=frame/30;
 const svg=renderHarborWorld(frame,{
  cameraX:Math.sin(t*.27)*2.2,cameraY:Math.sin(t*.19)*1.25,
  cloudDrift:t*.85,waterMotion:Math.sin(t*.46)*.12,
  foliage:Math.sin(t*.52)*.12,lightIntensity:1-.055*Math.sin(t*.3),
 });
 return <AbsoluteFill style={{background:'#123e55',overflow:'hidden'}}>
  <div style={{width:360,height:640,imageRendering:'pixelated'}} dangerouslySetInnerHTML={{__html:svg}}/>
 </AbsoluteFill>;
};
