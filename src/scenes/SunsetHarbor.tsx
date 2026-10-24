import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';

/**
 * Original, deterministic, frame-addressable pixel-art scene.
 * Native resolution: 360×640. Export low-res, then integer-upscale in FFmpeg.
 * All motion is derived from `frame`, never wall-clock time or random state.
 */
const SKY = [
  '#213a65', '#2a426e', '#324b79', '#405580', '#4d5b83', '#5b638a',
  '#6b6b94', '#7a7399', '#8f7898', '#a58099', '#b8879a', '#cd9296',
  '#db9e92', '#e6aa94', '#eeb49a', '#f4c09e', '#f5c99e', '#f4d0ac',
];
const pix = (x: number, y: number, w: number, h: number, fill: string, key?: string) =>
  <rect key={key} x={Math.round(x)} y={Math.round(y)} width={w} height={h} fill={fill} />;

const Cloud: React.FC<{x: number; y: number; scale?: number; shadow?: boolean}> = ({x, y, scale = 1, shadow = false}) => {
  const c = shadow ? '#9c7096' : '#f6c2ae';
  const d = shadow ? '#725e86' : '#d997a3';
  return <g transform={`translate(${Math.round(x)},${Math.round(y)}) scale(${scale})`}>
    {pix(0, 8, 76, 13, d)}{pix(15, 3, 51, 16, c)}{pix(24, -5, 31, 16, c)}
    {pix(9, 18, 90, 7, d)}{pix(39, 19, 56, 5, '#a67c9c')}
    {pix(68, 5, 21, 12, c)}{pix(86, 12, 16, 8, d)}
  </g>;
};

const House: React.FC<{x: number; baseY: number; w: number; h: number; fill: string; light?: string}> = ({x, baseY, w, h, fill, light = '#e9b989'}) => {
  const y = baseY - h;
  const cols = Math.max(1, Math.floor((w - 6) / 9));
  return <g>
    {pix(x, y, w, h, fill)}
    {pix(x - 3, y - 4, w + 6, 4, '#394b69')}
    {Array.from({length: Math.max(1, Math.floor((h - 12) / 12))}, (_, row) =>
      Array.from({length: cols}, (_, col) => {
        const lit = (Math.floor(x) + row * 3 + col * 5) % 4 !== 0;
        return pix(x + 5 + col * 9, y + 8 + row * 12, 3, 5, lit ? light : '#49627e', `${x}-${row}-${col}`);
      }),
    )}
  </g>;
};

const SunsetHarborArt: React.FC<{frame: number}> = ({frame}) => {
  const wave = (n: number) => Math.sin(frame * 0.055 + n * 2.17);
  const clouds = frame * 0.14;
  const boatX = Math.round(385 - (frame * 1.05) % 550);
  return <svg viewBox="0 0 360 640" width="100%" height="100%" style={{display: 'block', imageRendering: 'pixelated'}} shapeRendering="crispEdges">
    {pix(0, 0, 360, 640, '#233d65')}
    {SKY.map((color, i) => pix(0, i * 19, 360, 20, color, `sky-${i}`))}
    {Array.from({length: 46}, (_, i) => {
      const hash = (i * 1103515245 + 12345) >>> 0;
      const x = hash % 355;
      const y = 8 + (Math.floor(hash / 997) % 160);
      const bright = Math.sin(frame * 0.04 + i) > 0.4;
      return pix(x, y, bright ? 2 : 1, 1, i % 3 === 0 ? '#f9d5c4' : '#839ab4', `star-${i}`);
    })}
    {/* Diffuse sunset halo, rendered in stepped blocks rather than gradient blur */}
    {[48, 40, 32, 23, 16].map((r, i) => pix(279 - r, 243 - r, r * 2, r * 2, ['#f6c1a0','#f6c6a1','#fad2a9','#ffdfb5','#ffe9c2'][i], `sun-${i}`))}
    <Cloud x={-36 - clouds * 0.48} y={132} scale={1.65} shadow />
    <Cloud x={150 - clouds * 0.35} y={75} scale={0.95} />
    <Cloud x={245 - clouds * 0.65} y={179} scale={1.3} shadow />
    <Cloud x={-70 + (frame * 0.085) % 500} y={228} scale={0.8} />
    {/* Distant forested ridgeline */}
    <path d="M0 332 L20 319 L43 325 L64 304 L88 324 L115 300 L135 313 L166 292 L185 312 L216 290 L245 308 L270 295 L299 309 L329 302 L360 314 V406 H0Z" fill="#646f8d" />
    <path d="M0 359 L34 337 L58 349 L77 338 L111 355 L147 327 L172 342 L195 321 L240 349 L269 332 L300 354 L332 340 L360 357 V416 H0Z" fill="#425f7d" />
    {/* Water and atmospheric horizon */}
    {pix(0, 355, 360, 180, '#386584')}
    {Array.from({length: 19}, (_, i) => pix(0, 359 + i * 9, 360, 3, i % 3 === 0 ? '#4c7890' : '#35607f', `water-band-${i}`))}
    {Array.from({length: 100}, (_, i) => {
      const y = 362 + (i * 17) % 171;
      const x = ((i * 79 + Math.round(frame * ((i % 4) + 1) * 0.3)) % 393) - 20;
      const reflected = x > 222 && x < 318;
      return pix(x, y, reflected ? 13 : 6 + i % 8, 1 + i % 2, reflected ? (i % 2 ? '#e7b38f' : '#dba398') : '#7092a2', `ripple-${i}`);
    })}
    {/* Quaint shore buildings */}
    <House x={-5} baseY={375} w={38} h={71} fill="#475d79" />
    <House x={29} baseY={371} w={40} h={92} fill="#3e5675" />
    <House x={70} baseY={372} w={32} h={55} fill="#4a6080" />
    <House x={98} baseY={379} w={44} h={104} fill="#435674" />
    <House x={139} baseY={373} w={26} h={65} fill="#4b6380" />
    <House x={168} baseY={376} w={49} h={78} fill="#445875" />
    <House x={218} baseY={382} w={27} h={55} fill="#51657d" />
    <House x={253} baseY={376} w={42} h={74} fill="#445a77" />
    <House x={301} baseY={378} w={62} h={94} fill="#455773" />
    {pix(0, 375, 360, 8, '#344d6a')}
    {/* Small boat passing slowly across the harbour */}
    <g transform={`translate(${boatX},0)`}>
      {pix(0, 428, 55, 5, '#263f5b')}{pix(9, 433, 35, 4, '#243950')}
      {pix(16, 407, 24, 20, '#d4b0a0')}{pix(18, 404, 19, 3, '#e8c5b0')}
      {pix(26, 390, 3, 17, '#263f5b')}{pix(31, 411, 5, 5, '#6b8ba2')}
    </g>
    {/* Foreground promenade / seaside platform */}
    {pix(0, 510, 360, 130, '#344054')}
    {pix(0, 507, 360, 9, '#73808b')}
    {pix(0, 515, 360, 4, '#485b6a')}
    {Array.from({length: 16}, (_, i) => pix(i * 27 - 8, 548 + (i % 3) * 3, 23, 1, '#506077', `plank-${i}`))}
    {pix(0, 479, 360, 5, '#7c7584')}
    {Array.from({length: 11}, (_, i) => <g key={`rail-${i}`}>
      {pix(i * 36 + 7, 482, 4, 31, '#5d6776')}
      {pix(i * 36 + 7, 475, 5, 6, '#958b95')}
    </g>)}
    {/* Light pole with warm pixel-art lamp */}
    {pix(65, 425, 5, 85, '#313c55')}{pix(53, 426, 29, 5, '#475671')}
    {pix(54, 432, 24, 4, '#bba68d')}{pix(58, 436, 16, 6, '#ffdfad')}
    {pix(60, 442, 12, 3, '#e9b38d')}
    {pix(53, 444, 27, 2, '#736b78')}
    {/* A quiet person waiting by the water */}
    <g transform={`translate(${207 + Math.round(wave(2) * 1)},0)`}>
      {pix(4, 442, 10, 10, '#e6b7a1')}{pix(2, 440, 13, 5, '#30334c')}
      {pix(0, 454, 18, 25, '#293c59')}{pix(3, 479, 5, 31, '#252f45')}{pix(11, 479, 5, 31, '#252f45')}
      {pix(-3, 460, 5, 18, '#293c59')}{pix(17, 460, 5, 16, '#293c59')}
    </g>
    {/* Wind-blown foliage / reeds in the foreground */}
    {Array.from({length: 45}, (_, i) => {
      const x = (i * 83) % 360;
      const height = 10 + (i * 13) % 25;
      const dx = Math.round(Math.sin(frame * 0.05 + i) * 2);
      return <g key={`grass-${i}`}>
        {pix(x, 639 - height, 2, height, i % 2 ? '#335b5d' : '#476a63')}
        {pix(x + dx + 1, 635 - height, 5, 4, i % 3 ? '#50796c' : '#78987d')}
      </g>;
    })}
    {pix(0, 631, 360, 9, '#283b48')}
  </svg>;
};

export const SunsetHarbor: React.FC = () => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{backgroundColor: '#213a65', overflow: 'hidden'}}>
    <SunsetHarborArt frame={frame} />
  </AbsoluteFill>;
};
