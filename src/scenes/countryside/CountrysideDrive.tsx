/**
 * Agent 4 owns orchestration only. These three components MUST be the actual
 * authored specialist outputs from issues #21, #22 and #23; no placeholder art.
 * Native 360x640 @30fps. Final 3x nearest-neighbour upscale happens in FFmpeg.
 */
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CarLayer} from './CarLayer';
import {CountrysideWorldLayer} from './WorldLayers';
import {getCountrysideMotion} from './DrivingMotion';

export const CountrysideDrive: React.FC = () => {
  const frame = useCurrentFrame();
  const motion = getCountrysideMotion(frame);
  // One and only one source for offsets; WorldLayers must not add its own scroll.
  const offsets = motion.offsets;
  const layers = ['sky', 'farTrees', 'midTrees', 'nearTrees', 'verge', 'road'] as const;
  return (
    <AbsoluteFill style={{
      overflow: 'hidden',
      backgroundColor: '#6DB6E5',
      imageRendering: 'pixelated'
    }}>
      {layers.map((layer) =>
        <CountrysideWorldLayer
          key={layer}
          frame={frame}
          layer={layer}
          offsetX={layer === 'sky' ? 0 : Math.round(offsets[layer])}
        />
      )}
      <CarLayer
        frame={frame}
        x={Math.round(motion.carX)}
        wheelContactY={495 + Math.round(motion.bobY)}
      />
    </AbsoluteFill>
  );
};
