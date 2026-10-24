/** Hard gate for actual PR #33/#32/#30 native-pixel sources; no demo art fallback. */
import {existsSync,mkdirSync,writeFileSync} from 'node:fs';
const required=[
 ['PR #33 native world master','studio/countryside/world/build-world-v2.mjs'],
 ['PR #33 native layer compositor','src/scenes/countryside/WorldLayers.tsx'],
 ['PR #32 192px coupe master','studio/countryside/car/build-car-v2.mjs'],
 ['PR #32 V2 grounded car renderer','src/scenes/countryside/CarLayer.tsx'],
 ['PR #32 body sprite','public/countryside/car/coupe-v2-body.png'],
 ['PR #32 eight wheel poses','public/countryside/car/coupe-v2-wheels-8.png'],
 ['PR #30 road-driven motion','src/scenes/countryside/DrivingMotion.ts'],
 ['PR #33 manifest','public/countryside/world/manifest.json'],
 ...['sky','farTrees','midTrees','nearTrees','verge','road'].map(n=>['V2 native world '+n,'public/countryside/world/'+n+'.png']),
];
const missing=required.filter(([,p])=>!existsSync(p));
const report={ready:!missing.length,required,missing,assessedAt:new Date().toISOString()};
mkdirSync('out/countryside-final-qa',{recursive:true});
writeFileSync('out/countryside-final-qa/readiness.json',JSON.stringify(report,null,2)+'\n');
if(missing.length){console.error('COUNTRYSIDE_V2_NOT_READY '+JSON.stringify(missing));process.exitCode=1;}
else console.log('COUNTRYSIDE_V2_NATIVE_ASSETS_READY');
