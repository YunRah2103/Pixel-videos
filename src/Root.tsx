import React from 'react';
import {Composition} from 'remotion';
import {SunsetHarbor} from './scenes/SunsetHarbor';

export const RemotionRoot: React.FC = () => <Composition
  id="SunsetHarbor" component={SunsetHarbor} durationInFrames={360}
  fps={30} width={360} height={640}
/>;