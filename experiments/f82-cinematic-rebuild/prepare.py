from PIL import Image
from pathlib import Path
import json
P=Path(__file__).resolve().parent/'assets';a=Image.open(P/'car-original.png').convert('RGBA')
for name,top,bottom in [('front',90,530),('side',590,970),('rear',1000,1490)]:
 b=a.crop((0,top,1024,bottom));alpha=b.getchannel('A').point(lambda v:255 if v>150 else 0);b.putalpha(alpha);box=b.getbbox();print(name,box);b=b.crop(box)
 # Normalise each sprite onto the shared native pixel grid, retain original master.
 b=b.resize((360,round(b.height*360/b.width)),Image.Resampling.NEAREST);b.save(P/(name+'.png'))
bg=Image.open(P/'environment-original.png').convert('RGB').resize((960,640),Image.Resampling.NEAREST);bg.save(P/'environment.png')
# Rim coordinates at the prepared 360px-wide sprite scale.
w={'front': [[177, 104, 14, 20, 0.1], [328, 101, 8, 17, 0.08]], 'side': [[61, 84, 19, 19, 0], [282, 84, 19, 19, 0]], 'rear': [[24, 109, 6, 18, -0.08], [154, 115, 12, 23, -0.12]]}
(P/'wheels.json').write_text(json.dumps(w,indent=2))
