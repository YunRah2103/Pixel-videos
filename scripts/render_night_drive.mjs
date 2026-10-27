import {spawnSync} from 'node:child_process';
import {existsSync, mkdirSync, rmSync} from 'node:fs';

// Usage: node scripts/render_night_drive.mjs [--audio path/to/audio-or-video] [--out out/night-drive-1080p.mp4]
const arg = (name, fallback) => {
  const i = process.argv.indexOf(name);
  return i > -1 ? process.argv[i + 1] : fallback;
};
const audio = arg('--audio');
const out = arg('--out', 'out/night-drive-1080p.mp4');
const frames = 'out/night-drive-frames';
const run = (cmd, args) => {
  const r = spawnSync(cmd, args, {stdio: 'inherit'});
  if (r.status !== 0) process.exit(r.status ?? 1);
};

mkdirSync('out', {recursive: true});
rmSync(frames, {recursive: true, force: true});
const npx = process.platform === 'win32' ? 'npx.cmd' : 'npx';
const browser = process.env.REMOTION_BROWSER ? [`--browser-executable=${process.env.REMOTION_BROWSER}`] : [];
// PNG frames avoid the chroma smearing yuv420 would add to a 180x320 render.
run(npx, ['remotion', 'render', 'src/index.ts', 'NightDrive', frames, '--sequence', '--image-format=png', ...browser]);

const inputs = ['-framerate', '30', '-i', `${frames}/element-%03d.png`];
if (audio && existsSync(audio)) inputs.push('-i', audio);
const maps = audio && existsSync(audio) ? ['-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-shortest'] : [];
run('ffmpeg', ['-y', ...inputs, ...maps, '-vf', 'scale=1080:1920:flags=neighbor,format=yuv420p', '-c:v', 'libx264', '-crf', '14', '-movflags', '+faststart', out]);
console.log(`Done: ${out}`);
