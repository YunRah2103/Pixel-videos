import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {sunsetHarborSvg} from '../sunsetHarborSvg.mjs';
import {getHarborMotion} from './HarborMotion.mjs';
import {harborLifeSvg} from './HarborLife.mjs';

/**
 * Agent 2 V3 motion proof; renders against the V2 painting until HarborWorld
 * lands. The motion and life API is intentionally art-independent: Agent 1
 * can replace the underlay with HarborWorld without changing choreography.
 */
export const SunsetHarborV3: React.FC=()=>{
  const frame=useCurrentFrame();
  const motion=getHarborMotion(frame);
  const art=sunsetHarborSvg(frame);
  const life=harborLifeSvg(motion);
  const transform=`translate(${motion.cameraX.toFixed(3)}px,${motion.cameraY.toFixed(3)}px) scale(${motion.cameraZoom.toFixed(5)})`;
  return <AbsoluteFill style={{width:360,height:640,background:'#153c53',overflow:'hidden'}}>
    <div style={{
      width:360,height:640,position:'absolute',inset:0,transform,
      transformOrigin:'50% 48%',imageRendering:'pixelated',willChange:'transform'
    }}>
      <div style={{position:'absolute',inset:0,width:360,height:640,imageRendering:'pixelated'}}
           dangerouslySetInnerHTML={{__html:art}}/>
      <div style={{position:'absolute',inset:0,width:360,height:640,imageRendering:'pixelated'}}
           dangerouslySetInnerHTML={{__html:life}}/>
    </div>
  </AbsoluteFill>;
};
