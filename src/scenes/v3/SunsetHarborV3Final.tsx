import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {renderHarborWorld} from './HarborWorld.mjs';
import {getHarborMotion} from './HarborMotion.mjs';
import {harborLifeSvg} from './HarborLife.mjs';

/**
 * V3 FINAL — Agent 1's sculpted environment + Agent 2's timed
 * cinematography and hand-drawn animated life.  No realtime state.
 * Canvas stays native 360 x 640 before x3 nearest-neighbour export.
 */
export const SunsetHarborV3Final: React.FC = () => {
  const frame = useCurrentFrame();
  const m = getHarborMotion(frame);
  const world = renderHarborWorld(frame, {
    cameraX: m.cameraX * 0.6,
    cameraY: m.cameraY * 0.6,
    cameraZoom: 1 + (m.cameraZoom - 1) * 0.35,
    cloudDrift: m.cloudDrift,
    waterMotion: Math.sin(m.waterPhase * 0.55) * 0.2,
    foliage: m.foliageSway * 0.16,
    lightIntensity: 0.96 + (m.lightIntensity - 0.82) * 0.45,
  });
  const life = harborLifeSvg(m);
  const transform = `translate(${m.cameraX.toFixed(3)}px,${m.cameraY.toFixed(3)}px) scale(${m.cameraZoom.toFixed(5)})`;
  return <AbsoluteFill style={{width:360,height:640,background:'#123e55',overflow:'hidden'}}>
    <div style={{position:'absolute',inset:0,width:360,height:640,transform,
      transformOrigin:'50% 48%',imageRendering:'pixelated'}}>
      <div style={{position:'absolute',inset:0,width:360,height:640,
        imageRendering:'pixelated'}} dangerouslySetInnerHTML={{__html:world}}/>
      <div style={{position:'absolute',inset:0,width:360,height:640,
        imageRendering:'pixelated'}} dangerouslySetInnerHTML={{__html:life}}/>
    </div>
  </AbsoluteFill>;
};
