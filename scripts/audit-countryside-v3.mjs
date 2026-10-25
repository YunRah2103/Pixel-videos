/**
 * Countryside V3 production audit.
 * This is a strict existence/wiring PRE-FLIGHT, not proof that GUI programs
 * actually ran: PR reviewers must still inspect native files + real logs.
 * Never convert missing evidence into a "pass".
 */
import {readFileSync, existsSync, readdirSync, mkdirSync, writeFileSync} from 'node:fs';
import {extname, join, dirname, resolve} from 'node:path';

const cwd=process.cwd();
const strict=process.argv.includes('--strict');
const result={revision:'countryside-v3',status:'BLOCKED',technicalBaseline:'V2',
  machineChecks:[],manualChecksRequired:[],missing:[],generatedAt:new Date().toISOString()};
const all=[];
function walk(p){if(!existsSync(p))return;for(const d of readdirSync(p,{withFileTypes:true})){
  const f=join(p,d.name);if(d.isDirectory()){if(!['node_modules','.git','out','.cache'].includes(d.name))walk(f);}
  else all.push(f.replaceAll('\\','/'));
}}
walk('studio/countryside');walk('src/scenes/countryside');walk('public/countryside');walk('evidence/countryside-v3');
function check(label,ok,detail){result.machineChecks.push({label,pass:!!ok,detail});if(!ok)result.missing.push(label);}
function native(label,extensions,parts=[]){let matches=all.filter(f=>extensions.includes(extname(f).toLowerCase())&&parts.every(p=>f.toLowerCase().includes(p)));
  check(label,matches.length>0,matches);return matches;}
function evidence(agent,requiredFields){const p='evidence/countryside-v3/'+agent+'/tool-execution.json';
 let a=null;try{a=JSON.parse(readFileSync(p,'utf8'))}catch{}
 check(agent+' committed tool-execution evidence',!!a,p);
 if(a)for(const field of requiredFields){check(agent+' evidence '+field,typeof a[field]==='string'&&a[field].length>8,field);}
 return a;
}
// Pixelorama and Krita can both edit legitimate layered .ora projects.
 // Their own native .pxo / .kra extensions are welcome, but not required.
 // Require an original editable art pipeline + independently verifiable CI
 // artifact, not extension theatre or a mere package installation.
const ev1=evidence('agent1',['pixeloramaRunUrl','kritaRunUrl','ldtkRunUrl','originalArtArtifactUrl']);
const ev2=evidence('agent2',['pixeloramaRunUrl','originalArtArtifactUrl']);
const ev3=evidence('agent3',['pixiRunUrl','proofRunUrl']);
native('Agent 1 actual LDtk countryside layout',['.ldtk'],['world']);
const originalWorld=all.some(f=>/studio\/countryside\/world\/.*\.(pxo|kra|ora)$/.test(f))
  || existsSync('scripts/build-v3-openraster.py');
check('Agent 1 editable original pixel source (.ora/.pxo/.kra or reproducible source)',originalWorld,
  'Krita and Pixelorama must perform verifiable genuine import/edit/export on layered original');
const originalCar=all.some(f=>/studio\/countryside\/car\/.*\.(pxo|ora)$/.test(f))
  || existsSync('studio/countryside/car/build-car-v3.py');
check('Agent 2 original layered car sprite source (.ora/.pxo or reproducible source)',originalCar,
  'Pixelorama output logs and downloadable original must be independently checked');

/* Walk real Remotion import graph, rather than accepting a dead PixiJS test. */
const start='src/scenes/countryside/CountrysideDrive.tsx',seen=new Set();
let connectedPixi=false,pixiProductionFiles=[];
function readGraph(file){
 if(seen.has(file)||!existsSync(file))return;
 seen.add(file);const code=readFileSync(file,'utf8');
 if(/(?:from\s*|import\s*\(\s*)['"]pixi\.js['"]/.test(code)){
   connectedPixi=true;pixiProductionFiles.push(file);
 }
 const deps=[...code.matchAll(/(?:from\s*|import\s*\(\s*)['"](\.[^'"]+)['"]/g)];
 for(const [,d] of deps){
  const base=resolve(dirname(file),d);
  for(const ext of ['','.tsx','.ts','.mjs','.jsx','.js'])if(existsSync(base+ext)){readGraph(base+ext);break;}
 }
}
readGraph(start);
check('Agent 3 PixiJS actually imported in active Countryside Remotion graph',connectedPixi,pixiProductionFiles);
const root=existsSync('src/Root.tsx')?readFileSync('src/Root.tsx','utf8'):'';
check('CountrysideDrive production composition registered',root.includes('id="CountrysideDrive"'),'src/Root.tsx');
const motion=existsSync('src/scenes/countryside/CountrysideDrive.tsx')?readFileSync('src/scenes/countryside/CountrysideDrive.tsx','utf8'):'';
check('Shared distance-led wheel clock consumed in production',motion.includes('wheelRotationTurns={m.wheelRotationTurns}'),'source must avoid a second clock');
check('Actual Pixel Studio V3 toolkit scripts exist',existsSync('scripts/setup-agent-studio.mjs')&&existsSync('scripts/test-studio-rigs.mjs'),'npm run studio:setup; npm run rigs:test');
result.manualChecksRequired=[
 'Open actual layered .ora/.pxo in Pixelorama and compare pixel frames with Pixelorama-produced export and logs',
 'Open actual layered .ora/.kra in Krita and inspect real editor export/render logs',
 'Inspect .ldtk project and trace exported level into the rendered world',
 'Review execution logs referenced by tool-execution.json (self-authored claims are insufficient)',
 'Inspect Agent 3 PixiJS draw calls in the exact Remotion production path (import alone is insufficient)',
 'Watch the full 12-second decoded MP4 at mobile size and examine car, foliage, depth, seams and contact'
];
result.status=result.missing.length?'BLOCKED':'PRELIMINARY_MACHINE_PASS_REQUIRES_MANUAL_EVIDENCE';
mkdirSync('out/countryside-v3-qa',{recursive:true});
writeFileSync('out/countryside-v3-qa/tool-audit.json',JSON.stringify(result,null,2)+'\n');
console.log('COUNTRYSIDE_V3_TOOL_AUDIT '+JSON.stringify(result));
if(strict&&result.missing.length){console.error('V3 FINAL RELEASE REJECTED: unverified agent source/tools: '+result.missing.join('; '));process.exitCode=1}
