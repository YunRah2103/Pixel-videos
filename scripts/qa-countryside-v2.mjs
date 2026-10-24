/** Native pixel-art geometry, V2 palette and transparent front-verge verification. */
import sharp from 'sharp';
import {existsSync,mkdirSync,writeFileSync,readFileSync} from 'node:fs';
const world={sky:[360,480],farTrees:[720,300],midTrees:[840,265],nearTrees:[960,235],verge:[384,160],road:[384,160]};
const checks=[];
for(const [layer,[w,h]] of Object.entries(world)){
 const path='public/countryside/world/'+layer+'.png';
 if(!existsSync(path))throw Error('Missing original V2 art '+path);
 const {data,info}=await sharp(path).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 if(info.width!==w||info.height!==h)throw Error('Wrong V2 native dimensions '+layer);
 const palette=new Set(),alpha=new Set();
 for(let i=0;i<data.length;i+=4){
  alpha.add(data[i+3]);if(data[i+3])palette.add(data[i]+','+data[i+1]+','+data[i+2]);
 }
 if(!palette.size||palette.size>25)throw Error('Non-indexed pixel palette '+layer+': '+palette.size);
 if([...alpha].some(a=>a!==0&&a!==255))throw Error('Non-native alpha '+layer);
 if(layer==='sky'&&alpha.has(0))throw Error('Sky must cover canvas');
 if(layer==='verge'&&!alpha.has(0))throw Error('Foreground verge must be transparent over road');
 checks.push({layer,width:w,height:h,colors:palette.size,alpha:[...alpha]});
}
const sprites={'coupe-v2-body.png':[192,80],'coupe-v2-wheels-8.png':[256,32]};
for(const [name,[w,h]] of Object.entries(sprites)){
 const p='public/countryside/car/'+name;
 if(!existsSync(p))throw Error('Missing real V2 car asset '+name);
 const md=await sharp(p).metadata();
 if(md.width!==w||md.height!==h)throw Error('Wrong car dimensions '+name);
 checks.push({asset:name,width:w,height:h});
}
const manifest=JSON.parse(readFileSync('public/countryside/world/manifest.json','utf8'));
if(manifest.version!==2)throw Error('Invalid V2 world manifest');
mkdirSync('out/countryside-final-qa',{recursive:true});
writeFileSync('out/countryside-final-qa/art-source-qa.json',JSON.stringify({pass:true,sourcePRs:[33,32,30],checks},null,2)+'\n');
console.log('COUNTRYSIDE_V2_ART_QA_PASS '+JSON.stringify(checks));
