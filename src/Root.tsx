import React from 'react';
import {Composition} from 'remotion';
import {SunsetHarbor} from './scenes/SunsetHarbor';
import {SunsetHarborV3} from './scenes/v3/SunsetHarborV3';

export const RemotionRoot: React.FC = () => <>
  <Composition id="SunsetHarbor" component={SunsetHarbor}
    durationInFrames={360} fps={30} width={360} height={640}/>
  <Composition id="SunsetHarborV3" component={SunsetHarborV3}
    durationInFrames={360} fps={30} width={360} height={640}/>
</>;
