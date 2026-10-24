import React from 'react';
import {Composition} from 'remotion';
import {SunsetHarbor} from './scenes/SunsetHarbor';

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SunsetHarbor"
        component={SunsetHarbor}
        durationInFrames={240}
        fps={30}
        width={360}
        height={640}
      />
    </>
  );
};
