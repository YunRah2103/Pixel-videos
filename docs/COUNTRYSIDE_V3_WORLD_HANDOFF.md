# Countryside Drive V3 — Agent 1 World Art

**Branch:** `agent/countryside-v3-world-art` (based on `integration/countryside-drive-v2-art`). **Do not merge to main.**

## Scope and original source
This branch retains the existing CarLayer, DrivingMotion and final CountrysideDrive interfaces unchanged. Six drop-in native pixel planes are authored by `studio/countryside/world/build-world-v3.mjs` and positioned by the real editable `studio/countryside/world/countryside-v3.ldtk` entity layout.

**Tree silhouettes:** distinct oak, maple, birch, beech, poplar and pine; native outline clusters, single- and multiple-pixel leaf highlights, trunks and undergrowth. Repeating far/mid/near groves are stored as LDtk entities, whose position, species and scale are read by the Sharp builder rather than decorative metadata.

**Scenery:** three-band palette sky with authored pixel clouds and rolling hills; foliage parallax planes; textured roadway, precise shoulder lines, asphalt detail, roadside grass and yellow-green verge highlights. Transparent planes and authored 1:1 pixels; no blurry upscaling or pixelated 3D.

## Rebuild
```bash
npm install --no-audit --no-fund
npm run studio:setup
node studio/countryside/world/build-world-v3.mjs
python3 scripts/build-v3-openraster.py
node scripts/render-world-v3-proof.mjs
```

World PNGs: `public/countryside/world/{sky,farTrees,midTrees,nearTrees,road,verge}.png` and `manifest.json`.
Editable native art: `studio/countryside/world/countryside-v3.ldtk` and generated `studio/countryside/world/sources/*.ora` for Krita / Pixelorama. The Sharp builder is editable source as well.

**Native contracts preserved:** original sky 360×480 @ y=0; far 720×300 @ 180; mid 840×265 @ 215; near 960×235 @ 245; road/verge 384×160 @ y=480. Existing renderer controls scroll offsets and car wheel motion. The world agent does not alter the car.

## Verification and mandatory editor evidence
The workflow `.github/workflows/countryside-v3-world-art.yml` runs actual Pixel Studio V3 setup, installs official Pixelorama and LDtk and packaged Krita, authors six PNGs with **Sharp**, then tries to perform meaningful editor operations:
- Pixelorama imports/exports a real tree sprite; PNG dimensions are checked.
- Krita opens editable `.ora` sky and exports PNG, checked on disk.
- LDtk opens the actual `.ldtk` level on a virtual display; window enumeration/screenshot are saved; the builder independently proves that LDtk entities determine the rendered grove placements.
- FFmpeg encodes 120 genuinely distinct 30-fps native frames with integer parallax offsets; 3× nearest scaling to 1080×1920; FFprobe and a full decode verify the proof.
- Art sources, PNGs, tool logs, screenshot, MP4, nine-frame contact sheet and verification JSON are uploaded as a single Actions artifact.

**Evidence is not a claim of success until the workflow run completes with green checks.** Download all deliverables from the workflow's `countryside-v3-world-art-originals-and-proof` artifact. Local proof is an additional render from the same original native pixel drawing algorithm, but only CI proves external desktop editor execution.

## Boundaries
This is an isolated world-only pass; the final 12-second film belongs to the integrator. Do not merge or claim Pixelorama/Krita/LDtk were used on another host based only on installations. Reject the artwork if visual inspection reveals repeated/clipped tree shapes, bad road contact, or an unattractive overall scene.
