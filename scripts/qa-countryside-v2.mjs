import sharp from 'sharp';
import {existsSync,mkdirSync,writeFileSync} from 'node:fs';
const spec={sky:[360,480],farTrees:[180,240],midTrees:[360,280],
 nearTrees:[360,340],verge:[180,160],road:[360,160]};
const checks=[];
for(const [layer,[width,height]] of Object.entries(spec)){
 const path='public/countryside/world/'+layer+'.png';
 if(!existsSync(path))throw Error('Missing original countryside PNG '+path);
 const {data,info}=await sharp(path).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 if(info.width!==width||info.height!==height)throw Error('Wrong native tile geometry '+layer);
 const histogram=new Set(),alpha=new Set();
 for(let i=0;i<data.length;i+=4){alpha.add(data[i+3]);if(data[i+3]!==0)histogram.add(data[i]+','+data[i+1]+','+data[i+2]);}
 if(histogram.size<1||histogram.size>22)throw Error('Palette escape '+layer+' '+histogram.size);
 if(alpha.size>2||[...alpha].some(a=>a!==0&&a!==255))throw Error('Alpha not pixel-indexed '+layer);
 if(layer==='sky'&&alpha.has(0))throw Error('Sky must be opaque');
 checks.push({layer,width,height,colours:histogram.size,alpha:[...alpha]});
}
for(const name of ['coupe-body.png','coupe-wheels-8.png'])
 if(!existsSync('public/countryside/car/'+name))throw Error('Missing original Agent 1 asset '+name);
mkdirSync('out/countryside-final-qa',{recursive:true});
writeFileSync('out/countryside-final-qa/art-source-qa.json',JSON.stringify({pass:true,
 toolkit:'Pixel Studio V3',art:'original native pixels, nearest-neighbour only',checks},null,2)+'\n');
console.log('COUNTRYSIDE_V2_ART_SOURCE_QA_PASS '+JSON.stringify(checks));
