import test from 'node:test';
import assert from 'node:assert/strict';
import {
  COUNTRYSIDE_FRAMES,
  COUNTRYSIDE_LAYER_SPEC,
  DEFAULT_WHEEL_RADIUS_PX,
  getCountrysideMotion,
  nativeOffset,
  wheelPoseIndex,
  wrapTileOffset,
} from '../src/scenes/countryside/DrivingMotion.ts';

test('all frame addressed outputs use integer native pixel offsets', () => {
  for (let frame = 0; frame < 360; frame++) {
    const state = getCountrysideMotion(frame);
    assert.equal(state.carX, 180);
    assert.ok(Number.isInteger(state.roadTravelPx));
    assert.ok(Number.isInteger(state.bobY));
    assert.ok(Math.abs(state.bobY) <= 1);
    for (const layer of Object.keys(state.offsets)) {
      assert.ok(Number.isInteger(state.offsets[layer]), `${layer} frame ${frame}`);
      assert.equal(state.offsets[layer], nativeOffset(frame, layer));
    }
  }
});

test('deterministic random-access seek forward, backward, and out-of-order', () => {
  const frames = [0, 359, 3, 180, 90, 359, 1, 248, 30, 0, 360, 719, 90];
  const reference = new Map(frames.map(f => [f, JSON.stringify(getCountrysideMotion(f))]));
  for (const frame of frames.reverse()) {
    assert.equal(JSON.stringify(getCountrysideMotion(frame)), reference.get(frame));
  }
});

test('parallax near > mid > far, and road moves fastest', () => {
  const a = getCountrysideMotion(0).offsets;
  const b = getCountrysideMotion(240).offsets;
  assert.ok(Math.abs(b.farTrees - a.farTrees) < Math.abs(b.midTrees - a.midTrees));
  assert.ok(Math.abs(b.midTrees - a.midTrees) < Math.abs(b.nearTrees - a.nearTrees));
  assert.ok(Math.abs(b.nearTrees - a.nearTrees) < Math.abs(b.verge - a.verge));
  assert.ok(Math.abs(b.verge - a.verge) < Math.abs(b.road - a.road));
});

test('no reversals and each integer jump is at most ceil(layer speed)', () => {
  for (const [layer, {pixelsPerFrame}] of Object.entries(COUNTRYSIDE_LAYER_SPEC)) {
    for (let f = 1; f < COUNTRYSIDE_FRAMES; f++) {
      const delta = nativeOffset(f, layer) - nativeOffset(f - 1, layer);
      assert.ok(delta <= 0 && delta >= -Math.ceil(pixelsPerFrame),
        `${layer} frame ${f}: invalid delta ${delta}`);
    }
  }
});

test('seam aligns for prescribed tile periods at frame 360', () => {
  for (const [layer, spec] of Object.entries(COUNTRYSIDE_LAYER_SPEC)) {
    const fullDistance = Math.round(COUNTRYSIDE_FRAMES * spec.pixelsPerFrame);
    assert.equal(fullDistance % spec.periodPx, 0, layer);
    assert.equal(wrapTileOffset(nativeOffset(COUNTRYSIDE_FRAMES, layer), spec.periodPx),
      wrapTileOffset(nativeOffset(0, layer), spec.periodPx));
    assert.equal(wrapTileOffset(-fullDistance, spec.periodPx), 0, layer);
  }
  assert.equal(getCountrysideMotion(0).bobY, getCountrysideMotion(360).bobY);
  assert.equal(getCountrysideMotion(0).roadTravelPx, getCountrysideMotion(360).roadTravelPx);
});

test('wheel angle travels exactly road distance for measured radius', () => {
  const r = 12;
  for (const f of [0, 1, 23, 77, 180, 359]) {
    const m = getCountrysideMotion(f, r);
    assert.ok(Math.abs(m.wheelRotationTurns * 2 * Math.PI * r - m.roadTravelPx) < 1e-8);
  }
  assert.ok(Math.abs(getCountrysideMotion(359).wheelRotationTurns - 17.95) < .00001);
  assert.equal(DEFAULT_WHEEL_RADIUS_PX > 9 && DEFAULT_WHEEL_RADIUS_PX < 10, true);
});

test('pose index is deterministic and wraps without resizing any sprite', () => {
  assert.equal(wheelPoseIndex(0, 8), 0);
  assert.equal(wheelPoseIndex(0.25, 8), 2);
  assert.equal(wheelPoseIndex(1, 8), 0);
  assert.equal(wheelPoseIndex(17.95, 8), 7);
});

test('bounded tiling handles negative offsets and rejects subpixels', () => {
  for (const off of [0, -1, -179, -180, -181, -1008]) {
    const x = wrapTileOffset(off, 180);
    assert.ok(x <= 0 && x > -180);
    assert.equal(((x - off) % 180), 0);
  }
  assert.throws(() => getCountrysideMotion(-1), /integer/);
  assert.throws(() => getCountrysideMotion(1.5), /integer/);
  assert.throws(() => getCountrysideMotion(1, 0), /radius/);
  assert.throws(() => wrapTileOffset(-1.5, 360), /integer/);
});
