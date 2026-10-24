# SUNSET HARBOR V5 — AGENT 3 ANIMATION HANDOFF

## Scope
- Branch: agent/sunset-harbor-v5-animation; PR target: integration/sunset-harbor-v4-final.
- Owned: src/scenes/v5/MotionV5.mjs and src/scenes/v5/StoryV5.tsx.
- Isolated proof: src/scenes/v5/StoryV5Proof.tsx, scripts/render-v5-story.mjs and dedicated V5 story workflow.
- No Root, shared final, V4 source, Agent 1 world or Agent 2 atmosphere edits.

## Story beats
0–3s: open sunset vista, expressive gulls and a boat approaching from beyond the right pier.
3–8s: deliberate lateral camera recompose and push, six individually planted walking steps,
natural head turns, responsive scarf, companion hand reach, travelling cat.
8–12s: the characters connect hands and look toward the light; cat settles;
yacht carries a physical wake; camera releases into an afterglow hold.
No captions, no camera shake, no static stills or stock sprites.

## Stable integration API
Original native stage is 360x640 at 30fps and 360 frames; sun (225,252), horizon 353,
promenade around 510–640. getV5Motion(frame) clamps frames 0–359 and returns:
cameraX, cameraY, cameraZoom, cloudDrift, waterPhase, lightIntensity, foliageSway,
parallax with V4-compatible layer depths, story fields including boatX/boatY/boatHeel,
actorX/actorFeet/actorLook, partnerX, partnerLook, reach, handsJoined,
catX/catY/catSit and finalGlint.

V5StoryPlane React component takes {frame:number,motion:any,
plane:'birds'|'waterInteraction'|'boat'|'characters'|'cat'|'foregroundLife'}.
Also exported renderV5StoryPlane returns native SVG fragments for all six planes.
Apply the camera transform only once in Agent 4's composition.
Order: sky, birds, distant, ocean, wake, architecture, piers, boat,
promenade, characters, cat, foreground, foregroundLife.
Disable legacy bird flock, wake and V4 story animals to avoid duplicates.

## Render and verification
Run: npm install --no-audit --no-fund && node scripts/render-v5-story.mjs.
Native Remotion → FFmpeg nearest-neighbour 3x → 1080x1920 H.264/AAC.
Check complete decode, 360 frames, 12s, audio in all 12 seconds,
9 distinct extracted frames, contact sheet, 3 close crops and same-frame V4 comparison.
The workflow uploads playable MP4 plus all proof captures and verification.json.
Do not call complete until the GitHub Actions artifact genuinely exists and is reviewed.

Audio is the existing owner-supplied V3/V4 Day & Night fragment from
assets/v3-chill-part01.b64 with the same 420ms crossfades. The full recording is
not in the repository. No new music added; owner must confirm public music rights.
