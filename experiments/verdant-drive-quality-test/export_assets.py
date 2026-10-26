"""Export individual reusable sprites from the hand-authored renderer."""
from pathlib import Path
from PIL import Image
from render import HERE,car_sprite,OAKS,FIR,BUSH,CLOUD,P,draw_frame
out=HERE/'assets';out.mkdir(exist_ok=True)
items={'gold_hatchback_274x132.png':car_sprite(0),'oak_tree_a_164x204.png':OAKS[0],'oak_tree_b_164x204.png':OAKS[1],'fir_47x86.png':FIR,'hedgerow_84x43.png':BUSH,'cloud_122x53.png':CLOUD}
for name,art in items.items():
 art.save(out/name)
 print('EXPORT',name)
# Transparent sprite contact sheet for quick sprite preview
sheet=Image.new('RGBA',(536,412),'#d1e4d0')
sheet.paste(items['gold_hatchback_274x132.png'],(18,12),items['gold_hatchback_274x132.png'])
sheet.paste(OAKS[0],(14,160),OAKS[0]);sheet.paste(OAKS[1],(188,160),OAKS[1]);sheet.paste(FIR,(366,226),FIR)
sheet.save(out/'sprite_atlas_preview.png')
