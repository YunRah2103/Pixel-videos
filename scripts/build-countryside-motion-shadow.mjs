/**
 * Uses Pixel Studio V3's native contactShadow generator. Quantise alpha to
 * a few visible native-pixel steps; NO CSS blur, radial gradient or filter.
 * Run after npm run studio:setup and before the Agent 3 isolated proof.
 */
import sharp from 'sharp';
import {mkdir} from 'node:fs/promises';
import {contactShadow} from '../src/toolkit/pixelLighting.mjs';
const path='public/countryside/motion';
await mkdir(path,{recursive:true});
const img=await contactShadow({width:142,height:7,opacity:.26});
const {data,info}=await sharp(img).ensureAlpha().raw().toBuffer({resolveWithObject:true});
for(let i=3;i<data.length;i+=4){
 const a=data[i];
 data[i]=a<14?0:a<36?32:a<65?56:80;
}
await sharp(data,{raw:{width:info.width,height:info.height,channels:4}})
 .png({palette:true,compressionLevel:9}).toFile(path+'/contact-shadow.png');
console.log('AGENT3_PIXEL_CONTACT_SHADOW_READY');
