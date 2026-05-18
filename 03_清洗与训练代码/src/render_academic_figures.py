"""Render polished academic figures from enhanced training outputs."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    import scienceplots  # noqa: F401
    plt.style.use(["science", "no-latex"])
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "outputs" / "tables"
FIGS = ROOT / "outputs" / "figures" / "academic"
FIGS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 7.2,
    "axes.titlesize": 8.2,
    "axes.labelsize": 7.4,
    "xtick.labelsize": 6.8,
    "ytick.labelsize": 6.8,
    "legend.fontsize": 6.5,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "axes.linewidth": 0.55,
    "grid.linewidth": 0.4,
    "grid.alpha": 0.2,
})

BLUE = "#1F5AA6"
GREEN = "#207A4A"
ORANGE = "#C96F1A"
PURPLE = "#7141B8"
RED = "#B63A3A"
GRAY = "#6B7280"
LIGHT = "#E5E7EB"


def ds_label(x: str) -> str:
    return {
        "stage1_sme_size_class": "Stage 1\nSME size class",
        "stage2_industry_region_GE10": "Stage 2\nGE10 validation",
    }.get(x, x)


def model_label(x: str) -> str:
    return {
        "ridge": "Ridge",
        "random_forest": "RF",
        "extra_trees": "ExtraTrees",
        "hist_gradient_boosting": "HGBR",
    }.get(x, x)


def clean_feature(x: str) -> str:
    mapping = {
        "ML capability": "Machine learning capability",
        "Deployment readiness": "Deployment readiness",
        "Natural language generation": "Natural language generation",
        "Cloud development": "Cloud development",
        "Digital foundation": "Digital foundation",
        "Security concern": "Security concern",
    }
    if x in mapping:
        return mapping[x]
    x = x.replace("ecommerce sales  ", "E-commerce: ")
    x = x.replace("ecommerce value  ", "E-commerce value: ")
    x = x.replace("digital intensity  ", "Digital intensity: ")
    x = x.replace("cloud  ", "Cloud: ")
    x = x.replace("ai  ", "AI: ")
    return x


def add_panel_label(ax, label: str):
    ax.text(-0.08, 1.08, label, transform=ax.transAxes, fontsize=9, fontweight="bold", va="top")


def fig_main():
    cv = pd.read_csv(TABLES / "enhanced_cv_results.csv")
    q = pd.read_csv(TABLES / "enhanced_data_quality_audit.csv")
    gpu = pd.read_csv(TABLES / "enhanced_gpu_baseline.csv")
    imp = pd.read_csv(TABLES / "enhanced_permutation_importance.csv")

    fig = plt.figure(figsize=(7.2, 5.1), constrained_layout=True)
    fig.set_constrained_layout_pads(w_pad=0.08, h_pad=0.10, wspace=0.12, hspace=0.18)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.05], width_ratios=[1.05, 1])

    ax = fig.add_subplot(gs[0, 0])
    order = ["ridge", "random_forest", "extra_trees", "hist_gradient_boosting"]
    cv = cv[cv["model"].isin(order)].copy()
    pivot = cv.pivot(index="model", columns="dataset", values="r2_mean").loc[order]
    err = cv.pivot(index="model", columns="dataset", values="r2_std").loc[order]
    x_models = np.arange(len(order))
    width = 0.34
    for i, ds in enumerate(pivot.columns):
        off = (i - 0.5) * width
        ax.bar(x_models + off, pivot[ds], width, yerr=err[ds], capsize=2, label=ds_label(ds).replace("\n", " "), color=[BLUE, GREEN][i], edgecolor="white", linewidth=0.35)
    ax.set_xticks(x_models)
    ax.set_xticklabels([model_label(m) for m in order], rotation=18, ha="right")
    ax.set_ylabel("Group-CV $R^2$")
    ax.set_ylim(0, 1.02)
    ax.grid(axis="y")
    ax.legend(loc="lower left", frameon=True)
    ax.set_title("Model comparison under country-group cross-validation")
    add_panel_label(ax, "A")

    ax = fig.add_subplot(gs[0, 1])
    width = 0.36
    g = gpu.copy()
    x = np.arange(len(g))
    ax.bar(x, g["r2"], width, color=ORANGE, label="Torch MLP")
    best = cv.sort_values("r2_mean", ascending=False).groupby("dataset").head(1).set_index("dataset")
    ax.scatter(x, [best.loc[d, "r2_mean"] for d in g["dataset"]], marker="D", s=26, color=BLUE, label="Best tree/linear CV")
    for i, row in enumerate(g.itertuples()):
        ax.text(i, row.r2 + 0.035, f"{row.r2:.2f}", ha="center", fontsize=6.5)
    ax.set_xticks(x)
    ax.set_xticklabels([ds_label(d) for d in g["dataset"]])
    ax.set_ylabel("$R^2$")
    ax.set_ylim(0, 1.02)
    ax.grid(axis="y")
    ax.legend(loc="lower left", frameon=True)
    ax.set_title("A10 GPU neural baseline vs. tabular models")
    add_panel_label(ax, "B")

    ax = fig.add_subplot(gs[1, 0])
    top = imp[imp["dataset"].eq("stage1_sme_size_class")].head(10).iloc[::-1].copy()
    top["label"] = top["feature_label"].map(clean_feature)
    ax.barh(top["label"], top["importance_mean"], xerr=top["importance_std"], color=BLUE, alpha=0.9, capsize=1.8)
    ax.set_xlabel("Permutation importance in $R^2$")
    ax.grid(axis="x")
    ax.set_title("SME mechanism drivers after leakage control")
    add_panel_label(ax, "C")

    ax = fig.add_subplot(gs[1, 1])
    q = q.set_index("dataset")
    vals = q.loc[g["dataset"], "rows"]
    ax.barh([ds_label(d) for d in vals.index], vals.values, color=[BLUE, GREEN], height=0.5)
    for y, v in enumerate(vals.values):
        ax.text(v * 1.08, y, f"{int(v):,}", va="center", fontsize=7)
    ax.set_xscale("log")
    ax.set_xlabel("Modeling rows (log scale)")
    ax.grid(axis="x")
    ax.set_title("Cross-sectional coverage used for modeling")
    add_panel_label(ax, "D")

    fig.suptitle("Empirical validation of AI workflow automation adoption", fontsize=9.5, fontweight="bold")
    fig.savefig(FIGS / "fig1_academic_validation_clean.png", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(FIGS / "fig1_academic_validation_clean.svg", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)

    # PPT-friendly individual panels.
    fig, ax = plt.subplots(figsize=(5.4, 3.0), constrained_layout=True)
    for i, ds in enumerate(pivot.columns):
        off = (i - 0.5) * width
        ax.bar(x_models + off, pivot[ds], width, yerr=err[ds], capsize=2, label=ds_label(ds).replace("\n", " "), color=[BLUE, GREEN][i], edgecolor="white", linewidth=0.35)
    ax.set_xticks(x_models)
    ax.set_xticklabels([model_label(m) for m in order])
    ax.set_ylabel("Group-CV $R^2$")
    ax.set_ylim(0, 1.02)
    ax.grid(axis="y")
    ax.legend(loc="lower left", frameon=True)
    ax.set_title("Leakage-controlled model comparison")
    fig.savefig(FIGS / "fig1a_model_comparison_ppt.png", bbox_inches="tight", pad_inches=0.05)
    fig.savefig(FIGS / "fig1a_model_comparison_ppt.svg", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5.2, 3.2), constrained_layout=True)
    top = imp[imp["dataset"].eq("stage1_sme_size_class")].head(10).iloc[::-1].copy()
    top["label"] = top["feature_label"].map(clean_feature)
    ax.barh(top["label"], top["importance_mean"], xerr=top["importance_std"], color=BLUE, alpha=0.9, capsize=2)
    ax.set_xlabel("Permutation importance in $R^2$")
    ax.grid(axis="x")
    ax.set_title("SME mechanism drivers")
    fig.savefig(FIGS / "fig1b_sme_importance_ppt.png", bbox_inches="tight", pad_inches=0.05)
    fig.savefig(FIGS / "fig1b_sme_importance_ppt.svg", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(4.8, 3.0), constrained_layout=True)
    x = np.arange(len(g))
    ax.bar(x, g["r2"], width, color=ORANGE, label="Torch MLP (A10)")
    ax.scatter(x, [best.loc[d, "r2_mean"] for d in g["dataset"]], marker="D", s=30, color=BLUE, label="Best Group-CV tabular")
    for i, row in enumerate(g.itertuples()):
        ax.text(i, row.r2 + 0.035, f"{row.r2:.2f}", ha="center", fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels([ds_label(d) for d in g["dataset"]])
    ax.set_ylabel("$R^2$")
    ax.set_ylim(0, 1.02)
    ax.grid(axis="y")
    ax.legend(loc="lower left", frameon=True)
    ax.set_title("GPU baseline under country-group holdout")
    fig.savefig(FIGS / "fig1c_gpu_baseline_ppt.png", bbox_inches="tight", pad_inches=0.05)
    fig.savefig(FIGS / "fig1c_gpu_baseline_ppt.svg", bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def fig_stage2():
    imp = pd.read_csv(TABLES / "enhanced_permutation_importance.csv")
    top = imp[imp["dataset"].eq("stage2_industry_region_GE10")].head(14).iloc[::-1].copy()
    top["label"] = top["feature_label"].map(clean_feature)
    fig, ax = plt.subplots(figsize=(4.8, 3.4), constrained_layout=True)
    ax.barh(top["label"], top["importance_mean"], xerr=top["importance_std"], color=GREEN, alpha=0.92, capsize=1.8)
    ax.set_xlabel("Permutation importance in $R^2$")
    ax.grid(axis="x")
    ax.set_title("Industry/region external validation drivers")
    fig.savefig(FIGS / "fig2_stage2_importance_clean.png", bbox_inches="tight", pad_inches=0.04)
    fig.savefig(FIGS / "fig2_stage2_importance_clean.svg", bbox_inches="tight", pad_inches=0.04)
    plt.close(fig)


if __name__ == "__main__":
    fig_main()
    fig_stage2()
    print("Rendered clean academic figures to", FIGS)
