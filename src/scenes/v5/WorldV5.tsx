import React from 'react';
import {Img, staticFile} from 'remotion';
import {getHarborMotionV4} from '../v4/HarborMotionV4.mjs';

/**
 * Sunset Harbor V5: FIVE separately crop-able, original, hand-authored PIXEL planes.
 * All artwork is drawn at native 360x640 pixel resolution; no filters or external assets.
 * The bundled atlas is 360x3200: far, architecture, harbor, promenade, foreground.
 * Run python3 scripts/generate-v5-world.py to rebuild/edit original pixels.
 * Do NOT duplicate the sky/water/boats/people here: those belong to other agents.
 */
export type WorldPlane = 'far'|'architecture'|'harbor'|'promenade'|'foreground';
export type V5WorldProps = {
  frame:number;
  motion?:any;
  plane:WorldPlane;
};
const INDEX:Record<WorldPlane,number> = {
  far:0, architecture:1, harbor:2, promenade:3, foreground:4
};
const DEPTH:Record<WorldPlane,number> = {
  far:.28,architecture:.55,harbor:.63,promenade:1,foreground:1.28
};
const ART=staticFile('v5/world/world-v5-atlas.png');
const numeric=(v:any,base=0)=>Number.isFinite(v)?Number(v):base;

/**
 * A single 360x640 pixel plane. Parallax may be handled by the final director;
 * in that case pass motion.disableWorldParallax=true and apply external camera
 * once (the isolated V5 proof demonstrates the exact V4-final depth contract).
 * With missing motion we deterministically fall back to the existing V4 motion.
 */
export const V5WorldPlane:React.FC<V5WorldProps>=({frame,motion,plane})=>{
  const safeFrame=Math.max(0,Math.min(359,Math.floor(numeric(frame))));
  const m=motion??getHarborMotionV4(safeFrame);
  const depth=DEPTH[plane];
  const dx=m.disableWorldParallax?0:Math.round(numeric(m.cameraX)*depth);
  const dy=m.disableWorldParallax?0:Math.round(numeric(m.cameraY)*depth);
  const index=INDEX[plane];
  return <div data-v5-world-plane={plane} style={{
    position:'absolute',left:0,top:0,width:360,height:640,overflow:'hidden',
    transform:`translate(${dx}px,${dy}px)`,imageRendering:'pixelated',
    pointerEvents:'none'
  }}>
    <Img src={ART} alt="" draggable={false} style={{
      position:'absolute',top:-640*index,left:0,width:360,height:3200,
      maxWidth:'none',objectFit:'fill',imageRendering:'pixelated'
    }}/>
  </div>;
};
