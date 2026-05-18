from pathlib import Path
from PIL import Image
ROOT=Path(r"D:\桌面\codex\机械挖掘学习汇报\github_upload\sme-ai-workflow-adoption")
chartdir=ROOT/"05_学术图表"/"汇报图片稿_4K待审核"/"图表"
out=ROOT/"07_PPT正式版"/"assets"/"图表白底RGB"
out.mkdir(parents=True,exist_ok=True)
for p in chartdir.glob("*.png"):
    im=Image.open(p).convert("RGBA")
    bg=Image.new("RGBA", im.size, (255,255,255,255))
    bg.alpha_composite(im)
    rgb=bg.convert("RGB")
    rgb.save(out/p.name, quality=95)
    print(out/p.name, rgb.size)
# Also convert academic chart figures if needed
acad=ROOT/"outputs"/"figures"/"academic"
for p in acad.glob("*.png"):
    im=Image.open(p).convert("RGBA")
    bg=Image.new("RGBA", im.size, (255,255,255,255))
    bg.alpha_composite(im)
    bg.convert("RGB").save(out/p.name, quality=95)
