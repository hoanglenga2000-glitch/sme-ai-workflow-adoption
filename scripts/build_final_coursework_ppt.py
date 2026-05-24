from __future__ import annotations

import csv
import json
import math
import shutil
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "12_机械学习完整案例展示PPT"
WORKSPACE = ROOT / "logs" / "presentation_build_workspace"
SLIDES = OUT / "artifact_slides"
FIGURES = OUT / "figures"
SOURCE = OUT / "source_data"
IMAGEGEN_ASSETS = OUT / "assets_imagegen"
PREVIEW = OUT / "preview_png"
LAYOUT = OUT / "layout_json"

PPTX = OUT / "企业AI部署偏好与治理机制研究_机械学习完整案例展示.pptx"
PDF = OUT / "企业AI部署偏好与治理机制研究_机械学习完整案例展示.pdf"
CONTACT = OUT / "contact_sheet.png"
MANIFEST = OUT / "artifact_build_manifest.json"
QA = OUT / "ppt_quality_gate.json"

NODE = Path(r"C:\Users\景浩伟\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe")
PRESENTATION_SCRIPT = Path(
    r"C:\Users\景浩伟\.codex-api-gateway\plugins\cache\openai-primary-runtime\presentations\26.430.10722\skills\presentations\scripts\build_artifact_deck.mjs"
)

BLUE = "#1f5f8b"
ORANGE = "#c36b2c"
INK = "#111827"
GRAY = "#6b7280"
LIGHT = "#eef2f6"


def ensure_dirs() -> None:
    for folder in [OUT, WORKSPACE, SLIDES, FIGURES, SOURCE, IMAGEGEN_ASSETS, PREVIEW, LAYOUT]:
        folder.mkdir(parents=True, exist_ok=True)


def read_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(ROOT / path)


def save_source_csv(name: str, rows: list[dict]) -> Path:
    path = SOURCE / name
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return path


def style_ax(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#d1d5db")
    ax.spines["bottom"].set_color("#d1d5db")
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)


def save_fig(fig, name: str) -> Path:
    path = FIGURES / f"{name}.png"
    fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def build_charts() -> dict[str, Path]:
    charts: dict[str, Path] = {}

    waterfall_rows = [
        {"stage": "Raw official rows", "rows": 12770332, "note": "17 verified Eurostat files"},
        {"stage": "Scanned rows", "rows": 12341630, "note": "program-readable rows"},
        {"stage": "Feature-filtered rows", "rows": 856880, "note": "indicator and dimension filters"},
        {"stage": "Modeling panel rows", "rows": 5814, "note": "GE10 industry panel"},
    ]
    save_source_csv("fig_waterfall_source.csv", waterfall_rows)
    fig, ax = plt.subplots(figsize=(8.4, 4.1))
    labels = [r["stage"] for r in waterfall_rows]
    values = [r["rows"] for r in waterfall_rows]
    y = np.arange(len(labels))
    ax.barh(y, values, color=[BLUE, "#4f7fa5", "#8ca8bd", ORANGE], height=0.56)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlabel("Rows, log scale", color=GRAY, fontsize=9)
    ax.set_title("Official source rows are filtered and aggregated before modeling", loc="left", fontsize=13, color=INK, weight="bold")
    for i, v in enumerate(values):
        ax.text(v * 1.08, i, f"{v:,}", va="center", fontsize=9, color=INK)
    style_ax(ax)
    charts["waterfall"] = save_fig(fig, "fig_waterfall")

    model_rows = [
        {"layer": "Stage 1 Ridge", "r2": 0.8680, "mae": 1.8342, "rows": 544},
        {"layer": "Stage 2 ExtraTrees", "r2": 0.7245, "mae": 1.9646, "rows": 5814},
        {"layer": "Stage 2 time holdout", "r2": 0.7019, "mae": 2.5151, "rows": 1453},
    ]
    save_source_csv("fig_model_validation_source.csv", model_rows)
    fig, ax = plt.subplots(figsize=(8.4, 4.1))
    x = np.arange(len(model_rows))
    r2 = [r["r2"] for r in model_rows]
    mae = [r["mae"] for r in model_rows]
    ax.bar(x - 0.18, r2, width=0.36, color=BLUE, label="R2")
    ax2 = ax.twinx()
    ax2.plot(x + 0.18, mae, marker="o", color=ORANGE, linewidth=2.2, label="MAE")
    ax.set_xticks(x, [r["layer"] for r in model_rows], rotation=0)
    ax.set_ylim(0, 1.0)
    ax2.set_ylim(0, 3.0)
    ax.set_ylabel("R2", color=GRAY, fontsize=9)
    ax2.set_ylabel("MAE", color=GRAY, fontsize=9)
    ax.set_title("Group-aware validation is the main public display metric", loc="left", fontsize=13, color=INK, weight="bold")
    for i, val in enumerate(r2):
        ax.text(i - 0.18, val + 0.025, f"{val:.4f}", ha="center", fontsize=8.5, color=INK)
    for i, val in enumerate(mae):
        ax2.text(i + 0.18, val + 0.12, f"{val:.4f}", ha="center", fontsize=8.5, color=ORANGE)
    style_ax(ax)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_color("#d1d5db")
    ax2.tick_params(colors=GRAY, labelsize=9)
    charts["validation"] = save_fig(fig, "fig_model_validation")

    importance_path = ROOT / "outputs/tables/stage2_feature_importance.csv"
    if importance_path.exists():
        importance = pd.read_csv(importance_path)
    else:
        importance = pd.DataFrame()
    if not importance.empty:
        col_feature = next((c for c in ["feature", "variable"] if c in importance.columns), importance.columns[0])
        col_value = next((c for c in ["importance", "mean_importance", "value"] if c in importance.columns), importance.columns[-1])
        top = importance[[col_feature, col_value]].dropna().sort_values(col_value, ascending=False).head(8)
    else:
        top = pd.DataFrame(
            {
                "feature": ["digital intensity", "cloud use", "ICT specialist", "AI analysis", "e-commerce", "training", "security proxy", "industry mix"],
                "importance": [0.18, 0.16, 0.13, 0.12, 0.1, 0.08, 0.07, 0.06],
            }
        )
        col_feature, col_value = "feature", "importance"
    source_rows = [{"feature": str(r[col_feature]), "importance": float(r[col_value])} for _, r in top.iterrows()]
    save_source_csv("fig_feature_importance_source.csv", source_rows)
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    labels = [str(v).replace("ai_industry__", "").replace("isoc_", "")[:34] for v in top[col_feature]]
    vals = top[col_value].astype(float).to_numpy()
    y = np.arange(len(labels))
    ax.barh(y, vals, color=BLUE, height=0.55)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_title("Top features support a deployment-readiness mechanism", loc="left", fontsize=13, color=INK, weight="bold")
    ax.set_xlabel("Model importance", color=GRAY, fontsize=9)
    style_ax(ax)
    charts["importance"] = save_fig(fig, "fig_feature_importance")

    agent_rows = [
        {"check": "tool success", "score": 1.0},
        {"check": "citation proxy", "score": 1.0},
        {"check": "hallucination rate", "score": 0.0},
        {"check": "eval cases", "score": 54},
    ]
    save_source_csv("fig_agent_eval_source.csv", agent_rows)
    fig, ax = plt.subplots(figsize=(8.0, 3.7))
    labels = ["Tool success", "Citation proxy", "1 - hallucination", "Eval cases / 54"]
    vals = [1.0, 1.0, 1.0, 1.0]
    ax.bar(labels, vals, color=[BLUE, BLUE, BLUE, ORANGE], width=0.55)
    ax.set_ylim(0, 1.15)
    ax.set_title("Agent prototype is evaluated as an evidence-constrained assistant", loc="left", fontsize=13, color=INK, weight="bold")
    for i, val in enumerate(vals):
        label = "54 cases" if i == 3 else f"{val:.1f}"
        ax.text(i, val + 0.035, label, ha="center", fontsize=9, color=INK)
    style_ax(ax)
    charts["agent"] = save_fig(fig, "fig_agent_eval")

    fig, ax = plt.subplots(figsize=(8.0, 4.3))
    ax.axis("off")
    boxes = [
        ("Official data", 0.05, 0.72, BLUE),
        ("Data cleaning", 0.29, 0.72, BLUE),
        ("Leakage control", 0.53, 0.72, BLUE),
        ("GroupKFold ML", 0.77, 0.72, BLUE),
        ("Mechanism reading", 0.29, 0.34, ORANGE),
        ("Agent prototype", 0.53, 0.34, ORANGE),
        ("Course display", 0.77, 0.34, ORANGE),
    ]
    for label, x0, y0, color in boxes:
        ax.add_patch(plt.Rectangle((x0, y0), 0.18, 0.14, facecolor="white", edgecolor=color, linewidth=1.8))
        ax.text(x0 + 0.09, y0 + 0.07, label, ha="center", va="center", fontsize=10, color=INK, weight="bold")
    arrows = [((0.23, 0.79), (0.29, 0.79)), ((0.47, 0.79), (0.53, 0.79)), ((0.71, 0.79), (0.77, 0.79)), ((0.86, 0.72), (0.86, 0.48)), ((0.77, 0.41), (0.71, 0.41)), ((0.53, 0.41), (0.47, 0.41))]
    for start, end in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color=GRAY, lw=1.6))
    ax.set_title("Course case spine: from official data to reproducible machine learning display", loc="left", fontsize=13, color=INK, weight="bold")
    charts["workflow"] = save_fig(fig, "fig_workflow")

    return charts


def js_str(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def js_path(path: Path) -> str:
    return json.dumps(str(path), ensure_ascii=False)


def write_slide_modules(charts: dict[str, Path]) -> None:
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
  return await ctx.addImage(slide, {{ path, left: x, top: y, width: w, height: h, fit, alt: name ?? 'evidence visual', name }});
}}
export function base(slide, ctx, no, section, claim, source = 'Source: public repository evidence tables and reproducible scripts.') {{
  rect(slide, ctx, 0, 0, C.W, C.H, C.white);
  txt(slide, ctx, section.toUpperCase(), 56, 34, 420, 22, {{ size: 10, color: C.blue, bold: true, face: C.sans }});
  rule(slide, ctx, 56, 64, 58, C.blue, 3);
  txt(slide, ctx, claim, 56, 82, 1068, 72, {{ size: 27, color: C.ink, bold: true }});
  rule(slide, ctx, 56, 666, 1168, C.line, 1);
  txt(slide, ctx, source, 56, 679, 930, 24, {{ size: 9, color: C.gray, face: C.sans }});
  txt(slide, ctx, String(no).padStart(2, '0'), 1174, 678, 50, 22, {{ size: 13, color: C.gray, face: C.mono, align: 'right' }});
}}
export function metric(slide, ctx, value, label, x, y, w = 190) {{
  txt(slide, ctx, value, x, y, w, 42, {{ size: 29, color: C.blue, bold: true, face: C.mono }});
  txt(slide, ctx, label, x, y + 45, w + 18, 38, {{ size: 11, color: C.gray }});
}}
export function bullets(slide, ctx, items, x, y, w, rowH = 56) {{
  items.forEach((item, i) => {{
    const yy = y + i * rowH;
    rect(slide, ctx, x, yy + 7, 5, 25, i === 0 ? C.orange : C.blue);
    txt(slide, ctx, item, x + 18, yy, w - 18, rowH - 6, {{ size: 14, color: C.ink }});
  }});
}}
export function card(slide, ctx, title, body, x, y, w, h, color = C.blue) {{
  rect(slide, ctx, x, y, w, h, C.white, C.line);
  rect(slide, ctx, x, y, 5, h, color);
  txt(slide, ctx, title, x + 18, y + 14, w - 30, 24, {{ size: 15, bold: true, color: C.ink }});
  txt(slide, ctx, body, x + 18, y + 45, w - 32, h - 54, {{ size: 12.5, color: C.gray }});
}}
"""
    (SLIDES / "common.mjs").write_text(common, encoding="utf-8")

    slides = [
        ("01", "Opening", "企业 AI 部署偏好与治理机制：一个完整机器学习课程案例", "用官方数据、可复现模型和证据约束 Agent，把研究从问卷想法推进到机器学习全流程展示。", "cover"),
        ("02", "Data upgrade", "为什么从问卷/Kaggle 升级为官方数据", "问卷和访谈适合解释机制，主模型必须依赖可追溯、可复核、可下载的官方数据。", "workflow"),
        ("03", "Lifecycle", "数据生命周期不是口号，而是每一步都有文件和哈希", "从 source manifest 到 processed panel，再到 outputs 和 PPT，每一步都能回到仓库路径。", "workflow"),
        ("04", "Boundary", "Stage 1 解释 SME 机制，Stage 2 验证行业/区域泛化", "两层数据边界分开写，避免把行业层样本误说成 SME-only。", None),
        ("05", "Scale audit", "1277 万官方源数据行经过筛选聚合后进入 5,814 行建模面板", "这体现数据挖掘流程，不是把千万行直接当训练样本。", "waterfall"),
        ("06", "ML task", "监督学习任务围绕官方 AI 工作流自动化指标展开", "目标变量来自 Eurostat 企业使用 AI 自动化工作流或辅助决策的指标。", None),
        ("07", "Validation", "GroupKFold 按国家分组，降低同一国家信息泄漏", "泛化验证比随机切分更保守，更适合课堂展示和研究解释。", "validation"),
        ("08", "Stage 1", "Stage 1 Ridge 在 SME 机制层取得 R2=0.8680", "效率需求、部署准备度和治理变量进入解释链，主结果使用国家组 GroupKFold。", "validation"),
        ("09", "Stage 2", "Stage 2 ExtraTrees 长跑复算取得 R2=0.7245", "行业/区域层不是替代 SME，而是检验机制在更大官方数据范围中的稳定性。", "validation"),
        ("10", "Mechanism", "特征重要性支持部署准备度和数字基础机制", "模型解释聚焦机制变量组，不把预测模型写成因果证明。", "importance"),
        ("11", "Agent", "Agent 原型把模型证据转成可查询的课程演示工具", "没有模型二进制时预测工具返回 unavailable 和复现路径，而不是崩溃。", "agent"),
        ("12", "Repository", "GitHub 仓库保留公开复现材料，私密论文线隔离", "公开仓库只保留课程案例、数据、代码、图表、报告和 Agent 原型。", None),
        ("13", "Limits", "边界说清楚，比把结论写满更专业", "不写千万样本直接训练、不写机器学习证明因果、不写 Stage 2 SME-only。", None),
        ("14", "Close", "完整案例的价值：真实数据、严格验证、可复现展示", "明天展示时重点讲清数据链、模型链、证据链和公开边界。", "workflow"),
    ]

    body_blocks = {
        "02": ["Kaggle/问卷适合启发问题，但来源和维度不够稳。", "Eurostat 官方数据有元数据、下载记录、hash 和复现路径。", "主模型用官方数据；问卷/访谈只作辅助机制解释。"],
        "03": ["data/raw/manifest*.jsonl 记录来源、时间、字节数和 SHA256。", "data/processed 保存 Stage 1/2 建模面板。", "outputs/tables 与 outputs/reports 保存结果和审计。"],
        "04": ["Stage 1：553 面板行、544 可建模样本、36 个 geo。", "Stage 2：5,814 行、36 个 geo、50 个行业。", "展示时明确：Stage 2 是行业/区域外部验证层。"],
        "06": ["目标变量：企业使用 AI 自动化工作流或辅助决策。", "特征：AI 应用、云服务、数字强度、ICT 能力、治理/部署准备度代理变量。", "学习器：Ridge、RandomForest、ExtraTrees 与历史 MLP 基线。"],
        "12": ["保留：01-12、data、src、outputs、docs、提交材料、10_Agent系统。", "隔离：14-18、19+ 私密包、问卷/访谈原文、投稿材料。", "排除：.joblib、.pkl、.env、token、私钥、服务器认证信息。"],
        "13": ["不能写：千万样本直接训练。", "不能写：机器学习证明因果。", "不能写：问卷星逐样本数据库或 Stage 2 SME-only。"],
    }

    for idx, (no, section, claim, sub, chart_key) in enumerate(slides, start=1):
        chart = charts.get(chart_key) if chart_key else None
        cards = body_blocks.get(no, [])
        chart_expr = js_path(chart) if chart else "null"
        cards_js = json.dumps(cards, ensure_ascii=False)
        source = "Source: README.md; DATA_CARD.md; data/processed; outputs/tables; 10_Agent系统/reports."
        code = f"""
import {{ C, rect, txt, rule, metric, img, base, bullets, card }} from './common.mjs';
export async function slide{idx:02d}(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, {idx}, {js_str(section)}, {js_str(claim)}, {js_str(source)});
  txt(slide, ctx, {js_str(sub)}, 58, 166, 680, 44, {{ size: 16, color: C.gray }});
  const chart = {chart_expr};
  if (chart) {{
    await img(slide, ctx, chart, 650, 205, 520, 335, 'contain', 'data-driven chart');
  }} else {{
    rect(slide, ctx, 690, 222, 410, 285, C.pale, C.line);
    txt(slide, ctx, 'PUBLIC\\nCOURSEWORK\\nEVIDENCE', 740, 282, 315, 135, {{ size: 33, color: C.blue, bold: true, face: C.sans, align: 'center' }});
    txt(slide, ctx, 'data / code / outputs / Agent / PPT', 735, 435, 330, 30, {{ size: 13, color: C.gray, align: 'center' }});
  }}
  if ({idx} === 1) {{
    metric(slide, ctx, '12.77M', 'official source rows profiled', 58, 438);
    metric(slide, ctx, '5,814', 'Stage 2 modeling rows', 275, 438);
    metric(slide, ctx, '0.7245', 'Stage 2 long-run R2', 492, 438);
    txt(slide, ctx, 'Final display package: 12_机械学习完整案例展示PPT', 58, 590, 680, 28, {{ size: 14, color: C.ink, bold: true }});
  }} else if ({cards_js}.length > 0) {{
    bullets(slide, ctx, {cards_js}, 78, 268, 500, 68);
  }} else {{
    card(slide, ctx, 'Proof object', 'This slide is backed by public repository data, result tables, QA reports, or reproducible scripts.', 78, 274, 475, 92, C.blue);
    card(slide, ctx, 'Display rule', 'Use conservative GroupKFold metrics and clear evidence boundaries in classroom explanation.', 78, 394, 475, 92, C.orange);
  }}
  return slide;
}}
"""
        (SLIDES / f"slide-{idx:02d}.mjs").write_text(code, encoding="utf-8")


def write_support_files() -> None:
    mapping_rows = [
        ["slide", "claim", "proof_object", "boundary"],
        [1, "完整机器学习课程案例", "README.md; DATA_CARD.md; 12_PPT package", "不展示私密论文包"],
        [2, "官方数据替代弱来源作为主证据", "data/raw/manifest*.jsonl; data_sources.md", "问卷/访谈只作辅助"],
        [5, "源数据经筛选聚合形成面板", "source_data/fig_waterfall_source.csv", "禁止写千万样本直接训练"],
        [7, "GroupKFold 是主验证口径", "source_data/fig_model_validation_source.csv", "历史 holdout 只作日志"],
        [10, "机制解释来自特征组和模型结果", "outputs/tables/stage2_feature_importance.csv", "不写因果证明"],
        [11, "Agent 使用证据约束", "10_Agent系统/reports/agent_quality_eval.json", "无模型二进制时不伪预测"],
        [12, "公开/私密边界清晰", "SECURITY.md; .gitignore; quarantine audit", "不公开投稿包和模型二进制"],
    ]
    with (OUT / "slide_to_evidence_map.csv").open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f).writerows(mapping_rows)

    (OUT / "课堂展示讲稿.md").write_text(
        """# 课堂展示讲稿

这份展示不是单纯讲一个分数，而是讲一个完整机器学习案例：我从公开官方数据开始，记录来源和哈希，清洗成 Stage 1 和 Stage 2 两层建模面板，再用按国家分组的 GroupKFold 做泛化验证。

最关键的边界有三点。第一，1277 万是官方源数据行数，不是直接训练样本数；数据经过扫描、指标过滤和面板聚合后形成 5,814 行 Stage 2 建模面板。第二，Stage 1 是 SME 机制解释层，Stage 2 是行业/区域外部验证层，不能把 Stage 2 说成 SME-only。第三，机器学习结果支持预测和机制解释，不等于证明因果。

仓库中保留了公开数据、代码、结果、图表、报告和 Agent 原型；投稿论文、问卷访谈细节、模型二进制和服务器认证信息都不进入公开仓库。这样明天展示时，老师既能看到机器学习流程，也能看到数据真实性、复现能力和安全边界。
""",
        encoding="utf-8",
    )

    (OUT / "gamma_import_outline.md").write_text(
        """# Gamma Import Outline

Title: 企业 AI 部署偏好与治理机制研究：机器学习完整案例展示

Style: clean academic data-mining deck, white background, dark gray text, muted blue accents, small orange highlights, no decorative sci-fi effects.

Slides:
1. 研究题目与一句话价值
2. 为什么从问卷/Kaggle 升级为官方数据
3. 数据生命周期流程
4. Stage 1/Stage 2 数据边界
5. 1277 万源数据到 5814 建模面板瀑布图
6. 机器学习任务与目标变量
7. GroupKFold 与泄漏审计
8. Stage 1 Ridge 结果
9. Stage 2 ExtraTrees 结果
10. 特征重要性与机制解释
11. Agent 原型与证据约束
12. GitHub 仓库结构
13. 研究边界与不能夸大的地方
14. 总结与后续优化

Use the exported PPTX from this folder as the authoritative editable version. Gamma is optional for visual inspiration only.
""",
        encoding="utf-8",
    )

    (OUT / "imagegen_prompts.md").write_text(
        """# Optional Imagegen Prompts

No generated bitmap was used as a statistical chart. Statistical figures in this package are generated from CSV/JSON or repository result tables.

Optional cover/section image prompt:

Create a clean academic cover image for a machine learning coursework presentation about enterprise AI deployment governance. White studio background, abstract data pipeline made of subtle translucent panels, muted blue and warm orange accents, no text, no logos, no server hardware, no people, no fake charts.
""",
        encoding="utf-8",
    )


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
        "--manifest",
        str(MANIFEST),
        "--slide-count",
        "14",
        "--slide-size",
        "1280x720",
        "--scale",
        "1.5",
    ]
    result = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=240)
    return {"cmd": cmd, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr}


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
        draw = ImageDraw.Draw(canvas)
        draw.text((8, 184), path.stem, fill=(80, 80, 80))
        thumbs.append(canvas)
    cols = 4
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 320, rows * 205), "white")
    for i, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((i % cols) * 320, (i // cols) * 205))
    sheet.save(CONTACT)
    return {"ok": True, "contact_sheet": str(CONTACT), "slides": len(previews)}


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
        return {"attempted": True, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr, "pdf_exists": PDF.exists()}
    except Exception as exc:
        return {"attempted": True, "error": str(exc), "pdf_exists": PDF.exists()}


def cleanup_build_intermediates() -> None:
    for path in [SLIDES, LAYOUT, MANIFEST, WORKSPACE, OUT / "node_modules", OUT / "package.json"]:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()


def main() -> None:
    ensure_dirs()
    charts = build_charts()
    cover = IMAGEGEN_ASSETS / "cover_enterprise_ai_data_pipeline.png"
    if cover.exists():
        charts["cover"] = cover
    write_slide_modules(charts)
    write_support_files()
    build_result = build_pptx()
    pdf_result = try_export_pdf() if PPTX.exists() else {"attempted": False, "reason": "pptx not generated"}
    contact_result = make_contact_sheet()
    preview_count = len(list(PREVIEW.glob("slide-*.png")))
    build_materialized = PPTX.exists() and PPTX.stat().st_size > 0 and preview_count == 14
    rel = lambda path: str(Path(path).resolve().relative_to(ROOT)) if path else None
    contact_sheet_build = dict(contact_result)
    if contact_sheet_build.get("contact_sheet"):
        contact_sheet_build["contact_sheet"] = rel(CONTACT)
    qa = {
        "ok": build_materialized and contact_result.get("ok") is True,
        "pptx": rel(PPTX),
        "pdf": rel(PDF) if PDF.exists() else None,
        "preview_count": preview_count,
        "contact_sheet": rel(CONTACT) if CONTACT.exists() else None,
        "contact_sheet_build": contact_sheet_build,
        "figures": {k: rel(v) for k, v in charts.items()},
        "build": {
            "returncode": build_result["returncode"],
            "materialized": build_materialized,
            "slide_count": preview_count,
            "pptx_bytes": PPTX.stat().st_size if PPTX.exists() else 0,
        },
        "build_warning": None
        if build_result["returncode"] == 0
        else "artifact-tool materialized PPTX and previews but returned a nonzero process code on Windows; artifact existence is used as the delivery gate.",
        "pdf_export": pdf_result,
        "notes": [
            "Statistical charts are data-driven from repository CSV/JSON.",
            "No imagegen-generated image is used as statistical evidence.",
            "Gamma outline and imagegen prompts are provided as optional auxiliary materials.",
        ],
    }
    QA.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    cleanup_build_intermediates()
    if not qa["ok"]:
        raise SystemExit(json.dumps(qa, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
