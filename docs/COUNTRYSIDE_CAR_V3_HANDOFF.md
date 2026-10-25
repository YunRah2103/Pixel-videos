# Countryside V3 — Agent 2 car-art contract

## Scope
This is an **isolated side-view car art** update, created from branch `agent/countryside-v2-car-art`. Do not merge to main. No changes to scenery, camera physics, sound, final scene or Agent 4 editing.

## Original art
- `studio/countryside/car/build-car-v3.py`: source of the original hand-authored native-pixel body, individually editable paint/glass/lamp OpenRaster layers and eight distinct forged-spoke wheel frames.
- `studio/countryside/car/v3-source/coupe-v3-editable.ora` and `coupe-v3-wheels-editable.ora`: generated original editable layer projects, downloadable with the workflow artifact. Both open in Pixelorama's File > Open.
- `public/countryside/car/coupe-v3-preview.png` and `coupe-v3-wheels-preview.png`: previews only, NOT final production exports.
- Actual Pixelorama v1.2.3 PNG exports: `public/countryside/car/coupe-v3-pixelorama-{body,wheels}.png`, generated in CI by Pixelorama itself. These are fed to Sharp for validation and compressed copies.
- V2 integration paths `public/countryside/car/coupe-v2-{body,wheels-8}.png` are filled from Pixelorama exports so existing `CarLayer` works unchanged.

**Actual Pixelorama requirement:** `npm run car:v3:pixelorama` installs an official Pixelorama Linux release, calls its `--headless -- --export --output ...` CLI twice on original editable OpenRaster projects, captures version + command logs, and requires two nonempty output PNGs. A tool installation alone does not pass; Sharp checks both outputs and verifies eight distinct 32×32 wheel poses. No fallback/simulation is allowed. The generated, layered OpenRaster projects can be further manually refined using the Pixelorama UI, then exported by the same CLI.

## Mobile and animation
- Native body canvas **192×80**; original silhouette uses robust rear/front overhangs, believable roof height and long athletic hood.
- Wheel sheet **256×32**, eight native 32×32 poses; measured wheel radius **15.5 native pixels**.
- Wheel centers are **43 and 151 native px**; wheel contact **Y=495** in 360×640 scene.
- Production `CarLayer` interface is unchanged. Agent 3 should supply `wheelRotationTurns=roadTravelPx/(2*Math.PI*15.5)` and only bob the body, never tyres.
- Pure integer 3× upscaling to 1080×1920 with no smoothing.
- Real Remotion proof: `out/car-v2-proof/coupe-v2-1080x1920.mp4`, 120 native frames, 30fps, 4.0 seconds, FFprobe/full-decode and nine independently decoded captures.
- Pixel Studio V3 exercised in CI: setup, atlas build, rigs tests, visual QA.
- GitHub CI artifact includes source ORAs, editor version/export logs, original and production PNGs, native moving Remotion proof, contact sheet, captured frames, and machine-readable validation.

## Evidence and limitations
Pixelorama was **not installed in this assistant's local runtime**. The local offline preview is a visual-only independent reference, **not** evidence Pixelorama or Remotion ran locally. Authentic Pixelorama usage must be proven by a successful GitHub Actions run, whose editor invocation logs and exported sprites are published. Any failing CI step blocks a verification claim. Artistic approval belongs to the owner/Agent 4.
