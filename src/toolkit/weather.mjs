/**
 * Strict native-grid effects: no blur, antialias, smooth SVG or shader-based pixelation.
 * Overlays are exact 1x1/1x2 pixel marks placed in integer coordinates.
 */
import sharp from 'sharp';
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const hash=(n)=>{let x=n|0;x=Math.imul(x^x>>>16,0x7feb352d);x=Math.imul(x^x>>>15,0x846ca68b);return ((x^x>>>16)>>>0)/4294967296;};
export async function weatherOverlay(frame,{width=180,height=320,type='clear',intensity=.6,wind=1}={}){
 if(!Number.isInteger(frame)||frame<0||width<1||height<1||width*height>1200000||intensity<0||intensity>1)throw Error('invalid effect params');
 if(!['clear','rain','snow','leaves','fireflies','dust'].includes(type))throw Error('bad weather type');
 const arr=Buffer.alloc(width*height*4);
 const px=(x,y,c,alpha=255)=>{x=Math.round(x);y=Math.round(y);if(x<0||y<0||x>=width||y>=height)return;
  const i=(y*width+x)*4;arr[i]=c[0];arr[i+1]=c[1];arr[i+2]=c[2];arr[i+3]=alpha;};
 if(type!=='clear'){
  const particles=Math.round(({rain:110,snow:40,leaves:19,fireflies:13,dust:34})[type]*intensity);
  const colors={rain:[179,211,222],snow:[245,243,219],leaves:[215,154,68],fireflies:[249,217,115],dust:[190,177,132]};
  for(let k=0;k<particles;k++){
    const x0=hash(k*71+123),y0=hash(k*97+847);
    const vx={rain:1.5,snow:.32,leaves:.66,fireflies:.12,dust:.32}[type]*wind;
    const vy={rain:4.5,snow:.65,leaves:.4,fireflies:.12,dust:.23}[type];
    const x=((x0*width+frame*vx+k*.17)%width+width)%width;
    const y=((y0*height+frame*vy)%height+height)%height;
    const c=colors[type];
    px(x,y,c,type==='fireflies'?200:215);
    if(type==='rain'){px(x-1,y+1,c,120);px(x-1,y+2,c,80);}
    if(type==='snow')px(x+1,y,c,165);
    if(type==='leaves'){px(x+1,y,c,150);px(x,y+1,[118,94,57],210);}
    if(type==='fireflies'&&k%3===0)px(x-1,y,c,80);
  }
 }
 return sharp(arr,{raw:{width,height,channels:4}}).png().toBuffer();
}
export async function pixelGrade(src,{mood='day',frame=0}={}){
 const grades={
  day:{mul:[1,1,1],add:[0,0,0]},
  golden:{mul:[1.08,1.01,.86],add:[8,2,0]},
  dusk:{mul:[.98,.83,1.03],add:[8,-4,13]},
  night:{mul:[.49,.62,.83],add:[0,3,12]},
  storm:{mul:[.70,.79,.88],add:[-4,-3,3]}
 };
 const g=grades[mood];if(!g)throw Error('Unknown pixel colour grade '+mood);
 const {data,info}=await sharp(src).ensureAlpha().raw().toBuffer({resolveWithObject:true});
 const out=Buffer.from(data);
 for(let i=0;i<out.length;i+=4){
  if(out[i+3]===0)continue;
  for(let ch=0;ch<3;ch++){out[i+ch]=clamp(Math.round(data[i+ch]*g.mul[ch]+g.add[ch]),0,255);}
 }
 return sharp(out,{raw:{width:info.width,height:info.height,channels:4}}).png().toBuffer();
}
