/** World-art acceptance gate for the exact PixiJS/Remotion layer contract. */
import sharp from 'sharp';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
const m=JSON.parse(readFileSync('public/countryside/world/manifest.json'));
const tiles={sky:[360,480,0],farTrees:[720,300,180],midTrees:[840,265,215],nearTrees:[960,235,245],road:[384,160,480],verge:[384,160,480]};
if(m.version!==3||m.nativeCanvas.join('x')!=='360x640')throw Error('Native scene contract incompatible with PixiJS');
const results={};
for(const [id,[w,h,y]] of Object.entries(tiles)){
 const spec=m.tiles[id];
 if(spec?.width!==w||spec?.height!==h||spec?.y!==y)throw Error('PixiJS layout mismatch '+id);
 const {data,info}=await sharp(spec.file).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 if(info.width!==w||info.height!==h||info.channels!==4)throw Error('Native PNG dimensions mismatch '+id);
 let painted=0,upper=0;const colors=new Set();
 for(let py=0;py<h;py++)for(let px=0;px<w;px++){
  const at=(py*w+px)*4;
  if(data[at+3]===0)continue;
  painted++;if(py<(id==='farTrees'?245:id==='midTrees'?190:id==='nearTrees'?120:h*.35))upper++;
  colors.add([data[at],data[at+1],data[at+2]].join('-'));
 }
 if(colors.size<2)throw Error('Unfinished single-colour layer '+id);
 if(id==='sky'&&painted!==w*h)throw Error('Sky alpha incomplete');
 if(id.endsWith('Trees')&&upper<150)throw Error('Tree canopies missing from upper tile '+id);
 if(id==='nearTrees'&&colors.size<4)throw Error('Near forest lacks clustered highlights');
 results[id]={width:w,height:h,y,paintedPixels:painted,upperTilePixels:upper,paletteColors:colors.size};
}
const l=JSON.parse(readFileSync('studio/countryside/world/countryside-v3.ldtk'));
const layerNames=l.levels[0].layerInstances.map(x=>x.__identifier);
for(const id of ['farTrees','midTrees','nearTrees']){
 if(!layerNames.includes(id))throw Error('Missing LDtk layer '+id);
 if(!l.levels[0].layerInstances.find(x=>x.__identifier===id).entityInstances.length)
  throw Error('No actual LDtk entity positions '+id);
}
mkdirSync('out/countryside-v3-world',{recursive:true});
writeFileSync('out/countryside-v3-world/art-qa.json',JSON.stringify({passed:true,source:'actual Sharp-rendered native PNGs and LDtk entities',pixiContract:tiles,results},null,2));
console.log('COUNTRYSIDE_V3_PIXI_WORLD_COMPATIBLE',JSON.stringify(results));
