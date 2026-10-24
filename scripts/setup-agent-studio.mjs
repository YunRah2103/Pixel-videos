#!/usr/bin/env node
/**
 * Agent quickstart. Run from repository root:
 *   npm run studio:setup
 *   npm run studio:setup -- --editors
 * --editors requests official external native desktop programs (Linux supported).
 * They are intentionally NOT committed to git or silently preinstalled.
 */
import {spawnSync} from 'node:child_process';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const argv=new Set(process.argv.slice(2));
const exec=(cmd,args)=>{
 console.log('> '+cmd+' '+args.join(' '));
 const p=spawnSync(cmd,args,{cwd:root,stdio:'inherit'});
 if(p.error||p.status!==0)throw Error(cmd+' failed with status '+(p.status??p.error));
};
const npm=process.platform==='win32'?'npm.cmd':'npm';
exec(npm,['install','--no-audit','--no-fund']);
if(argv.has('--editors')){
 const py=process.platform==='win32'?'python':'python3';
 exec(py,['scripts/install_studio_v2.py','--all']);
}
exec(npm,['run','studio:verify']);
console.log('PIXEL_STUDIO_V3_READY: core tools, atlas, original scene, rigs, lighting, MP4 proof, and objective QA verified.');
if(!argv.has('--editors'))console.log('Optional native art editors are on-demand. Re-run with --editors if needed.');

