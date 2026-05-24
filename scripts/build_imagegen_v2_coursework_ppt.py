from __future__ import annotations

import csv
import json
import math
import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "12_机械学习完整案例展示PPT"
OUT = ROOT / "12_机械学习完整案例展示PPT_v2_imagegen"
WORKSPACE = OUT / "_artifact_workspace"
SLIDES = OUT / "artifact_slides"
ASSETS = OUT / "assets_imagegen_v2"
FIGURES = OUT / "figures"
SOURCE = OUT / "source_data"
PREVIEW = OUT / "preview_png"
LAYOUT = OUT / "layout_json"

PPTX = OUT / "企业AI部署偏好与治理机制研究_机械学习完整案例展示_v2_imagegen.pptx"
PDF = OUT / "企业AI部署偏好与治理机制研究_机械学习完整案例展示_v2_imagegen.pdf"
CONTACT = OUT / "contact_sheet_v2.png"
QA = OUT / "ppt_quality_gate_v2.json"
PROMPT_MANIFEST = OUT / "imagegen_prompt_manifest.csv"
IMAGE_QA = OUT / "imagegen_asset_qa.json"
SLIDE_MAP = OUT / "slide_to_evidence_map_v2.csv"

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
IMAGEGEN = Path(
    os.environ.get("IMAGEGEN_CLI", CODEX_HOME / "skills" / ".system" / "imagegen" / "scripts" / "image_gen.py")
)

BLUE = "#1f5f8b"
ORANGE = "#c36b2c"
INK = "#111827"
GRAY = "#6b7280"
LIGHT = "#eef2f6"


VISUALS = [
    {
        "key": "cover",
        "file": "01_cover_enterprise_ai_data_pipeline.png",
        "prompt": "Clean academic cover image for a machine learning coursework presentation about enterprise AI deployment preferences and governance mechanisms. White studio background, abstract official data pipeline with translucent panels, tabular data blocks, governance shield, model nodes, muted deep blue and warm orange accents, premium editorial style. No text, no logos, no fake statistical chart, no people, no watermark.",
    },
    {
        "key": "data_upgrade",
        "file": "02_data_upgrade_official_sources.png",
        "prompt": "Pure abstract conceptual visual showing low-quality informal data being transformed into verified official data sources. White background, clean folders, sealed document stacks, database blocks, validation shields, checksum-like dots, subtle arrows, muted blue and orange accents, academic presentation style. Absolutely no text, no letters, no words, no labels, no readable numbers, no logos, no chart panels, no fake statistical charts, no people, no watermark.",
    },
    {
        "key": "lifecycle",
        "file": "03_data_lifecycle_pipeline.png",
        "prompt": "Abstract data lifecycle scene: acquisition, cleaning, feature engineering, model validation, presentation output represented by connected translucent modules. White background, technical but calm, enterprise AI governance mood, muted blue and orange accents. No text, no logos, no fake charts, no people, no watermark.",
    },
    {
        "key": "stage_boundary",
        "file": "04_stage1_stage2_boundary.png",
        "prompt": "Conceptual two-layer evidence architecture: one layer for SME mechanism interpretation and one layer for industry and regional external validation. Use two parallel translucent lanes, bridge nodes, country and industry icons as abstract shapes. White background, muted blue and orange. No text, no logos, no fake charts, no people, no watermark.",
    },
    {
        "key": "ml_task",
        "file": "05_ml_task_tabular_modeling.png",
        "prompt": "Pure abstract machine learning task visual for tabular official enterprise ICT data. Show feature columns as simple blank vertical data blocks flowing into two abstract model processing modules and one decision-support node. White background, low saturation blue and orange, clean academic style. Absolutely no text, no letters, no numbers, no labels, no axes, no scatterplots, no line charts, no trend lines, no decision-tree diagrams, no fake statistical chart, no logos, no people, no watermark.",
    },
    {
        "key": "agent",
        "file": "06_agent_evidence_constrained.png",
        "prompt": "Evidence-constrained AI agent prototype visual: retrieval index, tool calls, citations, safe unavailable fallback, all represented as abstract interface panels and connected nodes. White background, polished academic product style, muted blue and orange accents. No text, no logos, no fake charts, no people, no watermark.",
    },
    {
        "key": "github_boundary",
        "file": "07_github_public_private_boundary.png",
        "prompt": "Public repository governance visual: clean open repository area separated from private manuscript and questionnaire vault by a transparent boundary. Abstract folders, lock symbol, checkmarks, data pipeline nodes. White background, muted blue and orange. No text, no logos, no fake charts, no people, no watermark.",
    },
    {
        "key": "summary",
        "file": "08_summary_reproducible_research.png",
        "prompt": "Final summary visual for reproducible machine learning research: official data, robust validation, professional slides, and future research roadmap represented as elegant connected panels. White background, premium academic editorial look, muted blue and orange accents. No text, no logos, no fake charts, no people, no watermark.",
    },
]


def ensure_dirs() -> None:
    for folder in [OUT, WORKSPACE, SLIDES, ASSETS, FIGURES, SOURCE, PREVIEW, LAYOUT]:
        folder.mkdir(parents=True, exist_ok=True)


def run(cmd: list[str], timeout: int = 240) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=timeout)


def generate_image_asset(item: dict, retry: int = 1) -> dict:
    path = ASSETS / item["file"]
    if path.exists() and path.stat().st_size > 0:
        return {"key": item["key"], "path": str(path), "status": "reused", "bytes": path.stat().st_size}
    last_error = ""
    for attempt in range(retry + 1):
        cmd = [
            "python",
            str(IMAGEGEN),
            "generate",
            "--model",
            "gpt-image-2",
            "--size",
            "1536x1024",
            "--quality",
            "high",
            "--out",
            str(path),
            "--force",
            "--prompt",
            item["prompt"],
        ]
        result = run(cmd, timeout=180)
        if result.returncode == 0 and path.exists() and path.stat().st_size > 0:
            return {"key": item["key"], "path": str(path), "status": "generated", "attempt": attempt + 1, "bytes": path.stat().st_size}
        last_error = (result.stderr or result.stdout or "").strip()[-1000:]
    return {"key": item["key"], "path": str(path), "status": "failed", "error": last_error}


def generate_assets() -> dict[str, Path]:
    rows = []
    qa = []
    assets = {}
    for item in VISUALS:
        rows.append({"key": item["key"], "file": item["file"], "model": "gpt-image-2", "prompt": item["prompt"]})
        result = generate_image_asset(item)
        clean_result = dict(result)
        if "path" in clean_result:
            clean_result["path"] = str(Path(clean_result["path"]).resolve().relative_to(ROOT))
        qa.append(clean_result)
        path = ASSETS / item["file"]
        if path.exists() and path.stat().st_size > 0:
            assets[item["key"]] = path
    with PROMPT_MANIFEST.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["key", "file", "model", "prompt"])
        writer.writeheader()
        writer.writerows(rows)
    IMAGE_QA.write_text(json.dumps({"ok": all(r["status"] != "failed" for r in qa), "assets": qa}, ensure_ascii=False, indent=2), encoding="utf-8")
    return assets


def copy_data_artifacts() -> dict[str, Path]:
    charts = {}
    for name in ["fig_waterfall.png", "fig_model_validation.png", "fig_feature_importance.png", "fig_agent_eval.png", "fig_workflow.png"]:
        src = BASE / "figures" / name
        dst = FIGURES / name
        if src.exists():
            shutil.copy2(src, dst)
            charts[name.removesuffix(".png").replace("fig_", "")] = dst
    for src in (BASE / "source_data").glob("*.csv"):
        shutil.copy2(src, SOURCE / src.name)
    return charts


def js_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def js_path(path: Path | None) -> str:
    return "null" if path is None else json.dumps(str(path), ensure_ascii=False)


def write_slide_modules(assets: dict[str, Path], charts: dict[str, Path]) -> None:
    common = f"""
export const C = {{
  W: 1280, H: 720, white: '#FFFFFF', ink: '{INK}', gray: '{GRAY}', line: '#d8dee6',
  light: '{LIGHT}', blue: '{BLUE}', orange: '{ORANGE}', pale: '#f7fafc',
  font: 'Microsoft YaHei', sans: 'Aptos', mono: 'Cascadia Mono'
}};
export function rect(slide, ctx, x, y, w, h, fill = C.white, line = 'rgba(0,0,0,0)', name = undefined) {{
  return ctx.addShape(slide, {{ left: x, top: y, width: w, height: h, fill, line: ctx.line(line, line === 'rgba(0,0,0,0)' ? 0 : 1), name }});
}}
export function txt(slide, ctx, text, x, y, w, h, opts = {{}}) {{
  return ctx.addText(slide, {{
    text: String(text ?? ''), left: x, top: y, width: w, height: h,
    fontSize: opts.size ?? 18, color: opts.color ?? C.ink, bold: Boolean(opts.bold),
    typeface: opts.face ?? C.font, align: opts.align ?? 'left', valign: opts.valign ?? 'top',
    fill: opts.fill ?? 'rgba(0,0,0,0)', line: opts.line ?? ctx.line(),
    insets: opts.insets ?? {{ left: 0, right: 0, top: 0, bottom: 0 }}, name: opts.name
  }});
}}
export function rule(slide, ctx, x, y, w, color = C.line, h = 1) {{ rect(slide, ctx, x, y, w, h, color); }}
export async function img(slide, ctx, path, x, y, w, h, fit = 'contain', name = undefined) {{
  if (!path) return null;
  return await ctx.addImage(slide, {{ path, left: x, top: y, width: w, height: h, fit, alt: name ?? 'visual asset', name }});
}}
export function base(slide, ctx, no, section, claim, source) {{
  rect(slide, ctx, 0, 0, C.W, C.H, C.white);
  txt(slide, ctx, section.toUpperCase(), 56, 34, 430, 22, {{ size: 10, color: C.blue, bold: true, face: C.sans }});
  rule(slide, ctx, 56, 64, 58, C.blue, 3);
  txt(slide, ctx, claim, 56, 82, 760, 74, {{ size: 27, color: C.ink, bold: true }});
  rule(slide, ctx, 56, 666, 1168, C.line, 1);
  txt(slide, ctx, source, 56, 679, 930, 24, {{ size: 9, color: C.gray, face: C.sans }});
  txt(slide, ctx, String(no).padStart(2, '0'), 1174, 678, 50, 22, {{ size: 13, color: C.gray, face: C.mono, align: 'right' }});
}}
export function metric(slide, ctx, value, label, x, y, w = 185) {{
  txt(slide, ctx, value, x, y, w, 42, {{ size: 27, color: C.blue, bold: true, face: C.mono }});
  txt(slide, ctx, label, x, y + 44, w + 20, 38, {{ size: 10.5, color: C.gray }});
}}
export function bullets(slide, ctx, items, x, y, w, rowH = 58) {{
  items.forEach((item, i) => {{
    const yy = y + i * rowH;
    rect(slide, ctx, x, yy + 7, 5, 25, i === 0 ? C.orange : C.blue);
    txt(slide, ctx, item, x + 18, yy, w - 18, rowH - 6, {{ size: 13.5, color: C.ink }});
  }});
}}
"""
    (SLIDES / "common.mjs").write_text(common, encoding="utf-8")

    slide_defs = [
        ("Opening", "企业 AI 部署偏好与治理机制：完整机器学习案例", "用官方数据、机器学习验证和证据约束 Agent，形成明天可展示的完整课程案例。", assets.get("cover"), ["12.77M official source rows", "5,814 Stage 2 modeling rows", "0.7245 Stage 2 R2"]),
        ("Data upgrade", "主证据从问卷/Kaggle 升级为官方数据", "问卷和访谈解释机制，公开主模型必须依赖可追溯官方数据。", assets.get("data_upgrade"), ["Eurostat source manifests", "SHA256 and download records", "Questionnaire only as auxiliary evidence"]),
        ("Lifecycle", "数据生命周期每一步都有仓库证据", "从 source manifest 到 processed panel，再到 outputs 和 PPT，路径可复查。", assets.get("lifecycle"), ["data/raw/manifest*.jsonl", "data/processed/*.csv", "outputs/tables and reports"]),
        ("Boundary", "Stage 1 解释 SME 机制，Stage 2 验证行业/区域泛化", "两层数据边界分开讲，避免把 Stage 2 误说成 SME-only。", assets.get("stage_boundary"), ["Stage 1: 553 / 544 / 36", "Stage 2: 5,814 / 36 / 50", "2021, 2023-2025"]),
        ("Scale audit", "1277 万源数据行不是直接训练样本", "官方源数据经过扫描、筛选和聚合，形成 5,814 行建模面板。", charts.get("waterfall"), ["12,770,332 raw rows", "856,880 feature-filtered rows", "5,814 modeling rows"]),
        ("ML task", "监督学习任务围绕官方 AI 工作流指标展开", "目标变量来自企业使用 AI 自动化工作流或辅助决策的官方指标。", assets.get("ml_task"), ["Target: workflow automation", "Ridge and ExtraTrees", "Leakage-controlled features"]),
        ("Validation", "GroupKFold 按国家分组降低泄漏", "公开展示使用保守的分组验证，不用随机切分夸大结果。", charts.get("validation"), ["Stage 1 R2=0.8680", "Stage 2 R2=0.7245", "Time holdout as boundary check"]),
        ("Stage 1", "Stage 1 Ridge 支撑 SME 机制解释", "553 行面板、544 行可建模样本、36 个 geo，主指标 R2=0.8680。", charts.get("validation"), ["Ridge", "MAE=1.8342", "SME mechanism layer"]),
        ("Stage 2", "Stage 2 ExtraTrees 支撑行业/区域外部验证", "5,814 行、36 个 geo、50 个行业，长跑复算 R2=0.7245。", charts.get("validation"), ["ExtraTrees", "MAE=1.9646", "External validation layer"]),
        ("Mechanism", "特征重要性服务机制解释，不写成因果证明", "数字基础、部署准备度和治理相关变量进入解释链。", charts.get("importance"), ["Feature importance", "Deployment readiness", "No causal proof claim"]),
        ("Agent", "Agent 原型把证据约束转成可演示工具", "无模型二进制时返回 unavailable 和复现路径，不伪造预测。", assets.get("agent"), ["Evidence-bound answers", "Safe unavailable fallback", "8 unit tests pass"]),
        ("GitHub", "公开仓库只保留课程复现材料", "论文、问卷/访谈隐私、模型二进制和认证信息不进入公开仓库。", assets.get("github_boundary"), ["Public: data/code/outputs/PPT", "Private: manuscript/questionnaire", "No joblib / pkl / env"]),
        ("Limits", "边界说清楚，比把结论写满更专业", "不写千万样本直接训练、不写机器学习证明因果、不写 Stage 2 SME-only。", assets.get("github_boundary"), ["Correct source-chain wording", "No causal overclaim", "Questionnaire is aggregate only"]),
        ("Close", "真实数据、严格验证、可复现展示", "这套案例能体现机器学习课程的数据治理、模型训练、解释和工程复现。", assets.get("summary"), ["Final PPTX and PDF", "14 previews + contact sheet", "Evidence map and QA"]),
    ]

    rows = [["slide", "claim", "proof_object", "visual_type", "boundary"]]
    for idx, (section, claim, sub, visual, bullets, *_) in enumerate(slide_defs, start=1):
        visual_type = "gpt-image-2" if visual and visual.parent == ASSETS else "data-chart"
        rows.append([idx, claim, "; ".join(bullets), visual_type, "Generated visuals are not statistical evidence" if visual_type == "gpt-image-2" else "Chart is data-driven"])
        code = f"""
import {{ C, rect, txt, rule, metric, img, base, bullets }} from './common.mjs';
export async function slide{idx:02d}(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, {idx}, {js_str(section)}, {js_str(claim)}, 'Source: public repository data, result tables, imagegen manifest, and QA reports.');
  txt(slide, ctx, {js_str(sub)}, 58, 166, 600, 48, {{ size: 15.5, color: C.gray }});
  await img(slide, ctx, {js_path(visual)}, 682, 128, 500, 382, 'contain', 'slide visual');
  bullets(slide, ctx, {json.dumps(bullets, ensure_ascii=False)}, 78, 270, 500, 64);
  if ({idx} === 1) {{
    metric(slide, ctx, '12.77M', 'official source rows', 78, 516);
    metric(slide, ctx, '5,814', 'modeling panel rows', 286, 516);
    metric(slide, ctx, '0.7245', 'Stage 2 long-run R2', 494, 516);
  }}
  return slide;
}}
"""
        (SLIDES / f"slide-{idx:02d}.mjs").write_text(code, encoding="utf-8")

    with SLIDE_MAP.open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(rows)


def build_pptx() -> dict:
    cmd = [
        str(NODE),
        str(PRESENTATION_SCRIPT),
        "--workspace",
        str(WORKSPACE),
        "--slides-dir",
        str(SLIDES),
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
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=300, env=env)
    return {"returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


def make_contact_sheet() -> dict:
    previews = sorted(PREVIEW.glob("slide-*.png"))
    if not previews:
        return {"ok": False, "error": "no preview PNGs found"}
    thumbs = []
    for path in previews:
        im = Image.open(path).convert("RGB")
        im.thumbnail((320, 180), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (320, 205), "white")
        canvas.paste(im, ((320 - im.width) // 2, 0))
        ImageDraw.Draw(canvas).text((8, 184), path.stem, fill=(80, 80, 80))
        thumbs.append(canvas)
    sheet = Image.new("RGB", (4 * 320, math.ceil(len(thumbs) / 4) * 205), "white")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % 4) * 320, (i // 4) * 205))
    sheet.save(CONTACT)
    return {"ok": True, "slides": len(previews), "contact_sheet": str(CONTACT.relative_to(ROOT))}


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
        result = subprocess.run(["powershell", "-NoProfile", "-Command", ps], text=True, capture_output=True, timeout=90)
        return {"attempted": True, "returncode": result.returncode, "pdf_exists": PDF.exists(), "stderr": result.stderr[-500:]}
    except Exception as exc:
        return {"attempted": True, "error": str(exc), "pdf_exists": PDF.exists()}


def cleanup() -> None:
    for path in [
        SLIDES,
        LAYOUT,
        WORKSPACE,
        OUT / "node_modules",
        OUT / "package.json",
        OUT / "artifact_build_manifest.json",
        OUT / "artifact-build-manifest.json",
    ]:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def main() -> None:
    ensure_dirs()
    assets = generate_assets()
    charts = copy_data_artifacts()
    write_slide_modules(assets, charts)
    build = build_pptx()
    contact = make_contact_sheet()
    pdf = try_export_pdf() if PPTX.exists() else {"attempted": False}
    preview_count = len(list(PREVIEW.glob("slide-*.png")))
    image_qa = json.loads(IMAGE_QA.read_text(encoding="utf-8"))
    ok = PPTX.exists() and PPTX.stat().st_size > 0 and preview_count == 14 and contact.get("ok") and image_qa.get("ok")
    rel = lambda path: str(Path(path).resolve().relative_to(ROOT)) if path else None
    qa = {
        "ok": bool(ok),
        "pptx": rel(PPTX) if PPTX.exists() else None,
        "pdf": rel(PDF) if PDF.exists() else None,
        "preview_count": preview_count,
        "contact_sheet": rel(CONTACT) if CONTACT.exists() else None,
        "imagegen_assets": len(assets),
        "imagegen_asset_qa": rel(IMAGE_QA),
        "prompt_manifest": rel(PROMPT_MANIFEST),
        "slide_to_evidence_map": rel(SLIDE_MAP),
        "build": {
            "returncode": build["returncode"],
            "slide_count": preview_count,
            "pptx_bytes": PPTX.stat().st_size if PPTX.exists() else 0,
            "materialized": PPTX.exists() and PPTX.stat().st_size > 0,
        },
        "pdf_export": pdf,
        "rules": [
            "GPT image 2 assets are used only for conceptual and scene visuals.",
            "Statistical/model/data-chain figures are copied from data-driven v1 artifacts.",
            "No API keys are stored in output files.",
        ],
    }
    QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    if ok:
        cleanup()
    if not ok:
        raise SystemExit(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
