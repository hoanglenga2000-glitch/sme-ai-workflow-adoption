from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageStat
import math, json
DIR = Path(r"D:\桌面\codex\机械挖掘学习汇报\github_upload\sme-ai-workflow-adoption\07_PPT正式版\预览图\slides_png")
OUT = Path(r"D:\桌面\codex\机械挖掘学习汇报\github_upload\sme-ai-workflow-adoption\07_PPT正式版\预览图")
imgs = sorted({p.resolve() for p in DIR.glob("*") if p.suffix.lower() == ".png"}, key=lambda p: int("".join([c for c in p.stem if c.isdigit()]) or 0))
records=[]
thumb_w=480
cols=3
loaded=[]
for p in imgs:
    im=Image.open(p).convert('RGB')
    stat=ImageStat.Stat(im)
    mean=sum(stat.mean)/3
    bbox=Image.eval(im, lambda x: 255 if x<250 else 0).getbbox()
    records.append({"file":p.name,"size":im.size,"bytes":p.stat().st_size,"mean_brightness":round(mean,2),"nonblank_bbox":bbox is not None})
    loaded.append((p,im))
if loaded:
    ratio=loaded[0][1].height/loaded[0][1].width
    thumb_h=int(thumb_w*ratio)
    sheet=Image.new('RGB',(thumb_w*cols,(thumb_h+38)*math.ceil(len(loaded)/cols)),(236,241,247))
    draw=ImageDraw.Draw(sheet)
    for idx,(p,im) in enumerate(loaded):
        t=im.copy(); t.thumbnail((thumb_w,thumb_h))
        x=(idx%cols)*thumb_w; y=(idx//cols)*(thumb_h+38)
        sheet.paste(t,(x,y))
        draw.rectangle([x,y+t.height,x+thumb_w,y+t.height+36],fill=(255,255,255))
        draw.text((x+10,y+t.height+8),f"{idx+1:02d} {p.name}",fill=(8,28,48))
    sheet.save(OUT/'正式版PPT预览总览_contact_sheet.png')
(OUT/'正式版PPT视觉QA.json').write_text(json.dumps({"slide_count":len(records),"records":records},ensure_ascii=False,indent=2),encoding='utf-8')
print(OUT/'正式版PPT预览总览_contact_sheet.png')
print(OUT/'正式版PPT视觉QA.json')
print(json.dumps({"slide_count":len(records),"all_nonblank":all(r['nonblank_bbox'] for r in records),"sizes":sorted(set(tuple(r['size']) for r in records))},ensure_ascii=False))

