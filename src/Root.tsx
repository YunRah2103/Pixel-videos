import React from 'react';
import {Composition} from 'remotion';
import {SunsetHarbor} from './scenes/SunsetHarbor';
import {HarborEnvironmentProof} from './scenes/v3/HarborEnvironmentProof';

export const RemotionRoot:React.FC=()=><>
  <Composition id="SunsetHarbor" component={SunsetHarbor} durationInFrames={360} fps={30} width={360} height={640}/>
  <Composition id="HarborEnvironmentProof" component={HarborEnvironmentProof} durationInFrames={360} fps={30} width={360} height={640}/>
</>;
