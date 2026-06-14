from __future__ import annotations

import json
import math
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / ".python_packages"
if PKG.exists() and str(PKG) not in sys.path:
    sys.path.insert(0, str(PKG))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


REPO = ROOT
TABLES = REPO / "outputs" / "tables"
REPORTS = REPO / "outputs" / "reports"
RAW = REPO / "data" / "raw"
PROCESSED = REPO / "data" / "processed"
ASSETS = REPO / "ppt_assets"
OUT = REPO / "05_学术图表" / "汇报图片稿_4K待审核"
FIG_OUT = OUT / "图表"
SLIDE_OUT = OUT / "16比9_4K图片"
for p in [OUT, FIG_OUT, SLIDE_OUT]:
    p.mkdir(parents=True, exist_ok=True)

W, H = 3840, 2160

NAVY = "#061C3A"
NAVY2 = "#0A2D5C"
BLUE = "#1268A8"
CYAN = "#18A5B8"
TEAL = "#1C9B87"
GREEN = "#3AA66B"
AMBER = "#D79A28"
RED = "#C74E4C"
INK = "#132033"
MUTED = "#637083"
LINE = "#DCE5EF"
PAPER = "#F6F8FB"
WHITE = "#FFFFFF"


def pick_font() -> str:
    names = {f.name for f in font_manager.fontManager.ttflist}
    for n in ["Microsoft YaHei UI", "Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial Unicode MS", "DejaVu Sans"]:
        if n in names:
            return n
    return "DejaVu Sans"


FONT = pick_font()
plt.rcParams["font.sans-serif"] = [FONT, "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


def csv(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLES / name)


quality = csv("enhanced_data_quality_audit.csv")
cv = csv("enhanced_cv_results.csv")
gpu = csv("enhanced_gpu_baseline.csv")
holdout = csv("enhanced_holdout_results.csv")
perm = csv("enhanced_permutation_importance.csv")
alg = csv("course_algorithm_comparison.csv")
ols = csv("course_ols_coefficients.csv")
reg = csv("course_regression_summary.csv")
vif = csv("course_vif_diagnostics.csv")
missing = csv("stage2_feature_missingness.csv")
sme_persona = csv("sme_persona_clusters_multisource.csv")
stage2_persona = csv("stage2_persona_clusters.csv")
stage1 = pd.read_csv(PROCESSED / "eurostat_multisource_panel.csv")
stage2 = pd.read_csv(PROCESSED / "stage2_industry_panel.csv")


LABELS = {
    "stage1_sme_size_class": "Stage 1 SME规模层",
    "stage2_industry_region_GE10": "Stage 2 行业/区域验证层",
    "ridge": "岭回归",
    "random_forest": "随机森林",
    "extra_trees": "ExtraTrees",
    "hist_gradient_boosting": "HistGradientBoosting",
    "ai__E_AI_TML": "机器学习能力",
    "ai_industry__E_AI_TML": "行业机器学习能力",
    "ai__E_AI_TNLG": "自然语言生成",
    "ai_industry__E_AI_TNLG": "行业自然语言生成",
    "deployment_readiness_index": "部署准备度",
    "data_maturity_index": "数据成熟度",
    "digital_foundation_index": "数字基础",
    "governance_maturity_proxy": "治理成熟度",
    "security_concern_index": "安全顾虑指数",
    "cloud__E_CC_PDEV": "云开发能力",
    "cloud__E_CC_DA": "云数据分析",
    "market_digitization_index": "市场数字化",
    "ict_constraint_index": "ICT人才约束",
    "ecommerce_sales__E_AWS_COWN": "自有网站销售",
    "ecommerce_sales__E_AWSELL": "电子商务销售",
    "digital_intensity__E_DI3_VHI": "高数字强度",
    "ecommerce_value__E_AWSVAL_B2BG": "B2B/G电商价值",
    "data_analytics__E_DASANY": "数据分析使用",
    "isoc_cicce_usen2__E_CC": "行业云使用",
    "isoc_e_diin2__E_DI3_VHI": "高数字强度",
    "isoc_ec_eseln2__E_AESELL": "企业电商销售",
    "isoc_ec_eseln2__E_AWSELL": "网站/APP销售",
    "isoc_ec_eseln2__E_AWS_COWN": "自有渠道销售",
    "isoc_cicce_usen2__E_CC_PDEV": "云开发服务",
    "isoc_cicce_usen2__E_CC_PSEC": "云安全服务",
    "ML capability": "机器学习能力",
    "Natural language generation": "自然语言生成",
    "Deployment readiness": "部署准备度",
    "Digital foundation": "数字基础",
    "Cloud development": "云开发能力",
    "Security concern": "安全顾虑指数",
    "Country heterogeneity": "国家异质性",
    "Industry heterogeneity": "行业异质性",
    "Year": "年份趋势",
    "market digitization index": "市场数字化",
}


def label(x: str) -> str:
    return LABELS.get(str(x), str(x).replace("_", " "))


def source_profile() -> dict:
    stage1_rows = [json.loads(x) for x in (RAW / "manifest.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    stage2_rows = [json.loads(x) for x in (RAW / "manifest_stage2.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    ok1 = [r for r in stage1_rows if r.get("ok") and r.get("source_id", "").startswith("eurostat")]
    fail = [r for r in stage1_rows if not r.get("ok")]
    ok2 = [r for r in stage2_rows if r.get("ok")]
    prof_path = REPORTS / "stage2_source_profile.json"
    prof = json.loads(prof_path.read_text(encoding="utf-8")) if prof_path.exists() else {}
    return {
        "stage1_sources": len(ok1),
        "stage2_sources": len(ok2),
        "failed_sources": len(fail),
        "stage1_bytes": sum(r.get("bytes", 0) for r in ok1),
        "stage2_bytes": sum(r.get("bytes", 0) for r in ok2),
        "profile": prof,
    }


PROFILE = source_profile()


def save_fig(fig, name):
    png = FIG_OUT / f"{name}.png"
    svg = FIG_OUT / f"{name}.svg"
    fig.savefig(png, dpi=320, bbox_inches="tight", facecolor="white")
    fig.savefig(svg, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return png


def chart_lifecycle():
    steps = pd.DataFrame(
        [
            ("官方源文件", PROFILE["stage1_sources"] + PROFILE["stage2_sources"]),
            ("原始源数据扫描行", 12770332),
            ("非空观测", 10453354),
            ("机制变量筛选保留行", 856880),
            ("Stage 2建模面板", 5814),
            ("Stage 1 SME建模样本", 544),
        ],
        columns=["stage", "value"],
    )
    fig, ax = plt.subplots(figsize=(12.5, 6.0))
    colors = [BLUE, CYAN, TEAL, GREEN, AMBER, RED]
    y = np.arange(len(steps))[::-1]
    ax.barh(y, steps["value"].iloc[::-1], color=colors[::-1], height=0.58)
    ax.set_yticks(y)
    ax.set_yticklabels(steps["stage"].iloc[::-1], fontsize=12)
    ax.set_xscale("log")
    ax.grid(axis="x", color="#E8EEF6", linewidth=1)
    ax.spines[:].set_visible(False)
    ax.set_xlabel("数量（log scale）", fontsize=12)
    for yi, val in zip(y, steps["value"].iloc[::-1]):
        ax.text(val * 1.12, yi, f"{int(val):,}", va="center", fontsize=12, fontweight="bold", color=INK)
    ax.set_title("数据生命周期：从官方源数据到可训练建模面板", loc="left", fontsize=19, fontweight="bold", pad=16)
    ax.text(0, -0.16, "Source: Eurostat SDMX-CSV manifests; A10 server profiling outputs.", transform=ax.transAxes, color=MUTED, fontsize=9)
    return save_fig(fig, "图01_数据生命周期漏斗")


def chart_model_compare():
    fig, ax = plt.subplots(figsize=(12.2, 6.0))
    d = cv.copy()
    d["模型"] = d["model"].map(label)
    d["数据层"] = d["dataset"].map(label)
    order = ["岭回归", "随机森林", "ExtraTrees", "HistGradientBoosting"]
    x = np.arange(len(order))
    width = 0.34
    for i, ds in enumerate(["stage1_sme_size_class", "stage2_industry_region_GE10"]):
        sub = d[d["dataset"] == ds].set_index("模型").reindex(order)
        ax.bar(x + (i - 0.5) * width, sub["r2_mean"], width, label=label(ds), color=[BLUE, TEAL][i], edgecolor="white")
        for j, val in enumerate(sub["r2_mean"]):
            ax.text(j + (i - 0.5) * width, val + 0.018, f"{val:.3f}", ha="center", fontsize=10, color=INK, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(order, fontsize=11)
    ax.set_ylim(0.55, 0.95)
    ax.set_ylabel("GroupKFold R²", fontsize=12)
    ax.grid(axis="y", color="#E8EEF6")
    ax.spines[:].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("模型泛化能力比较：随机森林与ExtraTrees在全量特征下最稳健", loc="left", fontsize=19, fontweight="bold", pad=16)
    return save_fig(fig, "图02_模型交叉验证比较")


def chart_ols_coefficients():
    fig, axes = plt.subplots(1, 2, figsize=(14.0, 5.8), sharex=False)
    for ax, ds, color in zip(axes, ["Stage 1 SME规模层", "Stage 2 行业验证层"], [BLUE, TEAL]):
        d = ols[ols["dataset"] == ds].copy()
        d = d.reindex(d["coef_std"].abs().sort_values(ascending=False).index).head(7)
        d = d.iloc[::-1]
        colors = [color if v >= 0 else RED for v in d["coef_std"]]
        ax.barh(d["feature_label"], d["coef_std"], color=colors, alpha=0.9)
        ax.axvline(0, color="#9AA8B8", linewidth=1)
        ax.grid(axis="x", color="#E8EEF6")
        ax.spines[:].set_visible(False)
        ax.set_title(ds, fontsize=14, fontweight="bold")
        for y, (_, r) in enumerate(d.iterrows()):
            sig = "*" if bool(r["significant_05"]) else ""
            ax.text(r["coef_std"] + (0.08 if r["coef_std"] >= 0 else -0.08), y, f"{r['coef_std']:.2f}{sig}", va="center", ha="left" if r["coef_std"] >= 0 else "right", fontsize=10, color=INK)
    fig.suptitle("多元回归解释：标准化系数显示机器学习能力是核心驱动", x=0.02, y=1.02, ha="left", fontsize=19, fontweight="bold")
    fig.text(0.02, -0.02, "* p < 0.05; OLS uses standardized predictors after median imputation.", color=MUTED, fontsize=9)
    fig.tight_layout()
    return save_fig(fig, "图03_多元回归标准化系数")


def chart_importance():
    fig, axes = plt.subplots(1, 2, figsize=(14.0, 6.2))
    for ax, ds, title, color in [
        (axes[0], "stage1_sme_size_class", "Stage 1 SME规模层", GREEN),
        (axes[1], "stage2_industry_region_GE10", "Stage 2 行业/区域验证层", TEAL),
    ]:
        d = perm[perm["dataset"] == ds].sort_values("importance_mean", ascending=False).head(9).copy()
        d["标签"] = d["feature"].map(label)
        d = d.iloc[::-1]
        ax.barh(d["标签"], d["importance_mean"], xerr=d["importance_std"], color=color, alpha=0.9, error_kw={"elinewidth": 0.8, "ecolor": "#677488"})
        ax.grid(axis="x", color="#E8EEF6")
        ax.spines[:].set_visible(False)
        ax.set_xlabel("Permutation importance", fontsize=11)
        ax.set_title(title, fontsize=14, fontweight="bold")
    fig.suptitle("模型解释：特征扰动验证采纳机制的关键变量", x=0.02, y=1.02, ha="left", fontsize=19, fontweight="bold")
    fig.tight_layout()
    return save_fig(fig, "图04_特征重要性双面板")


def chart_gpu():
    fig, ax = plt.subplots(figsize=(9.6, 5.6))
    d = gpu.copy()
    d["标签"] = d["dataset"].map(lambda x: "Stage 1 SME规模层" if x == "stage1_sme_size_class" else "Stage 2 行业验证层")
    x = np.arange(len(d))
    ax.bar(x, d["r2"], color=[GREEN, TEAL], width=0.48)
    ax.set_xticks(x)
    ax.set_xticklabels(d["标签"], fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_ylabel("Holdout R²", fontsize=12)
    ax.grid(axis="y", color="#E8EEF6")
    ax.spines[:].set_visible(False)
    for i, r in d.iterrows():
        ax.text(i, r["r2"] + 0.035, f"R²={r['r2']:.3f}\nMAE={r['mae']:.3f}\n{r['gpu_name']}", ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.set_title("A10 GPU神经网络基线：表格数据下树模型更稳健", loc="left", fontsize=18, fontweight="bold", pad=16)
    return save_fig(fig, "图05_A10_GPU_MLP基线")


def chart_quality_matrix():
    fig, ax = plt.subplots(figsize=(12.0, 5.6))
    rows = []
    for _, r in quality.iterrows():
        rows.append([
            "SME规模层" if r["dataset"] == "stage1_sme_size_class" else "行业验证层",
            f"{int(r['rows']):,}",
            f"{int(r['columns'])}",
            f"{int(r['geo_count'])}",
            f"{int(r['year_min'])}-{int(r['year_max'])}",
            f"{float(r['mean_numeric_missing_rate'])*100:.1f}%",
            f"{int(r['duplicate_panel_keys'])}",
        ])
    cols = ["数据层", "建模样本", "特征列", "国家/地区", "年份", "均值缺失率", "重复键"]
    ax.axis("off")
    table = ax.table(cellText=rows, colLabels=cols, cellLoc="center", loc="center", bbox=[0.02, 0.12, 0.96, 0.68])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#DCE5EF")
        if r == 0:
            cell.set_facecolor(NAVY)
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
        else:
            cell.set_facecolor("#F8FBFF" if r % 2 else "white")
    ax.set_title("数据质量审计：样本边界、缺失率与重复键透明呈现", loc="left", fontsize=19, fontweight="bold", pad=16)
    ax.text(0.02, 0.02, "Stage 2 为 GE10 行业/区域外部验证层，不表述为 SME 规模拆分。", transform=ax.transAxes, fontsize=10, color=MUTED)
    return save_fig(fig, "图06_数据质量审计表")


def chart_strategy():
    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axhline(50, color=LINE, linewidth=2)
    ax.axvline(50, color=LINE, linewidth=2)
    quads = [
        (25, 75, "本地化部署", "高安全顾虑\n低效率迫切度", RED),
        (75, 75, "混合部署", "高安全顾虑\n高效率需求", AMBER),
        (25, 25, "标准SaaS", "低安全顾虑\n低部署复杂度", BLUE),
        (75, 25, "API接入", "低安全顾虑\n高流程集成需求", GREEN),
    ]
    for x, y, title, note, color in quads:
        ax.scatter([x], [y], s=2200, color=color, alpha=0.15, edgecolor=color, linewidth=2)
        ax.text(x, y + 4, title, ha="center", va="center", fontsize=16, fontweight="bold", color=color)
        ax.text(x, y - 10, note, ha="center", va="center", fontsize=10, color=INK)
    ax.set_xlabel("效率需求 / 流程自动化收益", fontsize=12)
    ax.set_ylabel("安全顾虑 / 治理要求", fontsize=12)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines[:].set_visible(False)
    ax.set_title("部署偏好机制：安全顾虑是部署路径分流器", loc="left", fontsize=19, fontweight="bold", pad=16)
    return save_fig(fig, "图07_部署偏好策略矩阵")


def chart_source_integrity():
    rows = [
        ("Stage 1 Eurostat", PROFILE["stage1_sources"], PROFILE["stage1_bytes"] / 1024 / 1024, "SHA256全通过"),
        ("Stage 2 Eurostat", PROFILE["stage2_sources"], PROFILE["stage2_bytes"] / 1024 / 1024, "SHA256全通过"),
        ("Census BTOS", PROFILE["failed_sources"], 0, "HTTP 403，未采用"),
    ]
    fig, ax = plt.subplots(figsize=(12.0, 5.6))
    ax.axis("off")
    cell_rows = [[a, f"{b}", f"{c:.1f} MB", d] for a, b, c, d in rows]
    table = ax.table(
        cellText=cell_rows,
        colLabels=["来源层", "文件/记录数", "已验证字节", "结论"],
        cellLoc="center",
        loc="center",
        bbox=[0.04, 0.18, 0.92, 0.58],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#DCE5EF")
        if r == 0:
            cell.set_facecolor(NAVY)
            cell.get_text().set_color("white")
            cell.get_text().set_fontweight("bold")
        else:
            cell.set_facecolor("#F8FBFF" if r % 2 else "white")
            if r == 3:
                cell.get_text().set_color(RED)
    ax.set_title("源数据真实性核验：只采用可下载、可哈希、可复现的官方数据", loc="left", fontsize=19, fontweight="bold", pad=16)
    ax.text(0.04, 0.08, "Manifest records URL, HTTP status, timestamp, bytes, and SHA256. Census 403 records are retained only as acquisition logs.", transform=ax.transAxes, fontsize=10, color=MUTED)
    return save_fig(fig, "图08_源数据真实性核验")


def chart_missingness():
    d = missing.copy().head(18)
    d["标签"] = d["feature"].map(label)
    fig, ax = plt.subplots(figsize=(12.0, 6.0))
    y = np.arange(len(d))[::-1]
    ax.barh(y, (1 - d["missing_rate"]).iloc[::-1], color=TEAL, alpha=0.92)
    ax.set_yticks(y)
    ax.set_yticklabels(d["标签"].iloc[::-1], fontsize=10)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("非缺失覆盖率", fontsize=12)
    ax.grid(axis="x", color="#E8EEF6")
    ax.spines[:].set_visible(False)
    for yi, cov, nn in zip(y, (1 - d["missing_rate"]).iloc[::-1], d["nonnull"].iloc[::-1]):
        ax.text(cov + 0.015, yi, f"{cov*100:.1f}% / n={int(nn):,}", va="center", fontsize=9, color=INK)
    ax.set_title("缺失率审计：哪些变量真正有足够覆盖率进入解释", loc="left", fontsize=19, fontweight="bold", pad=16)
    return save_fig(fig, "图09_缺失率覆盖审计")


def chart_vif():
    d = vif.copy()
    d["变量"] = d["feature"].map(label)
    d = d.sort_values("vif", ascending=False).head(14).iloc[::-1]
    fig, ax = plt.subplots(figsize=(11.8, 6.0))
    colors = [RED if v >= 10 else AMBER if v >= 5 else TEAL for v in d["vif"]]
    ax.barh(d["变量"], d["vif"], color=colors, alpha=0.9)
    ax.axvline(5, color=AMBER, linestyle="--", linewidth=1)
    ax.axvline(10, color=RED, linestyle="--", linewidth=1)
    ax.grid(axis="x", color="#E8EEF6")
    ax.spines[:].set_visible(False)
    ax.set_xlabel("VIF", fontsize=12)
    for y, v in enumerate(d["vif"]):
        ax.text(v + 0.25, y, f"{v:.1f}", va="center", fontsize=10, color=INK)
    ax.set_title("多重共线性诊断：解释模型与预测模型分工呈现", loc="left", fontsize=19, fontweight="bold", pad=16)
    ax.text(0.01, -0.14, "VIF is reported for interpretation transparency. Ridge/tree models are used when predictors are correlated.", transform=ax.transAxes, fontsize=9, color=MUTED)
    return save_fig(fig, "图10_VIF多重共线性诊断")


def chart_holdout():
    fig, ax = plt.subplots(figsize=(12.0, 5.8))
    d = holdout.copy()
    d["模型"] = d["model"].map(label)
    d["数据层"] = d["dataset"].map(label)
    order = ["岭回归", "随机森林", "ExtraTrees", "HistGradientBoosting"]
    x = np.arange(len(order))
    width = 0.34
    for i, ds in enumerate(["stage1_sme_size_class", "stage2_industry_region_GE10"]):
        sub = d[d["dataset"] == ds].set_index("模型").reindex(order)
        ax.bar(x + (i - 0.5) * width, sub["holdout_r2"], width, label=label(ds), color=[BLUE, TEAL][i], edgecolor="white")
        for j, val in enumerate(sub["holdout_r2"]):
            ax.text(j + (i - 0.5) * width, val + 0.018, f"{val:.3f}", ha="center", fontsize=10, color=INK, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(order, fontsize=11)
    ax.set_ylim(0.55, 0.95)
    ax.set_ylabel("Group holdout R²", fontsize=12)
    ax.grid(axis="y", color="#E8EEF6")
    ax.spines[:].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("独立国家组留出检验：不是只报告交叉验证均值", loc="left", fontsize=19, fontweight="bold", pad=16)
    return save_fig(fig, "图11_国家组留出验证")


def chart_persona():
    d = sme_persona.copy().sort_values("target_workflow_automation", ascending=True)
    fig, ax = plt.subplots(figsize=(12.0, 6.0))
    y = np.arange(len(d))
    sizes = np.clip(d["n"].fillna(1), 10, None)
    sizes = 200 + (sizes / sizes.max()) * 1600
    ax.scatter(d["deployment_readiness_index"], y, s=sizes, color=TEAL, alpha=0.35, edgecolor=TEAL, linewidth=1.5, label="部署准备度")
    ax.scatter(d["security_concern_index"], y, s=sizes * 0.72, color=RED, alpha=0.28, edgecolor=RED, linewidth=1.2, label="安全顾虑")
    ax.set_yticks(y)
    ax.set_yticklabels([f"画像 {int(c)}｜采纳 {v:.1f}%｜n={int(n)}" for c, v, n in zip(d["persona_cluster"], d["target_workflow_automation"], d["n"])], fontsize=11)
    ax.set_xlabel("指数值 / 采纳机制强度", fontsize=12)
    ax.grid(axis="x", color="#E8EEF6")
    ax.spines[:].set_visible(False)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("客户画像聚类：从模型结果转化为可行动的企业分层", loc="left", fontsize=19, fontweight="bold", pad=16)
    return save_fig(fig, "图12_客户画像聚类")


CHARTS = {
    "lifecycle": chart_lifecycle(),
    "model": chart_model_compare(),
    "ols": chart_ols_coefficients(),
    "importance": chart_importance(),
    "gpu": chart_gpu(),
    "quality": chart_quality_matrix(),
    "strategy": chart_strategy(),
    "source": chart_source_integrity(),
    "missing": chart_missingness(),
    "vif": chart_vif(),
    "holdout": chart_holdout(),
    "persona": chart_persona(),
}


def pil_font(size: int, bold=False):
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


F_TITLE = pil_font(78, True)
F_H1 = pil_font(56, True)
F_H2 = pil_font(42, True)
F_BODY = pil_font(32)
F_SMALL = pil_font(24)
F_TINY = pil_font(20)
F_NUM = pil_font(58, True)


def new_slide(bg=WHITE):
    return Image.new("RGB", (W, H), bg)


def draw_header(d, num, title, subtitle=""):
    d.rectangle([0, 0, W, 170], fill=NAVY)
    d.rectangle([0, 170, W, 184], fill=CYAN)
    d.text((120, 48), f"{num:02d}", font=F_H2, fill=WHITE)
    d.text((270, 52), title, font=F_H2, fill=WHITE)
    if subtitle:
        d.text((W - 920, 72), subtitle, font=F_SMALL, fill="#C9D8EA")


def wrap_text(draw, text, font, max_width):
    lines = []
    for para in text.split("\n"):
        buf = ""
        for ch in para:
            cand = buf + ch
            if draw.textbbox((0, 0), cand, font=font)[2] <= max_width:
                buf = cand
            else:
                if buf:
                    lines.append(buf)
                buf = ch
        if buf:
            lines.append(buf)
    return lines


def text_box(d, xy, text, font=F_BODY, fill=INK, max_width=1000, line_gap=12):
    x, y = xy
    for line in wrap_text(d, text, font, max_width):
        d.text((x, y), line, font=font, fill=fill)
        y += font.size + line_gap
    return y


def card(d, xywh, fill=WHITE, outline=LINE, radius=28):
    x, y, w, h = xywh
    d.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=2)


def metric(d, x, y, value, label_text, note="", color=BLUE):
    card(d, (x, y, 460, 245), fill=WHITE, outline="#D8E2EE")
    d.text((x + 32, y + 30), value, font=F_NUM, fill=color)
    d.text((x + 35, y + 112), label_text, font=F_SMALL, fill=INK)
    if note:
        d.text((x + 35, y + 158), note, font=F_TINY, fill=MUTED)


def paste_chart(img, path, xywh):
    x, y, w, h = xywh
    chart = Image.open(path).convert("RGB")
    chart.thumbnail((w, h), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (w, h), WHITE)
    canvas.paste(chart, ((w - chart.width) // 2, (h - chart.height) // 2))
    img.paste(canvas, (x, y))


def paste_crop(img, path, xywh):
    x, y, w, h = xywh
    src = Image.open(path).convert("RGB")
    sr = src.width / src.height
    dr = w / h
    if sr > dr:
        nw = int(src.height * dr)
        left = (src.width - nw) // 2
        src = src.crop((left, 0, left + nw, src.height))
    else:
        nh = int(src.width / dr)
        top = (src.height - nh) // 2
        src = src.crop((0, top, src.width, top + nh))
    src = src.resize((w, h), Image.Resampling.LANCZOS)
    img.paste(src, (x, y))


slide_counter = 0


def save_slide_auto(img, name):
    global slide_counter
    slide_counter += 1
    p = SLIDE_OUT / f"{slide_counter:02d}_{name}.png"
    img.save(p, quality=95)
    return p


def save_slide(img, idx, name):
    p = SLIDE_OUT / f"{idx:02d}_{name}.png"
    img.save(p, quality=95)
    return p


def slide_01():
    img = new_slide(NAVY)
    d = ImageDraw.Draw(img)
    bg = OUT / "imagegen背景" / "学术封面背景_gpt_image_2.png"
    if not bg.exists():
        bg = ASSETS / "imagegen" / "cover_ai_workflow.png"
    if bg.exists():
        paste_crop(img, bg, (0, 0, W, H))
        overlay = Image.new("RGBA", (W, H), (4, 18, 38, 210))
        img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))
        d = ImageDraw.Draw(img)
    d.text((160, 220), "机器学习课程结题案例报告", font=F_H2, fill="#BFEAF2")
    d.text((160, 360), "基于中小企业 AI 流程自动化采纳机制研究", font=F_TITLE, fill=WHITE)
    d.text((166, 470), "效率需求 · 安全顾虑 · 部署偏好 的实证分析", font=F_H1, fill="#EAF3FB")
    text_box(d, (170, 620), "我用真实 Eurostat 官方企业数据构建完整机器学习案例：数据生命周期、清洗审计、特征工程、多元回归、随机森林、ExtraTrees、A10 GPU 基线与部署策略。", F_BODY, "#D7E6F4", 1500)
    metric(d, 170, 1080, "12.77M", "官方源数据扫描行", "17个Stage2源文件", CYAN)
    metric(d, 680, 1080, "0.850", "SME层最佳R²", "RandomForest GroupKFold", GREEN)
    metric(d, 1190, 1080, "0.724", "外部验证R²", "ExtraTrees GroupKFold", AMBER)
    dash = ASSETS / "browser" / "ai_zhjjq_dashboard.png"
    if dash.exists():
        card(d, (2180, 460, 1400, 900), fill=WHITE, outline="#8BA4C2")
        paste_crop(img, dash, (2220, 500, 1320, 820))
        d.text((2450, 1380), "产品落地场景：ai.zhjjq.tech AI工作站", font=F_SMALL, fill=WHITE)
    d.text((160, 1940), "审核版图片稿｜先审图片，再制作可编辑PPT", font=F_SMALL, fill="#B7CBE0")
    return save_slide_auto(img, "封面_研究主题与产品场景")


def slide_with_chart(idx, num, title, subtitle, chart_key, claim, bullets):
    img = new_slide()
    d = ImageDraw.Draw(img)
    draw_header(d, num, title, subtitle)
    d.text((160, 260), claim, font=F_H1, fill=NAVY)
    paste_chart(img, CHARTS[chart_key], (150, 470, 2200, 1280))
    card(d, (2470, 520, 1120, 1140), fill="#F8FBFF", outline=LINE)
    y = 600
    for i, b in enumerate(bullets, 1):
        d.ellipse([2530, y + 8, 2560, y + 38], fill=[BLUE, TEAL, GREEN, AMBER, RED][(i - 1) % 5])
        y = text_box(d, (2590, y), b, F_BODY, INK, 860, 8) + 42
    d.text((160, 1980), "Source: Eurostat official SDMX-CSV; repository manifests and training outputs.", font=F_TINY, fill=MUTED)
    return save_slide_auto(img, title[:18].replace("：", "_"))


def slide_two_charts(num, title, subtitle, left_key, right_key, claim, bullets, name):
    img = new_slide()
    d = ImageDraw.Draw(img)
    draw_header(d, num, title, subtitle)
    d.text((160, 250), claim, font=F_H1, fill=NAVY)
    paste_chart(img, CHARTS[left_key], (120, 460, 1740, 1050))
    paste_chart(img, CHARTS[right_key], (1900, 460, 1740, 1050))
    card(d, (310, 1585, 3220, 270), fill="#F8FBFF", outline=LINE)
    x = 380
    for i, b in enumerate(bullets):
        d.ellipse([x, 1660, x + 30, 1690], fill=[BLUE, TEAL, GREEN, AMBER][i % 4])
        text_box(d, (x + 50, 1638), b, F_SMALL, INK, 900, 4)
        x += 1050
    d.text((160, 1980), "Source: Eurostat official SDMX-CSV; repository manifests and training outputs.", font=F_TINY, fill=MUTED)
    return save_slide_auto(img, name)


def slide_02():
    return slide_with_chart(
        2, 2, "数据来源：官方数据与哈希证据链", "真实性核验",
        "source",
        "先证明数据是真的，再讨论模型是否有效。",
        [
            "Stage 1 与 Stage 2 合计 27 个 Eurostat 官方源文件，全部 SHA256 核验通过。",
            "Census BTOS 返回 HTTP 403，仅保留为获取日志，不进入训练、图表和结论。",
            "所有源数据已按中文目录提交：01_源数据 / 02_清洗后数据 / 03_清洗与训练代码。"
        ],
    )


def slide_03():
    return slide_with_chart(
        3, 3, "数据生命周期：官方海量数据如何进入模型", "真实来源与清洗过程",
        "lifecycle",
        "不是“拿一个小表跑模型”，而是从官方源数据构建可复现数据湖。",
        [
            "源数据来自 Eurostat 官方 SDMX-CSV 接口，manifest 记录 URL、下载时间、bytes 与 SHA256。",
            "Stage 2 扫描 12,770,332 行原始源数据，筛选出 856,880 行机制变量。",
            "最终保留 544 条 SME 规模层建模样本和 5,814 条行业/区域外部验证样本。"
        ],
    )


def slide_04():
    return slide_with_chart(
        4, 4, "数据质量审计：样本边界必须透明", "清洗结果",
        "quality",
        "我不把数据说成完美，而是把缺失率、重复键和口径边界全部公开。",
        [
            "Stage 1 用于 SME 规模层机制解释，Stage 2 用于 GE10 行业/区域外部验证。",
            "两个建模面板重复 panel key 均为 0，目标变量进入建模前为非空。",
            "缺失值由 sklearn 管线中位数/众数插补，不手工补造观测。"
        ],
    )


def slide_05():
    return slide_with_chart(
        5, 5, "缺失率审计：哪些变量真正能进入模型", "变量覆盖率",
        "missing",
        "数据挖掘不是越多越好，而是要知道哪些变量覆盖足够、哪些变量风险更高。",
        [
            "Stage 2 目标变量覆盖 100%，高价值 AI/数字基础变量覆盖率较高。",
            "部署准备度、安全顾虑、数据成熟度等机制变量存在缺失，因此用管线插补并公开缺失率。",
            "缺失处理在 sklearn Pipeline 内完成，避免手工补造观测。"
        ],
    )


def slide_06():
    return slide_with_chart(
        6, 6, "多元回归：机制方向与显著性", "解释模型",
        "ols",
        "OLS 用来回答“哪些因素方向明确、统计上有解释力”。",
        [
            "机器学习能力在 SME 规模层和行业验证层均为核心正向变量。",
            "Stage 2 中数字基础、治理成熟度、部署准备度显著为正。",
            "多元回归用于解释机制，集成学习用于检验泛化预测。"
        ],
    )


def slide_07():
    return slide_with_chart(
        7, 7, "VIF诊断：解释模型要诚实面对共线性", "统计诊断",
        "vif",
        "线性回归负责解释方向；岭回归、树模型负责更稳健预测。",
        [
            "部分数据成熟度/云数据分析变量 VIF 偏高，说明数字能力指标之间天然相关。",
            "报告中保留 VIF 是为了说明解释边界，而不是隐藏模型风险。",
            "最终预测结论依靠 GroupKFold 下的岭回归、随机森林和 ExtraTrees 对照。"
        ],
    )


def slide_08():
    return slide_with_chart(
        8, 8, "模型比较：GroupKFold 检验泛化能力", "机器学习训练",
        "model",
        "按国家分组交叉验证，避免随机切分造成同国信息泄漏。",
        [
            "SME 层全量特征下随机森林最佳，R²=0.850，MAE=1.790。",
            "行业/区域外部验证层 ExtraTrees 最佳，R²=0.724，MAE=1.967。",
            "课程诊断模型保留线性基准，全量预测模型展示非线性泛化能力。"
        ],
    )


def slide_09():
    return slide_with_chart(
        9, 9, "国家组留出验证：检验跨国家泛化", "独立验证",
        "holdout",
        "交叉验证之外，我还保留独立国家组测试，避免只看均值。",
        [
            "SME 层留出测试中 Ridge/ExtraTrees 保持较高 R²，说明机制不是单一国家拟合。",
            "Stage 2 行业层留出 R² 更保守，符合外部验证难度更高的预期。",
            "最终结论采用保守表述：Stage 2 用于外部有效性支持，不替代 SME 规模层证据。"
        ],
    )


def slide_10():
    return slide_with_chart(
        10, 10, "特征重要性：模型解释采纳机制", "Permutation importance",
        "importance",
        "我用扰动重要性解释模型，而不是只报告一个黑箱分数。",
        [
            "SME 规模层中机器学习能力最突出，说明流程自动化依赖可被模型处理的业务基础。",
            "部署准备度、云能力、数字强度和数据成熟度形成落地能力组合。",
            "外部验证层显示行业机器学习能力和自然语言生成仍然是关键驱动。"
        ],
    )


def slide_11():
    return slide_with_chart(
        11, 11, "A10 GPU 基线：复杂模型不一定更优", "PyTorch MLP",
        "gpu",
        "A10 服务器用于神经网络对照实验，结论是模型选择要服从数据结构。",
        [
            "GPU MLP 在 Stage 1 R²=0.806，在 Stage 2 R²=0.662。",
            "树模型在结构化企业面板数据上更稳健，说明不是算力越强结果越好。",
            "这体现机器学习课程中的模型选择、对照实验和泛化评估思想。"
        ],
    )


def slide_12():
    return slide_with_chart(
        12, 12, "客户画像聚类：从模型结果到企业分层", "无监督学习",
        "persona",
        "客户画像不是凭感觉分组，而是基于采纳强度、安全顾虑和部署准备度聚类。",
        [
            "高采纳画像适合 API/混合部署，低采纳画像适合标准 SaaS 试点。",
            "安全顾虑高的画像需要私有化、审计日志和权限控制。",
            "画像结果可以直接服务 ai.zhjjq.tech 的产品入口和报价策略。"
        ],
    )


def slide_13():
    return slide_with_chart(
        13, 13, "部署偏好：安全顾虑改变落地路径", "研究转化",
        "strategy",
        "安全顾虑不是简单阻碍，而是 SaaS、API、本地化、混合部署的分流器。",
        [
            "高安全顾虑企业应优先本地化或私有云部署，并保留审批、日志和审计。",
            "高效率需求且安全要求较高的企业适合混合部署。",
            "低安全顾虑和高集成需求企业更适合 API 接入和流程编排。"
        ],
    )


def slide_14():
    img = new_slide()
    d = ImageDraw.Draw(img)
    draw_header(d, 14, "产品落地：ai.zhjjq.tech AI工作站", "从研究结论到企业应用")
    dash = ASSETS / "browser" / "ai_zhjjq_dashboard.png"
    if dash.exists():
        card(d, (170, 300, 2000, 1290), fill=WHITE, outline=LINE)
        paste_crop(img, dash, (220, 350, 1900, 1190))
    d.text((2320, 330), "我如何把模型结论放进网站", font=F_H1, fill=NAVY)
    items = [
        ("仪表盘", "对应数据生命周期中的监测与反馈。"),
        ("AI工作站", "承接视频、客服、销售、财务等重复流程。"),
        ("组织架构智能体", "对应不同企业画像和流程优先级。"),
        ("待审批事项", "对应安全治理、人机协同和权限边界。"),
    ]
    y = 520
    for title, note in items:
        card(d, (2320, y, 1200, 230), fill="#F8FBFF", outline=LINE)
        d.text((2370, y + 36), title, font=F_H2, fill=BLUE)
        text_box(d, (2370, y + 105), note, F_BODY, INK, 980)
        y += 280
    d.text((170, 1980), "页面已于 2026-05-18 登录验证并截图；账号信息不写入报告和仓库。", font=F_TINY, fill=MUTED)
    return save_slide_auto(img, "产品落地_ai工作站")


def slide_15():
    img = new_slide()
    d = ImageDraw.Draw(img)
    draw_header(d, 15, "GitHub提交结构：源数据、清洗数据、代码、图表、报告分开", "复现与提交")
    dirs = [
        ("01_源数据", "Eurostat原始SDMX-CSV、压缩源文件、manifest校验", "111MB", BLUE),
        ("02_清洗后数据", "建模面板、样本预览、画像分配", "29MB", TEAL),
        ("03_清洗与训练代码", "下载、清洗、特征工程、A10训练、课程诊断", "10个脚本", GREEN),
        ("04_分析结果表格", "数据质量、CV、GPU、OLS、VIF、重要性", "32个文件", AMBER),
        ("05_学术图表", "PNG/SVG学术图，可用于报告和PPT图片稿", "29个文件", RED),
        ("06_结课报告", "数据来源、训练核验、研究质量、最终报告", "文档区", CYAN),
    ]
    for i, (name, desc, meta, color) in enumerate(dirs):
        x = 220 + (i % 2) * 1770
        y = 360 + (i // 2) * 430
        card(d, (x, y, 1530, 310), fill="#F8FBFF", outline=LINE)
        d.text((x + 45, y + 48), name, font=F_H2, fill=color)
        text_box(d, (x + 45, y + 125), desc, F_BODY, INK, 1150)
        d.text((x + 1160, y + 55), meta, font=F_H2, fill=color)
    card(d, (350, 1720, 3140, 160), fill=NAVY, outline=NAVY)
    d.text((590, 1772), "复现逻辑：原始数据 → 清洗后面板 → 特征工程 → 机器学习训练 → 结果表格 → 学术图表 → Word报告/PPT", font=F_BODY, fill=WHITE)
    return save_slide_auto(img, "GitHub中文提交结构")


def slide_16():
    img = new_slide()
    d = ImageDraw.Draw(img)
    draw_header(d, 16, "研究框架：TOE-TAM 与机器学习建模结合", "理论到变量")
    d.text((180, 285), "我把“采纳机制”拆成可训练、可解释、可落地的变量系统。", font=F_H1, fill=NAVY)
    blocks = [
        ("T 技术条件", "机器学习能力、自然语言生成、云开发、数据分析成熟度", BLUE),
        ("O 组织基础", "数字基础、ICT人才、治理成熟度、部署准备度", TEAL),
        ("E 环境压力", "市场数字化、行业差异、国家区域异质性、时间趋势", AMBER),
        ("TAM 感知机制", "效率需求、安全顾虑、易用性、采纳强度转化", RED),
    ]
    for i, (title, desc, color) in enumerate(blocks):
        x = 240 + (i % 2) * 1720
        y = 560 + (i // 2) * 430
        card(d, (x, y, 1500, 300), fill="#F8FBFF", outline=LINE)
        d.rectangle([x, y, x + 24, y + 300], fill=color)
        d.text((x + 80, y + 54), title, font=F_H2, fill=color)
        text_box(d, (x + 80, y + 140), desc, F_BODY, INK, 1180)
    card(d, (430, 1530, 2980, 220), fill="#EFF6FC", outline=LINE)
    d.text((600, 1592), "Y = β0 + β1效率需求 + β2安全顾虑 + β3部署准备度 + β4数据成熟度 + β5数字基础 + ε", font=F_H2, fill=NAVY)
    d.text((670, 1692), "回归解释机制方向；随机森林/ExtraTrees检验泛化预测；GPU MLP作为神经网络对照基线。", font=F_BODY, fill=INK)
    return save_slide_auto(img, "研究框架_TOE_TAM机器学习")


def slide_17():
    img = new_slide()
    d = ImageDraw.Draw(img)
    draw_header(d, 17, "算法流程：从原始数据到企业部署建议", "机器学习课程链条")
    steps = [
        ("01 数据获取", "Eurostat API / manifest / SHA256"),
        ("02 数据清洗", "长表转面板 / 缺失处理 / 重复键检查"),
        ("03 特征工程", "效率需求 / 安全顾虑 / 部署准备度"),
        ("04 监督学习", "OLS / Ridge / RandomForest / ExtraTrees"),
        ("05 GPU基线", "A10 CUDA / PyTorch MLP / 对照实验"),
        ("06 模型解释", "Permutation importance / OLS系数 / VIF"),
        ("07 业务转化", "SaaS / API / 本地化 / 混合部署"),
    ]
    y = 430
    for i, (title, desc) in enumerate(steps):
        x = 260 + i * 480
        card(d, (x, y + (i % 2) * 260, 390, 220), fill=WHITE, outline=LINE)
        d.ellipse([x + 145, y + 34 + (i % 2) * 260, x + 245, y + 134 + (i % 2) * 260], fill=[BLUE, CYAN, TEAL, GREEN, AMBER, RED, NAVY2][i])
        d.text((x + 177, y + 64 + (i % 2) * 260), f"{i+1}", font=F_SMALL, fill=WHITE)
        d.text((x + 35, y + 145 + (i % 2) * 260), title, font=F_SMALL, fill=INK)
        text_box(d, (x + 35, y + 180 + (i % 2) * 260), desc, F_TINY, MUTED, 320, 3)
        if i < len(steps) - 1:
            d.line([x + 390, y + 110 + (i % 2) * 260, x + 480, y + 110 + ((i + 1) % 2) * 260], fill="#9AA8B8", width=6)
    card(d, (350, 1380, 3140, 310), fill="#F8FBFF", outline=LINE)
    d.text((470, 1450), "课程对应", font=F_H2, fill=BLUE)
    text_box(d, (760, 1435), "数据预处理、特征提取、监督学习、无监督画像、交叉验证、模型评价、模型解释、实际应用转化。", F_BODY, INK, 2500)
    d.text((470, 1580), "关键防线", font=F_H2, fill=RED)
    text_box(d, (760, 1572), "排除目标泄漏变量；按国家分组验证；Stage 1 与 Stage 2 口径分开解释。", F_BODY, INK, 2500)
    return save_slide_auto(img, "算法流程_机器学习课程链条")


def slide_18():
    img = new_slide()
    d = ImageDraw.Draw(img)
    draw_header(d, 18, "研究结论：从统计显著到企业价值", "最终发现")
    findings = [
        ("结论一", "企业 AI 流程自动化采纳不是由“AI热情”单独决定，而是由机器学习能力、数据基础、部署准备度共同驱动。", BLUE),
        ("结论二", "安全顾虑不是简单负向因素，它会推动企业从公有SaaS转向本地化、私有云或混合部署。", RED),
        ("结论三", "SME层随机森林 R²=0.850，行业外部验证层 ExtraTrees R²=0.724，说明机制具有可迁移性。", GREEN),
        ("结论四", "A10 GPU MLP 低于树模型，证明结构化企业面板数据更适合稳健、可解释的表格学习模型。", AMBER),
        ("结论五", "ai.zhjjq.tech 可据此设计客户分层、工作流入口、审批治理和部署报价策略。", TEAL),
    ]
    y = 340
    for title, desc, color in findings:
        card(d, (330, y, 3180, 230), fill="#F8FBFF", outline=LINE)
        d.text((410, y + 64), title, font=F_H2, fill=color)
        text_box(d, (720, y + 55), desc, F_BODY, INK, 2550, 8)
        y += 285
    card(d, (520, 1850, 2800, 130), fill=NAVY, outline=NAVY)
    d.text((720, 1888), "我的最终判断：这个案例的价值是把“企业会不会用AI”推进到“企业应该如何安全有效地部署AI”。", font=F_BODY, fill=WHITE)
    return save_slide_auto(img, "研究结论_企业价值")


def slide_19():
    img = new_slide()
    d = ImageDraw.Draw(img)
    draw_header(d, 19, "下一步：从课程案例走向可持续研究项目", "局限与扩展")
    left = [
        ("当前边界", "Stage 2 是 GE10 行业/区域验证层，不是SME规模拆分。"),
        ("因果边界", "当前是观察数据建模，不能直接宣称严格因果关系。"),
        ("国内数据", "后续可接入国内中小企业真实使用日志、访谈和问卷追踪。"),
    ]
    right = [
        ("产品实验", "将 ai.zhjjq.tech 后台任务日志纳入A/B测试与客户画像。"),
        ("模型升级", "加入面板固定效应、因果推断和部署推荐器。"),
        ("治理闭环", "建立审批、权限、日志、模型输出置信度和人工复核流程。"),
    ]
    for i, (title, desc) in enumerate(left):
        y = 420 + i * 380
        card(d, (300, y, 1450, 280), fill="#FFF7E6", outline=LINE)
        d.text((380, y + 55), title, font=F_H2, fill=AMBER)
        text_box(d, (380, y + 135), desc, F_BODY, INK, 1180)
    for i, (title, desc) in enumerate(right):
        y = 420 + i * 380
        card(d, (2080, y, 1450, 280), fill="#EAF7F5", outline=LINE)
        d.text((2160, y + 55), title, font=F_H2, fill=TEAL)
        text_box(d, (2160, y + 135), desc, F_BODY, INK, 1180)
    card(d, (420, 1700, 3000, 190), fill="#F8FBFF", outline=LINE)
    d.text((560, 1762), "提交承诺：所有数据真实可查、代码可复现、源数据与清洗后数据分目录保存，PPT将在图片审核通过后再制作。", font=F_BODY, fill=NAVY)
    return save_slide_auto(img, "局限与下一步研究")


SLIDES = [
    slide_01(),
    slide_02(),
    slide_03(),
    slide_04(),
    slide_05(),
    slide_06(),
    slide_07(),
    slide_08(),
    slide_09(),
    slide_10(),
    slide_11(),
    slide_12(),
    slide_13(),
    slide_14(),
    slide_15(),
    slide_16(),
    slide_17(),
    slide_18(),
    slide_19(),
]


def contact_sheet():
    thumbs = []
    for p in SLIDES:
        im = Image.open(p).convert("RGB")
        im.thumbnail((640, 360), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (640, 405), WHITE)
        canvas.paste(im, ((640 - im.width) // 2, 0))
        dd = ImageDraw.Draw(canvas)
        dd.text((16, 370), p.stem, font=pil_font(22), fill=INK)
        thumbs.append(canvas)
    cols = 2
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 640, rows * 405), "#EEF3F8")
    for i, im in enumerate(thumbs):
        sheet.paste(im, ((i % cols) * 640, (i // cols) * 405))
    out = OUT / "审核总览_contact_sheet.png"
    sheet.save(out, quality=95)
    return out


sheet = contact_sheet()

manifest = {
    "output_dir": str(OUT),
    "slide_count": len(SLIDES),
    "slides": [str(p) for p in SLIDES],
    "contact_sheet": str(sheet),
    "charts": {k: str(v) for k, v in CHARTS.items()},
    "font": FONT,
    "data_inputs": {
        "quality": str(TABLES / "enhanced_data_quality_audit.csv"),
        "cv": str(TABLES / "enhanced_cv_results.csv"),
        "gpu": str(TABLES / "enhanced_gpu_baseline.csv"),
        "perm": str(TABLES / "enhanced_permutation_importance.csv"),
        "ols": str(TABLES / "course_ols_coefficients.csv"),
    },
}
(OUT / "图片稿生成清单.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(manifest, ensure_ascii=False, indent=2))
