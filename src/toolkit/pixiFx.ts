/**
 * Optional PixiJS v8 WebGL-only effects for selected planes.
 * Create once per composition, then setFrame(...) with Remotion's frame index.
 * Do NOT blur an entire native pixel-art scene or use wall-clock time.
 */
import {Filter} from 'pixi.js';

const vertexGL = [
 'in vec2 aPosition;',
 'out vec2 vTextureCoord;',
 'uniform vec4 uInputSize;',
 'uniform vec4 uOutputFrame;',
 'uniform vec4 uOutputTexture;',
 'vec4 filterVertexPosition(void) {',
 ' vec2 p=aPosition*uOutputFrame.zw+uOutputFrame.xy;',
 ' p.x=p.x*(2.0/uOutputTexture.x)-1.0;',
 ' p.y=p.y*(2.0*uOutputTexture.z/uOutputTexture.y)-uOutputTexture.z;',
 ' return vec4(p,0.0,1.0);',
 '}',
 'void main(void) {',
 ' gl_Position=filterVertexPosition();',
 ' vTextureCoord=aPosition*(uOutputFrame.zw*uInputSize.zw);',
 '}'
].join('\n');

const waterGL = [
 'in vec2 vTextureCoord;',
 'out vec4 finalColor;',
 'uniform sampler2D uTexture;',
 'uniform float uFrame;',
 'uniform float uStrength;',
 'void main(void) {',
 ' vec2 uv = vTextureCoord;',
 ' float offset = sin(uv.y*55.0 + uFrame*0.13)*0.003*uStrength;',
 ' offset += sin(uv.y*112.0 - uFrame*0.085)*0.0015*uStrength;',
 ' uv.x = clamp(uv.x + offset, 0.0, 1.0);',
 ' vec4 pixel = texture(uTexture, uv);',
 ' float sparkle = max(0.0, sin(uv.y*155.0 + uFrame*0.12 + uv.x*17.0));',
 ' sparkle = step(0.94,sparkle) * 0.045*uStrength;',
 ' finalColor = vec4(min(vec3(1.0),pixel.rgb+vec3(sparkle*1.0,sparkle*0.72,sparkle*0.37)),pixel.a);',
 '}'
].join('\n');
const windowGL = [
 'in vec2 vTextureCoord;',
 'out vec4 finalColor;',
 'uniform sampler2D uTexture;',
 'uniform float uFrame;',
 'uniform float uStrength;',
 'void main(void) {',
 ' vec4 p = texture(uTexture,vTextureCoord);',
 ' float warm = clamp(p.r-p.b*0.7,0.0,1.0);',
 ' float flicker=0.985+0.015*sin(uFrame*0.035);',
 ' p.rgb = min(vec3(1.0),p.rgb+warm*uStrength*flicker*vec3(0.07,0.035,0.0));',
 ' finalColor=p;',
 '}'
].join('\n');
export type PixelFilterController = { filter:Filter; setFrame:(frame:number)=>void };
function makeFilter(fragment:string,strength:number):PixelFilterController {
 if(!Number.isFinite(strength)||strength<0||strength>2)throw Error('strength must be in 0..2');
 const filter=Filter.from({
   gl:{vertex:vertexGL,fragment},
   resources:{motionUniforms:{uFrame:{value:0,type:'f32'},uStrength:{value:strength,type:'f32'}}}
 });
 return {filter,setFrame(frame:number){
  if(!Number.isInteger(frame)||frame<0)throw Error('frame must be a nonnegative integer');
  (filter.resources.motionUniforms as any).uniforms.uFrame=frame;
 }};
}
export function createPixelWaterFilter(strength=0.6):PixelFilterController {
 return makeFilter(waterGL,strength);
}
export function createWarmWindowFilter(strength=0.5):PixelFilterController {
 return makeFilter(windowGL,strength);
}
/** Deterministic occasional embers, fireflies and leaf motes. */
export function pixelMotes(frame:number,count=18,seed=31){
 if(frame<0||!Number.isInteger(frame)||count<0||count>250)throw Error('Invalid particle frame/count');
 const frac=(x:number)=>x-Math.floor(x);
 return Array.from({length:count},(_,i)=>{
  const base=frac(Math.sin(i*124.71+seed*93.13)*43758.5453);
  const phase=frac(Math.sin(i*24.85+seed*7.03)*13579.2468);
  const t=(frame%450)/450;
  return {x:frac(base+Math.sin(frame*.015+i)*.009),y:frac(phase-t*.23+1),opacity:.25+.55*frac(i*.618)};
 });
}
