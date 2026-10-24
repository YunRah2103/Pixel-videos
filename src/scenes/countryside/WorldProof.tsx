import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CountrysideWorldLayer, type CountrysideLayer} from './WorldLayers';

/** Standalone 5s proof; offsets are TEST INPUTS, never part of production layer. */
const bands: Array<{layer: CountrysideLayer; nativePxPerFrame: number}> = [
  {layer: 'farTrees', nativePxPerFrame: 0.43},
  {layer: 'midTrees', nativePxPerFrame: 0.95},
  {layer: 'nearTrees', nativePxPerFrame: 1.84},
  {layer: 'verge', nativePxPerFrame: 2.48},
  {layer: 'road', nativePxPerFrame: 2.88},
];
export const CountrysideWorldProof: React.FC = () => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{backgroundColor: '#739D53'}}>
    <CountrysideWorldLayer frame={frame} layer="sky" />
    {bands.map(({layer, nativePxPerFrame}) => (
      <CountrysideWorldLayer key={layer} frame={frame} layer={layer}
        offsetX={-Math.round(frame * nativePxPerFrame)} />
    ))}
  </AbsoluteFill>;
};
