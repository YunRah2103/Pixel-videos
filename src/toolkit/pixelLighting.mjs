import sharp from 'sharp';
const bound=(x,a,b)=>Math.max(a,Math.min(b,x));
/** Selective pixel-quantised lighting. Operates at native resolution, never at output resolution. */
export async function lightPixelScene(png,{ambient=.96,lights=[],fog=null}={}){
 if(ambient<0||ambient>1.4)throw Error('ambient out of range');
 const {data,info}=await sharp(png).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const {width,height,channels}=info; if(width*height>3_000_000)throw Error('Use native resolution for pixel lighting');
 const out=Buffer.from(data);
 for(let y=0;y<height;y++)for(let x=0;x<width;x++){
  const i=(y*width+x)*channels;if(data[i+3]===0)continue;
  let gain=ambient, red=0,green=0,blue=0;
  for(const lamp of lights){
   const dx=(x-lamp.x),dy=(y-lamp.y),rad=lamp.radius;
   if(!(rad>0))continue;
   const distance=Math.hypot(dx,dy)/rad;
   if(distance>=1)continue;
   const attenuation=Math.floor((1-distance)**2*8)/8*(lamp.intensity??.65);
   gain+=attenuation*.12;
   red+=attenuation*(lamp.color?.[0]??255)/255*48;
   green+=attenuation*(lamp.color?.[1]??198)/255*35;
   blue+=attenuation*(lamp.color?.[2]??118)/255*22;
  }
  // Fog strength is depth limited; no unsharp global overlay.
  let fogMix=0;
  if(fog&&y>=fog.top&&y<=fog.bottom){
   fogMix=bound(fog.alpha??.08,0,.4);
  }
  out[i]=bound(Math.round((data[i]*gain+red)*(1-fogMix)+(fog?.color?.[0]??172)*fogMix),0,255);
  out[i+1]=bound(Math.round((data[i+1]*gain+green)*(1-fogMix)+(fog?.color?.[1]??183)*fogMix),0,255);
  out[i+2]=bound(Math.round((data[i+2]*gain+blue)*(1-fogMix)+(fog?.color?.[2]??177)*fogMix),0,255);
 }
 return sharp(out,{raw:{width,height,channels:4}}).png({palette:false}).toBuffer();
}
/** Original source pixels are unmodified; this generates a separate opaque-footprint shadow. */
export async function contactShadow({width=80,height=8,opacity=0.26}={}){
 if(width<4||width>400||height<2||height>80)throw Error('invalid shadow size');
 const b=Buffer.alloc(width*height*4);
 for(let y=0;y<height;y++)for(let x=0;x<width;x++){
  const r=((x-width/2)/(width/2))**2+((y-height/2)/(height/2))**2;
  if(r<1){const p=(y*width+x)*4;b[p]=13;b[p+1]=19;b[p+2]=33;b[p+3]=Math.round(255*opacity*(1-r/2));}
 }
 return sharp(b,{raw:{width,height,channels:4}}).png().toBuffer();
}
