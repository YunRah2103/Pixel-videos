/**
 * Sunset Harbor V4 — deterministic, hand-clustered character acting and life.
 * Each returned value is a raw SVG fragment (NO root <svg>); 360×640 coordinates.
 * Ordering for the integrator: birds over sky, water+wake over sea, boat over water,
 * characters over promenade, foreground over characters.
 * World/art/atmosphere stay in Agents 1 and 2's modules.
 */
import {getHarborMotionV4} from './HarborMotionV4.mjs';
const N=x=>Math.round(x);
const S=x=>Number.isFinite(x)?x:0;
const r=(x,y,w,h,c)=>'<rect x="'+N(x)+'" y="'+N(y)+'" width="'+Math.max(1,N(w))+'" height="'+Math.max(1,N(h))+'" fill="'+c+'"/>';
const p=(points,c)=>'<polygon points="'+points.map(q=>N(q[0])+','+N(q[1])).join(' ')+'" fill="'+c+'"/>';
const group=(x,y,body,extra='')=>'<g transform="translate('+N(x)+' '+N(y)+')" '+extra+'>'+body+'</g>';
const rotate=(angle,x,y,body)=>'<g transform="rotate('+Number(angle.toFixed(2))+' '+x+' '+y+')">'+body+'</g>';
const sine=(frame,period,phase=0)=>Math.sin(frame*2*Math.PI/period+phase);
const fade=x=>Math.max(0,Math.min(1,x));
const ease=t=>{t=fade(t);return t*t*(3-2*t);};
const makeBird=(x,y,phase,size=1)=>{
 const wing=Math.round(3*sine(phase,24,0.4)),c='#47697f';
 let q=r(0,0,4,2,c)+r(1,-1,2,1,'#7892a1');
 q+=p([[-1,0],[-7,-3-wing],[-11,-2-wing],[-7,-1],[-1,1]],c);
 q+=p([[4,0],[10,-2-wing],[13,-1-wing],[9,1],[4,1]],c);
 q+=r(4,1,2,1,'#e7bda6');
 return group(x,y,q,'scale('+size+')');
};
export function harborV4Birds(f,m){
 let svg='';
 const drift=m.birdsTravel*73;
 for(let i=0;i<5;i++){
   const baseX=48+i*23+(i%2)*8,baseY=192+i*13-(i%3)*12;
   svg+=makeBird(baseX+drift*(0.65+i*0.055),baseY+4*sine(f,91,i*0.8),f+i*8,i<2?0.95:0.75);
 }
 // A single distant gull crosses the high open sky; no synchronized flock loops.
 const alone=185+f*0.22;
 svg+=makeBird(alone,152+10*sine(f,280,1.1),f+10,.65);
 return svg;
}
export function harborV4Wake(f,m) {
 if(m.boatReveal<=0.01)return '';
 let svg='',x=m.boatX+4,y=m.boatY+14;
 for(let i=0;i<14;i++){
   const elapsed=(i*11)%103;
   const spread=6+elapsed*.15;
   const wx=x+37+elapsed*.49;
   const wy=y+(i%2?1:-1)*spread*.43+2*sine(f,35,i);
   svg+=r(wx,wy,3+(i%3)*3,1,i%4?'#85aeaa':'#e0bda2');
 }
 svg+=r(x+3,y+1,37,2,'#5d8888')+r(x+7,y+4,23,1,'#e1ba9b');
 return '<g opacity="'+(0.25+0.63*m.boatReveal).toFixed(3)+'">'+svg+'</g>';
}
export function harborV4Boat(f,m) {
 const x=m.boatX,y=m.boatY,roll=m.boatHeel,alpha=m.boatReveal;
 // Clipper-style fishing sailboat designed in coherent 1–3px clusters, not a rectangle.
 let q='';
 q+=r(-2,10,54,2,'#91acaa');
 q+=p([[0,1],[51,1],[44,13],[8,13],[3,7]],'#24394e');
 q+=p([[2,3],[49,3],[44,7],[6,7]],'#915e6d');
 q+=r(8,0,33,3,'#e4b493')+r(14,4,24,2,'#e8c4a0');
 for(let i=0;i<10;i++)q+=r(9+i*3,8+(i%3===0?1:0),2,1,i%3?'#724e60':'#c17f7c');
 q+=p([[14,-5],[29,-5],[33,1],[10,1]],'#526b79');
 q+=r(17,-8,8,3,'#ffdcb0')+r(20,-12,1,4,'#3d5263');
 // Mast, asymmetric warm sail, seam stitches and fluttering pennant.
 q+=r(31,-52,2,53,'#354a5b')+r(32,-47,1,45,'#e6b59b');
 q+=p([[29,-48],[29,-7],[11,-8],[14,-22],[19,-36]],'#f6dfbf');
 q+=p([[28,-44],[27,-11],[16,-11],[17,-18],[23,-32]],'#e3b5a8');
 q+=p([[34,-38],[36+m.sailFlutter,-8],[46,-7],[41,-26]],'#f5d0a9');
 q+=r(21,-36,2,2,'#fff1d0')+r(15,-17,8,1,'#fff1cf');
 q+=p([[33,-51],[44+m.sailFlutter,-49],[34,-46]],'#dc8b8c');
 // Visible human sailor leaning under the sail.
 q+=r(36,-8,5,8,'#3a6373')+r(35,-14,7,7,'#deb199')+r(34,-16,8,3,'#425368');
 q+=r(40,-8,3,3,'#ba8584')+r(18,12,25,1,'#c89d92');
 return '<g opacity="'+alpha.toFixed(3)+'" transform="translate('+N(x)+' '+N(y)+') rotate('+roll.toFixed(2)+' 26 6)">'+q+'</g>';
}
function personA(f,m){
 // Actor A: teal fisher's coat, beret, scarf; joined arm and torso rotations.
 const walk=m.firstStep,step=sine(f,18,.4)*walk,meet=m.meet;
 const x=210+9*meet, y=493+(walk>0.05?Math.abs(step)*1.5:0);
 let q=r(-7,44,29,2,'#263f50');
 // Pivot each leg independently rather than translate a solid character.
 q+=rotate(10*step,6,32,r(2,29,5,17,'#283e50')+r(2,44,9,3,'#263447'));
 q+=rotate(-11*step,13,32,r(12,29,5,17,'#344354')+r(12,44,9,3,'#28394b'));
 q+=p([[1,15],[16,15],[21,34],[-3,34]],'#537c89');
 q+=p([[1,16],[7,17],[8,32],[-2,32]],'#376476');
 q+=p([[9,17],[16,15],[20,31],[13,29]],'#79a0a0');
 q+=r(7,15,3,17,'#bf9b94')+r(0,33,20,2,'#3e6170');
 for(let i=0;i<4;i++)q+=r(11,20+i*4,1,1,'#f1d5aa');
 // Cloth hems ripple only in the breeze.
 q+=p([[17,27],[21,29],[22+m.coatBreeze*1.8,36],[16,33]],'#6d9299');
 // Arms: elbow and wrist are separate articulating segments.
 q+=rotate(-8-13*walk,-1,17,
   r(-5,17,5,15,'#406a79')+r(-6,30,5,4,'#dda995'));
 const reaching=-8-46*m.handhold+8*sine(f,140,1)*walk;
 q+=rotate(reaching,18,18,
   r(17,16,5,15,'#517988')+
   rotate(-19*m.handhold,19,29,r(18,28,4,9,'#d8a993')));
 // Hair, ear, brows, eye and mouth have distinct 1-pixel expression changes.
 q+=r(3,1,13,14,'#dca98f')+r(4,4,10,7,'#e9b79a')+
    r(2,5,3,7,'#835969')+r(4,-2,13,5,'#454b64')+
    r(2,-4,16,4,'#587084')+r(7,-5,7,3,'#3c5369')+
    r(14,5,3,4,'#c48c7f')+r(12,7,1,1,'#4c485b')+
    r(12,10+m.blinking,2,1,'#9c626b');
 q+=r(5,14,10,3,'#c98883')+
    p([[12,14],[17,17],[17+m.coatBreeze*3,25],[14,22]],'#e5ab9a')+
    r(8,18,7,2,'#f2c6a9');
 // Ephemeral cheek highlight as A turns to meet B.
 if(m.glance>0.25)q+=r(14,9,2,1,'#f7c5a8');
 return group(x,y,q);
}
function personB(f,m){
 // Actor B: lavender cape with a hair ribbon; head and free arm respond to A.
 const x=251-7*m.meet, y=491;
 const lean=2*m.glance+0.7*sine(f,156,.7);
 let q=r(-8,47,32,2,'#253b50');
 q+=rotate(2*sine(f,87)*m.nextStep,5,35,r(3,33,5,15,'#2d4258')+r(0,46,10,3,'#29394d'));
 q+=rotate(-8*m.nextStep,13,35,r(12,34,6,14,'#344459')+r(12,46,10,3,'#29394d'));
 q+=p([[-1,15],[15,14],[22,37],[-5,37]],'#a27d99');
 q+=p([[8,15],[19,18],[24,36],[11,35]],'#cc98a5');
 q+=p([[-1,15],[4,18],[0,32],[-5,36]],'#785f85');
 for(let i=0;i<5;i++)q+=r(-2+i*4,35+(i%2),2,2,i%2?'#d3a2a1':'#77577c');
 q+=rotate(-5+7*m.glance,17,17,r(16,18,5,17,'#ac7994')+r(17,32,5,5,'#e6b6a1'));
 q+=rotate(11-48*m.handhold,0,18,r(-4,17,5,16,'#9f7592')+r(-5,31,5,5,'#e8b59f'));
 // Loose hair, cheek, expressive glance and lashes.
 q+=rotate(-lean,8,7,
   r(2,-1,13,17,'#4c4563')+
   r(4,2,10,13,'#e6b399')+
   r(2,3,3,10,'#635169')+
   r(2,-3,15,5,'#55435c')+
   r(12,4,5,7,'#4e3e55')+
   r(5,7,1,1,'#4b5262')+
   r(6,10,3,1,m.quietSmile>0.4?'#b57479':'#9e7277')+
   r(5,6,4,1,'#6c5265')+
   r(14,0,3,9,'#76607d'));
 q+=r(5,15,8,3,'#eabf9f')+
   p([[8,16],[14,17],[17+m.coatBreeze*2,26],[10,20]],'#eeb0a1');
 q+=r(13,0,4,2,'#e6aa9c')+r(15,-4,3,6,'#a46f85');
 return group(x,y,q);
}
function joinedHands(m){
 if(m.handhold<0.08)return '';
 const a=219+2*m.meet,y=521;
 const hand=fade(m.handhold);
 // Connect only when limbs have reached, not from frame zero.
 return '<g opacity="'+Math.min(1,hand*2.5).toFixed(3)+'">'+
   r(a+5,y,6,3,'#dfad95')+r(a+10,y+1,4,2,'#e5b89d')+
   (m.handhold>0.7?r(a+8,y+3,3,2,'#f2c8a6'):'')+'</g>';
}
export function harborV4Characters(f,m){
 // Animate two independent actors; the held hand contact is a specific final beat.
 return personA(f,m)+personB(f,m)+joinedHands(m);
}
export function harborV4Cat(f,m){
 const walking=1-m.catSit, stride=sine(m.catStep,Math.PI*2)*walking;
 const x=m.catX,y=541+(walking?Math.abs(stride)*1.2:2*m.catSit);
 let q=r(-1,13,30,2,'#263e50');
 q+=r(2,1,20,11,'#2b3c4d')+r(8,0,13,6,'#3c4b5c');
 q+=p([[18,2],[19,-5],[22,0],[24,-5],[28,3],[27,11],[17,10]],'#29394b');
 q+=r(20,-2,2,3,'#be8990')+r(24,-2,2,3,'#bc868d')+
    r(25,4,2,1,'#fae2ae')+r(22,8,2,1,'#ddaa98');
 // Opposed front and back paws only move while actually walking.
 q+=r(3,9,4,4+Math.max(0,2*stride),'#263748')+
    r(10,9+Math.max(0,-2*stride),4,5,'#29394b')+
    r(19,10,4,4+Math.max(0,-2*stride),'#283a4b');
 // Deliberate sit pose sinks rear haunch; tail curls beside paws.
 if(m.catSit>0.1)q+=r(1,7,17,7,'#344152')+r(6,12,15,3,'#263849');
 q+=r(-3,4,5,3,'#283a4c')+
    r(-6,-2+m.catTail*2,4,8,'#28394c')+
    r(-8,-5+m.catTail*2,4,4,'#33475a')+
    r(-10,-7+m.catTail*2,3,3,'#3c4c5d');
 return group(x,y,q);
}
export function harborV4Foreground(f,m){
 let svg='';
 // Near-plane reed flowerheads, deliberate irregular silhouettes.
 for(let i=0;i<19;i++){
   const x=(i*47+11)%359,y=624+i%6*3;
   const sway=Math.round(sine(f,89+i%7*8,i*1.2)*2.3 +m.foliageSway*(i%3?0.6:1.15));
   svg+=r(x,y-22-(i%3)*5,1,26,'#365f60');
   svg+=p([[x,y-14],[x-4+sway,y-18],[x-7+sway,y-17],[x-3,y-10]],i%2?'#67927c':'#8cac90');
   svg+=r(x+sway,y-26-i%3*5,3,3,i%4?'#df989f':'#f1c09f');
 }
 // An occasional petal crosses the lovers during the last musical phrase.
 for(let i=0;i<7;i++){
   const progress=((f*0.26+i*57)%315)/315;
   const x=32+i*48+progress*8+sine(f,100,i)*4;
   const y=562-progress*61+(i%3)*8;
   svg+=r(x,y,2+(i%3===0?1:0),2,i%2?'#d7a3a4':'#e7c1a9');
 }
 // Final sun-kissed edge of the railing, brighter precisely as camera comes to rest.
 if(m.finalGlint>0.07)svg+='<g opacity="'+(m.finalGlint*.55).toFixed(3)+'">'+r(195,506,73,1,'#fff0bf')+r(264,507,21,1,'#f7d8aa')+'</g>';
 return svg;
}
/** Independent source layers for V4 integration. Fragments never include root svg tags. */
export function renderHarborLifeV4(frame=0,motion){
 const m=motion||getHarborMotionV4(frame),f=m.frame??frame;
 const birds=harborV4Birds(f,m);
 const water=harborV4Wake(f,m);
 const boat=harborV4Boat(f,m);
 const characters=harborV4Characters(f,m);
 const cat=harborV4Cat(f,m);
 const foreground=harborV4Foreground(f,m);
 return {birds,water,boat,characters,cat,foreground,
   sky:birds,waterHighlights:water,actors:characters+cat,
   // Legacy-friendly name, still a RAW SVG FRAGMENT, not a wrapper.
   combined:birds+water+boat+characters+cat+foreground};
}
