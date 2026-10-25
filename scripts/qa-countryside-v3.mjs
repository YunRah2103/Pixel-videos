/** Actual V3 source checks; rejects fallback V2 art and unverified Pixelorama car exports. */
import sharp from 'sharp';
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const md=JSON.parse(readFileSync('public/countryside/world/manifest.json','utf8'));
const ldtk=JSON.parse(readFileSync('studio/countryside/world/countryside-v3.ldtk','utf8'));
if(md.version!==3||!ldtk.levels?.[0]?.layerInstances)throw Error('NOT genuine V3 LDtk world');
const expected={sky:[360,480],farTrees:[720,300],midTrees:[840,265],nearTrees:[960,235],road:[384,160],verge:[384,160]};
const planes=[];
for(const [name,[w,h]] of Object.entries(expected)){
 const meta=await sharp('public/countryside/world/'+name+'.png').metadata();
 if(meta.width!==w||meta.height!==h||md.tiles?.[name]?.width!==w||md.tiles[name]?.height!==h)throw Error('Bad V3 layer '+name);
 planes.push({name,width:w,height:h});
}
let trees=0;
for(const name of ['farTrees','midTrees','nearTrees']){
 const layer=ldtk.levels[0].layerInstances.find(x=>x.__identifier===name);
 if(!layer?.entityInstances?.length)throw Error('Missing actual LDtk tree instances '+name);
 trees+=layer.entityInstances.length;
}
if(trees<20)throw Error('Empty or fake countryside LDtk level');
const px=JSON.parse(readFileSync('out/car-v3-proof/pixelorama-export-validation.json','utf8'));
if(px.validated!==true||px.distinctWheelFrames!==8||px.sprites?.length!==2)throw Error('Pixelorama editor export not verified');
const known={
 'coupe-v2-body.png':'cffad6f4a75e38c2a3e4c8cb1d12b379514bcb8d75693863b14ee1747444b148',
 'coupe-v2-wheels-8.png':'4864cc3fdaa95454fde4e01a3e912379b6c17a4f9bf9612a76625dafab70738d'
};
const sprites=[];
for(const [name,hash] of Object.entries(known)){
 const path='public/countryside/car/'+name;
 const file=readFileSync(path),actual=createHash('sha256').update(file).digest('hex');
 if(hash!==actual)throw Error('Pixelorama car not same as verified PR36 art: '+name+' '+actual);
 const meta=await sharp(file).metadata();
 sprites.push({name,width:meta.width,height:meta.height,sha256:actual});
}
const sheet='public/countryside/car/coupe-v2-wheels-8.png';
const poses=new Set();
for(let frame=0;frame<8;frame++){
 const image=await sharp(sheet).extract({left:frame*32,top:0,width:32,height:32}).raw().toBuffer();
 poses.add(createHash('sha256').update(image).digest('hex'));
}
if(poses.size!==8)throw Error('Static or repeated wheels');
const result={pass:true,artVersion:3,ldtkTreeCount:trees,worldLayers:planes,car:sprites,wheelRadiusNativePx:15.5,wheelPoses:8,sources:{worldPR:37,carPR:36,latestMotionPR:35},artisticSignoff:false};
mkdirSync('out/countryside-final-qa',{recursive:true});
writeFileSync('out/countryside-final-qa/art-source-qa.json',JSON.stringify(result,null,2)+'\n');
console.log('COUNTRYSIDE_V3_ART_SOURCE_QA_PASS '+JSON.stringify(result));
