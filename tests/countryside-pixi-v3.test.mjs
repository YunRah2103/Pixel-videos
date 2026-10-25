import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {getCountrysideMotion} from '../src/scenes/countryside/DrivingMotion.ts';
import {PIXI_WORLD_LAYERS,planPixiWorld} from '../src/scenes/countryside/PixiWorldPlan.ts';

test('exact six real native V2 PNGs are assigned to Pixi tiling planes in correct layering',()=>{
 assert.deepEqual(PIXI_WORLD_LAYERS.map(l=>l.name),
  ['sky','farTrees','midTrees','nearTrees','road','verge']);
 assert.deepEqual(PIXI_WORLD_LAYERS.map(l=>l.width),[360,720,840,960,384,384]);
 assert.ok(PIXI_WORLD_LAYERS.every(l=>Number.isInteger(l.y)));
});
test('Pixi tile positions equal original wheel-linked Remotion motion on all 360 frames',()=>{
 for(let f=0;f<360;f++){
  const motion=getCountrysideMotion(f,15.5);
  const plan=planPixiWorld(f,motion);
  assert.equal(plan.frame,f);
  assert.equal(plan.layers.find(l=>l.name==='sky').tileX,0);
  for(const l of plan.layers.filter(l=>l.name!=='sky')){
   assert.equal(l.tileX,motion.offsets[l.name],l.name+' @'+f);
   assert.ok(Number.isInteger(l.tileX));
  }
  assert.ok(plan.lightPixels.every(p=>Number.isInteger(p.x)&&Number.isInteger(p.y)));
  assert.ok(plan.lightPixels.length<=7);
  assert.equal(plan.contactShadow.y,494);
  assert.equal(plan.contactShadow.x,107);
  assert.ok(plan.contactShadow.alpha<=.34&&plan.contactShadow.alpha>=.22);
 }
});
test('random access and rewind yield deterministic Pixi graphics instructions',()=>{
 for(const frame of [150,1,355,90,0,35,150,355,0]){
  const m=getCountrysideMotion(frame,15.5);
  assert.deepEqual(planPixiWorld(frame,m),planPixiWorld(frame,m));
 }
 assert.throws(()=>planPixiWorld(3,getCountrysideMotion(4,15.5)),/Stale/);
});
test('Pixi is genuinely used to render video textures and effects, not just imported',()=>{
 const pixi=readFileSync('src/scenes/countryside/PixiCountrysideWorld.tsx','utf8');
 const scene=readFileSync('src/scenes/countryside/CountrysideDrive.tsx','utf8');
 assert.match(pixi,/new pixi\.Application\(/);
 assert.match(pixi,/new pixi\.TilingSprite\(/);
 assert.match(pixi,/pixi\.Assets\.load\(/);
 assert.match(pixi,/tile\.tilePosition\.x=layer\.tileX/);
 assert.match(pixi,/new pixi\.Graphics\(/);
 assert.match(pixi,/renderer\.render\(/);
 assert.match(pixi,/continueRender\(renderHandle\)/);
 assert.match(scene,/<PixiCountrysideWorld/);
 assert.match(scene,/wheelRotationTurns=\{m\.wheelRotationTurns\}/);
 assert.doesNotMatch(pixi,/blur\(|filter:\s*['"]blur|requestAnimationFrame|setInterval/);
});
