/**
 * A real cinematic 12-second pixel-world DRIVE, not the unchanged V2 shot.
 * 0–6.83s: accelerating wide tracking, 6.83–9.03s: native 2x wheel shot,
 * 9.03–12s: wide reveal. Hard integer zoom/cut (no filtered scaling).
 *
 * Runtime PixiJS TilingSprite/Graphics draws all six original art planes.
 * The hero car remains Agent 2's compatible CarLayer.
 */
import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {CarLayer,WHEEL_RADIUS_PX} from './CarLayer';
import {PixiCountrysideWorld} from './PixiCountrysideWorld';
import {getCinematicMotion} from './DrivingMotionV3';
export const CountrysideDrive:React.FC=()=>{
 const frame=useCurrentFrame();
 const m=getCinematicMotion(frame,WHEEL_RADIUS_PX);
 const close=m.shot==='wheel-closeup';
 // Integer 2x wheel-detail tracking: the full native Pixi+React scene is
 // enlarged by an EXACT 2x integer, without shader blur or fractional scale.
 // Normal wide view is 1x; no wobble, shake or CSS transitions.
 const left=close?-2*(m.carX+55-90):0;
 const top=close?-600:0;
 // Preserve the correct world layer order 'road','verge' under the car.
 return <AbsoluteFill style={{
  overflow:'hidden',backgroundColor:'#6DB6E5',imageRendering:'pixelated'
 }}>
  <div style={{
   position:'absolute',left,top,width:360,height:640,
   transform:close?'scale(2)':'none',transformOrigin:'0 0',
   imageRendering:'pixelated',pointerEvents:'none'
  }}>
   <PixiCountrysideWorld frame={frame} motion={m}/>
   <CarLayer frame={frame} x={m.carX} wheelContactY={495}
    wheelRotationTurns={m.wheelRotationTurns} bobY={m.bobY}/>
  </div>
 </AbsoluteFill>;
};
