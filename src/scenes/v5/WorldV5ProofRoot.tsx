import React from 'react';
import {Composition} from 'remotion';
import {WorldV5Proof} from './WorldV5Proof';
export const V5WorldProofRoot:React.FC=()=>(
  <Composition id="WorldV5Proof" component={WorldV5Proof}
    durationInFrames={360} fps={30} width={360} height={640}/>
);