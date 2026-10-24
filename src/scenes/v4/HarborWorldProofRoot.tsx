import React from 'react';
import {Composition} from 'remotion';
import {HarborWorldProof} from './HarborWorldProof';
export const HarborWorldProofRoot:React.FC=()=>(
 <Composition id="HarborWorldV4Proof" component={HarborWorldProof} durationInFrames={360} fps={30} width={360} height={640}/>
);
