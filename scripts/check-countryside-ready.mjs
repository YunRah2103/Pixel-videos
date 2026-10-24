/**
 * Hard gate: do not produce a fake final using demo art or missing specialists.
 * Called before npm/remotion render; intentionally fails while any agent is absent.
 */
import {existsSync, mkdirSync, writeFileSync} from 'node:fs';
import {dirname} from 'node:path';
const requirements = [
  ['#21 original car renderer', 'src/scenes/countryside/CarLayer.tsx'],
  ['#21 original body sprite', 'public/countryside/car/coupe-body.png'],
  ['#21 original eight-pose wheel sprite', 'public/countryside/car/coupe-wheels-8.png'],
  ['#22 world renderer', 'src/scenes/countryside/WorldLayers.tsx'],
  ['#23 shared motion', 'src/scenes/countryside/DrivingMotion.ts'],
  ...['sky','farTrees','midTrees','nearTrees','verge','road'].map(
    name=>['native authored world sprite: '+name,'public/countryside/world/'+name+'.png']
  ),
];
const missing = requirements.filter(([,path]) => !existsSync(path));
const status = {ready: missing.length === 0, required: requirements,
  missing, assessedAt: new Date().toISOString(),
  warning: 'Source-presence is a prerequisite, not evidence of verified quality, exported signatures, completed PRs, or moving MP4 previews.'};
const out = 'out/countryside-final-qa/readiness.json';
mkdirSync(dirname(out), {recursive:true});
writeFileSync(out,JSON.stringify(status,null,2)+'\n');
if (missing.length) {
  console.error('COUNTRYSIDE_BLOCKED: missing actual specialists:\n'+missing.map(([n,p])=>n+' -> '+p).join('\n'));
  process.exitCode=1;
} else {
  console.log('COUNTRYSIDE_SOURCE_PRESENT: verify the original authored assets, interfaces and Agent 1–3 proof renders before signing off.');
}
