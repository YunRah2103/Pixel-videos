import {mkdirSync, writeFileSync} from 'node:fs';
import {sunsetHarborSvg} from '../src/scenes/sunsetHarborSvg.mjs';
const start=Number(process.argv[2]||0),end=Number(process.argv[3]||360);
const dest=process.argv[4]||'out/svg-frames';mkdirSync(dest,{recursive:true});
for(let f=start;f<end;f++)writeFileSync(`${dest}/frame-${String(f).padStart(4,'0')}.svg`,sunsetHarborSvg(f));
console.log(`Wrote ${end-start} original SVG frames`);