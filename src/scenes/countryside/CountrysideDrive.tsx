/**
 * Countryside V3 motion pass: real PixiJS parallax behind a Remotion native
 * pixel car. All six scenery planes use the actual Agent 1 authored PNGs,
 * while the Agent 2 hero car rolls at exactly the same road distance.
 * No shake, CSS wheel clocks, blur, faux scanlines or generated placeholders.
 */
import React from 'react';
import {AbsoluteFill,useCurrentFrame} from 'remotion';
import {CarLayer,WHEEL_RADIUS_PX} from './CarLayer';
import {PixiCountrysideWorld} from './PixiCountrysideWorld';
import {getCountrysideMotion} from './DrivingMotion';

export const CountrysideDrive:React.FC=()=>{
  const frame=useCurrentFrame();
  const m=getCountrysideMotion(frame,WHEEL_RADIUS_PX);
  // Original artist layering: sky / far / mid / near / 'road','verge'.
  return <AbsoluteFill style={{
    overflow:'hidden',backgroundColor:'#6DB6E5',imageRendering:'pixelated'
  }}>
    <PixiCountrysideWorld frame={frame} motion={m}/>
    <CarLayer frame={frame} x={m.carX} wheelContactY={495}
      wheelRotationTurns={m.wheelRotationTurns} bobY={m.bobY}/>
  </AbsoluteFill>;
};
