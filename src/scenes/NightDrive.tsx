import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {BACKDROP, CHARS, GRID, PALETTE, PASSENGER_BOX, PASSENGER_TIMELINE, PASSENGER_VARIANTS} from './nightDriveData';
import {ADVANCE, GLYPHS} from './pixelFont';

/**
 * Night drive: a still pixel-art street scene (backdrop traced into nightDriveData.ts),
 * two animated passengers and word-by-word lyric captions with a decaying wobble.
 * Native resolution: 180×320. Export low-res, then integer-upscale 6× in FFmpeg.
 * All motion is derived from `frame`.
 */
type Word = {text: string; frame: number; retrigger?: number[]};
type Caption = {from: number; to: number; lines: Word[][]};

const w = (text: string, frame: number, retrigger?: number[]): Word => ({text, frame, retrigger});

const CAPTIONS: Caption[] = [
  {from: 5, to: 57, lines: [[w('MAKING', 5), w('MY', 12)], [w('WAY', 17), w('DOWNTOWN', 27)]]},
  {from: 57, to: 122, lines: [[w('WALKING', 57), w('FAST.', 72)], [w('FACES', 92), w('PASS', 110)]]},
  {from: 122, to: 155, lines: [[w('AND', 122), w("I'M", 127), w('HOMEBOUND', 132)]]},
  {from: 155, to: 212, lines: [
    [w('TI', 155), w('DI', 160), w('DI', 165)],
    [w('DI', 170), w('DI', 175), w('DI', 180), w('DIN', 185)],
  ]},
  {from: 212, to: 235, lines: [[w('DU', 212), w('DU', 217), w('DU', 222), w('DU', 227)]]},
  {from: 275, to: 310, lines: [[w('AND', 275), w('I', 280), w('NEED', 290), w('YOU', 300)]]},
  {from: 347, to: 385, lines: [[w('AND', 347), w('I', 352), w('MISS', 362), w('YOU', 372)]]},
  {from: 427, to: Infinity, lines: [[w('AND', 427), w('NOW', 440), w('I', 450), w('WONDER', 457, [500])]]},
];

const TICK = 2.5; // captions animate at 12fps
const WAVE_AMPLITUDE = [1, 1, 0.85, 0.85, 0.65, 0.55, 0.4];

/** Per-letter vertical wobble: a tilting ramp that flips every tick and fades out. */
const wobble = (word: Word, letter: number, frame: number): number => {
  const n = word.text.length;
  const base = (letter - (n - 1) / 2) * 0.875;
  for (const start of [word.frame, ...(word.retrigger ?? [])]) {
    const tick = Math.floor((frame - start) / TICK);
    if (tick < 0 || tick >= WAVE_AMPLITUDE.length) continue;
    return Math.round(WAVE_AMPLITUDE[tick] * ((tick % 2 ? -base : base) + 0.45));
  }
  return 0;
};

const lineWidth = (text: string): number => {
  const last = GLYPHS[text[text.length - 1]];
  return ADVANCE * (text.length - 1) + (last ? last.dx + last.rows[0].length : 0);
};

type Runs = Record<string, string>;
const addRun = (acc: Runs, color: string, x: number, y: number, len: number) => {
  acc[color] = (acc[color] ?? '') + `M${x} ${y}h${len}v1h-${len}z`;
};
const paths = (runs: Runs, prefix: string) =>
  Object.entries(runs).map(([color, d]) => <path key={`${prefix}${color}`} d={d} fill={color} />);

/** Collapse an indexed pixel grid into one path per colour of horizontal runs. */
const encode = (rows: string[], ox: number, oy: number): Runs => {
  const acc: Runs = {};
  rows.forEach((row, y) => {
    let x = 0;
    while (x < row.length) {
      let end = x + 1;
      while (end < row.length && row[end] === row[x]) end++;
      addRun(acc, PALETTE[CHARS.indexOf(row[x])], ox + x, oy + y, end - x);
      x = end;
    }
  });
  return acc;
};

const BACKDROP_PATHS = paths(encode(BACKDROP, 0, 0), 'bg');
const passengerCache = new Map<number, React.ReactNode>();
const passengers = (variant: number) => {
  let node = passengerCache.get(variant);
  if (!node) {
    const {w: bw, h: bh, x, y} = PASSENGER_BOX;
    const v = PASSENGER_VARIANTS[variant];
    const rows = Array.from({length: bh}, (_, r) => v.slice(r * bw, (r + 1) * bw));
    node = paths(encode(rows, x, y), `p${variant}-`);
    passengerCache.set(variant, node);
  }
  return node;
};

const passengerVariant = (frame: number): number => {
  let left = frame;
  for (const [variant, length] of PASSENGER_TIMELINE) {
    if (left < length) return variant;
    left -= length;
  }
  return PASSENGER_TIMELINE[PASSENGER_TIMELINE.length - 1][0];
};

const CaptionLayer: React.FC<{frame: number}> = ({frame}) => {
  const caption = CAPTIONS.find((c) => frame >= c.from && frame < c.to);
  if (!caption) return null;
  const runs: Runs = {};
  const top = caption.lines.length === 1 ? 111 : 103;
  caption.lines.forEach((words, row) => {
    const full = words.map((word) => word.text).join(' ');
    const x0 = Math.floor((GRID.width - lineWidth(full)) / 2 + 0.5);
    let cell = 0;
    words.forEach((word, i) => {
      if (i > 0) cell++; // the space between words
      [...word.text].forEach((ch, letter) => {
        const glyph = GLYPHS[ch];
        if (glyph && frame >= word.frame) {
          const y = top + row * 16 + glyph.dy + wobble(word, letter, frame);
          glyph.rows.forEach((bits, r) => {
            for (let c = 0; c < bits.length; c++) {
              if (bits[c] === '#') addRun(runs, '#ffffff', x0 + cell * ADVANCE + glyph.dx + c, y + r, 1);
            }
          });
        }
        cell++;
      });
    });
  });
  return <>{paths(runs, 'cap')}</>;
};

export const NightDrive: React.FC = () => {
  const frame = useCurrentFrame();
  return <AbsoluteFill style={{backgroundColor: '#062033'}}>
    <svg viewBox={`0 0 ${GRID.width} ${GRID.height}`} width="100%" height="100%" style={{display: 'block', imageRendering: 'pixelated'}} shapeRendering="crispEdges">
      {BACKDROP_PATHS}
      {passengers(passengerVariant(frame))}
      <CaptionLayer frame={frame} />
    </svg>
  </AbsoluteFill>;
};

export const NIGHT_DRIVE_FRAMES = 527;
