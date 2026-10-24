/**
 * Countryside Drive's single source of frame-exact native-pixel motion.
 *
 * One 360-frame cycle at 30 fps; neither wall-clock time nor scene-side scroll.
 * Pass offsets directly to CountrysideWorldLayer({layer, offsetX}).
 * Native integer pixels: do not CSS-scale, ease or round these again.
 */
export const COUNTRYSIDE_FRAMES = 360;
export const COUNTRYSIDE_FPS = 30;
export const COUNTRYSIDE_NATIVE_WIDTH = 360;
export const COUNTRYSIDE_WHEEL_CONTACT_Y = 495;

/**
 * All phases return to their original tile positions after 360 frames.
 * Agent 2 should author tiles with these periods (or integer divisors).
 * Each frame's movement is rounded to an exact native pixel.
 */
export const COUNTRYSIDE_LAYER_SPEC = {
  farTrees: {pixelsPerFrame: 0.5, periodPx: 180},
  midTrees: {pixelsPerFrame: 1, periodPx: 360},
  nearTrees: {pixelsPerFrame: 2, periodPx: 360},
  verge: {pixelsPerFrame: 2.5, periodPx: 180},
  road: {pixelsPerFrame: 3, periodPx: 360},
} as const;

export type CountrysideMovingLayer = keyof typeof COUNTRYSIDE_LAYER_SPEC;
export type CountrysideOffsets = Record<CountrysideMovingLayer, number>;

/**
 * A ~19px-diameter pixel wheel covers 1080px of travel in exactly 18 turns.
 * This is an initial design radius, NOT a claimed measurement of Agent 1 art.
 * Replace via wheelRadiusPx when Agent 1 reports the measured contact radius.
 */
export const DEFAULT_WHEEL_RADIUS_PX = 1080 / (2 * Math.PI * 18);

export interface CountrysideMotion {
  frame: number;
  cycleFrame: number;
  carX: number;
  bobY: number;
  roadTravelPx: number;
  wheelRotationTurns: number;
  offsets: CountrysideOffsets;
}

/** A negative, native-pixel-snapped scrolling position, not a fractional CSS transform. */
export function nativeOffset(frame: number, layer: CountrysideMovingLayer): number {
  assertFrame(frame);
  const cycleFrame = frame % COUNTRYSIDE_FRAMES;
  return -Math.round(cycleFrame * COUNTRYSIDE_LAYER_SPEC[layer].pixelsPerFrame);
}

/**
 * For tiled layer renderers that need a bounded offset: [-tileWidth+1, 0].
 * Do NOT simply render one tile translated by offset: render neighbouring
 * copies until the viewport is covered (usually 3 or 4 for 180/360px tiles).
 * Keeps negative offsets negative and works with random frame seeking.
 */
export function wrapTileOffset(offsetX: number, tileWidth: number): number {
  if (!Number.isInteger(offsetX) || !Number.isInteger(tileWidth) || tileWidth < 1) {
    throw new Error('Tile offsets and tile width must be integer native pixels');
  }
  const remainder = ((-offsetX % tileWidth) + tileWidth) % tileWidth;
  return remainder === 0 ? 0 : -remainder;
}

/**
 * One pose from N authored hub-angle sprite frames. Wheel artwork remains
 * static in size and position; only the discrete indexed hub pattern changes.
 */
export function wheelPoseIndex(wheelRotationTurns: number, poseCount: number): number {
  if (!Number.isFinite(wheelRotationTurns) || !Number.isInteger(poseCount) || poseCount < 1) {
    throw new Error('Invalid wheel pose input');
  }
  return ((Math.floor(wheelRotationTurns * poseCount + 1e-9) % poseCount) + poseCount) % poseCount;
}

export function getCountrysideMotion(frame: number, wheelRadiusPx = DEFAULT_WHEEL_RADIUS_PX): CountrysideMotion {
  assertFrame(frame);
  if (!Number.isFinite(wheelRadiusPx) || wheelRadiusPx <= 0) {
    throw new Error('wheelRadiusPx must be a finite positive measured native-pixel radius');
  }
  const cycleFrame = frame % COUNTRYSIDE_FRAMES;
  const roadTravelPx = Math.round(cycleFrame * COUNTRYSIDE_LAYER_SPEC.road.pixelsPerFrame);
  const offsets = {
    farTrees: nativeOffset(frame, 'farTrees'),
    midTrees: nativeOffset(frame, 'midTrees'),
    nearTrees: nativeOffset(frame, 'nearTrees'),
    verge: nativeOffset(frame, 'verge'),
    road: nativeOffset(frame, 'road'),
  };
  // Body-only suspension displacement, never move the wheel contact point.
  // 36-frame period divides the film length, preventing a bob loop cut.
  const bobY = Math.round(0.78 * Math.sin((2 * Math.PI * cycleFrame) / 36));
  return {
    frame,
    cycleFrame,
    carX: 180,
    bobY,
    roadTravelPx,
    wheelRotationTurns: roadTravelPx / (2 * Math.PI * wheelRadiusPx),
    offsets,
  };
}

function assertFrame(frame: number): void {
  if (!Number.isInteger(frame) || frame < 0) {
    throw new Error('Countryside motion frame must be an integer >= 0');
  }
}
