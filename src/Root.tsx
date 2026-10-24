import React from 'react';
import {Composition} from 'remotion';
import {SunsetHarbor} from './scenes/SunsetHarbor';
import {HarborEnvironmentProof} from './scenes/v3/HarborEnvironmentProof';
import {SunsetHarborV3} from './scenes/v3/SunsetHarborV3';
import {SunsetHarborV3Final} from './scenes/v3/SunsetHarborV3Final';
import {SunsetHarborV4Final} from './scenes/v4/SunsetHarborV4Final';
import {SunsetHarborV5Final} from './scenes/v5/SunsetHarborV5Final';

export const RemotionRoot:React.FC=()=><>
  <Composition id="SunsetHarbor" component={SunsetHarbor} durationInFrames={360} fps={30} width={360} height={640}/>
  <Composition id="HarborEnvironmentProof" component={HarborEnvironmentProof} durationInFrames={360} fps={30} width={360} height={640}/>
  <Composition id="SunsetHarborV3" component={SunsetHarborV3} durationInFrames={360} fps={30} width={360} height={640}/>
  <Composition id="SunsetHarborV3Final" component={SunsetHarborV3Final} durationInFrames={360} fps={30} width={360} height={640}/>
  <Composition id="SunsetHarborV4Final" component={SunsetHarborV4Final} durationInFrames={360} fps={30} width={360} height={640}/>
  <Composition id="SunsetHarborV5Final" component={SunsetHarborV5Final} durationInFrames={360} fps={30} width={360} height={640}/>
</>;
