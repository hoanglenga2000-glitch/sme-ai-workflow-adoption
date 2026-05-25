from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "12_机械学习完整案例展示PPT_v2_imagegen"
OUT = ROOT / "12_机械学习完整案例展示PPT_gamma_supervised"
PAYLOADS = OUT / "payloads"
SINGLE_PPTX = OUT / "single_page_pptx"
PREVIEW = OUT / "preview_png"
QA_DIR = OUT / "qa"
FINAL = OUT / "final"

API_BASE = "https://public-api.gamma.app/v1.0"
RAW_BASE = (
    "https://raw.githubusercontent.com/hoanglenga2000-glitch/"
    "sme-ai-workflow-adoption/main/"
)


SLIDES = [
    {
        "no": 1,
        "title": "企业 AI 部署偏好与治理机制：完整机器学习案例",
        "claim": "本项目把官方数据、机器学习验证和可复现展示合成一个完整课程案例。",
        "proof": "12.77M official source rows; 5,814 Stage 2 modeling rows; Stage 2 R2=0.7245.",
        "boundary": "本页图片是 GPT image 2 概念视觉，不作为统计证据。",
        "visual": "assets_imagegen_v2/01_cover_enterprise_ai_data_pipeline.png",
    },
    {
        "no": 2,
        "title": "主证据从问卷/Kaggle 升级为官方数据",
        "claim": "研究主证据采用 Eurostat 官方企业 ICT 数据，问卷和访谈只作为辅助说明。",
        "proof": "Eurostat source manifests, SHA256 records, data/raw and data/processed.",
        "boundary": "不得把问卷星聚合统计写成逐样本原始数据库。",
        "visual": "assets_imagegen_v2/02_data_upgrade_official_sources.png",
    },
    {
        "no": 3,
        "title": "数据生命周期每一步都有仓库证据",
        "claim": "从源数据、清洗、建模到展示，每一步都能在仓库中追踪。",
        "proof": "data/raw/manifest*.jsonl, data/processed/*.csv, src/, outputs/.",
        "boundary": "展示只讲公开复现材料，不暴露私密论文包。",
        "visual": "assets_imagegen_v2/03_data_lifecycle_pipeline.png",
    },
    {
        "no": 4,
        "title": "Stage 1 解释 SME 机制，Stage 2 验证行业/区域泛化",
        "claim": "两阶段数据承担不同角色，不能把 Stage 2 写成 SME-only。",
        "proof": "Stage 1: 553 / 544 / 36; Stage 2: 5,814 / 36 / 50; years 2021, 2023-2025.",
        "boundary": "Stage 2 是行业/区域外部验证层，不是中小企业专属样本。",
        "visual": "assets_imagegen_v2/04_stage1_stage2_boundary.png",
    },
    {
        "no": 5,
        "title": "1277 万源数据行不是直接训练样本",
        "claim": "千万级官方数据经扫描、筛选和面板聚合后进入建模。",
        "proof": "12,770,332 raw rows -> 12,341,630 scanned rows -> 856,880 feature-filtered rows -> 5,814 modeling rows.",
        "boundary": "禁止写成千万样本直接训练。",
        "visual": "figures/fig_waterfall.png",
    },
    {
        "no": 6,
        "title": "监督学习任务围绕官方 AI 工作流指标展开",
        "claim": "模型任务围绕官方 AI 工作流/流程自动化指标，而不是训练大语言模型。",
        "proof": "target_workflow_automation; Ridge and ExtraTrees; leakage-controlled features.",
        "boundary": "LLM/Agent 负责组织回答，表格模型负责可复现预测和解释。",
        "visual": "assets_imagegen_v2/05_ml_task_tabular_modeling.png",
    },
    {
        "no": 7,
        "title": "GroupKFold 按国家分组降低泄漏",
        "claim": "用国家分组验证降低同一国家信息在训练和测试间泄漏的风险。",
        "proof": "Stage 1 R2=0.8680; Stage 2 R2=0.7245; time holdout as boundary check.",
        "boundary": "模型验证说明泛化能力，不证明因果关系。",
        "visual": "figures/fig_model_validation.png",
    },
    {
        "no": 8,
        "title": "Stage 1 Ridge 支撑 SME 机制解释",
        "claim": "Stage 1 用 Ridge 给出更稳定、可解释的机制层结果。",
        "proof": "553 panel rows, 544 modeling rows, 36 geo groups; R2=0.8680; MAE=1.8342.",
        "boundary": "Stage 1 是 SME 机制解释层，不直接替代 Stage 2 外部验证。",
        "visual": "figures/fig_model_validation.png",
    },
    {
        "no": 9,
        "title": "Stage 2 ExtraTrees 支撑行业/区域外部验证",
        "claim": "Stage 2 在行业和区域层面检验模型是否能跨情境保持解释力。",
        "proof": "5,814 modeling rows, 36 geo groups, 50 industries; R2=0.7245; MAE=1.9646.",
        "boundary": "不把 Stage 2 说成 SME-only，不夸大为因果识别。",
        "visual": "figures/fig_model_validation.png",
    },
    {
        "no": 10,
        "title": "特征重要性服务机制解释，不写成因果证明",
        "claim": "特征重要性用于解释部署准备度、数字基础和治理约束的相对作用。",
        "proof": "feature importance table and mechanism interpretation.",
        "boundary": "重要性排序不等于因果效应。",
        "visual": "figures/fig_feature_importance.png",
    },
    {
        "no": 11,
        "title": "Agent 原型把证据约束转成可演示工具",
        "claim": "Agent 原型只基于仓库证据回答，并在缺少模型二进制时安全返回 unavailable。",
        "proof": "10_Agent系统 tests and reports; 8 unit tests pass.",
        "boundary": "公开仓库不提交 .joblib/.pkl 模型二进制。",
        "visual": "assets_imagegen_v2/06_agent_evidence_constrained.png",
    },
    {
        "no": 12,
        "title": "公开仓库只保留课程复现材料",
        "claim": "公开仓库保留课程案例和复现工程，私密论文与问卷/访谈材料不公开。",
        "proof": "Public: data/code/outputs/PPT; private: manuscript/questionnaire/interview; no .env/.joblib/.pkl.",
        "boundary": "不得把 private_research_archive 或投稿包推到 GitHub。",
        "visual": "assets_imagegen_v2/07_github_public_private_boundary.png",
    },
    {
        "no": 13,
        "title": "边界说清楚，比把结论写满更专业",
        "claim": "准确说明数据边界能提高课程展示和后续研究可信度。",
        "proof": "source-chain wording; no causal overclaim; questionnaire is aggregate only.",
        "boundary": "禁止机器学习证明因果、千万样本直接训练、问卷逐样本数据库等越界表述。",
        "visual": "assets_imagegen_v2/07_github_public_private_boundary.png",
    },
    {
        "no": 14,
        "title": "真实数据、严格验证、可复现展示",
        "claim": "最终展示交付包括 PPTX、PDF、预览、证据映射和 QA 报告。",
        "proof": "Final PPTX/PDF; 14 previews; contact sheet; slide_to_evidence_map.",
        "boundary": "课程展示版不是投稿论文终稿。",
        "visual": "assets_imagegen_v2/08_summary_reproducible_research.png",
    },
]


def ensure_dirs() -> None:
    for folder in [OUT, PAYLOADS, SINGLE_PPTX, PREVIEW, QA_DIR, FINAL]:
        folder.mkdir(parents=True, exist_ok=True)


def rel_source_path(relative_visual: str) -> Path:
    return SOURCE_DIR / relative_visual


def raw_url(relative_visual: str) -> str:
    repo_path = f"12_机械学习完整案例展示PPT_v2_imagegen/{relative_visual}"
    return RAW_BASE + urllib.parse.quote(repo_path.replace("\\", "/"), safe="/:")


def request_json(url: str, method: str = "GET", payload: dict | None = None, api_key: str | None = None) -> dict:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, method=method, data=data)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Codex-Gamma-API/1.0",
    )
    if api_key:
        req.add_header("X-API-KEY", api_key)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gamma API HTTP {exc.code}: {body[:1200]}") from exc


def download(url: str, path: Path) -> None:
    req = urllib.request.Request(url, method="GET")
    req.add_header(
        "User-Agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Codex-Gamma-API/1.0",
    )
    req.add_header("Accept", "application/vnd.openxmlformats-officedocument.presentationml.presentation,*/*")
    with urllib.request.urlopen(req, timeout=180) as resp:
        path.write_bytes(resp.read())


def slide_input_text(slide: dict) -> str:
    image_url = raw_url(slide["visual"])
    return f"""# {slide["title"]}

{image_url}

本页结论：{slide["claim"]}

证据对象：{slide["proof"]}

边界说明：{slide["boundary"]}
"""


def payload_for_slide(slide: dict, export_as: str) -> dict:
    return {
        "inputText": slide_input_text(slide),
        "additionalInstructions": (
            "你是机器学习课程展示 PPT 设计师。只生成这一页。"
            "这必须是一张 16:9 横版 PPT 页面，不是网页长卡片，不能有滚动内容，所有元素必须完整留在画布内。"
            "必须使用 inputText 中给出的唯一图片 URL 作为本页主视觉或证据图，"
            "不要把 URL 字符串显示在页面上，不要生成任何额外图片，不要搜索网络图片。"
            "白底、深灰正文、低饱和蓝、少量橙色强调。"
            "版式必须使用左右分栏：左侧 45% 放标题、两行说明和三枚小指标；右侧 45% 放图片。"
            "图片必须完整显示，使用 contain 方式，不允许裁切、放大到页面外、铺满背景或超出版心。"
            "整页所有内容必须在 16:9 画布内，底部至少保留 40px 空白。"
            "不要做全宽大图，不要做网页式长页面，不要做大卡片网格。"
            "每页只保留一个清晰 claim 和一个 proof object。不要添加额外章节标签、圆角卡片组、长段落或装饰信息。"
            "严禁新增或改写数值；严禁说千万样本直接训练、机器学习证明因果、Stage 2 是 SME-only。"
        ),
        "textMode": "preserve",
        "format": "presentation",
        "numCards": 1,
        "cardSplit": "auto",
        "exportAs": export_as,
        "textOptions": {
            "language": "zh-cn",
            "tone": "professional",
            "audience": "college machine learning course instructor",
            "amount": "brief",
        },
        "imageOptions": {
            "source": "noImages",
        },
        "cardOptions": {
            "dimensions": "16x9",
        },
    }


def pptx_info(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    with zipfile.ZipFile(path) as zf:
        slides = [n for n in zf.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
        media = [n for n in zf.namelist() if n.startswith("ppt/media/")]
    return {"exists": True, "bytes": path.stat().st_size, "slide_count": len(slides), "media_count": len(media)}


def render_preview(pptx: Path, png: Path) -> dict:
    ps = f"""
$ErrorActionPreference = 'Stop'
$ppt = New-Object -ComObject PowerPoint.Application
$ppt.Visible = [Microsoft.Office.Core.MsoTriState]::msoTrue
$presentation = $ppt.Presentations.Open('{str(pptx)}', $true, $false, $false)
$presentation.Slides.Item(1).Export('{str(png)}', 'PNG', 1600, 900)
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
        return {"attempted": True, "returncode": result.returncode, "png_exists": png.exists(), "stderr": result.stderr[-500:]}
    except Exception as exc:
        return {"attempted": True, "error": str(exc), "png_exists": png.exists()}


def wait_generation(generation_id: str, api_key: str) -> dict:
    final = {}
    for _ in range(90):
        final = request_json(f"{API_BASE}/generations/{generation_id}", api_key=api_key)
        state = str(final.get("status") or "").lower()
        if state in {"completed", "complete", "succeeded", "success", "failed", "error"}:
            return final
        time.sleep(5)
    return final | {"pollTimeout": True}


def run_slide(slide: dict, args: argparse.Namespace, api_key: str | None) -> dict:
    no = int(slide["no"])
    payload = payload_for_slide(slide, args.export_as)
    payload_path = PAYLOADS / f"slide_{no:02d}_payload.json"
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    local_visual = rel_source_path(slide["visual"])
    qa = {
        "ok": False,
        "slide": no,
        "title": slide["title"],
        "local_visual_exists": local_visual.exists(),
        "visual_url": raw_url(slide["visual"]),
        "payload": str(payload_path.relative_to(ROOT)),
        "mode": "dry_run" if args.dry_run or not api_key else "gamma_api",
        "note": "API key is read from GAMMA_API_KEY only and is never written to output files.",
    }

    if args.dry_run or not api_key:
        qa["blocked"] = "GAMMA_API_KEY missing or dry-run requested"
        qa["ok"] = bool(local_visual.exists())
        return qa

    try:
        created = request_json(f"{API_BASE}/generations", method="POST", payload=payload, api_key=api_key)
        generation_id = created.get("generationId") or created.get("id") or created.get("generation", {}).get("id")
        if not generation_id:
            raise RuntimeError(f"Could not find generation id in response: {created}")
        final = wait_generation(generation_id, api_key)
        qa["generationId"] = generation_id
        qa["status"] = final.get("status")
        qa["gammaUrl"] = final.get("gammaUrl")
        export_url = final.get("exportUrl")
        qa["exportUrlPresent"] = bool(export_url)
        if export_url:
            pptx = SINGLE_PPTX / f"slide_{no:02d}_gamma.pptx"
            download(export_url, pptx)
            qa["pptx"] = str(pptx.relative_to(ROOT))
            qa["pptx_info"] = pptx_info(pptx)
            png = PREVIEW / f"slide_{no:02d}_gamma.png"
            qa["render_preview"] = render_preview(pptx, png) if not args.skip_render else {"attempted": False}
            if png.exists():
                qa["preview_png"] = str(png.relative_to(ROOT))
            info = qa.get("pptx_info", {})
            qa["ok"] = bool(info.get("exists") and info.get("slide_count") == 1 and info.get("media_count", 0) >= 1)
        else:
            qa["ok"] = False
            qa["error"] = "Gamma did not return exportUrl"
    except Exception as exc:
        retry_payload = dict(payload)
        retry_payload["imageOptions"] = {"source": "noImages", "model": "dall-e-3"}
        qa["first_error"] = str(exc)
        qa["retryWithModelField"] = True
        try:
            created = request_json(f"{API_BASE}/generations", method="POST", payload=retry_payload, api_key=api_key)
            generation_id = created.get("generationId") or created.get("id") or created.get("generation", {}).get("id")
            if not generation_id:
                raise RuntimeError(f"Could not find generation id in retry response: {created}")
            final = wait_generation(generation_id, api_key)
            qa["generationId"] = generation_id
            qa["status"] = final.get("status")
            qa["gammaUrl"] = final.get("gammaUrl")
            export_url = final.get("exportUrl")
            qa["exportUrlPresent"] = bool(export_url)
            if export_url:
                pptx = SINGLE_PPTX / f"slide_{no:02d}_gamma.pptx"
                download(export_url, pptx)
                qa["pptx"] = str(pptx.relative_to(ROOT))
                qa["pptx_info"] = pptx_info(pptx)
                png = PREVIEW / f"slide_{no:02d}_gamma.png"
                qa["render_preview"] = render_preview(pptx, png) if not args.skip_render else {"attempted": False}
                if png.exists():
                    qa["preview_png"] = str(png.relative_to(ROOT))
                info = qa.get("pptx_info", {})
                qa["ok"] = bool(info.get("exists") and info.get("slide_count") == 1 and info.get("media_count", 0) >= 1)
            else:
                qa["ok"] = False
                qa["error"] = "Gamma retry did not return exportUrl"
        except Exception as retry_exc:
            qa["ok"] = False
            qa["error"] = str(retry_exc)
    return qa


def write_plan() -> None:
    plan_csv = OUT / "gamma_supervised_slide_plan.csv"
    with plan_csv.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["no", "title", "claim", "proof", "boundary", "visual", "visual_url"])
        writer.writeheader()
        for slide in SLIDES:
            writer.writerow({**slide, "visual_url": raw_url(slide["visual"])})
    readme = OUT / "README.md"
    readme.write_text(
        """# Gamma 逐页监督生成工作区

本目录用于把 GPT image 2 / 数据驱动图交给 Gamma 做版式生成。流程是一页一页生成：

1. Codex 提供已通过检查的图片 URL 和证据约束。
2. Gamma 只负责单页 PPT 排版。
3. 每页导出 PPTX 和 PNG 预览。
4. Codex 检查页面是否通过，确认后再生成下一页。

`payloads/` 保存每页发送给 Gamma 的脱敏请求体，不包含 API key。
`single_page_pptx/` 保存每页 Gamma 生成结果。
`preview_png/` 保存每页预览图。
`qa/` 保存每页质量门禁。

运行时必须临时设置 `GAMMA_API_KEY` 环境变量；不要把密钥写入仓库、脚本、JSON 或 Markdown。
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Supervised one-slide-at-a-time Gamma workflow.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--slide", type=int, help="Generate one slide number, 1-14.")
    group.add_argument("--all", action="store_true", help="Generate all slides, stopping on the first failed QA.")
    parser.add_argument("--dry-run", action="store_true", help="Only write payloads and plan; do not call Gamma.")
    parser.add_argument("--skip-render", action="store_true", help="Skip PowerPoint COM preview rendering.")
    parser.add_argument("--export-as", choices=["pptx", "pdf", "png"], default="pptx")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_dirs()
    write_plan()
    selected = SLIDES if args.all else [SLIDES[(args.slide or 1) - 1]]
    api_key = os.environ.get("GAMMA_API_KEY")
    all_results = []
    for slide in selected:
        qa = run_slide(slide, args, api_key)
        all_results.append(qa)
        qa_path = QA_DIR / f"slide_{int(slide['no']):02d}_qa.json"
        qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"slide": slide["no"], "ok": qa["ok"], "qa": str(qa_path.relative_to(ROOT))}, ensure_ascii=False))
        if args.all and not qa["ok"]:
            break
    summary = {
        "ok": all(item.get("ok") for item in all_results),
        "generated": len(all_results),
        "mode": "dry_run" if args.dry_run or not api_key else "gamma_api",
        "results": all_results,
    }
    (OUT / "gamma_supervised_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
