import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {CountrysideWorldProof} from './WorldProof';

const WorldProofRoot: React.FC = () => <Composition id="CountrysideWorldProof"
  component={CountrysideWorldProof} durationInFrames={150} fps={30} width={360} height={640} />;
registerRoot(WorldProofRoot);
