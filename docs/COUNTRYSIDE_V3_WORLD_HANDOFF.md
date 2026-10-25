# Countryside Drive V3 — Agent 1 World Art, final polish

**PR:** #37. **Branch:** `agent/countryside-v3-world-art`. **Base:** `integration/countryside-drive-v2-art`. **No merge to main.**

## Improved original artwork

`studio/countryside/world/build-world-v3.mjs` is original Sharp-based native-pixel sprite painting source. Its silhouette artist now paints non-rectangular stepped-canopy blobs and tiered needle silhouettes rather than stacks of repeating horizontal rectangular crown bands. Six species (oak, maple, birch, beech, pine, poplar) have distinct contours, asymmetrical placement, directional three-tone leaf clusters, individual trunks/branches and root vegetation. Sky cloud placements, hill height, foreground leaf density and road asphalt detail have also been recomposed.

The `studio/countryside/world/countryside-v3.ldtk` project defines **26 editable tree entities** across three depth planes, with species and scales actually consumed by Sharp. Two source editors are enabled: `scripts/build-v3-openraster.py` exports editable `.ora` background/forest documents, while `scripts/build-v3-pixelorama.py` writes editable native `.pxo` tree-sprite source.

## Agent 3 PixiJS contract (unchanged)

**Native composition:** 360×640 at 30fps, with 3× nearest-neighbour upscale to 1080×1920.

| Native plane | Size | Absolute top Y |
|---|---|---|
| sky | 360×480 | 0 |
| farTrees | 720×300 | 180 |
| midTrees | 840×265 | 215 |
| nearTrees | 960×235 | 245 |
| road | 384×160 | 480 |
| verge | 384×160 | 480 |

The public export paths `public/countryside/world/{sky,farTrees,midTrees,nearTrees,road,verge}.png` remain identical. Do not modify the V3 PixiJS motion speeds, sprite-placement interface, car artwork, native road boundary Y=480, wheel contact Y≈495, or final-composition files. Only Agent 3 or integrator applies scroll offsets. `scripts/qa-countryside-v3-world.mjs` checks all six native PNG planes and LDtk entity references.

## Actual external-tool execution and evidence (no continue-on-error)

`.github/workflows/countryside-v3-world-art.yml` performs these steps, all required to pass:

1. **Pixel Studio V3 + Sharp:** install packages, run `npm run studio:setup`, compile-check toolkit, build actual original six-layer native-PNG art and assert pixels/layout.
2. **Pixelorama:** install official v1.2.3, build `nearTrees.pxo`, actually inspect it headlessly (960×235), open the project in the GUI on Xvfb, capture the real Pixelorama window and validate its screenshot and window title. Pixelorama's PNG CLI exporter was unreliable; PNG render/export instead uses Sharp, with Krita also genuinely exporting a sky PNG. **Do not call Pixelorama the PNG exporter.**
3. **Krita:** install and execute the real application on Xvfb, import editable `sky.ora`, export `sky-by-Krita.png`; validate dimensions.
4. **LDtk:** install and run actual official Linux AppImage on Xvfb, open the editable `.ldtk` world project, record screenshot, window tree and logs. The LDtk file also drives the actual tree placements in the scene via the Sharp builder.
5. **FFmpeg/FFprobe:** encode 120 genuinely moving native frames, nearest-neighbour upscale to H.264 1080×1920 30fps, check metadata, complete decode, distinct hashes / nonstatic motion checkpoints, nine-frame contact sheet.

The workflow contains **no `continue-on-error` overrides**; any required step failure fails the workflow. Evidence is uploaded under the Actions artifact `countryside-v3-world-art-originals-and-proof`: actual original files, PNG planes, Krita PNG export, screenshots, execution logs, verification reports, MP4 and contact sheet. The CI run, not the presence of installer commands, is the external-tool evidence.

## Rebuild locally

```bash
npm install --no-audit --no-fund
npm run studio:setup
node studio/countryside/world/build-world-v3.mjs
python3 scripts/build-v3-openraster.py
python3 scripts/build-v3-pixelorama.py
node scripts/qa-countryside-v3-world.mjs
node scripts/render-world-v3-proof.mjs
```

**Scope:** world-only preview, not the 12-second full car film. Visual approval and merge require the owner. Inspect moving footage, not only rendered stills.
