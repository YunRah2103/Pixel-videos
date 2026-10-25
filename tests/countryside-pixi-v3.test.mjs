import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {PIXI_WORLD_LAYERS,planPixiWorld} from '../src/scenes/countryside/PixiWorldPlan.ts';
import {getCinematicMotion,getCinematicRoadTravel,roadStepForFrame} from '../src/scenes/countryside/DrivingMotionV3.ts';

test('Six authored PNG planes, correct far-to-near layering and crisp native sizes',()=>{
 assert.deepEqual(PIXI_WORLD_LAYERS.map(l=>l.name),
  ['sky','farTrees','midTrees','nearTrees','road','verge']);
 assert.deepEqual(PIXI_WORLD_LAYERS.map(l=>l.width),[360,720,840,960,384,384]);
});
test('Actual 360-frame road acceleration is substantial and keeps wheels locked',()=>{
 assert.equal(roadStepForFrame(0),3);
 assert.equal(roadStepForFrame(130),7);
 assert.equal(roadStepForFrame(359),5);
 assert.ok(getCinematicRoadTravel(330)>1500);
 for(let f=0;f<360;f++){
  const motion=getCinematicMotion(f,15.5);
  assert.ok(Number.isInteger(motion.carX)&&motion.carX>=152&&motion.carX<=206);
  assert.equal(motion.roadTravelPx,getCinematicRoadTravel(f));
  assert.ok(Math.abs(motion.wheelRotationTurns*2*Math.PI*15.5-motion.roadTravelPx)<1e-8);
  assert.ok(Number.isInteger(motion.bobY)&&Math.abs(motion.bobY)<=1);
  assert.equal(motion.foregroundTravelPx,Math.round(motion.roadTravelPx*1.3));
  assert.ok(Math.abs(motion.offsets.farTrees)<Math.abs(motion.offsets.nearTrees)||f===0);
 }
});
test('Pixi scene renders moving sky, prominent original foreground bush sprites and road shade',()=>{
 let moving=0;
 for(let f=0;f<360;f++){
  const m=getCinematicMotion(f,15.5),plan=planPixiWorld(f,m);
  assert.equal(plan.frame,f);
  for(const l of plan.layers){
   assert.equal(l.tileX,l.name==='sky'?-Math.round(f*.22):m.offsets[l.name]);
   assert.ok(Number.isInteger(l.tileX));
  }
  assert.ok(plan.shrubs.length>=3);
  assert.ok(plan.shadeBands.length>=2);
  assert.ok(plan.roadSpecks.length>=10);
  assert.ok(plan.leafMotes.length>=5);
  assert.ok(plan.lightPixels.every(p=>Number.isInteger(p.x)&&Number.isInteger(p.y)));
  assert.equal(plan.contactShadow.x,m.carX-73);
  assert.equal(plan.contactShadow.y,494);
  assert.ok(plan.contactShadow.alpha<=.34&&plan.contactShadow.alpha>=.22);
  moving+=plan.shadeBands[0].x;
 }
 assert.notEqual(moving,0);
});
test('Pixel-perfect wheel detail shot introduces an observable visual cut, then goes wide',()=>{
 assert.equal(getCinematicMotion(0,15.5).shot,'wheel-closeup');
 assert.equal(getCinematicMotion(44,15.5).shot,'wheel-closeup');
 assert.equal(getCinematicMotion(45,15.5).shot,'wide');
 assert.equal(getCinematicMotion(204,15.5).shot,'wide');
 assert.equal(getCinematicMotion(205,15.5).shot,'rear-closeup');
 assert.equal(getCinematicMotion(270,15.5).shot,'rear-closeup');
 assert.equal(getCinematicMotion(271,15.5).shot,'wide');
 const scene=readFileSync('src/scenes/countryside/CountrysideDrive.tsx','utf8');
 assert.match(scene,/transform:close\?'scale\(2\)'/);
 assert.match(scene,/wheelRotationTurns=\{m\.wheelRotationTurns\}/);
 assert.doesNotMatch(scene,/blur\(|transition:|perspective/);
});
test('Random seeking and rewind reproduce the identical plan',()=>{
 for(const f of [260,25,357,0,190,206,90,260,0]){
  const m=getCinematicMotion(f,15.5);
  assert.deepEqual(planPixiWorld(f,m),planPixiWorld(f,getCinematicMotion(f,15.5)));
 }
 assert.throws(()=>planPixiWorld(2,getCinematicMotion(3,15.5)),/Stale/);
});
test('Production PixiJS renderer actually draws scenery, shrubs, shadows, leaves and speed effects',()=>{
 const pixi=readFileSync('src/scenes/countryside/PixiCountrysideWorld.tsx','utf8');
 const scene=readFileSync('src/scenes/countryside/CountrysideDrive.tsx','utf8');
 for(const s of ['new pixi.Application(','new pixi.TilingSprite(','pixi.Assets.load(',
  'tile.tilePosition.x=layer.tileX','stage.shade.rect(','stage.shrubs.rect(',
  'stage.leaves.rect(','stage.dust.rect(','renderer.render(','continueRender(renderHandle)']){
  assert.ok(pixi.includes(s),s+' not truly used by Pixi renderer');
 }
 assert.match(scene,/<PixiCountrysideWorld/);
 assert.doesNotMatch(pixi,/blur\(|filter:\s*['"]blur|requestAnimationFrame|setInterval/);
});
