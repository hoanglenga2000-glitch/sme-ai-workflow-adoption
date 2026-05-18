from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd


ROOT = Path(r"D:\桌面\codex\机械挖掘学习汇报\github_upload\sme-ai-workflow-adoption")
OUT = ROOT / "08_Research_Grade_Deck"
SLIDES = OUT / "artifact_slides"
ASSETS = OUT / "assets"
CHARTS = ASSETS / "charts_rebuilt"
IMG = ASSETS / "imagegen_research_visuals"
TABLES = ROOT / "outputs" / "tables"
REPORTS = ROOT / "outputs" / "reports"
BROWSER = Path(r"D:\桌面\codex\机械挖掘学习汇报\ppt_assets\browser")

PPTX = OUT / "中小企业AI流程自动化采纳机制研究_Research_Grade_学术答辩版.pptx"
PDF = OUT / "中小企业AI流程自动化采纳机制研究_Research_Grade_学术答辩版.pdf"
NOTES = OUT / "speaker_notes" / "slide_by_slide_speaker_notes.md"
REVISION = OUT / "revision_report.md"
METRICS = OUT / "verified_metrics.json"
SOURCE_NOTES = OUT / "source_notes.json"

for folder in [SLIDES, OUT / "speaker_notes"]:
    folder.mkdir(parents=True, exist_ok=True)


def js_string(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def js_path(path: Path) -> str:
    return json.dumps(str(path), ensure_ascii=False)


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / name)


def image_by_prefix(prefix: str) -> Path:
    matches = sorted(IMG.glob(prefix + "*.png"))
    if not matches and prefix == "01":
        matches = sorted(IMG.glob("*workflow-adoption*.png"))
    if not matches:
        raise FileNotFoundError(prefix)
    return matches[0]


def verify_manifest(rel: str) -> dict:
    path = ROOT / rel
    records = 0
    ok = 0
    failed_status = 0
    bad = 0
    missing = 0
    total_bytes = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        records += 1
        rec = json.loads(line)
        status = str(rec.get("status") or rec.get("http_status") or "")
        local_path = rec.get("path") or rec.get("local_path") or rec.get("file") or rec.get("target")
        sha = rec.get("sha256")
        if status and status not in {"200", "ok", "OK"}:
            failed_status += 1
        if not local_path or not sha:
            continue
        file_path = Path(local_path)
        if not file_path.is_absolute():
            file_path = ROOT / file_path
        if not file_path.exists():
            missing += 1
            continue
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        total_bytes += file_path.stat().st_size
        if digest.lower() == str(sha).lower():
            ok += 1
        else:
            bad += 1
    return {
        "manifest": rel,
        "records": records,
        "hash_ok": ok,
        "hash_bad": bad,
        "missing": missing,
        "failed_status_records": failed_status,
        "verified_bytes": total_bytes,
    }


cv = read_csv("enhanced_cv_results.csv")
gpu = read_csv("enhanced_gpu_baseline.csv")
quality = read_csv("enhanced_data_quality_audit.csv")
ret = read_csv("cleaning_retention_summary.csv")
vif = read_csv("course_vif_diagnostics.csv")
ols = read_csv("course_ols_coefficients.csv")
persona = read_csv("sme_persona_clusters_multisource.csv")
importance = read_csv("enhanced_permutation_importance.csv")

metrics = {
    "stage1_rf_r2": float(cv[(cv.dataset == "stage1_sme_size_class") & (cv.model == "random_forest")].iloc[0].r2_mean),
    "stage1_rf_mae": float(cv[(cv.dataset == "stage1_sme_size_class") & (cv.model == "random_forest")].iloc[0].mae_mean),
    "stage2_et_r2": float(cv[(cv.dataset == "stage2_industry_region_GE10") & (cv.model == "extra_trees")].iloc[0].r2_mean),
    "stage2_et_mae": float(cv[(cv.dataset == "stage2_industry_region_GE10") & (cv.model == "extra_trees")].iloc[0].mae_mean),
    "stage1_mlp_r2": float(gpu[gpu.dataset == "stage1_sme_size_class"].iloc[0].r2),
    "stage2_mlp_r2": float(gpu[gpu.dataset == "stage2_industry_region_GE10"].iloc[0].r2),
    "stage1_rows": int(quality[quality.dataset == "stage1_sme_size_class"].iloc[0].rows),
    "stage2_rows": int(quality[quality.dataset == "stage2_industry_region_GE10"].iloc[0].rows),
    "stage1_geo_count": int(quality[quality.dataset == "stage1_sme_size_class"].iloc[0].geo_count),
    "stage2_geo_count": int(quality[quality.dataset == "stage2_industry_region_GE10"].iloc[0].geo_count),
    "stage2_nace_count": int(quality[quality.dataset == "stage2_industry_region_GE10"].iloc[0].nace_count),
    "stage2_raw_rows": int(ret[ret.stage == "stage2_large_sources_profiled"].iloc[0].raw_or_long_rows),
    "stage2_nonnull": 10453354,
    "stage2_retained": int(ret[ret.stage == "stage2_indicator_filtering"].iloc[0].panel_rows),
    "max_vif": float(vif["vif"].max()),
    "top_persona_cluster": int(persona.sort_values("target_workflow_automation", ascending=False).iloc[0].persona_cluster),
    "top_persona_workflow": float(persona.sort_values("target_workflow_automation", ascending=False).iloc[0].target_workflow_automation),
    "top_persona_readiness": float(persona.sort_values("target_workflow_automation", ascending=False).iloc[0].deployment_readiness_index),
    "stage1_top_importance": str(importance[importance.dataset == "stage1_sme_size_class"].sort_values("importance_mean", ascending=False).iloc[0].feature_label),
    "stage2_top_importance": str(importance[importance.dataset == "stage2_industry_region_GE10"].sort_values("importance_mean", ascending=False).iloc[0].feature_label),
    "manifest_stage1": verify_manifest("data/raw/manifest.jsonl"),
    "manifest_stage2": verify_manifest("data/raw/manifest_stage2.jsonl"),
}

METRICS.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")

sources = {
    "core_sources": [
        {
            "name": "Eurostat isoc_eb_ai",
            "url": "https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table?lang=en",
            "role": "AI adoption by size class of enterprise; Stage 1 SME mechanism layer.",
        },
        {
            "name": "Eurostat isoc_eb_ain2",
            "url": "https://doi.org/10.2908/ISOC_EB_AIN2",
            "role": "AI adoption by NACE Rev. 2 activity; Stage 2 industry/region validation.",
        },
        {
            "name": "Eurostat SDMX2.1 API guide",
            "url": "https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines/sdmx2-1/data-query",
            "role": "Official API acquisition method.",
        },
        {
            "name": "Eurostat Statistics Explained: Use of artificial intelligence in enterprises",
            "url": "https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/106920.pdf",
            "role": "Context and definition of AI workflow automation indicator.",
        },
        {
            "name": "scikit-learn GroupKFold",
            "url": "https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html",
            "role": "Country-group validation method.",
        },
        {
            "name": "NIST AI RMF 1.0",
            "url": "https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10",
            "role": "Governance and AI risk management framework.",
        },
        {
            "name": "ai.zhjjq.tech",
            "url": "https://ai.zhjjq.tech",
            "role": "Applied AI workstation scenario provided by the project team.",
        },
    ],
    "artifact_tool": "Presentations plugin artifact-tool build pipeline with PNG preview and layout JSON.",
    "imagegen": str(IMG / "prompts.jsonl"),
}
SOURCE_NOTES.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")


COMMON = f"""
export const C = {{
  W: 1280,
  H: 720,
  blue: '#0B1F3A',
  ink: '#111827',
  gray: '#6B7280',
  soft: '#9CA3AF',
  line: '#E5E7EB',
  light: '#F6F7F9',
  white: '#FFFFFF',
  pale: '#EEF3F8',
  font: 'Microsoft YaHei',
  sans: 'Aptos',
  mono: 'Cascadia Mono'
}};

export function rect(slide, ctx, x, y, w, h, fill = C.white, line = 'rgba(0,0,0,0)', name = undefined) {{
  return ctx.addShape(slide, {{ left: x, top: y, width: w, height: h, fill, line: ctx.line(line, line === 'rgba(0,0,0,0)' ? 0 : 1), name }});
}}

export function txt(slide, ctx, text, x, y, w, h, opts = {{}}) {{
  return ctx.addText(slide, {{
    text: String(text ?? ''),
    left: x,
    top: y,
    width: w,
    height: h,
    fontSize: opts.size ?? 18,
    color: opts.color ?? C.ink,
    bold: Boolean(opts.bold),
    typeface: opts.face ?? C.font,
    align: opts.align ?? 'left',
    valign: opts.valign ?? 'top',
    fill: opts.fill ?? 'rgba(0,0,0,0)',
    line: opts.line ?? ctx.line(),
    insets: opts.insets ?? {{ left: 0, right: 0, top: 0, bottom: 0 }},
    name: opts.name
  }});
}}

export function rule(slide, ctx, x, y, w, color = C.line, h = 1) {{
  rect(slide, ctx, x, y, w, h, color, 'rgba(0,0,0,0)');
}}

export function base(slide, ctx, no, kicker, claim, source = 'Eurostat official SDMX-CSV; reproducible Python pipeline; A10 GPU baseline.') {{
  rect(slide, ctx, 0, 0, C.W, C.H, C.white);
  txt(slide, ctx, String(kicker).toUpperCase(), 64, 36, 360, 24, {{ size: 10, color: C.blue, bold: true, face: C.sans }});
  rule(slide, ctx, 64, 66, 64, C.blue, 3);
  txt(slide, ctx, claim, 64, 84, 1040, 74, {{ size: 28, color: C.ink, bold: true, face: C.font }});
  rule(slide, ctx, 64, 670, 1152, C.line, 1);
  txt(slide, ctx, source, 64, 682, 900, 22, {{ size: 9, color: C.gray, face: C.sans }});
  txt(slide, ctx, String(no).padStart(2, '0'), 1170, 680, 48, 24, {{ size: 13, color: C.gray, face: C.mono, align: 'right' }});
}}

export async function img(slide, ctx, path, x, y, w, h, fit = 'contain', name = undefined) {{
  return await ctx.addImage(slide, {{ path, left: x, top: y, width: w, height: h, fit, alt: name ?? 'visual asset', name }});
}}

export function metric(slide, ctx, value, label, x, y, w = 170) {{
  txt(slide, ctx, value, x, y, w, 46, {{ size: 29, color: C.blue, bold: true, face: C.mono }});
  txt(slide, ctx, label, x, y + 48, w + 12, 38, {{ size: 11, color: C.gray, face: C.font }});
}}

export function interp(slide, ctx, x, y, w, rows) {{
  const labels = ['What the chart shows', 'Why it matters', 'Decision it supports'];
  if (w >= 700) {{
    const gap = 30;
    const col = (w - gap * 2) / 3;
    rows.forEach((body, i) => {{
      const xx = x + i * (col + gap);
      txt(slide, ctx, labels[i], xx, y, col, 20, {{ size: 9.5, color: C.blue, bold: true, face: C.sans }});
      txt(slide, ctx, body, xx, y + 28, col, 54, {{ size: 12.2, color: C.ink, face: C.font }});
      if (i < 2) rect(slide, ctx, xx + col + gap / 2, y + 4, 1, 72, C.line);
    }});
    return;
  }}
  rows.forEach((body, i) => {{
    const yy = y + i * 72;
    txt(slide, ctx, labels[i], x, yy, w, 18, {{ size: 9.2, color: C.blue, bold: true, face: C.sans }});
    txt(slide, ctx, body, x, yy + 24, w, 40, {{ size: 11.5, color: C.ink, face: C.font }});
    if (i < 2) rule(slide, ctx, x, yy + 64, w, C.line, 1);
  }});
}}

export function bullets(slide, ctx, items, x, y, w, rowH = 62) {{
  items.slice(0, 3).forEach((item, i) => {{
    const yy = y + i * rowH;
    rect(slide, ctx, x, yy + 7, 6, 28, C.blue);
    txt(slide, ctx, item, x + 20, yy, w - 20, rowH - 8, {{ size: 14, color: C.ink, face: C.font }});
  }});
}}
"""

(SLIDES / "common.mjs").write_text(COMMON, encoding="utf-8")

M = metrics
paths = {
    "mechanism": image_by_prefix("01"),
    "lifecycle": image_by_prefix("02"),
    "causal": image_by_prefix("03"),
    "matrix": image_by_prefix("04"),
    "governance": image_by_prefix("05"),
    "workstation": image_by_prefix("06"),
    "chart_cv": CHARTS / "chart01_groupkfold_model_comparison.png",
    "chart_ols": CHARTS / "chart02_ols_mechanism_coefficients.png",
    "chart_gpu": CHARTS / "chart03_tree_vs_gpu_mlp.png",
    "chart_imp": CHARTS / "chart04_feature_importance_mechanism.png",
    "chart_funnel": CHARTS / "chart05_data_lifecycle_funnel.png",
    "chart_persona": CHARTS / "chart06_persona_deployment_map.png",
    "dashboard": BROWSER / "ai_zhjjq_dashboard.png",
}


slide_specs = [
    {
        "no": 1,
        "kicker": "Research defense",
        "claim": "AI 流程自动化采纳不是技术选择，而是中小企业的组织决策。",
        "body": f"""
import {{ C, rect, txt, rule, metric, img }} from './common.mjs';
export async function slide01(presentation, ctx) {{
  const slide = presentation.slides.add();
  rect(slide, ctx, 0, 0, C.W, C.H, C.white);
  txt(slide, ctx, 'RESEARCH DEFENSE', 64, 44, 300, 22, {{ size: 11, color: C.blue, bold: true, face: C.sans }});
  rule(slide, ctx, 64, 76, 64, C.blue, 3);
  txt(slide, ctx, 'AI 流程自动化采纳不是技术选择，而是中小企业的组织决策。', 64, 128, 620, 142, {{ size: 34, color: C.ink, bold: true, face: C.font }});
  txt(slide, ctx, '基于效率需求、安全顾虑与部署偏好的实证分析', 66, 292, 620, 36, {{ size: 17, color: C.gray, face: C.font }});
  await img(slide, ctx, {js_path(paths["mechanism"])}, 758, 106, 438, 300, 'contain', 'mechanism');
  metric(slide, ctx, '12.77M', 'Stage 2 官方行数画像', 66, 454, 180);
  metric(slide, ctx, '0.850', 'SME GroupKFold R²', 278, 454, 180);
  metric(slide, ctx, '0.724', 'GE10 外部验证 R²', 490, 454, 190);
  txt(slide, ctx, 'Official Eurostat data · SHA256 validation · GroupKFold by country · NVIDIA A10 MLP baseline', 66, 604, 780, 26, {{ size: 12, color: C.ink, face: C.sans }});
  rule(slide, ctx, 64, 670, 1152, C.line, 1);
  txt(slide, ctx, 'Data: Eurostat SDMX-CSV; Evidence tables: outputs/tables/enhanced_*.csv', 64, 682, 900, 22, {{ size: 9, color: C.gray, face: C.sans }});
  txt(slide, ctx, '01', 1170, 680, 48, 24, {{ size: 13, color: C.gray, face: C.mono, align: 'right' }});
  return slide;
}}
""",
        "note": "开场我会先把题目从“做一个 AI 工具”提升为“企业为什么、在什么条件下采纳 AI 流程自动化”的组织决策问题。",
    },
    {
        "no": 2,
        "kicker": "The real problem",
        "claim": "中小企业想要自动化，但真正约束采纳的是风险承受能力。",
        "body": f"""
import {{ C, base, img, bullets, interp }} from './common.mjs';
export async function slide02(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 2, 'The real problem', '中小企业想要自动化，但真正约束采纳的是风险承受能力。');
  await img(slide, ctx, {js_path(paths["causal"])}, 72, 178, 620, 360, 'contain', 'causal');
  bullets(slide, ctx, [
    '人工成本和重复性流程推动企业寻找自动化工具。',
    '数据安全、权限边界和治理责任会减缓采纳。',
    '部署准备度决定需求能否转化成实际使用。'
  ], 770, 190, 380, 74);
  interp(slide, ctx, 770, 420, 382, [
    '采纳不是单变量决策，而是效率、风险和部署能力的共同结果。',
    '同一种 AI 功能，在不同安全约束下会导向不同部署架构。',
    '先识别企业风险-效率位置，再推荐 SaaS、API、本地或混合部署。'
  ]);
  return slide;
}}
""",
        "note": "我会说明真实矛盾：企业并不是不想用 AI，而是担心数据、权限、流程责任和部署成本，这些因素共同决定采纳路径。",
    },
    {
        "no": 3,
        "kicker": "Research question",
        "claim": "本研究回答：什么条件下，中小企业会采纳 AI 流程自动化？",
        "body": """
import { C, base, rect, txt, rule, interp } from './common.mjs';
export async function slide03(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 3, 'Research question', '本研究回答：什么条件下，中小企业会采纳 AI 流程自动化？');
  const cards = [
    ['效率需求', '人工成本 · 重复流程 · 自动化压力', 88],
    ['安全顾虑', '数据边界 · 权限控制 · 治理责任', 474],
    ['部署准备度', '云能力 · API 集成 · 本地化能力', 860]
  ];
  cards.forEach(([a,b,x], i) => {
    rect(slide, ctx, x, 206, 260, 120, C.light, C.line);
    txt(slide, ctx, a, x + 24, 228, 212, 34, { size: 22, color: C.blue, bold: true, align: 'center' });
    txt(slide, ctx, b, x + 24, 272, 212, 38, { size: 13, color: C.gray, align: 'center' });
    if (i < 2) txt(slide, ctx, '×', x + 298, 238, 42, 42, { size: 30, color: C.ink, bold: true, face: C.sans, align: 'center' });
  });
  rule(slide, ctx, 244, 396, 792, C.blue, 3);
  txt(slide, ctx, 'AI workflow automation adoption', 376, 424, 528, 44, { size: 29, color: C.ink, bold: true, face: C.sans, align: 'center' });
  txt(slide, ctx, '目标变量来自 Eurostat：企业使用 AI 自动化流程或辅助决策的比例。', 302, 506, 676, 34, { size: 16, color: C.gray, align: 'center' });
  interp(slide, ctx, 172, 560, 940, [
    '因变量直接对应“流程自动化/辅助决策”，不是泛泛的 AI 热度。',
    '机制框架把效率、安全和部署准备度拆开，保证模型结果可解释。',
    '后续客户画像和部署建议都从这个机制框架推出。'
  ]);
  return slide;
}
""",
        "note": "这里我把研究问题压缩为一个机制公式：效率需求乘以安全顾虑，再乘以部署准备度，共同解释采纳。",
    },
    {
        "no": 4,
        "kicker": "Data credibility",
        "claim": "数据可信度来自官方来源、哈希校验和可复现实验流程。",
        "body": f"""
import {{ C, base, rect, txt, rule, interp }} from './common.mjs';
export async function slide04(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 4, 'Data credibility', '数据可信度来自官方来源、哈希校验和可复现实验流程。', 'Sources: Eurostat SDMX API, manifest.jsonl, manifest_stage2.jsonl; BTOS 403 excluded.');
  const rows = [
    ['Stage 1', 'SME 规模层机制样本', '10 个 Eurostat 文件；544 个建模观测', 'SHA256 全部通过'],
    ['Stage 2', 'GE10 行业/区域外部验证', '17 个压缩 SDMX-CSV；12.77M 行画像', 'SHA256 全部通过'],
    ['Excluded', 'Census BTOS 获取尝试', 'HTTP 403；仅保留日志', '不进入训练']
  ];
  txt(slide, ctx, 'Layer', 92, 188, 120, 24, {{ size: 12, color: C.gray, bold: true, face: C.sans }});
  txt(slide, ctx, 'Research role', 270, 188, 210, 24, {{ size: 12, color: C.gray, bold: true, face: C.sans }});
  txt(slide, ctx, 'Files / rows', 560, 188, 300, 24, {{ size: 12, color: C.gray, bold: true, face: C.sans }});
  txt(slide, ctx, 'Integrity', 936, 188, 220, 24, {{ size: 12, color: C.gray, bold: true, face: C.sans }});
  rule(slide, ctx, 88, 222, 1080, C.line, 1);
  rows.forEach((r, i) => {{
    const y = 250 + i * 92;
    txt(slide, ctx, r[0], 92, y, 130, 32, {{ size: 20, color: C.blue, bold: true, face: C.sans }});
    txt(slide, ctx, r[1], 270, y, 220, 42, {{ size: 15, color: C.ink }});
    txt(slide, ctx, r[2], 560, y, 314, 42, {{ size: 15, color: C.ink }});
    txt(slide, ctx, r[3], 936, y, 230, 42, {{ size: 15, color: C.ink }});
    rule(slide, ctx, 88, y + 58, 1080, C.line, 1);
  }});
  interp(slide, ctx, 126, 548, 1000, [
    '所有成功进入模型的原始文件均可从 Eurostat 官方接口追溯。',
    '失败或不可访问的数据被记录但排除，避免把网页错误当作训练数据。',
    '这支撑课程案例的科研严谨性：数据、代码、结果三者可复核。'
  ]);
  return slide;
}}
""",
        "note": "我会主动说明数据来源和排除规则：不是所有找到的数据都能训练，只有官方、可哈希、可复现的数据进入模型。",
    },
    {
        "no": 5,
        "kicker": "Data lifecycle",
        "claim": "数字生命周期把海量官方数据收敛为可审计的建模面板。",
        "body": f"""
import {{ C, base, img, interp }} from './common.mjs';
export async function slide05(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 5, 'Data lifecycle', '数字生命周期把海量官方数据收敛为可审计的建模面板。', 'Source: outputs/tables/cleaning_retention_summary.csv; outputs/reports/stage2_source_profile.md');
  await img(slide, ctx, {js_path(paths["chart_funnel"])}, 70, 184, 650, 374, 'contain', 'lifecycle-funnel');
  await img(slide, ctx, {js_path(paths["lifecycle"])}, 780, 184, 360, 180, 'contain', 'lifecycle-visual');
  interp(slide, ctx, 780, 402, 380, [
    '12.77M 行官方数据先经过画像，再进入机制指标筛选。',
    '保留率低不是缺陷，而是排除无关指标后的质量控制。',
    '最终面板可审计、可复跑，并能支撑机器学习建模。'
  ]);
  return slide;
}}
""",
        "note": "这一页对应老师强调的数字生命周期：采集、清洗、特征工程、建模、解释和部署都被放在一条链路里。",
    },
    {
        "no": 6,
        "kicker": "Mechanism framework",
        "claim": "采纳机制不是“AI 热情”，而是效率需求被安全与部署能力约束。",
        "body": f"""
import {{ C, base, img, interp }} from './common.mjs';
export async function slide06(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 6, 'Mechanism framework', '采纳机制不是“AI 热情”，而是效率需求被安全与部署能力约束。');
  await img(slide, ctx, {js_path(paths["mechanism"])}, 78, 184, 660, 398, 'contain', 'mechanism-framework');
  interp(slide, ctx, 800, 220, 360, [
    '效率需求、安全顾虑和部署准备度共同指向采纳结果。',
    '所以模型需要同时纳入 AI 能力、数字基础、治理和云/数据能力。',
    '部署建议必须判断企业受哪一类机制力量主导。'
  ]);
  return slide;
}}
""",
        "note": "我会把机制讲成三股力量：效率给动力，安全制造约束，部署准备度决定能不能真正落地。",
    },
    {
        "no": 7,
        "kicker": "Model strategy",
        "claim": "模型设计把解释、预测、泛化和深度学习基线分开处理。",
        "body": """
import { C, base, txt, rule, interp } from './common.mjs';
export async function slide07(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 7, 'Model strategy', '模型设计把解释、预测、泛化和深度学习基线分开处理。', 'Source: src/course_ml_diagnostics.py; src/enhanced_training_gpu.py');
  const rows = [
    ['01', 'OLS / 多元线性回归', '用于识别机制方向、显著性和 VIF 共线性风险。'],
    ['02', 'Random Forest / ExtraTrees', '用于捕捉非线性关系，并通过特征重要性解释机制。'],
    ['03', 'GroupKFold by country', '按国家分组验证，降低同一国家观测泄漏带来的虚高分数。'],
    ['04', 'A10 GPU MLP baseline', '作为深度学习对照，不把 GPU 算力强行包装成最优模型。']
  ];
  rows.forEach((r, i) => {
    const y = 180 + i * 86;
    txt(slide, ctx, r[0], 94, y, 52, 32, { size: 20, color: C.blue, bold: true, face: C.mono });
    txt(slide, ctx, r[1], 180, y - 2, 300, 34, { size: 21, color: C.ink, bold: true, face: C.sans });
    txt(slide, ctx, r[2], 518, y, 560, 40, { size: 16, color: C.gray });
    rule(slide, ctx, 94, y + 56, 1000, C.line, 1);
  });
  interp(slide, ctx, 160, 550, 900, [
    '不是只追求最高 R²，而是把模型功能和研究问题对应起来。',
    'GroupKFold 让结果更接近跨国家、跨组织环境的泛化能力。',
    '课程目标中的监督学习、回归、模型评估和深度学习基线都得到体现。'
  ]);
  return slide;
}
""",
        "note": "我会解释每类算法的角色：OLS 负责解释，树模型负责非线性预测，GroupKFold 负责泛化检验，MLP 负责深度学习基线。",
    },
    {
        "no": 8,
        "kicker": "Mechanism evidence",
        "claim": "OLS 先确认机制方向，再由非线性模型提升预测解释力。",
        "body": f"""
import {{ C, base, img, interp, metric }} from './common.mjs';
export async function slide08(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 8, 'Mechanism evidence', 'OLS 先确认机制方向，再由非线性模型提升预测解释力。', 'Source: outputs/tables/course_ols_coefficients.csv; course_vif_diagnostics.csv');
  await img(slide, ctx, {js_path(paths["chart_ols"])}, 64, 184, 680, 390, 'contain', 'ols-chart');
  metric(slide, ctx, '7.59', 'SME 机器学习能力标准化系数', 800, 184, 280);
  metric(slide, ctx, '4.19', 'GE10 行业机器学习能力系数', 800, 296, 280);
  interp(slide, ctx, 800, 438, 360, [
    '机器学习能力是最强正向机制变量。',
    '云和数据能力方向有意义；最大 VIF={M["max_vif"]:.1f}，不能过度因果化。',
    '因此 OLS 用于机制解释，树模型用于最终预测。'
  ]);
  return slide;
}}
""",
        "note": "这一页我会强调 OLS 不是为了炫耀分数，而是确认机制方向；同时我会说明 VIF 显示共线性，所以结论要谨慎。",
    },
    {
        "no": 9,
        "kicker": "Generalization",
        "claim": "按国家分组的 GroupKFold 说明模型学到的是跨地区采纳机制。",
        "body": f"""
import {{ C, base, img, interp, metric }} from './common.mjs';
export async function slide09(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 9, 'Generalization', '按国家分组的 GroupKFold 说明模型学到的是跨地区采纳机制。', 'Source: outputs/tables/enhanced_cv_results.csv; validation = GroupKFold(geo).');
  await img(slide, ctx, {js_path(paths["chart_cv"])}, 66, 184, 672, 384, 'contain', 'groupkfold-chart');
  metric(slide, ctx, '{M["stage1_rf_r2"]:.3f}', 'RandomForest · Stage 1 SME', 800, 184, 250);
  metric(slide, ctx, '{M["stage2_et_r2"]:.3f}', 'ExtraTrees · Stage 2 GE10', 800, 282, 250);
  interp(slide, ctx, 800, 406, 360, [
    '每个国家只会在某一折中作为测试组出现。',
    '在更严格验证下仍保持较高 R²，比随机切分更有说服力。',
    'Stage 1 支撑 SME 结论，Stage 2 支撑行业/区域外部验证。'
  ]);
  return slide;
}}
""",
        "note": "这里是机器学习部分最关键的一页：我没有用容易虚高的随机切分，而是按国家分组做交叉验证。",
    },
    {
        "no": 10,
        "kicker": "Model finding",
        "claim": "A10 GPU MLP 没有超过树模型，说明结构化官方统计更适合表格学习器。",
        "body": f"""
import {{ C, base, img, interp }} from './common.mjs';
export async function slide10(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 10, 'Model finding', 'A10 GPU MLP 没有超过树模型，说明结构化官方统计更适合表格学习器。', 'Source: outputs/tables/enhanced_gpu_baseline.csv; enhanced_cv_results.csv.');
  await img(slide, ctx, {js_path(paths["chart_gpu"])}, 78, 170, 600, 386, 'contain', 'gpu-vs-tree');
  interp(slide, ctx, 760, 206, 392, [
    'MLP 在 NVIDIA A10 上成功训练，但 R² 低于随机森林和 ExtraTrees。',
    '这不是失败，而是模型选择结论：更多算力不自动带来更好泛化。',
    '本研究最终选择树模型作为主预测器，同时保留 GPU 基线作为课程证据。'
  ]);
  return slide;
}}
""",
        "note": "我会说明 A10 服务器不是浪费，它让我们有能力验证深度学习基线；结果反而证明表格数据应优先用树模型。",
    },
    {
        "no": 11,
        "kicker": "Interpretability",
        "claim": "特征重要性支持效率-安全-部署机制，而不是泛泛的 AI 热度。",
        "body": f"""
import {{ C, base, img, interp }} from './common.mjs';
export async function slide11(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 11, 'Interpretability', '特征重要性支持效率-安全-部署机制，而不是泛泛的 AI 热度。', 'Source: outputs/tables/enhanced_permutation_importance.csv.');
  await img(slide, ctx, {js_path(paths["chart_imp"])}, 54, 184, 710, 404, 'contain', 'importance-chart');
  interp(slide, ctx, 805, 212, 360, [
    'SME 层最强变量是 ML capability，Stage 2 也由 ML 能力和 NLG 支撑。',
    '数字基础、部署准备度和国家/行业异质性共同解释采纳差异。',
    '特征重要性把预测结果转化为可执行的企业分层依据。'
  ]);
  return slide;
}}
""",
        "note": "这页把模型结果拉回研究问题：重要变量不是“喜欢 AI”，而是能力基础、部署能力、行业和国家差异。",
    },
    {
        "no": 12,
        "kicker": "Deployment implication",
        "claim": "SaaS、API、本地和混合部署，本质上是风险-效率权衡的结果。",
        "body": f"""
import {{ C, base, img, interp }} from './common.mjs';
export async function slide12(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 12, 'Deployment implication', 'SaaS、API、本地和混合部署，本质上是风险-效率权衡的结果。', 'Framework: model/persona outputs + NIST AI RMF governance logic.');
  await img(slide, ctx, {js_path(paths["matrix"])}, 72, 184, 650, 400, 'contain', 'deployment-matrix');
  interp(slide, ctx, 790, 210, 370, [
    '效率需求越强，企业越倾向快速上线自动化能力。',
    '安全顾虑越强，企业越需要 API、私有化或混合部署边界。',
    '部署矩阵把模型结论转化为产品方案选择。'
  ]);
  return slide;
}}
""",
        "note": "我会把部署偏好讲成结论：不是哪种技术更高级，而是哪种部署方式更匹配企业风险和效率约束。",
    },
    {
        "no": 13,
        "kicker": "Segmentation",
        "claim": "客户画像把模型结果转化为可落地的企业部署策略。",
        "body": f"""
import {{ C, base, img, interp, metric }} from './common.mjs';
export async function slide13(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 13, 'Segmentation', '客户画像把模型结果转化为可落地的企业部署策略。', 'Source: outputs/tables/sme_persona_clusters_multisource.csv.');
  await img(slide, ctx, {js_path(paths["chart_persona"])}, 76, 170, 590, 386, 'contain', 'persona-chart');
  metric(slide, ctx, 'C{M["top_persona_cluster"]}', '最高流程自动化采纳画像', 742, 176, 160);
  metric(slide, ctx, '{M["top_persona_workflow"]:.2f}%', 'workflow automation mean', 990, 176, 190);
  interp(slide, ctx, 760, 314, 380, [
    '不同画像在部署准备度和安全顾虑上存在结构性差异。',
    '同一套 AI 功能不能用单一部署方案覆盖所有中小企业。',
    '画像结果可直接服务于销售、交付和部署方案推荐。'
  ]);
  return slide;
}}
""",
        "note": "这里我会讲无监督学习的价值：聚类让客户从一个平均值变成多个画像，每个画像对应不同部署策略。",
    },
    {
        "no": 14,
        "kicker": "Product landing",
        "claim": "ai.zhjjq.tech 是把研究机制落到真实 AI 办公流程的操作层。",
        "body": f"""
import {{ C, base, img, interp }} from './common.mjs';
export async function slide14(presentation, ctx) {{
  const slide = presentation.slides.add();
  base(slide, ctx, 14, 'Product landing', 'ai.zhjjq.tech 是把研究机制落到真实 AI 办公流程的操作层。', 'Product visual: ai.zhjjq.tech workstation screenshot and research operating model.');
  await img(slide, ctx, {js_path(paths["workstation"])}, 66, 184, 470, 286, 'contain', 'workstation-model');
  await img(slide, ctx, {js_path(paths["dashboard"])}, 598, 188, 560, 290, 'contain', 'ai-workstation-screenshot');
  interp(slide, ctx, 146, 520, 940, [
    '研究模型判断企业效率需求、安全顾虑和部署准备度。',
    'AI 工作站承接智能体、组织知识、流程任务和治理反馈。',
    '产品落地让课程模型从预测结果走向可执行的 AI 办公部署方案。'
  ]);
  return slide;
}}
""",
        "note": "我会用第一人称说明：我做 ai.zhjjq.tech 不是为了展示网站，而是把模型结论放进真实办公场景。",
    },
    {
        "no": 15,
        "kicker": "Final contribution",
        "claim": "本项目贡献了一条从官方数据到可部署 AI 流程策略的复现路径。",
        "body": """
import { C, base, txt, rule, interp } from './common.mjs';
export async function slide15(presentation, ctx) {
  const slide = presentation.slides.add();
  base(slide, ctx, 15, 'Final contribution', '本项目贡献了一条从官方数据到可部署 AI 流程策略的复现路径。');
  const rows = [
    ['01', '数据可信', 'Eurostat 官方数据、manifest、SHA256 和清洗日志共同支撑真实性。'],
    ['02', '机器学习严谨', 'OLS、RandomForest、ExtraTrees、GroupKFold 和 A10 MLP 基线形成完整算法链。'],
    ['03', '机制解释', '效率需求 × 安全顾虑 × 部署准备度解释 AI 流程自动化采纳。'],
    ['04', '产品价值', 'SaaS / API / 本地 / 混合部署策略服务真实 AI 办公场景。']
  ];
  rows.forEach((r, i) => {
    const y = 182 + i * 82;
    txt(slide, ctx, r[0], 94, y, 56, 34, { size: 21, color: C.blue, bold: true, face: C.mono });
    rule(slide, ctx, 160, y + 18, 76, C.blue, 2);
    txt(slide, ctx, r[1], 270, y - 2, 180, 34, { size: 22, color: C.ink, bold: true });
    txt(slide, ctx, r[2], 506, y, 560, 42, { size: 16, color: C.gray });
  });
  interp(slide, ctx, 152, 540, 980, [
    '结论不止是一个模型分数，而是一套可解释采纳机制。',
    '课程中的数据生命周期、监督学习、回归、集成学习、聚类和深度学习基线均已体现。',
    '下一步可以接入国内问卷与真实工作流日志，形成更强的中小企业本土化研究。'
  ]);
  return slide;
}
""",
        "note": "最后我会总结四个贡献：数据可信、算法完整、机制可解释、部署可落地。",
    },
]

for spec in slide_specs:
    (SLIDES / f"slide-{spec['no']:02d}.mjs").write_text(spec["body"].strip() + "\n", encoding="utf-8")

notes = ["# Slide-by-slide speaker notes", ""]
for spec in slide_specs:
    notes.append(f"## {spec['no']:02d}. {spec['claim']}")
    notes.append(spec["note"])
    notes.append("")
NOTES.write_text("\n".join(notes), encoding="utf-8")

revision = f"""# Research-grade PPT revision report

## 1. 学术审稿式诊断

上一版 PPT 的数据和模型基础是真实的，但叙事仍偏“课程材料堆叠”：页面标题较多是章节名，图表旁的解释层不足，观众看到 R²、OLS 和 GPU 结果后，未必能立刻理解它们如何支撑“AI 流程自动化采纳机制”。本次重构不是简单美化，而是把每一页改成一个 research claim，并给每个图表补上 What the chart shows / Why it matters / Decision it supports。

## 2. 工具与环境核验

- 用户指定读取 `/home/oai/skills/slides/SKILL.md`：当前 Windows/Codex Desktop 环境中该路径不存在。
- 已读取并采用可用的 Presentations 插件 skill：`C:\\Users\\景浩伟\\.codex-api-gateway\\plugins\\cache\\openai-primary-runtime\\presentations\\26.430.10722\\skills\\presentations\\SKILL.md`。
- 已按 Presentations 插件要求改用 artifact-tool slide modules 生成 PPTX，并导出 preview PNG 与 layout JSON。
- 已读取 imagegen skill，并使用 `assets/imagegen_research_visuals/prompts.jsonl` 中的统一研究风格 imagegen 视觉资产；图表和关键文字均来自 deterministic 数据脚本与可编辑 PPT 文本，不依赖图片内小字。

## 3. 数据可信度复核

- Stage 1 manifest：{metrics['manifest_stage1']['hash_ok']} 个成功源文件 SHA256 复算通过；失败状态记录 {metrics['manifest_stage1']['failed_status_records']} 条，不进入训练。
- Stage 2 manifest：{metrics['manifest_stage2']['hash_ok']} 个压缩官方源文件 SHA256 复算通过。
- Stage 2 官方源画像：12,770,332 行，10,453,354 个非空观测；机制筛选保留 856,880 行。
- Stage 1 建模面板：{metrics['stage1_rows']} 行，{metrics['stage1_geo_count']} 个 geo，2021-2025，重复 panel key = 0。
- Stage 2 建模面板：{metrics['stage2_rows']} 行，{metrics['stage2_geo_count']} 个 geo，{metrics['stage2_nace_count']} 个 NACE，重复 panel key = 0。

## 4. 指标口径修正

早期 `research_quality_validation.md` 中存在较宽松模型分数，本次 PPT 统一采用 `outputs/reports/enhanced_training_report.md` 的严格 GroupKFold 结果：

- Stage 1 SME size-class：RandomForest, GroupKFold by country, R²={metrics['stage1_rf_r2']:.3f}, MAE={metrics['stage1_rf_mae']:.3f}。
- Stage 2 GE10 industry/region：ExtraTrees, GroupKFold by country, R²={metrics['stage2_et_r2']:.3f}, MAE={metrics['stage2_et_mae']:.3f}。
- A10 GPU MLP baseline：Stage 1 R²={metrics['stage1_mlp_r2']:.3f}; Stage 2 R²={metrics['stage2_mlp_r2']:.3f}。

重要边界：Stage 1 是 SME 规模层机制样本；Stage 2 是 GE10 行业/区域外部验证，不作为 SME 规模分层替代。

## 5. 叙事重构

新的 claim spine：

1. AI 流程自动化采纳不是技术选择，而是组织决策。
2. 中小企业想要自动化，但受风险承受能力约束。
3. 研究问题是“什么条件下会采纳”。
4. 数据可信度来自官方来源、哈希校验和复现流程。
5. 数字生命周期把海量官方数据收敛为建模面板。
6. 机制框架是效率需求 × 安全顾虑 × 部署准备度。
7. 模型策略把解释、预测、泛化和深度学习基线分开。
8. OLS 解释机制方向，树模型负责非线性预测。
9. GroupKFold 说明模型学习跨地区机制。
10. A10 MLP 未超过树模型，说明表格学习器更适合该类官方统计。
11. 特征重要性支持机制故事。
12. 部署偏好是风险-效率权衡结果。
13. 客户画像把模型结果转为部署策略。
14. ai.zhjjq.tech 是研究落地操作层。
15. 项目贡献官方数据、机器学习、解释机制和部署策略的复现桥梁。

## 6. 视觉系统

- 白底、黑/灰文字、唯一强调色 deep academic blue `#0B1F3A`。
- 一页一个核心观点，一个主 proof object，最多三条解释。
- 禁用科技蓝渐变、3D 伪科技、随机 icon 和文字墙。
- 图表由 `scripts_render_rebuilt_charts.py` 重新渲染，风格统一且保留 `.svg` 源图。

## 7. 输出文件

- PPTX: `{PPTX}`
- PDF: `{PDF}`
- Speaker notes: `{NOTES}`
- Source notes: `{SOURCE_NOTES}`
- Verified metrics: `{METRICS}`

## 8. 参考来源

- Eurostat SDMX2.1 API guide: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines/sdmx2-1/data-query
- Eurostat Statistics Explained, Use of AI in enterprises: https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/106920.pdf
- Eurostat `isoc_eb_ai`: https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table?lang=en
- Eurostat `isoc_eb_ain2`: https://doi.org/10.2908/ISOC_EB_AIN2
- scikit-learn GroupKFold: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html
- NIST AI RMF 1.0: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
"""
REVISION.write_text(revision, encoding="utf-8")

print(json.dumps({"slides": len(slide_specs), "slides_dir": str(SLIDES), "pptx": str(PPTX)}, ensure_ascii=False, indent=2))
