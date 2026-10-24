/**
 * Final native-pixel 2D assembly. Source contributions: #32 V2 car,
 * #30 axle-based motion, #33 original V2 world art.
 * The scene contains no debug props, SVG or fallback graphics.
 */
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CarLayer, WHEEL_RADIUS_PX} from './CarLayer';
import {CountrysideWorldLayer} from './WorldLayers';
import {getCountrysideMotion} from './DrivingMotion';

export const CountrysideDrive: React.FC = () => {
 const frame = useCurrentFrame();
 const m = getCountrysideMotion(frame, WHEEL_RADIUS_PX);
 const layers = ['sky','farTrees','midTrees','nearTrees','road','verge'] as const;
 return <AbsoluteFill style={{
   overflow:'hidden', backgroundColor:'#6DB6E5', imageRendering:'pixelated'
 }}>
   {layers.map(layer=><CountrysideWorldLayer key={layer} frame={frame}
     layer={layer} offsetX={layer==='sky'?0:m.offsets[layer]}/>)}
   <CarLayer frame={frame} x={m.carX} wheelContactY={495}
     wheelRotationTurns={m.wheelRotationTurns} bobY={m.bobY}/>
 </AbsoluteFill>;
};
