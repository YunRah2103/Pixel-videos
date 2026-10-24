# Sunset Harbor V4 Final — cinematic integrated master

- Base: `integration/sunset-harbor-v3-final` (no modifications to main).
- Source: Agents #10 (World), #8 (Atmosphere), #9 (Story).
- Composition: `SunsetHarborV4Final`, native 360×640/30fps/360 frames.
- Build: `node scripts/render-v4-final.mjs`; output `out/sunset-harbor-v4-FINAL-1080p.mp4`.
- Proof: GH Actions V4 FINAL workflow requires H.264/AAC/1080×1920/360 decoded frames, full movie decode, nine distinct true-frame captures, no black sections and a nine-image contact sheet.
- All cloud/water/mountain/city/boat/character systems share the 360×640 scene coordinates; parallax is applied exactly once to each plane in the final composition.
- Atmospheric module's placeholder bird flock and stand-in wake are explicitly disabled; story owns both. Atmosphere's old V3 window overlays are disabled; original V4 illuminated buildings remain. Additional near-air haze is restricted to the horizon and lamp effects to the lantern district.
- Story's single travelling sailboat is separate from World Agent's moored fishing skiffs.
- User-provided V3 Day & Night short excerpt retained, joined with 420ms overlapping fades and a final 900ms tail; original longer track has not been recovered.
- No third-party visual assets or new soundtrack used. Music redistribution requires rights clearance.
- QA: inspect Actions artifact's contact sheet and opening/middle/closing frames. Automated checks **cannot substitute for manual art-direction inspection**. Do not mark the film as artistically approved until someone reviews the actual delivered MP4.
