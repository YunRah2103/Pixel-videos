import assert from 'node:assert/strict';
import sharp from 'sharp';
import {carPose,walkPose,boatPose,animalPose,clothPose,frameSlot,rigPose} from '../src/toolkit/rigs.mjs';
import {lightPixelScene,contactShadow} from '../src/toolkit/pixelLighting.mjs';
for(let f of [0,1,30,60,89,1000]){
 assert.deepEqual(carPose(f),carPose(f));
 assert.equal(walkPose(f).leftFootX,-walkPose(f).rightFootX);
 assert(Number.isFinite(boatPose(f).roll));
 assert(typeof animalPose(f).eyeClosed==='boolean');
 assert(Number.isFinite(clothPose(f).angle));
 assert.deepEqual(rigPose('car',f),carPose(f));
}
assert.equal(frameSlot(20,{count:4,hold:5}),0);
const raw=await sharp({create:{width:16,height:16,channels:4,background:'#364e74'}}).png().toBuffer();
const lit=await lightPixelScene(raw,{ambient:.65,lights:[{x:8,y:8,radius:7,color:[255,160,80],intensity:.5}],fog:{top:0,bottom:5,alpha:.05}});
assert.equal((await sharp(lit).metadata()).width,16);
assert.equal((await sharp(await contactShadow({width:30,height:8})).metadata()).height,8);
console.log('PIXEL_RIG_LIGHTING_TEST_PASS');
