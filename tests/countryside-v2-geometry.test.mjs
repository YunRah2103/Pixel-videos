import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {getCountrysideMotion,springFromRoad} from '../src/scenes/countryside/DrivingMotion.ts';
test('V2 wheel radius and actual two axle locations match the authored hero coupe',()=>{
 const car=readFileSync('src/scenes/countryside/CarLayer.tsx','utf8');
 assert.match(car,/WHEEL_RADIUS_PX=15\.5/);
 assert.match(car,/CAR_WHEEL_CENTERS_X[^=]*=\[43,151\]/);
 for(const f of [0,1,49,99,159,239,359]){
  const m=getCountrysideMotion(f,15.5);
  assert.ok(Math.abs(m.wheelRotationTurns*2*Math.PI*15.5-m.roadTravelPx)<1e-9);
  assert.equal(m.rearSpringPx,springFromRoad(m.roadTravelPx,127));
  assert.equal(m.frontSpringPx,springFromRoad(m.roadTravelPx,235));
 }
});
test('final scene overlays grass on road and bounces body only',()=>{
 const scene=readFileSync('src/scenes/countryside/CountrysideDrive.tsx','utf8');
 assert.ok(scene.includes("'road','verge'"));
 assert.match(scene,/bobY=\{m\.bobY\}/);
});
