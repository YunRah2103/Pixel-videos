import React from 'react';
import {Composition} from 'remotion';
import {SunsetHarbor} from './scenes/SunsetHarbor';
import {NeonStreet} from './scenes/NeonStreet';

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
      <Composition id="NeonStreet" component={NeonStreet} durationInFrames={246} fps={30} width={720} height={720} />
    </>
  );
};
