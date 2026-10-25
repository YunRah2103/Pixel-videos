import {registerRoot} from 'remotion';
import React from 'react';
import {Composition} from 'remotion';
import {CountrysideMotionProof} from './CountrysideMotionProof';

const MotionProofRoot: React.FC = () =>
  React.createElement(Composition, {
    id: 'CountrysideMotionProof',
    component: CountrysideMotionProof,
    width: 360,
    height: 640,
    fps: 30,
    durationInFrames: 360,
  });

registerRoot(MotionProofRoot);
