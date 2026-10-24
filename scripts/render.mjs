import {spawnSync} from 'node:child_process';
import {mkdirSync} from 'node:fs';

mkdirSync('out', {recursive: true});
const npmBin = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const render = spawnSync(npmBin, ['remotion', 'render', 'src/index.ts', 'SunsetHarbor', 'out/sunset-harbor-lowres.mp4', '--codec', 'h264'], {stdio: 'inherit'});
if (render.status !== 0) process.exit(render.status ?? 1);
const upsample = spawnSync('ffmpeg', ['-y', '-i', 'out/sunset-harbor-lowres.mp4', '-vf', 'scale=1080:1920:flags=neighbor,format=yuv420p', '-c:v', 'libx264', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', 'out/sunset-harbor-1080p.mp4'], {stdio: 'inherit'});
if (upsample.status !== 0) process.exit(upsample.status ?? 1);
console.log('Done: out/sunset-harbor-1080p.mp4');
