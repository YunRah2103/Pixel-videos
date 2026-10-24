import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {sunsetHarborSvg} from './sunsetHarborSvg.mjs';

/** V2: frame-addressable original pixel painting, 360 x 640 native canvas. */
export const SunsetHarbor: React.FC = () => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{backgroundColor:'#123e56',overflow:'hidden'}}>
    <div style={{width:360,height:640,imageRendering:'pixelated'}}
         dangerouslySetInnerHTML={{__html:sunsetHarborSvg(frame)}} />
  </AbsoluteFill>;
};