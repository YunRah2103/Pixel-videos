import React, {useLayoutEffect, useRef} from 'react';
import {AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

// Remotion port of scripts/render_neon_offline.py: 3 original scenes, hard cuts, rain, flicker, bloom.
// Native 180x180, shown pixelated; final upscale to 720x720 is the composition size.
export const NEON_W = 180;
export const NEON_BIG = 240;
const CUTS = [2.5, 5.53];
const START = [0, 30, 36];

type RGB = [number, number, number];
const hexc = (s: string): RGB => [1, 3, 5].map((i) => parseInt(s.slice(i, i + 2), 16)) as RGB;
const mix = (a: RGB, b: RGB, k: number): RGB => [0, 1, 2].map((i) => Math.floor(a[i] + (b[i] - a[i]) * k)) as RGB;
const css = (c: RGB | string) => (typeof c === 'string' ? c : `rgb(${c[0]},${c[1]},${c[2]})`);
const H_ = (s: string) => hexc(s);

function rng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

class Pen {
  constructor(public c: CanvasRenderingContext2D) {}
  R(x0: number, y0: number, x1: number, y1: number, col: RGB | string) {
    this.c.fillStyle = css(col);
    const x = Math.round(x0), y = Math.round(y0);
    this.c.fillRect(x, y, Math.round(x1) - x + 1, Math.round(y1) - y + 1);
  }
  P(x: number, y: number, col: RGB | string) {
    this.R(x, y, x, y, col);
  }
  line(x0: number, y0: number, x1: number, y1: number, col: RGB | string, w = 1) {
    const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0), 1);
    for (let i = 0; i <= n; i++) {
      const x = Math.round(x0 + ((x1 - x0) * i) / n), y = Math.round(y0 + ((y1 - y0) * i) / n);
      this.R(x, y, x + w - 1, y + (x1 === x0 ? 0 : w - 1), col);
    }
  }
  poly(pts: [number, number][], col: RGB | string) {
    this.c.fillStyle = css(col);
    this.c.beginPath();
    pts.forEach(([x, y], i) => (i ? this.c.lineTo(x, y) : this.c.moveTo(x, y)));
    this.c.closePath();
    this.c.fill();
  }
  ellipse(x0: number, y0: number, x1: number, y1: number, fill?: RGB | string, outline?: RGB | string, width = 1) {
    const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, rx = (x1 - x0) / 2 + 0.5, ry = (y1 - y0) / 2 + 0.5;
    for (let y = Math.floor(y0); y <= Math.ceil(y1); y++)
      for (let x = Math.floor(x0); x <= Math.ceil(x1); x++) {
        const d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2;
        if (d > 1) continue;
        const inner = ((x - cx) / Math.max(rx - width, 0.1)) ** 2 + ((y - cy) / Math.max(ry - width, 0.1)) ** 2;
        if (outline && inner > 1) this.P(x, y, outline);
        else if (fill) this.P(x, y, fill);
      }
  }
  pill(x0: number, y0: number, x1: number, y1: number, r: number, col: RGB | string, w = 2) {
    this.c.strokeStyle = css(col);
    this.c.lineWidth = w;
    this.c.beginPath();
    this.c.roundRect(x0 + 1, y0 + 1, x1 - x0 - 1, y1 - y0 - 1, r);
    this.c.stroke();
  }
}

const gradient = (p: Pen, w: number, h: number, top: RGB, bot: RGB) => {
  for (let y = 0; y < h; y++) p.R(0, y, w, y, mix(top, bot, y / (h - 1)));
};
const glyphs = (p: Pen, x: number, y: number, n: number, col: RGB | string, seed: number, h = 5, gap = 2, w = 4) => {
  const r = rng(seed);
  for (let i = 0; i < n; i++) {
    const gx = x + i * (w + gap), k = 2 + Math.floor(r() * 2);
    for (let j = 0; j < k; j++) {
      if (r() < 0.5) {
        const yy = y + Math.floor(r() * h);
        p.line(gx, yy, gx + w - 1, yy, col);
      } else {
        const xx = gx + Math.floor(r() * w);
        p.line(xx, y, xx, y + h - 1, col);
      }
    }
  }
};
const windows = (p: Pen, x0: number, y0: number, cols: number, rows: number, cw: number, ch: number, on: RGB, off: RGB, seed: number, pr = 0.5) => {
  const r = rng(seed);
  for (let i = 0; i < cols; i++)
    for (let j = 0; j < rows; j++)
      p.R(x0 + i * (cw + 1), y0 + j * (ch + 1), x0 + i * (cw + 1) + cw - 1, y0 + j * (ch + 1) + ch - 1, r() < pr ? on : off);
};
const pole = (p: Pen, x: number, g: number, col: RGB) => {
  p.line(x, g - 46, x, g, col); p.line(x - 6, g - 40, x + 6, g - 40, col); p.line(x - 4, g - 34, x + 4, g - 34, col);
};
const wires = (p: Pen, x0: number, x1: number, y: number, col: RGB, sag = 4) => {
  for (let k = 0; k < 3; k++) for (let x = x0; x < x1; x++) p.P(x, Math.floor(y + k * 3 + Math.sin(((x - x0) / (x1 - x0)) * Math.PI) * sag), col);
};
const flicker = (t: number, seed: number, rate = 9) => (Math.sin(t * rate + seed) * Math.sin(t * 2.3 + seed * 2) > -0.6 ? 1 : 0.55);
const skyline = (p: Pen, y: number, x0: number, x1: number, col: RGB, seed: number, lights?: RGB, t = 0) => {
  const r = rng(seed);
  let x = x0;
  while (x < x1) {
    const w = 8 + Math.floor(r() * 9), h = 14 + Math.floor(r() * 29);
    p.R(x, y - h, x + w, y, col);
    if (lights && r() < 0.5 && Math.floor(t * 1.5 + x) % 3 === 0) p.P(x + (w >> 1), y - h - 1, lights);
    x += w + Math.floor(r() * 4);
  }
};
const steam = (p: Pen, x: number, y: number, t: number, col: RGB) => {
  for (let i = 0; i < 6; i++) {
    const yy = y - i * 4 - ((t * 10) % 4), xx = x + Math.sin(t * 2 + i) * 2;
    p.ellipse(xx - 2, yy - 1, xx + 2, yy + 1, col);
  }
};
const rain = (p: Pen, t: number, seed: number, n: number, col: RGB, speed = 70, length = 5) => {
  const r = rng(seed);
  for (let i = 0; i < n; i++) {
    const x0 = r() * NEON_BIG, y0 = r() * NEON_W, v = 0.7 + r() * 0.6;
    const y = ((y0 + t * speed * v) % (NEON_W + length)) - length;
    const x = (x0 + y * 0.15) % NEON_BIG;
    p.line(x, y, x + 1, y + length, col);
  }
};
const reflect = (c: CanvasRenderingContext2D, water: number, t: number, strength = 0.5, tint: RGB = [0, 12, 24]) => {
  const w = NEON_BIG, h = NEON_W, img = c.getImageData(0, 0, w, h), a = img.data, out = new Uint8ClampedArray(a);
  for (let y = water; y < h; y++) {
    const src = water - (y - water) - 1;
    if (src < 0) break;
    const sh = Math.round(Math.sin(y * 0.9 + t * 2.5) * (1 + (y - water) / 18)), k = Math.max(0, strength - (y - water) / 90);
    for (let x = 0; x < w; x++) {
      const sx = (((x - sh) % w) + w) % w;
      for (let ch = 0; ch < 3; ch++) out[(y * w + x) * 4 + ch] = a[(y * w + x) * 4 + ch] * (1 - k) + (a[(src * w + sx) * 4 + ch] * 0.8 + tint[ch]) * k;
    }
  }
  c.putImageData(new ImageData(out, w, h), 0, 0);
};

function sceneRoadside(p: Pen, t: number) {
  const c = p.c, B = NEON_BIG;
  gradient(p, B, 112, H_('#0e5a74'), H_('#2f95a8'));
  p.poly([[100, 112], [118, 24], [150, 8], [205, 24], [230, 112]], H_('#0a2e45'));
  p.poly([[118, 24], [150, 8], [205, 24], [196, 24], [150, 14], [124, 28]], H_('#103e57'));
  for (let dx = 0; dx < 70; dx += 1) { const yy = 22 + Math.floor(Math.sin((dx / 70) * Math.PI) * -10) + 20; p.P(135 + dx, yy, H_('#ff4a5a')); p.P(135 + dx, yy + 1, H_('#c01f3a')); }
  const r = rng(4);
  for (let i = 0; i < 26; i++) p.P(120 + Math.floor(r() * 96), 26 + Math.floor(r() * 45), H_('#e0b43c'));
  p.R(0, 96, B, 112, H_('#0b3a4d'));
  for (let x = 0; x < B; x += 3) p.line(x, 96 - ((x * 7) % 9), x, 100, H_('#082c3a'));
  pole(p, 30, 112, H_('#0a2430')); pole(p, 120, 112, H_('#0a2430'));
  wires(p, 0, 120, 78, H_('#08202c')); wires(p, 30, B, 66, H_('#08202c'), 6);
  p.R(0, 112, B, 180, H_('#0a3a4e'));
  p.R(62, 94, 120, 112, H_('#0b2733')); p.R(60, 92, 124, 95, H_('#12384a'));
  for (const [x0, col] of [[66, '#f2e3a1'], [84, '#f7e9ad'], [103, '#e9d98c']] as [number, string][]) p.R(x0, 99, x0 + 10, 108, H_(col));
  p.R(124, 98, 150, 112, H_('#0f3445'));
  p.R(8, 104, 34, 112, H_('#7fa5b5')); p.R(14, 98, 28, 104, H_('#5d8da0'));
  p.R(12, 110, 16, 113, H_('#0a1c26')); p.R(26, 110, 30, 113, H_('#0a1c26'));
  skyline(p, 98, 130, B, H_('#0c4358'), 21);
  for (const [cx, cy, cw] of [[20, 14, 40], [70, 30, 30], [150, 6, 36]]) { const ox = Math.floor(t * 3) % 30; p.R(cx + ox, cy, cx + cw + ox, cy + 3, H_('#3aa6b8')); }
  p.R(62, 100, 124, 102, H_('#2a7a8c'));
  glyphs(p, 70, 94, 7, mix(H_('#0b2733'), H_('#ff7a8a'), flicker(t, 0.7)), 17, 3, 2, 4);
  p.R(128, 100, 138, 112, H_('#5fd0e0')); p.R(130, 102, 136, 106, H_('#b8f4ff'));
  p.R(10, 100, 32, 104, H_('#9fc2d0')); p.R(12, 100, 18, 103, H_('#1a4a62'));
  p.R(20, 100, 28, 103, H_('#1a4a62')); p.P(9, 107, H_('#fff2a8'));
  p.ellipse(11, 109, 17, 115, H_('#07141c')); p.ellipse(25, 109, 31, 115, H_('#07141c'));
  for (let i = 0; i < 4; i++) { const rr = (t * 6 + i * 5) % 14; p.ellipse(90 - rr, 150 - rr / 3, 90 + rr, 150 + rr / 3, undefined, H_('#3a8ea2')); }
  reflect(c, 112, t);
  rain(p, t, 1, 90, H_('#5fb3c4'));
}

function sceneIzakaya(p: Pen, t: number) {
  const c = p.c, B = NEON_BIG;
  gradient(p, B, 180, H_('#06102a'), H_('#02050f'));
  p.R(40, 0, 204, 140, H_('#0a0f1f'));
  p.poly([[30, 74], [122, 56], [214, 74], [214, 80], [30, 80]], H_('#101830'));
  for (let y = 8; y < 50; y += 6) p.R(66, y, 120, y + 3, H_('#3a1019'));
  const f = flicker(t, 1.3), red = mix(H_('#2a0508'), H_('#ff1b1b'), f), deep = mix(H_('#2a0508'), H_('#a80c18'), f);
  p.pill(86, 44, 158, 66, 10, deep, 2);
  p.ellipse(60, 40, 92, 72, red);
  p.R(68, 54, 84, 64, H_('#1a0408')); p.ellipse(66, 46, 74, 52, undefined, H_('#ffb0a0'));
  glyphs(p, 100, 48, 7, mix(H_('#401018'), H_('#ffe9e0'), f), 7);
  glyphs(p, 96, 60, 6, mix(H_('#401018'), H_('#ffd0c0'), f), 9, 2, 3, 3);
  p.R(170, 0, 186, 44, mix(H_('#2a0508'), H_('#e01420'), flicker(t, 4.1))); p.line(172, 22, 184, 22, H_('#ffd8c8'));
  for (let i = 0; i < 5; i++) p.R(84 + i * 9, 84, 87 + i * 9, 87, H_('#17bfd0'));
  p.R(62, 108, 160, 132, H_('#3b3414'));
  for (let i = 0; i < 100; i += 10) p.R(60 + i, 98, 64 + i, 106, (i / 10) % 2 === 0 ? H_('#d8c030') : H_('#241c08'));
  p.R(72, 108, 150, 132, H_('#f4e11c'));
  p.R(104, 114, 116, 132, H_('#16130a')); p.ellipse(105, 108, 115, 118, H_('#16130a'));
  for (const x of [166, 178]) p.ellipse(x, 106, x + 7, 114, H_('#ff2a2a'));
  skyline(p, 140, 0, 40, H_('#060b1a'), 31); skyline(p, 140, 204, B, H_('#060b1a'), 32);
  for (const x of [48, 190]) { p.R(x, 86, x + 10, 94, H_('#141c33')); p.line(x + 2, 88, x + 8, 88, H_('#243050')); }
  p.line(46, 20, 46, 96, H_('#1b2440')); p.line(200, 10, 200, 100, H_('#1b2440'));
  for (let x = 44; x < 168; x += 24) { p.R(x, 74, x + 18, 76, H_('#18213a')); p.R(x + 3, 66, x + 15, 73, H_('#0c142a')); }
  for (let x = 72; x < 150; x += 13) p.line(x, 108, x, 132, H_('#8a7a10'));
  p.line(72, 120, 150, 120, H_('#8a7a10'));
  for (let i = 0; i < 30; i++) p.P(100 + i * 3, 98 + Math.floor(Math.sin((i / 30) * Math.PI) * 6), H_('#0a1020'));
  steam(p, 128, 108, t, H_('#1e2c4c'));
  p.R(0, 140, B, 180, H_('#03060f'));
  reflect(c, 140, t, 0.35, [4, 6, 16]);
  rain(p, t, 2, 55, H_('#2c4066'), 80);
}

function sceneBridge(p: Pen, t: number) {
  const c = p.c, B = NEON_BIG;
  gradient(p, B, 130, H_('#07204a'), H_('#0b2c52'));
  p.R(140, 8, 206, 118, H_('#0c2a4e'));
  windows(p, 144, 18, 14, 14, 3, 5, H_('#134a70'), H_('#0a2442'), 5, 0.25);
  p.R(150, 16, 200, 30, H_('#0e3158'));
  glyphs(p, 156, 20, 4, H_('#4aa0d8'), 3, 6, 3, 5);
  p.poly([[20, 70], [130, 58], [200, 90], [200, 98], [130, 70], [20, 80]], H_('#0a1838'));
  for (const x of [36, 66, 96]) p.line(x, 78, x - 10, 124, H_('#06122a'), 2);
  for (let x = 10; x < 60; x += 8) p.R(x, 96, x + 5, 118, H_('#081832'));
  const f = flicker(t, 2.2, 6), g = mix(H_('#0a2a10'), H_('#9cff2a'), f);
  p.ellipse(136, 82, 152, 98, undefined, g, 2); p.line(144, 85, 144, 95, g);
  glyphs(p, 156, 86, 4, g, 11, 6, 3, 4);
  p.R(0, 124, B, 180, H_('#05122a'));
  p.R(90, 108, 128, 124, H_('#0a1830')); p.R(118, 112, 130, 124, H_('#cfd6df')); p.R(121, 116, 127, 120, H_('#ff6a3c'));
  for (let i = 0; i < 4; i++) p.R(154 + i * 12, 112, 162 + i * 12, 122, mix(H_('#0a3a40'), H_('#7af0e0'), flicker(t, 3 + i, 5)));
  p.R(150, 106, 206, 112, H_('#0c2a40')); p.R(40, 116, 44, 124, H_('#3b8fd0'));
  skyline(p, 124, 0, 86, H_('#081c3a'), 41, H_('#ff3a4a'), t);
  for (let x = 150; x < 200; x += 8) if (Math.floor(t * 4 + x) % 5 === 0) p.R(x, 40 + (x % 16) * 3, x + 2, 43 + (x % 16) * 3, H_('#7fd0ff'));
  p.ellipse(96, 120, 102, 126, H_('#03091a')); p.ellipse(112, 120, 118, 126, H_('#03091a'));
  p.R(118, 112, 130, 118, H_('#9fb2c6')); p.R(128, 114, 130, 116, H_('#fff0a0'));
  p.poly([[36, 104], [48, 104], [44, 112], [40, 112]], H_('#1c4f86'));
  for (let k = 0; k < 5; k++) p.line(30 + k * 3, 126 - k, 34 + k * 3, 126 - k, H_('#0b2a52'));
  reflect(c, 124, t, 0.45, [0, 10, 30]);
  rain(p, t, 3, 70, H_('#3f6fa8'), 75);
}

export const NeonStreet: React.FC = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ref = useRef<HTMLCanvasElement>(null);
  const t = frame / fps;
  useLayoutEffect(() => {
    const big = document.createElement('canvas');
    big.width = NEON_BIG; big.height = NEON_W;
    const bc = big.getContext('2d', {willReadFrequently: true})!;
    const s = t < CUTS[0] ? 0 : t < CUTS[1] ? 1 : 2, t0 = [0, ...CUTS][s];
    bc.fillStyle = '#000'; bc.fillRect(0, 0, NEON_BIG, NEON_W);
    [sceneRoadside, sceneIzakaya, sceneBridge][s](new Pen(bc), t);
    const off = Math.min(START[s] + Math.floor((t - t0) * 6), NEON_BIG - NEON_W);
    const c = ref.current!.getContext('2d', {willReadFrequently: true})!;
    c.imageSmoothingEnabled = false;
    c.drawImage(big, off, 0, NEON_W, NEON_W, 0, 0, NEON_W, NEON_W);
    // bloom: blur bright pixels, add back
    const img = c.getImageData(0, 0, NEON_W, NEON_W), m = new ImageData(NEON_W, NEON_W);
    for (let i = 0; i < img.data.length; i += 4) {
      if (Math.max(img.data[i], img.data[i + 1], img.data[i + 2]) > 105) { m.data[i] = img.data[i]; m.data[i + 1] = img.data[i + 1]; m.data[i + 2] = img.data[i + 2]; m.data[i + 3] = 255; }
    }
    const mc = document.createElement('canvas'); mc.width = mc.height = NEON_W;
    mc.getContext('2d')!.putImageData(m, 0, 0);
    const bl = document.createElement('canvas'); bl.width = bl.height = NEON_W;
    const bx = bl.getContext('2d')!; bx.filter = 'blur(2.2px)'; bx.drawImage(mc, 0, 0);
    c.globalCompositeOperation = 'lighter'; c.globalAlpha = 0.7; c.drawImage(bl, 0, 0);
    c.globalAlpha = 1; c.globalCompositeOperation = 'source-over';
    // vignette + scanlines
    const g = c.createRadialGradient(90, 90, 40, 90, 90, 130);
    g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,0.38)');
    c.fillStyle = g; c.fillRect(0, 0, NEON_W, NEON_W);
    c.fillStyle = 'rgba(0,0,0,0.04)';
    for (let y = 0; y < NEON_W; y += 2) c.fillRect(0, y, NEON_W, 1);
  });
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <canvas ref={ref} width={NEON_W} height={NEON_W} style={{width: '100%', height: '100%', imageRendering: 'pixelated'}} />
      <Audio src={staticFile('audio/neon-ambient.wav')} />
    </AbsoluteFill>
  );
};
