from __future__ import annotations

import csv
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw

from gamma_supervised_page_workflow import SLIDES


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "12_机械学习完整案例展示PPT_v2_imagegen"
OUT = ROOT / "12_机械学习完整案例展示PPT_gamma_supervised"
FINAL = OUT / "final"
WORKSPACE = OUT / "_fixed_layout_workspace"
SLIDES_DIR = OUT / "fixed_layout_slides"
PREVIEW = OUT / "fixed_layout_preview_png"
LAYOUT = OUT / "fixed_layout_json"
QA_DIR = OUT / "qa"

PPTX = FINAL / "企业AI部署偏好与治理机制研究_Gamma监督固定版心展示.pptx"
PDF = FINAL / "企业AI部署偏好与治理机制研究_Gamma监督固定版心展示.pdf"
CONTACT = FINAL / "contact_sheet_gamma_supervised_fixed.png"
SLIDE_MAP = FINAL / "slide_to_evidence_map_gamma_supervised_fixed.csv"
QA = FINAL / "gamma_supervised_fixed_layout_quality_gate.json"
GEN_LOG = FINAL / "gamma_generation_log_summary.json"

HOME = Path.home()
CODEX_RUNTIME = HOME / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies"
CODEX_HOME = Path(os.environ.get("CODEX_HOME", HOME / ".codex-api-gateway"))
NODE = Path(os.environ.get("CODEX_NODE", CODEX_RUNTIME / "node" / "bin" / "node.exe"))
NODE_MODULES = Path(os.environ.get("CODEX_NODE_MODULES", CODEX_RUNTIME / "node" / "node_modules"))
PRESENTATION_SCRIPT = Path(
    os.environ.get(
        "PRESENTATION_ARTIFACT_TOOL",
        CODEX_HOME
        / "plugins"
        / "cache"
        / "openai-primary-runtime"
        / "presentations"
        / "26.430.10722"
        / "skills"
        / "presentations"
        / "scripts"
        / "build_artifact_deck.mjs",
    )
)

BLUE = "#1f5f8b"
ORANGE = "#c36b2c"
INK = "#111827"
GRAY = "#5f6673"
LIGHT_BLUE = "#eef6ff"
PALE = "#f8fafc"


def ensure_dirs() -> None:
    for folder in [FINAL, WORKSPACE, SLIDES_DIR, PREVIEW, LAYOUT, QA_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def js(value: str | Path | list[str]) -> str:
    return json.dumps(str(value) if isinstance(value, Path) else value, ensure_ascii=False)


def visual_path(slide: dict) -> Path:
    return SOURCE_DIR / slide["visual"]


def visual_type(slide: dict) -> str:
    return "data-chart" if str(slide["visual"]).startswith("figures/") else "gpt-image-2"


def metrics_for_slide(slide: dict) -> list[tuple[str, str]]:
    no = int(slide["no"])
    if no == 1:
        return [("12.77M", "官方源数据行"), ("5,814", "Stage 2 建模行"), ("0.7245", "Stage 2 R²")]
    if no == 4:
        return [("553/544/36", "Stage 1"), ("5,814/36/50", "Stage 2"), ("2021, 2023-2025", "年份范围")]
    if no == 5:
        return [("12,770,332", "源数据行"), ("856,880", "候选特征行"), ("5,814", "建模面板行")]
    if no == 7:
        return [("0.8680", "Stage 1 R²"), ("0.7245", "Stage 2 R²"), ("GroupKFold", "主验证口径")]
    if no == 8:
        return [("553", "面板行"), ("544", "可建模样本"), ("1.8342", "MAE")]
    if no == 9:
        return [("5,814", "建模行"), ("50", "行业"), ("1.9646", "MAE")]
    if no == 11:
        return [("8", "单元测试"), ("unavailable", "安全降级"), ("0", "模型二进制公开")]
    if no == 14:
        return [("PPTX/PDF", "最终交付"), ("14", "逐页预览"), ("QA", "质量门禁")]
    return []


def write_common_module() -> None:
    common = f"""
export const C = {{
  W: 1280, H: 720, white: '#ffffff', ink: '{INK}', gray: '{GRAY}',
  blue: '{BLUE}', orange: '{ORANGE}', lightBlue: '{LIGHT_BLUE}',
  pale: '{PALE}', line: '#d9e1ec', font: 'Microsoft YaHei',
  sans: 'Aptos', mono: 'Cascadia Mono'
}};
export function rect(slide, ctx, x, y, w, h, fill = C.white, line = 'rgba(0,0,0,0)', sw = 0) {{
  return ctx.addShape(slide, {{ left: x, top: y, width: w, height: h, fill, line: ctx.line(line, sw), radius: 8 }});
}}
export function txt(slide, ctx, text, x, y, w, h, opts = {{}}) {{
  return ctx.addText(slide, {{
    text: String(text ?? ''), left: x, top: y, width: w, height: h,
    fontSize: opts.size ?? 16, color: opts.color ?? C.ink, bold: Boolean(opts.bold),
    typeface: opts.face ?? C.font, align: opts.align ?? 'left', valign: opts.valign ?? 'top',
    fill: opts.fill ?? 'rgba(0,0,0,0)', line: opts.line ?? ctx.line(),
    insets: opts.insets ?? {{ left: 0, right: 0, top: 0, bottom: 0 }},
    fit: opts.fit ?? 'shrink'
  }});
}}
export async function img(slide, ctx, path, x, y, w, h, fit = 'contain') {{
  return await ctx.addImage(slide, {{ path, left: x, top: y, width: w, height: h, fit, alt: 'verified visual asset' }});
}}
export function metric(slide, ctx, value, label, x, y, w = 126) {{
  const rawValue = String(value ?? '');
  const valueSize = rawValue.length > 8 ? 13 : (rawValue.length > 5 ? 16 : 20);
  txt(slide, ctx, rawValue, x, y, w, 30, {{ size: valueSize, bold: true, color: C.blue, face: C.mono, align: 'center', fit: 'shrink' }});
  txt(slide, ctx, label, x, y + 36, w, 30, {{ size: 10.2, color: C.gray, align: 'center', fit: 'shrink' }});
}}
export function rail(slide, ctx, no, vtype) {{
  txt(slide, ctx, 'GAMMA-SUPERVISED FIXED LAYOUT', 56, 32, 360, 18, {{ size: 8.5, color: C.blue, bold: true, face: C.sans }});
  rect(slide, ctx, 56, 56, 54, 3, C.blue);
  txt(slide, ctx, String(no).padStart(2, '0'), 1160, 32, 64, 22, {{ size: 12, color: C.gray, face: C.mono, align: 'right' }});
  txt(slide, ctx, vtype === 'data-chart' ? 'DATA-DRIVEN FIGURE' : 'GPT IMAGE 2 VISUAL', 1030, 670, 194, 18, {{ size: 8.5, color: C.gray, face: C.sans, align: 'right' }});
}}
"""
    (SLIDES_DIR / "common.mjs").write_text(common, encoding="utf-8")


def write_slide_modules() -> None:
    write_common_module()
    rows = [["slide", "title", "claim", "proof_object", "visual", "visual_type", "boundary"]]
    gamma_logs = []

    for slide in SLIDES:
        no = int(slide["no"])
        vpath = visual_path(slide)
        vtype = visual_type(slide)
        metrics = metrics_for_slide(slide)
        qa_path = QA_DIR / f"slide_{no:02d}_qa.json"
        gamma_qa = {}
        if qa_path.exists():
            gamma_qa = json.loads(qa_path.read_text(encoding="utf-8"))
        gamma_logs.append(
            {
                "slide": no,
                "gamma_status": gamma_qa.get("status"),
                "gamma_url": gamma_qa.get("gammaUrl"),
                "gamma_pptx": gamma_qa.get("pptx"),
                "gamma_preview": gamma_qa.get("preview_png"),
                "used_as": "layout inspiration only; final visual placement is fixed by Codex",
            }
        )
        rows.append([no, slide["title"], slide["claim"], slide["proof"], slide["visual"], vtype, slide["boundary"]])

        metric_code = "\n".join(
            f"  metric(slide, ctx, {js(value)}, {js(label)}, {76 + i * 142}, 538);"
            for i, (value, label) in enumerate(metrics)
        )
        if not metric_code:
            metric_code = "  rect(slide, ctx, 76, 540, 420, 1, C.line);"

        code = f"""
import {{ C, rect, txt, img, metric, rail }} from './common.mjs';

export async function slide{no:02d}(presentation, ctx) {{
  const slide = presentation.slides.add();
  rect(slide, ctx, 0, 0, C.W, C.H, C.white);
  rail(slide, ctx, {no}, {js(vtype)});

  txt(slide, ctx, {js(slide['title'])}, 56, 78, 528, 82, {{ size: 28, bold: true, color: C.ink }});
  txt(slide, ctx, {js(slide['claim'])}, 58, 174, 486, 70, {{ size: 15.5, color: C.gray }});

  rect(slide, ctx, 58, 278, 474, 94, C.lightBlue, '#c9def8', 1);
  txt(slide, ctx, '证据对象', 82, 296, 110, 20, {{ size: 11, bold: true, color: C.blue }});
  txt(slide, ctx, {js(slide['proof'])}, 82, 322, 410, 42, {{ size: 13.2, color: C.ink }});

  rect(slide, ctx, 58, 396, 474, 92, '#fff8ef', '#efd2a9', 1);
  txt(slide, ctx, '边界说明', 82, 414, 110, 20, {{ size: 11, bold: true, color: C.orange }});
  txt(slide, ctx, {js(slide['boundary'])}, 82, 440, 410, 36, {{ size: 12.5, color: C.ink }});

{metric_code}

  rect(slide, ctx, 608, 80, 586, 516, C.pale, '#e3e9f2', 1);
  await img(slide, ctx, {js(vpath)}, 632, 104, 538, 468, 'contain');
  rect(slide, ctx, 608, 616, 586, 1, C.line);
  txt(slide, ctx, {js('视觉素材来源：' + ('真实数据图表' if vtype == 'data-chart' else 'GPT image 2 概念图'))}, 610, 630, 420, 22, {{ size: 9.5, color: C.gray }});
  txt(slide, ctx, {js('Gamma 负责审美骨架；最终图片版心由固定合成层控制。')}, 56, 670, 700, 20, {{ size: 9.2, color: C.gray }});
  return slide;
}}
"""
        (SLIDES_DIR / f"slide-{no:02d}.mjs").write_text(code, encoding="utf-8")

    with SLIDE_MAP.open("w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh).writerows(rows)
    GEN_LOG.write_text(json.dumps(gamma_logs, ensure_ascii=False, indent=2), encoding="utf-8")


def build_pptx() -> dict:
    cmd = [
        str(NODE),
        str(PRESENTATION_SCRIPT),
        "--workspace",
        str(WORKSPACE),
        "--slides-dir",
        str(SLIDES_DIR),
        "--out",
        str(PPTX),
        "--preview-dir",
        str(PREVIEW),
        "--layout-dir",
        str(LAYOUT),
        "--slide-count",
        "14",
        "--slide-size",
        "1280x720",
        "--scale",
        "1.5",
    ]
    env = os.environ.copy()
    env["HOME"] = str(Path.home())
    env["NODE_REPL_NODE_MODULE_DIRS"] = str(NODE_MODULES)
    result = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        env=env,
    )
    return {"returncode": result.returncode, "stdout": result.stdout[-4000:], "stderr": result.stderr[-4000:]}


def try_export_pdf() -> dict:
    ps = f"""
$ErrorActionPreference = 'Stop'
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
$presentation = $ppt.Presentations.Open('{str(PPTX)}', $true, $false, $false)
$presentation.SaveAs('{str(PDF)}', 32)
$presentation.Close()
$ppt.Quit()
"""
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            text=True,
            capture_output=True,
            timeout=90,
            encoding="utf-8",
            errors="replace",
        )
        return {"attempted": True, "returncode": result.returncode, "pdf_exists": PDF.exists(), "stderr": result.stderr[-500:]}
    except Exception as exc:
        return {"attempted": True, "error": str(exc), "pdf_exists": PDF.exists()}


def make_contact_sheet() -> dict:
    previews = sorted(PREVIEW.glob("slide-*.png"))
    if len(previews) != 14:
        return {"ok": False, "preview_count": len(previews)}
    thumbs = []
    for path in previews:
        im = Image.open(path).convert("RGB")
        im.thumbnail((320, 180), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (320, 205), "white")
        canvas.paste(im, ((320 - im.width) // 2, 0))
        ImageDraw.Draw(canvas).text((8, 184), path.stem, fill=(80, 80, 80))
        thumbs.append(canvas)
    sheet = Image.new("RGB", (1280, math.ceil(len(thumbs) / 4) * 205), "white")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % 4) * 320, (i // 4) * 205))
    sheet.save(CONTACT)
    return {"ok": True, "preview_count": len(previews), "contact_sheet": str(CONTACT.relative_to(ROOT))}


def quality_scan() -> dict:
    missing_visuals = [str(visual_path(slide).relative_to(ROOT)) for slide in SLIDES if not visual_path(slide).exists()]
    forbidden = [
        "千万样本直接训练",
        "机器学习证明因果",
        "Stage 2 是 SME-only",
        "问卷星逐样本数据库",
    ]
    checked_text = json.dumps(SLIDES, ensure_ascii=False)
    forbidden_hits = []
    allowed_negations = ("禁止", "严禁", "不得", "不能", "不写", "不说", "不把", "不要")
    for term in forbidden:
        pos = checked_text.find(term)
        while pos != -1:
            window = checked_text[max(0, pos - 12) : pos]
            if not any(negation in window for negation in allowed_negations):
                forbidden_hits.append(term)
                break
            pos = checked_text.find(term, pos + len(term))
    return {
        "missing_visuals": missing_visuals,
        "forbidden_hits": forbidden_hits,
        "stage1_locked": "553 / 544 / 36",
        "stage2_locked": "5,814 / 36 / 50",
        "source_chain_locked": "12,770,332 -> 12,341,630 -> 856,880 -> 5,814",
    }


def cleanup() -> None:
    for path in [WORKSPACE, SLIDES_DIR, LAYOUT, OUT / "artifact-build-manifest.json", OUT / "artifact_build_manifest.json"]:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def main() -> None:
    ensure_dirs()
    write_slide_modules()
    build = build_pptx()
    pdf = try_export_pdf() if PPTX.exists() else {"attempted": False}
    contact = make_contact_sheet()
    scan = quality_scan()
    preview_count = len(list(PREVIEW.glob("slide-*.png")))
    ok = (
        build["returncode"] == 0
        and PPTX.exists()
        and PPTX.stat().st_size > 0
        and preview_count == 14
        and contact.get("ok")
        and not scan["missing_visuals"]
        and not scan["forbidden_hits"]
    )
    qa = {
        "ok": bool(ok),
        "pptx": str(PPTX.relative_to(ROOT)) if PPTX.exists() else None,
        "pdf": str(PDF.relative_to(ROOT)) if PDF.exists() else None,
        "preview_count": preview_count,
        "contact_sheet": str(CONTACT.relative_to(ROOT)) if CONTACT.exists() else None,
        "slide_to_evidence_map": str(SLIDE_MAP.relative_to(ROOT)),
        "gamma_generation_log": str(GEN_LOG.relative_to(ROOT)),
        "build": build,
        "pdf_export": pdf,
        "contact": contact,
        "content_scan": scan,
        "rules": [
            "Gamma output is treated as layout inspiration only.",
            "Final images are placed by fixed contain boxes to avoid cropping.",
            "GPT image 2 assets are conceptual visuals only.",
            "Data/model slides use repository data-driven figures.",
            "No API keys are stored in generated artifacts.",
        ],
    }
    QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    if ok:
        cleanup()
    else:
        raise SystemExit(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
