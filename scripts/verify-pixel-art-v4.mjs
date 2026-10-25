import assert from 'node:assert/strict';
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import sharp from 'sharp';
const ROOT=resolve(dirname(fileURLToPath(import.meta.url)),'..'),OUT=resolve(ROOT,'out','artist-v4');
await mkdir(OUT,{recursive:true});
const SRC=resolve(ROOT,'public/toolkit/sprites/oak-tree.png');
const src=await readFile(SRC).catch(()=>{throw Error('Run npm run assets:build before art:proof')});
const meta=await sharp(src).metadata();
assert.equal(meta.format,'png');
const SCALE=6,input=resolve(OUT,'sample-input.png'),output=resolve(OUT,'sample-snapper-output.png');
await sharp(src).resize(meta.width*SCALE,meta.height*SCALE,{kernel:'nearest'}).png().toFile(input);
const bin=process.env.PIXEL_SNAPPER_BIN||resolve(ROOT,'.tools/pixel-art-v4/bin',process.platform==='win32'?'spritefusion-pixel-snapper.exe':'spritefusion-pixel-snapper');
const args=[input,output,'16','--pixel-size','6'];
const p=spawnSync(bin,args,{cwd:ROOT,encoding:'utf8',maxBuffer:8*1024*1024});
if(p.error||p.status!==0)throw Error('Native Pixel Snapper did not run: '+(p.error?.message||p.stderr||p.stdout||p.status));
const target=await sharp(output).metadata();
if(target.format!=='png'||!target.width||!target.height)throw Error('Native tool did not create a valid PNG');
const {data,info}=await sharp(output).ensureAlpha().raw().toBuffer({resolveWithObject:true});
let opaque=0;const colors=new Set();
for(let i=0;i<data.length;i+=info.channels)if(data[i+3]){
 opaque++;colors.add(data[i]+','+data[i+1]+','+data[i+2]+','+data[i+3]);
}
if(opaque<20||colors.size<2||colors.size>32)throw Error('Native pixel fixer output is unexpectedly blank or malformed: '+JSON.stringify({opaque,colors:colors.size}));
const report={verified:true,actual_cli_invocation:true,program:bin,argv:args.map(x=>x.startsWith(ROOT)?x.slice(ROOT.length+1):x),
source:'original repository oak-tree sprite',input:'out/artist-v4/sample-input.png',output:'out/artist-v4/sample-snapper-output.png',
output_dimensions:[target.width,target.height],opaque_pixels:opaque,colors:colors.size,
note:'This tests that a real native fixer runs. It is not proof the image is artistically excellent.'};
await writeFile(resolve(OUT,'tool-evidence.json'),JSON.stringify(report,null,2)+'\n');
console.log('PIXEL_ART_TOOL_PROOF_OK '+JSON.stringify({width:target.width,height:target.height,opaque,colors:colors.size}));
