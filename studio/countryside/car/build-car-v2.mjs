/**
 * Countryside Drive V2: ORIGINAL authored indexed pixel-art sprite.
 * Editable 192x80 body rows use palette-indexed horizontal pixel runs.
 * This is source pixel art, never downsampled vector artwork.
 * Rebuild with: node studio/countryside/car/build-car-v2.mjs
 */
import sharp from 'sharp';
import {mkdir} from 'node:fs/promises';
const palette=[
 [0,0,0,0],[38,48,59,255],[40,63,82,255],[66,109,128,255],
 [91,107,112,255],[94,41,57,255],[137,48,58,255],
 [139,196,195,255],[187,64,62,255],[199,209,189,255],
 [217,90,69,255],[240,120,84,255],[245,162,93,255],
 [249,172,112,255],[255,241,181,255]
];
const bodyRows=[
 ...Array(11).fill('192a'),
 '83a30b79a',
 '76a40n3b73a',
 '70a46n1b7l68a',
 '63a2l52f9l1f2l1b62a',
 '61a2l66f1l1b61a',
 '60a1l70f2b59a',
 '58a1l8f21c44f2b58a',
 '56a1l7n1f23c6f27c13f2b56a',
 '55a1l1f7n24c6f30c12f1b55a',
 '53a2l7f6c16d4c6f32c11f2b53a',
 '52a2l7f5c2d12h4d4c6f4c22d9c8f3b52a',
 '51a2l6f4c16h5d4c6f4c2d18h4d8c8f2b52a',
 '50a2l6f3c1d16h6d4c6f4c5d17h5d6c7f3b51a',
 '49a3l5f3c1d1h22d4c6f4c7d18h3d5c8f2b51a',
 '49a2l6f2c1d1h23d4c6f4c12d14h3d5c7f3b50a',
 '48a2l6f2c2d1h23d4c6f4c18d9h3d5c7f3b49a',
 '47a2l6f3c1d1h25d3c7f3c23d5h3d5c6f1l2b49a',
 '46a2l6f3c1d1h26d3c7f3c28d1h4d4c6f3b48a',
 '45a2l6f3c1d1h27d3c7f3c34d4c5f1l2b48a',
 '44a2l7f2c30d3c7f3c35d3c6f1l2b47a',
 '44a1l7f2c31d3c7f3c36d3c5f1l3b46a',
 '43a2l6f1c33d3c7f3c37d3c4f5l45a',
 '42a2l6f38c7f3c39d5f3l3n1l43a',
 '42a2l5f39c7f42c2f3b3f3n2f42a',
 '41a2l7n38c7f41c3f3b8f1b41a',
 '40a2l1f7n45f43c1f22b31a',
 '40a2l104f26l20a',
 '39a2l102f1n3f28l17a',
 '37a105l1f29n6l14a',
 '34a57l2g51l31n7l10a',
 '32a22l11n26l2g51l34n5l2b7a',
 '29a7l6n12l11n26l2g51l4n35l3i6a',
 '27a121n33l3n3i5a',
 '21a6l10n13f94n1l13f27n2i2b3a',
 '14a21n8f1a8f32l7j1f1g50l8f1a8f27n2k1b2a',
 '11a4f18n5f11a5f33l5f1g48l5f11a5f9n10l6o2k1b2a',
 '9a6f17l3f17a3f29l8f1g47l3f17a3f18l6o2k1g1b1a',
 '6a1m4o2m2f16k3f19a3f35k2g1k1l44k3f19a3f19k8o1a',
 '5a1i1m4o2m1f16k3f21a3f34k2g1k1l43k3f21a3f18k3o6n',
 '5a1i1m4o2m1f14k3l25a3l32k2g1k1l41k3l25a3l16k3o6n',
 '4a2l7m1f14k3f25a3f9k11l12k2g1k1l41k3f25a3f19k6n',
 '4a2l7m1f13k3b27a3b8k11l12k2g1k1l40k3b27a3b19k5f',
 '3a1b7l16k2b29a2b31k2g42k2b29a2b19k5f',
 '2a6b5i5k8i2b31a2b30i2g41i2b31a2b18i3g2b',
 '2a6b5i5k8i2b31a2b30i3f40i2b31a2b5i18g',
 '1a7b10i7l3b31a3b29i3f39i3b31a3b4i10g8b',
 '1a7b10i7l2b33a2b8i59g4i2b33a2b4i10g8b',
 '1a7b17i2b33a2b8i59g4i2b33a2b4i18b',
 '1a12f12i2b33a2b8i59g4i2b33a2b4i18b',
 '2a11f12g2b33a2b4g59l8g2b33a2b7g9b6g',
 '2a11f12g2b33a2b71g2b33a2b7g9b5f1a',
 '3a1b21g1b35a1b3g60f8g1b35a1b10g11f1a',
 '3a1b21g2b33a2b3g60f8g2b33a2b10g10f2a',
 '4a23g33a7g59j9g33a22g2a',
 '7a20b33a75b33a19b5a',
 '10a17b33a75b33a17b7a',
 '13a14b33a75b33a14b10a',
 '66a4b56e2b64a',
 '66a62b64a',
 ...Array(10).fill('192a')
];
if(bodyRows.length!==80)throw Error('Body source must have exactly 80 original pixel rows; got '+bodyRows.length);
const body=Buffer.alloc(192*80*4);
for(let y=0;y<80;y++){
 let x=0;const row=bodyRows[y],parts=[...row.matchAll(/(\d+)([a-o])/g)];
 if(parts.map(p=>p[0]).join('')!==row)throw Error('Malformed original pixel row '+y);
 for(const part of parts){const n=Number(part[1]),color=palette[part[2].charCodeAt(0)-97];for(let i=0;i<n;i++){if(x>=192)throw Error('Overflow on row '+y);body.set(color,(y*192+x++)*4);}}
 if(x!==192)throw Error('Invalid pixel row '+y+' width '+x);
}
const wheel=Buffer.alloc(256*32*4);
function pixel(x,y,key){if(x<0||x>=256||y<0||y>=32)return;wheel.set(palette[key],(y*256+x)*4);}
function line(x1,y1,x2,y2,key){for(let x=x1;x<=x2;x++)for(let y=y1;y<=y2;y++)pixel(x,y,key);}
for(let f=0;f<8;f++){
 const ox=f*32,c=15.5;
 for(let y=0;y<32;y++)for(let x=0;x<32;x++){
  const d=Math.hypot(x-c,y-c);
  // Charcoal rubber, two-depth sidewall, chrome lip and deep spoke wells.
  const key=d<=15.4?(d>=13.3?1:d>=12.1?4:d>=10.8?1:d>=9.4?4:d>=8?9:1):null;
  if(key!==null)pixel(ox+x,y,key);
 }
 for(let k=0;k<12;k++){
  const a=k*2*Math.PI/12,x=Math.round(c+13.9*Math.cos(a)),y=Math.round(c+13.9*Math.sin(a));
  if(x>=0&&x<32&&y>=0&&y<32)pixel(ox+x,y,k%2?1:4);
 }
 for(let spoke=0;spoke<5;spoke++){
  const a=f*2*Math.PI/8+spoke*2*Math.PI/5;
  for(let radius=4;radius<10;radius++){
   const x=Math.round(c+radius*Math.cos(a)),y=Math.round(c+radius*Math.sin(a));
   for(let dx=0;dx<=(radius<8?1:0);dx++)pixel(ox+x+dx,y,radius<8?9:4);
  }
 }
 for(let y=12;y<=19;y++)for(let x=12;x<=19;x++)if(((x-15.5)**2+(y-15.5)**2)<=4**2)pixel(ox+x,y,1);
 line(ox+14,14,ox+17,17,9);
 pixel(ox+15,15,13);
}
await mkdir('public/countryside/car',{recursive:true});
await sharp(body,{raw:{width:192,height:80,channels:4}}).png({compressionLevel:9}).toFile('public/countryside/car/coupe-v2-body.png');
await sharp(wheel,{raw:{width:256,height:32,channels:4}}).png({compressionLevel:9}).toFile('public/countryside/car/coupe-v2-wheels-8.png');
console.log('CAR_V2_SPRITES_OK: 192x80 authentic editable indexed body, 8x32px animated wheel frames');
