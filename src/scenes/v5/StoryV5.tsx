import React from 'react';
import {getV5Motion} from './MotionV5.mjs';

/**
 * ORIGINAL HAND-AUTHORED V5 PIXEL SPRITES.
 * Native canvas 360x640. Plane SVG fragments have NO baked camera transforms.
 * No raster scaling, external character assets, mutable animation or timers.
 */
const n=(v:number)=>Math.round(v);
const R=(x:number,y:number,w:number,h:number,c:string,a=1)=>
 w<=0||h<=0?'': '<rect x="'+n(x)+'" y="'+n(y)+'" width="'+Math.max(1,n(w))+
 '" height="'+Math.max(1,n(h))+'" fill="'+c+'"'+(a===1?'':' opacity="'+a.toFixed(3)+'"')+'/>';
const P=(points:number[][],c:string,a=1)=>
 '<polygon points="'+points.map(p=>n(p[0])+','+n(p[1])).join(' ')+
 '" fill="'+c+'"'+(a===1?'':' opacity="'+a.toFixed(3)+'"')+'/>';
const G=(x:number,y:number,body:string,extra='')=>
 '<g transform="translate('+n(x)+' '+n(y)+')'+(extra?' '+extra:'')+'">'+body+'</g>';
const rot=(degrees:number,cx:number,cy:number,body:string)=>
 '<g transform="rotate('+degrees.toFixed(2)+' '+cx+' '+cy+')">'+body+'</g>';
const clamp=(x:number,a=0,b=1)=>Math.min(b,Math.max(a,x));
const wave=(f:number,p:number,o=0)=>Math.sin(f*Math.PI*2/p+o);
const head=(hair:string,skin:string,highlight:string,blink:boolean,turn:number,smile:boolean)=>{
 let q='';
 // Geometric individual hair clusters and 1px face markings with shaded neck.
 q+=P([[-9,0],[-7,-5],[-3,-8],[4,-8],[9,-4],[10,6],[8,10],[-9,9]],hair);
 q+=P([[-6,-1],[5,-3],[8,3],[7,11],[3,15],[-4,14],[-8,9]],skin);
 q+=R(-5,1,4,3,highlight)+R(-8,3,2,7,hair)+R(6,0,3,5,hair);
 q+=R(turn>0.45?2:4,6,blink?4:2,blink?1:2,'#464558');
 q+=R(turn>0.45?-4:0,7,1,1,'#795764');
 q+=R(1,12,smile?4:2,1,smile?'#ac6376':'#9b777b');
 q+=R(-4,14,9,4,'#ca908b')+R(5,10,2,2,'#e7b69b');
 return q;
};
function sleeveArm(ax:number,ay:number,endx:number,endy:number,c:string,lit:string,skin:string){
 const elbowX=ax+(endx-ax)*.54,elbowY=ay+(endy-ay)*.56+2;
 return P([[ax-3,ay-2],[ax+3,ay],[elbowX+3,elbowY],[endx+2,endy],
 [endx-2,endy+2],[elbowX-3,elbowY+3]],c)+
 P([[ax+1,ay],[elbowX+2,elbowY],[endx,endy]],lit)+R(endx-2,endy-1,5,4,skin);
}
function legs(x:number,fy:number,lx:number,ly:number,rx:number,ry:number){
 // Two independent knee joints; their shoe anchors do not move while planted.
 const hipL=x-4,hipR=x+5;
 const kneeL=(hipL+lx)*.55-1,kneeR=(hipR+rx)*.56+1;
 let q=P([[hipL-3,527],[hipL+2,527],[kneeL+3,537],[lx+2,ly-5],
  [lx-3,ly-5],[kneeL-2,536]],'#273b50');
 q+=P([[hipR-2,527],[hipR+4,527],[kneeR+3,537],[rx+3,ry-5],
  [rx-2,ry-5],[kneeR-2,537]],'#37475b');
 q+=R(lx-5,ly-4,10,4,'#263447')+R(lx-6,ly-2,11,2,'#202f40');
 q+=R(rx-3,ry-4,10,4,'#2b3548')+R(rx-3,ry-2,11,2,'#202f40');
 q+=R(hipL-2,529,2,4,'#5b6372')+R(hipR+1,529,2,4,'#77808a');
 return q;
}
function personOne(f:number,m:any){
 const x=m.actorX,feet=m.actorFeet;
 const glance=m.actorLook,reach=m.reach,wind=m.scarfWind;
 const bob=feet.walk?Math.sin(Math.PI*feet.phase)*1.25:0;
 // Foot shadows remain in scene-space even when hips lift.
 let q=R(feet.leftX-7,550,15,2,'#21384b',.68)+
 R(feet.rightX-6,550,14,2,'#25394e',.52);
 q+=legs(x,550,feet.leftX,feet.leftY,feet.rightX,feet.rightY);
 const skin='#dfad97';
 let body='';
 // Sculpted coat silhouette: waist taper, turned collar, asymmetrical coat hem.
 body+=P([[-9,497],[-3,494],[8,495],[12,504],[10,528],[3,534],[-10,532],[-12,517]],'#365f74');
 body+=P([[-7,499],[-1,499],[-3,526],[-8,531],[-11,522]],'#4b7c88');
 body+=P([[3,498],[10,502],[9,524],[4,533],[1,530]],'#7c9b99');
 body+=P([[5,519],[13,526+wind*.45],[9+wind*1.4,534],[3,531]],'#527787');
 body+=R(-1,500,3,28,'#c39e98')+R(-2,528,10,3,'#314d62');
 for(let i=0;i<3;i++)body+=R(3,509+i*6,1,1,'#f6cfaa');
 // Walk cycle influences free elbow only while moving.
 body+=sleeveArm(-9,502,-12-(feet.walk?2:0),519+Math.sin(f/9)*2,
  '#365e74','#62909a',skin).replaceAll('NaN','0');
 // The reaching sleeve is drawn in world-coordinates OUTSIDE the translated body.
 q+=G(x,-bob,body);
 const rightHandX=x+12+9*reach,rightHandY=522-4*reach;
 q+=sleeveArm(x+9,503,rightHandX,rightHandY,'#4b7583','#8ba8a4',skin);
 // The neck/head have independent deliberate orientation and brief natural blinks.
 let portrait='';
 portrait+=R(-4,493,8,7,skin);
 portrait+=rot(-glance*8,0,489,head('#3a485f','#e4b397','#f1c3a3',m.blinkA,glance,m.quietSmile>.6));
 // Beret and rim shading; asymmetric original silhouette.
 portrait+=P([[-11,480],[-8,475],[2,474],[8,478],[9,481],[-11,482]],'#4d6071');
 portrait+=R(-13,481,20,3,'#263e54')+R(-5,474,6,2,'#74838c');
 // Scarf grows from neck and blows at the current wind direction.
 portrait+=P([[-4,496],[8,495],[11,500],[1,503],[-6,502]],'#efa99a');
 portrait+=P([[6,499],[12,501],[13+wind*3.1,512+wind*.5],[7,508]],'#d7868a');
 portrait+=R(-5,499,3,4,'#ffe0b7');
 q+=G(x,-bob,portrait);
 return q;
}
function personTwo(f:number,m:any){
 const x=m.partnerX,look=m.partnerLook,hold=m.reach,wind=m.scarfWind;
 const skin='#edbaa2',sway=.5*wave(f,149,1.3);
 let q=R(x-13,552,29,2,'#203749',.59);
 // Steady foot contact; a single small weight-shift, NO looping treadmill.
 q+=P([[x-6,527],[x-2,527],[x-4,547],[x-11,551],[x-13,548]],'#394454');
 q+=P([[x+4,526],[x+10,526],[x+9,547],[x+2,551],[x,548]],'#283b50');
 q+=R(x-13,548,11,3,'#253447')+R(x,548,12,3,'#28384b');
 let coat='';
 coat+=P([[-9,496],[3,493],[12,498],[15,519],[18+wind,536],[6,538],
  [-15,537],[-13,523]],'#9c758f');
 coat+=P([[-7,496],[-1,496],[-5,526],[-14,536],[-13,510]],'#78647f');
 coat+=P([[3,497],[10,499],[16,535],[6,536],[3,522]],'#d6a0ad');
 coat+=P([[0,517],[6,520],[11,536],[-4,537]],'#b28aa0');
 for(let i=0;i<5;i++)coat+=R(-11+i*5,536+i%2,3,2,i%2?'#f0b1aa':'#705f80');
 q+=G(x,sway,coat);
 // The left sleeve raises as the person accepts the other person's hand.
 const leftX=x-8-7*hold,leftY=524-7*hold;
 q+=sleeveArm(x-9,500,leftX,leftY,'#876783','#c296a5',skin);
 q+=sleeveArm(x+10,501,x+15+1.5*wave(f,87),518,
  '#ac8299','#deb0b0',skin);
 let portrait='';
 portrait+=R(-4,493,8,7,skin);
 portrait+=rot(look*9,0,488,
  head('#51435f',skin,'#f8c9b0',m.blinkB,look,m.quietSmile>.4));
 // Wind-swept bangs, ribbon and layered hair must move with the body.
 portrait+=P([[-11,484],[-12,478],[-7,474],[0,473],[7,477],[10,484],
  [8,491],[5,483]],'#52445c');
 portrait+=P([[-11,482],[-14-wind,486],[-12-wind,500],[-8,498]],'#6b5270');
 portrait+=R(-5,475,6,2,'#8c6882');
 portrait+=P([[5,479],[11,474],[13,477],[10,482]],'#dd98a5');
 portrait+=P([[11,474],[16+wind*2,470],[14,480]],'#f1aab1');
 portrait+=P([[-3,498],[4,498],[10,505],[-4,504]],'#f0b9a8');
 portrait+=P([[6,502],[10,503],[10+wind*2,515],[5,510]],'#f0a6a3');
 q+=G(x,sway,portrait);
 if(m.handsJoined>.03){
  const alpha=clamp(m.handsJoined);
  // Small connected knuckles appear only AFTER wrists actually meet.
  q+='<g opacity="'+alpha.toFixed(3)+'">'+
   R(231,517,6,3,'#e9b59e')+R(234,519,3,2,'#f5c7ac')+'</g>';
 }
 return q;
}
function cat(f:number,m:any){
 const x=m.catX,y=m.catY,move=1-m.catSit;
 const phase=m.catStride*2*Math.PI;
 const s=wave(f,103,.1),stride=Math.sin(phase);
 const liftA=Math.max(0,stride)*3*move,liftB=Math.max(0,-stride)*3*move;
 let q=R(x-12,y+1,30,2,'#203749',.58);
 const tailY=-Math.round(3*s*move);
 q+=G(x,y-15,
  R(-10,-1,6,6,'#364358')+R(-13,-5+tailY,4,8,'#35465a')+
  R(-15,-10+tailY,5,5,'#40516a')+
  P([[-9,-1],[-6,-8],[6,-9],[11,-5],[9,1],[-8,2]],'#33445a')+
  P([[-5,-7],[5,-8],[10,-5],[4,-4]],'#586276')+
  P([[6,-8],[9,-16],[12,-10],[15,-16],[19,-8],[18,0],[8,0]],'#2b3d51')+
  R(10,-12,2,2,'#d18e9b')+R(15,-12,2,2,'#d18e9b')+
  R(16,-5,2,1,'#f2d5a9')+R(13,-2,2,1,'#d49791'));
 q+=R(x-8,y-5-liftA,3,6+liftA,'#27384c')+
 R(x+1,y-5-liftB,3,6+liftB,'#2b3c4e')+
 R(x+11,y-5-liftA,3,6+liftA,'#283849');
 if(m.catSit>.01){
  // Sit sinks haunch to the same contact point rather than teleporting sprite.
  const alpha=clamp(m.catSit);
  q+='<g opacity="'+alpha.toFixed(3)+'">'+
   R(x-8,y-11,15,11,'#354659')+R(x-9,y-4,20,5,'#293d50')+
   R(x+10,y-5,4,5,'#273b4e')+'</g>';
 }
 return q;
}
function vessel(f:number,m:any){
 const x=m.boatX,y=m.boatY;
 const flutter=m.sailFlutter;
 let q='';
 // Sea-contact pitch about the hull, not a floating flat sprite.
 q+=R(-4,10,60,2,'#96ada5');
 q+=P([[0,0],[53,0],[48,12],[11,13],[5,9]],'#263d51');
 q+=P([[2,2],[51,2],[47,6],[7,7]],'#a9696d');
 q+=P([[9,3],[48,4],[41,8],[12,9]],'#d59a85');
 q+=R(9,10,36,2,'#4d6f73')+R(15,11,23,1,'#e8bca1');
 q+=P([[12,-3],[29,-3],[35,1],[10,1]],'#4a6072');
 q+=R(16,-5,10,3,'#fff0c8')+R(20,-12,2,9,'#2e455b');
 // Original asymmetric mainsail, reinforced seam and boom.
 q+=R(29,-57,2,58,'#2e485c')+R(30,-53,1,44,'#f7cca5');
 q+=P([[28,-51],[27,-7],[4,-8],[8,-20],[17,-39]],'#fce3c1');
 q+=P([[26,-46],[25,-11],[11,-12],[14,-22],[19,-36]],'#dca9a4');
 q+=P([[32,-41],[39+flutter,-10],[49,-6],[42,-25]],'#efd2ae');
 q+=R(7,-7,28,2,'#aa8987')+R(7,-8,23,1,'#fff1cb');
 q+=R(18,-38,4,2,'#ffeccb')+R(13,-20,7,1,'#fff6d2');
 q+=P([[29,-56],[43+flutter,-53],[31,-49]],'#d98284');
 // Lively small sailor, scaled to the same perspective.
 q+=R(37,-14,5,6,'#d7aa98')+R(36,-16,7,3,'#3f5368');
 q+=P([[35,-8],[42,-8],[44,1],[35,1]],'#527b85');
 q+=R(38,-6,3,1,'#d2bb9d');
 return '<g opacity="'+clamp(m.boatReveal).toFixed(3)+'" transform="translate('+
  n(x)+' '+n(y)+') rotate('+m.boatHeel.toFixed(3)+' 27 7)">'+q+'</g>';
}
function wake(f:number,m:any){
 if(m.boatReveal<.02)return '';
 let out='',x=m.boatX+51,y=m.boatY+8;
 // Wake streaks derive from stern current position and age in frames; the
 // trail continues behind a LEFTWARD boat, matching hull speed and sea flow.
 for(let i=0;i<13;i++){
  const age=i*6+((f+i*13)%7);
  if(f<age)continue;
  const dx=4+age*.51,spread=2+age*.13;
  const yy=y+(i%2?1:-1)*spread*.38+wave(f+i*7,71)*1.1;
  const opacity=clamp(m.boatWake*(1-age/140)*.8);
  out+=R(x+dx,yy,3+(i%4)*2,1,i%3===0?'#f9d5b7':'#a6c9bd',opacity);
 }
 out+=R(x-1,y+2,15,1,'#f5d6ae',m.boatReveal*.8);
 return out;
}
function birds(f:number,m:any){
 let q='';
 for(let i=0;i<6;i++){
  const phase=f*(i%2?0.29:0.32)+i*17;
  const x=35+i*26+phase*.44;
  const y=167+i%3*13+wave(f,81+i*15,i*2.5)*4.1;
  const wing=Math.sin(f*Math.PI*2/(17+i*4)+i*.83)*4;
  const col=i%2?'#516779':'#3d5f71';
  q+=G(x,y,
   P([[0,0],[-3,-1],[-8,-4-wing],[-12,-3-wing],[-8,-1],[-3,2]],col)+
   P([[0,0],[4,-1],[9,-4+wing],[12,-3+wing],[8,-1],[4,2]],col)+
   R(-2,0,5,2,col));
 }
 return q;
}
function foreground(f:number,m:any){
 let q='';
 for(let i=0;i<11;i++){
  const t=(f*.26+i*57)%440;
  const x=(i*37+t*.33)%376-8;
  const y=590-(t*.21)+10*(i%4)+wave(f,70+i*3,i)*2;
  if(y<480)continue;
  const color=i%3===0?'#f3cba5':i%3===1?'#d9a3b0':'#bad0ab';
  q+=R(x,y,2+(i%4===0?1:0),2,color,.75);
 }
 if(m.finalGlint>.03){
  q+='<g opacity="'+(m.finalGlint*.7).toFixed(3)+'">'+
   R(201,512,44,1,'#fff0c7')+R(248,515,23,1,'#e9c29d')+'</g>';
 }
 return q;
}
export type V5StoryPlaneName='birds'|'waterInteraction'|'boat'|'characters'|'cat'|'foregroundLife';
export const renderV5StoryPlane=(frame:number,motion:any,plane:V5StoryPlaneName):string=>{
 const m=motion||getV5Motion(frame),f=m.frame??frame;
 switch(plane){
 case 'birds':return birds(f,m);
 case 'waterInteraction':return wake(f,m);
 case 'boat':return vessel(f,m);
 case 'characters':return personOne(f,m)+personTwo(f,m);
 case 'cat':return cat(f,m);
 case 'foregroundLife':return foreground(f,m);
 default:return '';
 }
};
const svg=(raw:string)=>'<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640" shape-rendering="crispEdges">'+raw+'</svg>';
export const V5StoryPlane:React.FC<{frame:number,motion:any,plane:V5StoryPlaneName}>=
 ({frame,motion,plane})=>{
  const content=renderV5StoryPlane(frame,motion,plane);
  return <div data-v5-plane={plane} style={{position:'absolute',inset:0,width:360,height:640,
   pointerEvents:'none',imageRendering:'pixelated'}}
    dangerouslySetInnerHTML={{__html:svg(content)}}/>;
 };
