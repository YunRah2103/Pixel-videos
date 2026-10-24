# Sunset Harbor V4 — Film Direction / Agent 3 Integration Contract

## Ownership and provenance
This PR owns the frame-exact director score \`src/scenes/v4/HarborMotionV4.mjs\`, independent SVG life animator \`src/scenes/v4/HarborLifeV4.mjs\`, and standalone Remotion composition \`src/scenes/v4/HarborStoryProof.tsx\`. V3 \`HarborWorld.mjs\` is imported **only as the proof underlay**. No V3 or V4 Agent 1/2 files are changed. All new sprites are authored in this PR as original vector-pixel geometry, not lifted from games/anime/assets.

## 12-second beat sheet (360 frames at 30 FPS)

| Time | Camera / emotional beat | Acting |
| --- | --- | --- |
| 00:00–00:03 | Wonder: one warm harbour sunset, quietly revealed with a 1.8–4.4% opening push (gradually growing to ~11% as the story approaches the waterfront) and subtle pan. | Bird flock gains height. Characters are present, not constantly busy. |
| 00:03–00:06 | Belonging: drift toward lively waterfront, differentiated parallax. | A walks closer; scarf, cape and flowerheads respond to breeze; the sailor appears on the water. Cat begins walking. |
| 00:06–00:09 | Connection: camera holds its slow drift; water and rigging continue. | Two actors glance, hands approach and meet; boat visibly travels with wake; cat approaches. |
| 00:09–00:12 | Afterglow: ease down into a composed final tableau without cut or title. | Hands remain linked; cat sits; gentle light/railing accent peaks. |

There is no static jump or abrupt camera edit between acts. All activity is computed from one integer frame and functions of that frame. Blinks, walking cycles, boat bob, independent paws/tail, hair and cloth all follow meaningful time windows.

## Stable API

\`getHarborMotionV4(frame)\` returns:
- \`cameraX,cameraY,cameraZoom\` in 360×640 native pixels and scale; world camera is continuous.
- \`parallax\` mapping \`sky,distant,architecture,water,promenade,foreground,lifeFar,lifeNear\` to camera strength.
- \`cloudDrift,waterPhase,waterMotion,foliageSway,lightIntensity,finalGlint\` for Atmosphere agent.
- \`boatX,boatY,boatWake,boatHeel,boatReveal,sailFlutter\` for boat/wake.
- \`glance,handhold,firstStep,nextStep,coatBreeze,quietSmile,blinking,meet\` for articulated acting.
- \`catX,catStep,catSit,catTail,birdsTravel,gullWing\` for secondary life.
- \`frame,seconds,progress,act,endingEase\` etc. All are finite, deterministic, clamped by frame 0–359.

\`renderHarborLifeV4(frame,motion)\` returns an object of **raw SVG fragments** (not SVG wrappers): \`birds,water,boat,characters,cat,foreground\` plus \`sky,waterHighlights,actors,combined\` aliases. Each fragment uses native 360×640 coordinates and shape-rendering crisp pixel clusters. No direct imports from Agent 1 or 2.

### Recommended integrated layer stack (bottom to top)

1. Agent 1 \`renderHarborBaseLayers(frame,m)\`: \`sky\`, \`distant\` (\`parallax.sky\`, \`parallax.distant\`), \`architecture\`, \`harbourStructures\` (\`parallax.architecture\`), \`promenade\`, \`foreground\` (\`parallax.foreground\`).
2. Agent 2 \`renderHarborFxLayers(frame,m)\`: \`clouds\` over sky, \`water\` over distant/water region, \`waterHighlights\` over sea, \`illumination\` over structures, \`nearAir\` last/low opacity.
3. Agent 3 \`renderHarborLifeV4(frame,m)\`: \`birds\` above sky/clouds, \`water\` (boat wake) above sea, \`boat\` at \`lifeFar\`, \`characters\` and \`cat\` above promenade at \`lifeNear\`, \`foreground\` behind/over near flora per composition. Couple must be occluded only by deliberately placed near objects, not a duplicate pre-painted sprite.
4. One restrained film camera using \`cameraX,cameraY,cameraZoom\` with factor \`parallax[layer]\`. Keep same \`transformOrigin: '50% 46%'\` at 360×640 for all layers. Agents 1/2 should NOT independently shake or zoom their art.

**Important:** Agent 1 must omit V3's prepainted humans/cat/boat; these are a stand-in in the V3 underlay only. In the final integrated V4, do not draw duplicate actors. The V3 proof scene naturally still contains V3 residents and skiff in its backdrop; those are treated as static harbour extras during proof.

## Music direction and fragment limitation

Score is the newer **owner-provided Day & Night** music from the V3 integration branch \`assets/v3-chill-part01.b64\`; V2 jazz is forbidden. That V3 file contains only a ~4s compressed excerpt, not the complete owner upload. Proof score uses deliberate ~0.42-second crossfades between excerpt repetitions, smooth outer fades and a final mellow resolution. This mitigates hard seams; **it cannot restore 12 seconds of missing original musical development**. Integrator should substitute the complete owner-supplied audio if it becomes available, with proof ending arranged to its final phrase. Audio/music redistribution rights are not asserted.

## Proof, commands and verification

\`\`\`sh
npm install --no-audit --no-fund
node scripts/render-v4-story.mjs
# out/sunset-harbor-v4-STORY-1080p.mp4
# out/v4-story-qa/{opening,story,meeting,ending}.png
# out/v4-story-qa/verification.json
\`\`\`

- A temporary entry component is created under \`src/\` and removed after native Remotion render.
- Native render is 360×640, 360 frames, 30fps; FFmpeg ×3 integer-neighbour upscale to 1080×1920 with H.264 yuv420p and AAC music.
- FFprobe checks codec/frame count/duration/channel resolution. FFmpeg must decode **the entire delivered MP4** without errors.
- Four captured story beats must have distinct SHA256 values; the generated PNGs need **visual** review.
- GitHub Actions \`sunset-harbor-v4-story.yml\` renders and uploads both MP4 and captures. A successful run and valid artifact, not only a script commit, are required before claiming completion.

No merge to main; PR targets \`integration/sunset-harbor-v3-final\`.
