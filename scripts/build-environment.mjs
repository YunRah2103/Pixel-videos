import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import sharp from 'sharp';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const sceneFile=process.argv[2]?resolve(root,process.argv[2]):resolve(root,'studio/countryside.scene.json');
if(!sceneFile.startsWith(resolve(root,'studio')+'/'))throw Error('Scene must live under studio/');
const scene=JSON.parse(await readFile(sceneFile,'utf8'));
if(scene.schemaVersion!==1||scene.width<64||scene.height<64||scene.stageWidth<scene.width||scene.stageWidth>8192)throw Error('Invalid scene geometry');
const slug=(scene.slug||'countryside');
if(!/^[a-z][a-z0-9-]{1,50}$/.test(slug))throw Error('Invalid scene slug');
const output=resolve(root,'public/toolkit/environments',slug);
await mkdir(output,{recursive:true});
const assets={};
const assetReport=JSON.parse(await readFile(resolve(root,'out/toolkit/assets-report.json'),'utf8'));
for(const art of assetReport.entries){assets[art.id]=await readFile(resolve(root,art.destination));}
const pixelPanel=async(width,height,color)=>sharp({create:{width,height,channels:4,background:color}}).png().toBuffer();
const fit=(sprite,scale)=>{
 if(!Number.isInteger(scale)||scale<1||scale>8)throw Error('Invalid sprite integer scale');
 return sharp(sprite).metadata().then(meta=>sharp(sprite).resize(meta.width*scale,meta.height*scale,{kernel:'nearest'}).png().toBuffer());
};
const safeLayer=(s)=>/^[a-z0-9-]+$/.test(s);
const exported=[];
for(const layer of scene.layers){
 if(!safeLayer(layer.id)||layer.depth<0||layer.depth>2)throw Error('Invalid layer name or depth');
 const elements=[];
 if(layer.color)elements.push({input:await pixelPanel(scene.stageWidth,scene.height,layer.color),left:0,top:0});
 for(const band of layer.bands||[]){
  if(!Number.isInteger(band.top)||!Number.isInteger(band.bottom)||band.top<0||band.bottom>scene.height||band.bottom<=band.top)throw Error('bad colour band '+layer.id);
  elements.push({input:await pixelPanel(scene.stageWidth,band.bottom-band.top,band.color),left:0,top:band.top});
 }
 if(layer.roadMarkers){
  const road=layer.roadMarkers;
  if(!Number.isInteger(road.count)||road.count<0||road.count>80)throw Error('invalid road marking count');
  for(let i=0;i<road.count;i++)elements.push({input:await pixelPanel(road.width,road.height,road.color),
    left:i*road.step,top:road.y});
 }
 for(const obj of layer.sprites||[]){
  if(!assets[obj.sprite])throw Error('Missing hand-authored sprite '+obj.sprite);
  if(!Number.isInteger(obj.x)||!Number.isInteger(obj.y)||obj.x<0||obj.y<0)throw Error('Negative or fractional placements unsupported');
  const sprite=await fit(assets[obj.sprite],obj.scale||1);
  const meta=await sharp(sprite).metadata();
  if(obj.x+meta.width>scene.stageWidth||obj.y+meta.height>scene.height)throw Error('Sprite '+obj.sprite+' exceeds stage: '+layer.id);
  elements.push({input:sprite,left:obj.x,top:obj.y});
 }
 const png=await sharp({create:{width:scene.stageWidth,height:scene.height,channels:4,background:'#00000000'}})
  .composite(elements).png({palette:false}).toBuffer();
 const file=resolve(output,layer.id+'.png');await writeFile(file,png);
 exported.push({id:layer.id,depth:layer.depth,image:'toolkit/environments/'+slug+'/'+layer.id+'.png',objects:(layer.sprites||[]).length});
}
const payload={name:scene.name,width:scene.width,height:scene.height,stageWidth:scene.stageWidth,camera:scene.camera,
 layers:exported,hero:scene.hero,license:'original authored artwork; MIT'};
await writeFile(resolve(output,'scene.json'),JSON.stringify(payload,null,2)+'\n');
console.log('PIXEL_ENVIRONMENT_BUILT '+JSON.stringify({layers:exported.length,artworkAssets:Object.keys(assets).length,output}));
