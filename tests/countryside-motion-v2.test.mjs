import test from 'node:test';
import assert from 'node:assert/strict';
import {getCountrysideMotion, springFromRoad, AUTHOR_WHEEL_RADIUS_PX,
 COUNTRYSIDE_LAYER_SPEC, COUNTRYSIDE_FRAMES,wrapTileOffset} from
 '../src/scenes/countryside/DrivingMotion.ts';
import {carPose} from '../src/toolkit/rigs.mjs';
test('road roughness is linked to axle position, never frame-only wobble',()=>{
 const front=[],rear=[];
 for(let frame=0;frame<360;frame++){
  const m=getCountrysideMotion(frame,AUTHOR_WHEEL_RADIUS_PX);
  assert.ok(Number.isInteger(m.bobY)&&Math.abs(m.bobY)<=1);
  assert.ok(Number.isInteger(m.frontSpringPx)&&Math.abs(m.frontSpringPx)<=1);
  assert.ok(Number.isInteger(m.rearSpringPx)&&Math.abs(m.rearSpringPx)<=1);
  if(m.frontSpringPx)front.push(frame);
  if(m.rearSpringPx)rear.push(frame);
  assert.equal(m.frontSpringPx,springFromRoad(m.roadTravelPx,222));
  assert.equal(m.rearSpringPx,springFromRoad(m.roadTravelPx,137));
  assert.ok(m.shadowOpacity>=.22&&m.shadowOpacity<=.34);
  // Preserve all five actual source tile widths and stepped integer motion.
  for(const [layer,config] of Object.entries(COUNTRYSIDE_LAYER_SPEC))
   assert.ok(Number.isInteger(wrapTileOffset(m.offsets[layer],config.periodPx)));
  // The V3 car rig was reviewed; its generic wheelAngle/body pitch are
  // explicitly NOT applied over the authored 8 wheel poses or shared road clock.
  const candidate=carPose(frame,{speed:0,roadRoughness:.25});
  assert.ok(Math.abs(candidate.bodyY)<=1);
 }
 assert.ok(front.length>0 && rear.length>0);
 assert.notDeepEqual(front,rear,'front/rear axles do not hit the same bump simultaneously');
});
test('road, world and body loops are frame-addressed, not wall clock',()=>{
 for(let f=0;f<COUNTRYSIDE_FRAMES;f++){
  const a=getCountrysideMotion(f,AUTHOR_WHEEL_RADIUS_PX);
  const b=getCountrysideMotion(f+COUNTRYSIDE_FRAMES,AUTHOR_WHEEL_RADIUS_PX);
  assert.deepEqual({...a,frame:0,cycleFrame:0},{...b,frame:0,cycleFrame:0});
 }
});
test('measured wheel radius rolls exactly the actual road distance',()=>{
 for(const frame of [0,1,44,89,180,299,359]){
  const m=getCountrysideMotion(frame,AUTHOR_WHEEL_RADIUS_PX);
  assert.ok(Math.abs(m.wheelRotationTurns*2*Math.PI*AUTHOR_WHEEL_RADIUS_PX-m.roadTravelPx)<1e-9);
 }
});
