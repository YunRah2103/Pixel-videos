/** Stable, frame-addressable pixel-cinema controls for Remotion or Pixi. */
export type ParallaxName='far'|'architecture'|'harbor'|'promenade'|'foreground';
const depth:Record<ParallaxName,number>={far:.08,architecture:.28,harbor:.52,promenade:.8,foreground:1.1};
const clamp=(v:number,a=0,b=1)=>Math.max(a,Math.min(b,v));
export const easeInOut=(t:number)=>{const x=clamp(t);return x*x*(3-2*x);};
export function cinematicCamera(frame:number,duration=360){
 if(!Number.isInteger(frame)||frame<0||duration<2)throw Error('Bad film frames');
 const t=easeInOut(frame/(duration-1));
 return {x:-9*t,y:-4*t,zoom:1+0.075*t,focusX:180,focusY:400};
}
export function parallaxTransform(plane:ParallaxName,frame:number,duration=360){
 const c=cinematicCamera(frame,duration),z=1+(c.zoom-1)*depth[plane];
 return {translateX:c.x*depth[plane],translateY:c.y*depth[plane],scale:z};
}
export function spriteFrame(frame:number,stepFrames:number,totalFrames:number){
 if(frame<0||stepFrames<1||totalFrames<1||!Number.isInteger(frame))throw Error('Invalid sprite timing');
 return Math.floor(frame/stepFrames)%totalFrames;
}
export function waveSurface(frame:number,x:number){
 return Math.sin(x*.095+frame*.13)*1.35+Math.sin(x*.027-frame*.045)*.65;
}
