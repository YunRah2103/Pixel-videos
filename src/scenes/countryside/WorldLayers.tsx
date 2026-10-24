import React from 'react';
import {Img, staticFile} from 'remotion';

/** Agent 2 public environment contract. Coordinates are native 360 × 640 pixels. */
export type CountrysideLayer = 'sky' | 'farTrees' | 'midTrees' | 'nearTrees' | 'verge' | 'road';
export type CountrysideWorldProps = {
  frame: number;
  layer: CountrysideLayer;
  /** Native integer-coordinate translation from Agent 3; NEGATIVE scrolls LEFT. */
  offsetX?: number;
};
export const COUNTRYSIDE_WORLD_TILES = {
  sky: {width: 360, height: 480, y: 0, scrolling: false},
  farTrees: {width: 180, height: 240, y: 240, scrolling: true},
  midTrees: {width: 360, height: 280, y: 200, scrolling: true},
  nearTrees: {width: 360, height: 340, y: 140, scrolling: true},
  verge: {width: 180, height: 160, y: 480, scrolling: true},
  road: {width: 360, height: 160, y: 480, scrolling: true},
} as const;
const FRAME_WIDTH = 360;
const asset = (layer: CountrysideLayer) => staticFile('countryside/world/' + layer + '.png');
/** Coordinates wrapped in integer space. Never produces subpixel painting or tile gaps. */
export function wrapWorldOffset(offsetX: number, tileWidth: number): number {
  if (!Number.isFinite(offsetX)) throw new Error('offsetX must be finite');
  const dx = Math.round(offsetX);
  return ((dx % tileWidth) + tileWidth) % tileWidth;
}
/**
 * Pure pixel-image layer, with no independent clock, internal scrolling or camera.
 * Agent 3 owns offsets; Agent 4 owns z-order and final render.
 */
export const CountrysideWorldLayer: React.FC<CountrysideWorldProps> = ({frame, layer, offsetX = 0}) => {
  if (!Number.isInteger(frame) || frame < 0) throw new Error('frame must be a nonnegative integer');
  const tile = COUNTRYSIDE_WORLD_TILES[layer];
  const common: React.CSSProperties = {
    position: 'absolute', top: 0, width: tile.width, height: tile.height,
    imageRendering: 'pixelated', maxWidth: 'none', pointerEvents: 'none',
  };
  if (!tile.scrolling) {
    return <Img src={asset(layer)} draggable={false} style={{...common, left: 0, top: tile.y}} />;
  }
  const shift = wrapWorldOffset(offsetX, tile.width);
  const firstX = shift - tile.width;
  // Three copies cover any 360-wide viewport for all tile widths, including 180.
  return (
    <div style={{position: 'absolute', left: 0, top: tile.y, width: FRAME_WIDTH,
      height: tile.height, overflow: 'hidden', pointerEvents: 'none'}}>
      {[0, 1, 2].map(i => <Img key={i} src={asset(layer)} draggable={false}
        style={{...common, left: firstX + i * tile.width}} />)}
    </div>
  );
};
