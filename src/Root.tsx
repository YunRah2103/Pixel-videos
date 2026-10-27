import React from 'react';
import {Composition} from 'remotion';
import {SunsetHarbor} from './scenes/SunsetHarbor';
import {NightDrive, NIGHT_DRIVE_FRAMES} from './scenes/NightDrive';

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
      <Composition
        id="NightDrive"
        component={NightDrive}
        durationInFrames={NIGHT_DRIVE_FRAMES}
        fps={30}
        width={180}
        height={320}
      />
    </>
  );
};
