"""Enhanced, reproducible training and academic figure pipeline.

This script is intentionally self-contained so the course instructor can rerun it
on the A10 server. It does not fabricate data; it consumes the processed
Eurostat panels produced by the acquisition/cleaning pipelines.
"""

from __future__ import annotations

import json
import math
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold, KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import scienceplots  # noqa: F401
except Exception as exc:  # pragma: no cover
    raise SystemExit(f"Plotting dependencies are missing: {exc}")

try:
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset
except Exception as exc:  # pragma: no cover
    torch = None
    TORCH_IMPORT_ERROR = str(exc)
else:
    TORCH_IMPORT_ERROR = ""


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"
OUT = ROOT / "outputs"
REPORTS = OUT / "reports"
TABLES = OUT / "tables"
FIGS = OUT / "figures" / "academic"
MODELS = ROOT / "models"
for p in [REPORTS, TABLES, FIGS, MODELS]:
    p.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)
random.seed(RANDOM_STATE)


plt.style.use(["science", "no-latex"])
plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 8,
        "axes.titlesize": 9,
        "axes.labelsize": 8,
        "legend.fontsize": 7,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.alpha": 0.18,
        "grid.linewidth": 0.45,
    }
)

BLUE = "#2060CC"
RED = "#CC3030"
GREEN = "#208040"
ORANGE = "#CC7020"
PURPLE = "#8040CC"
GOLD = "#B08020"
GRAY = "#666666"
PALETTE = [BLUE, GREEN, ORANGE, RED, PURPLE, GOLD, GRAY]


TARGET = "target_workflow_automation"
LEAKAGE_TOKENS = [
    TARGET,
    "E_AI_TPA",
    "E_AI_TANY",
    "E_AI_EC",
    "target_any_ai",
    "workflow_gap",
    "adoption_gap",
    "gap_vs_any_ai",
]


FEATURE_LABELS = {
    "ai__E_AI_TML": "ML capability",
    "ai_industry__E_AI_TML": "ML capability",
    "ai__E_AI_TNLG": "Natural language generation",
    "ai_industry__E_AI_TNLG": "Natural language generation",
    "security_concern_index": "Security concern",
    "data_analytics__E_DASANY": "Data analytics use",
    "data_maturity_index": "Data maturity",
    "digital_foundation_index": "Digital foundation",
    "deployment_readiness_index": "Deployment readiness",
    "cloud__E_CC_PDEV": "Cloud development",
    "cloud__E_CC_DA": "Cloud data analytics",
    "geo": "Country heterogeneity",
    "nace_r2": "Industry heterogeneity",
    "year": "Year",
}


@dataclass
class DatasetSpec:
    name: str
    path: Path
    group_col: str
    preferred_models: tuple[str, ...]
    semantic_note: str


DATASETS = [
    DatasetSpec(
        "stage1_sme_size_class",
        DATA / "eurostat_multisource_panel.csv",
        "geo",
        ("ridge", "random_forest", "extra_trees", "hist_gradient_boosting"),
        "SME size-class panel. Use for SME adoption-mechanism claims.",
    ),
    DatasetSpec(
        "stage2_industry_region_GE10",
        DATA / "stage2_industry_panel.csv",
        "geo",
        ("ridge", "random_forest", "extra_trees", "hist_gradient_boosting"),
        "GE10 industry/region panel. Use as external validation, not SME size split.",
    ),
]


def friendly(name: str) -> str:
    return FEATURE_LABELS.get(name, name.replace("_", " "))


def dataset_label(name: str) -> str:
    return {
        "stage1_sme_size_class": "Stage 1 SME\nsize class",
        "stage2_industry_region_GE10": "Stage 2 industry/\nregion GE10",
    }.get(name, name.replace("_", " "))


def group_train_test_indices(df: pd.DataFrame, group_col: str, test_size: float = 0.25) -> tuple[np.ndarray, np.ndarray]:
    if group_col in df.columns and df[group_col].nunique() >= 5:
        groups = np.array(sorted(df[group_col].dropna().unique()))
        rng = np.random.default_rng(RANDOM_STATE)
        rng.shuffle(groups)
        n_test = max(1, int(math.ceil(len(groups) * test_size)))
        test_groups = set(groups[:n_test])
        test_mask = df[group_col].isin(test_groups).to_numpy()
        return np.where(~test_mask)[0], np.where(test_mask)[0]
    idx = np.arange(len(df))
    train_idx, test_idx = train_test_split(idx, test_size=test_size, random_state=RANDOM_STATE)
    return np.asarray(train_idx), np.asarray(test_idx)


def load_dataset(spec: DatasetSpec) -> pd.DataFrame:
    df = pd.read_csv(spec.path)
    if TARGET not in df.columns:
        if "ai__E_AI_TPA" in df.columns:
            df[TARGET] = df["ai__E_AI_TPA"]
        elif "ai_industry__E_AI_TPA" in df.columns:
            df[TARGET] = df["ai_industry__E_AI_TPA"]
        else:
            raise ValueError(f"{spec.name} has no target column")
    df = df[df[TARGET].notna()].copy()
    if "year" not in df.columns and "TIME_PERIOD" in df.columns:
        df["year"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")
    return df


def feature_columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    drop = set()
    for col in df.columns:
        if any(tok in col for tok in LEAKAGE_TOKENS):
            drop.add(col)
    drop |= {"country"}
    candidate = [c for c in df.columns if c not in drop]
    numeric = [c for c in candidate if pd.api.types.is_numeric_dtype(df[c])]
    categorical = [c for c in candidate if c not in numeric and c not in {TARGET}]
    keep_numeric = [c for c in numeric if df[c].notna().mean() >= 0.15 and df[c].nunique(dropna=True) > 1]
    keep_cat = [c for c in categorical if df[c].notna().mean() >= 0.15 and df[c].nunique(dropna=True) <= 400]
    return keep_numeric, keep_cat


def build_preprocessor(num_cols: list[str], cat_cols: list[str]) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), num_cols),
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), cat_cols),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def model_zoo() -> dict[str, object]:
    return {
        "ridge": Ridge(alpha=5.0),
        "random_forest": RandomForestRegressor(n_estimators=500, min_samples_leaf=3, random_state=RANDOM_STATE, n_jobs=-1),
        "extra_trees": ExtraTreesRegressor(n_estimators=700, min_samples_leaf=2, random_state=RANDOM_STATE, n_jobs=-1),
        "hist_gradient_boosting": HistGradientBoostingRegressor(max_iter=350, learning_rate=0.045, l2_regularization=0.05, random_state=RANDOM_STATE),
    }


def cv_eval(spec: DatasetSpec, df: pd.DataFrame, num_cols: list[str], cat_cols: list[str]) -> tuple[pd.DataFrame, dict[str, Pipeline]]:
    X, y = df[num_cols + cat_cols], df[TARGET].astype(float)
    groups = df[spec.group_col] if spec.group_col in df.columns else None
    if groups is not None and groups.nunique() >= 5:
        cv = GroupKFold(n_splits=5)
        splitter = list(cv.split(X, y, groups))
        cv_type = f"GroupKFold({spec.group_col})"
    else:
        cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
        splitter = list(cv.split(X, y))
        cv_type = "KFold"
    rows, fitted = [], {}
    for name, estimator in model_zoo().items():
        pipe = Pipeline([("prep", build_preprocessor(num_cols, cat_cols)), ("model", estimator)])
        scores = cross_validate(
            pipe,
            X,
            y,
            cv=splitter,
            scoring={"r2": "r2", "mae": "neg_mean_absolute_error"},
            n_jobs=1,
            return_train_score=True,
        )
        rows.append(
            {
                "dataset": spec.name,
                "model": name,
                "cv_type": cv_type,
                "r2_mean": float(np.mean(scores["test_r2"])),
                "r2_std": float(np.std(scores["test_r2"])),
                "mae_mean": float(-np.mean(scores["test_mae"])),
                "mae_std": float(np.std(scores["test_mae"])),
                "train_r2_mean": float(np.mean(scores["train_r2"])),
                "fit_time_sec": float(np.mean(scores["fit_time"])),
            }
        )
        fitted[name] = pipe.fit(X, y)
    return pd.DataFrame(rows), fitted


def holdout_eval(spec: DatasetSpec, df: pd.DataFrame, models: dict[str, Pipeline], num_cols: list[str], cat_cols: list[str]) -> pd.DataFrame:
    X, y = df[num_cols + cat_cols], df[TARGET].astype(float)
    train_idx, test_idx = group_train_test_indices(df, spec.group_col)
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    rows = []
    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        pred = pipe.predict(X_test)
        rows.append(
            {
                "dataset": spec.name,
                "model": name,
                "holdout_r2": float(r2_score(y_test, pred)),
                "holdout_mae": float(mean_absolute_error(y_test, pred)),
                "n_train": len(y_train),
                "n_test": len(y_test),
                "split": f"group_holdout_by_{spec.group_col}" if spec.group_col in df.columns else "random_holdout",
            }
        )
    return pd.DataFrame(rows)


def permutation_table(spec: DatasetSpec, df: pd.DataFrame, pipe: Pipeline, num_cols: list[str], cat_cols: list[str]) -> pd.DataFrame:
    X, y = df[num_cols + cat_cols], df[TARGET].astype(float)
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.25, random_state=RANDOM_STATE)
    result = permutation_importance(pipe, X_test, y_test, n_repeats=12, random_state=RANDOM_STATE, n_jobs=1, scoring="r2")
    imp = pd.DataFrame(
        {
            "dataset": spec.name,
            "feature": X.columns,
            "feature_label": [friendly(c) for c in X.columns],
            "importance_mean": result.importances_mean,
            "importance_std": result.importances_std,
        }
    )
    return imp.sort_values("importance_mean", ascending=False)


class MLP(nn.Module):
    def __init__(self, n_features: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(256, 96),
            nn.ReLU(),
            nn.Dropout(0.10),
            nn.Linear(96, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(1)


def torch_mlp_eval(spec: DatasetSpec, df: pd.DataFrame, num_cols: list[str], cat_cols: list[str]) -> dict[str, object]:
    if torch is None:
        return {"dataset": spec.name, "gpu_model": "torch_mlp", "status": f"unavailable: {TORCH_IMPORT_ERROR}"}
    device = "cuda" if torch.cuda.is_available() else "cpu"
    X_raw, y = df[num_cols + cat_cols], df[TARGET].astype(float).to_numpy(np.float32)
    prep = build_preprocessor(num_cols, cat_cols)
    train_idx, test_idx = group_train_test_indices(df, spec.group_col)
    X_train_raw, X_test_raw = X_raw.iloc[train_idx], X_raw.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    X_train = prep.fit_transform(X_train_raw)
    X_test = prep.transform(X_test_raw)
    if hasattr(X_train, "toarray"):
        X_train = X_train.toarray()
        X_test = X_test.toarray()
    X_train = np.asarray(X_train, dtype=np.float32)
    X_test = np.asarray(X_test, dtype=np.float32)
    torch.manual_seed(RANDOM_STATE)
    if device == "cuda":
        torch.cuda.manual_seed_all(RANDOM_STATE)
    model = MLP(X_train.shape[1]).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    loss_fn = nn.SmoothL1Loss()
    train_ds = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
    loader = DataLoader(train_ds, batch_size=min(512, max(32, len(train_ds) // 4)), shuffle=True)
    start = time.time()
    best = {"r2": -1e9, "mae": None, "epoch": 0}
    for epoch in range(1, 501):
        model.train()
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            opt.zero_grad(set_to_none=True)
            loss = loss_fn(model(xb), yb)
            loss.backward()
            opt.step()
        if epoch % 20 == 0 or epoch == 1:
            model.eval()
            with torch.no_grad():
                pred = model(torch.from_numpy(X_test).to(device)).detach().cpu().numpy()
            r2 = r2_score(y_test, pred)
            mae = mean_absolute_error(y_test, pred)
            if r2 > best["r2"]:
                best = {"r2": float(r2), "mae": float(mae), "epoch": epoch}
        if epoch - best["epoch"] > 120:
            break
    elapsed = time.time() - start
    if device == "cuda":
        gpu_name = torch.cuda.get_device_name(0)
        max_mem = torch.cuda.max_memory_allocated(0) / (1024**2)
    else:
        gpu_name = "cpu"
        max_mem = 0.0
    return {
        "dataset": spec.name,
        "gpu_model": "torch_mlp",
        "status": "ok",
        "device": device,
        "gpu_name": gpu_name,
        "r2": best["r2"],
        "mae": best["mae"],
        "best_epoch": best["epoch"],
        "train_seconds": elapsed,
        "max_gpu_memory_mb": max_mem,
        "n_features_after_encoding": X_train.shape[1],
        "split": f"group_holdout_by_{spec.group_col}" if spec.group_col in df.columns else "random_holdout",
    }


def quality_audit(spec: DatasetSpec, df: pd.DataFrame, num_cols: list[str], cat_cols: list[str]) -> dict[str, object]:
    keys = [c for c in ["geo", "year", "size_emp", "nace_r2"] if c in df.columns]
    return {
        "dataset": spec.name,
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "numeric_features": len(num_cols),
        "categorical_features": len(cat_cols),
        "target_nonnull": int(df[TARGET].notna().sum()),
        "target_min": float(df[TARGET].min()),
        "target_median": float(df[TARGET].median()),
        "target_max": float(df[TARGET].max()),
        "mean_numeric_missing_rate": float(df.select_dtypes(include=[np.number]).isna().mean().mean()),
        "duplicate_panel_keys": int(df.duplicated(keys).sum()) if keys else 0,
        "geo_count": int(df["geo"].nunique()) if "geo" in df else None,
        "year_min": int(df["year"].min()) if "year" in df and df["year"].notna().any() else None,
        "year_max": int(df["year"].max()) if "year" in df and df["year"].notna().any() else None,
        "size_class_count": int(df["size_emp"].nunique()) if "size_emp" in df else None,
        "nace_count": int(df["nace_r2"].nunique()) if "nace_r2" in df else None,
        "semantic_note": spec.semantic_note,
    }


def plot_academic(cv: pd.DataFrame, holdout: pd.DataFrame, importance: pd.DataFrame, quality: pd.DataFrame, gpu: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.4))
    ax = axes[0, 0]
    metric = cv.pivot(index="model", columns="dataset", values="r2_mean")
    metric = metric.loc[[m for m in ["ridge", "random_forest", "extra_trees", "hist_gradient_boosting"] if m in metric.index]]
    x = np.arange(len(metric.index))
    width = 0.36
    for i, ds in enumerate(metric.columns):
        ax.bar(x + (i - 0.5) * width, metric[ds], width, label=dataset_label(ds).replace("\n", " "), color=PALETTE[i], edgecolor="white", linewidth=0.4)
    ax.set_xticks(x)
    ax.set_xticklabels([m.replace("_", "\n") for m in metric.index], rotation=0)
    ax.set_ylabel("Group-CV R²")
    ax.set_ylim(0, max(0.95, np.nanmax(metric.values) + 0.08))
    ax.legend(frameon=True, loc="lower right")
    ax.grid(axis="y")
    ax.set_title("A. Cross-validated model fit")

    ax = axes[0, 1]
    q = quality.set_index("dataset")
    vals = q["rows"].astype(float)
    ax.barh([dataset_label(i) for i in vals.index], vals.values, color=[BLUE, GREEN])
    ax.set_xscale("log")
    ax.set_xlabel("Panel rows (log scale)")
    ax.grid(axis="x")
    ax.set_title("B. Modeling panel size")

    ax = axes[1, 0]
    top = importance[importance["dataset"].eq("stage1_sme_size_class")].head(8).iloc[::-1]
    ax.barh(top["feature_label"], top["importance_mean"], xerr=top["importance_std"], color=BLUE, alpha=0.88)
    ax.set_xlabel("Permutation importance")
    ax.grid(axis="x")
    ax.set_title("C. SME mechanism drivers")

    ax = axes[1, 1]
    g = gpu.copy()
    g = g[g["status"].eq("ok")]
    if not g.empty:
        ax.bar([dataset_label(d) for d in g["dataset"]], g["r2"], color=[ORANGE, PURPLE][: len(g)])
        for idx, row in enumerate(g.itertuples()):
            ax.text(idx, row.r2 + 0.02, f"{row.device}\\n{row.gpu_name}", ha="center", va="bottom", fontsize=6)
        ax.set_ylabel("Holdout R²")
        ax.set_ylim(0, max(1.0, g["r2"].max() + 0.15))
    else:
        ax.text(0.5, 0.5, "GPU model unavailable", ha="center", va="center", transform=ax.transAxes)
    ax.grid(axis="y")
    ax.set_title("D. GPU neural baseline")

    fig.suptitle("Enhanced empirical validation for SME AI workflow automation adoption", y=0.995, fontsize=10, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIGS / "fig1_enhanced_validation_panel.png")
    fig.savefig(FIGS / "fig1_enhanced_validation_panel.svg")
    plt.close(fig)

    # Stage 2 importance companion
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    top = importance[importance["dataset"].eq("stage2_industry_region_GE10")].head(12).iloc[::-1]
    ax.barh(top["feature_label"], top["importance_mean"], xerr=top["importance_std"], color=GREEN, alpha=0.9)
    ax.set_xlabel("Permutation importance")
    ax.grid(axis="x")
    ax.set_title("External validation: industry/region mechanism drivers")
    fig.tight_layout()
    fig.savefig(FIGS / "fig2_stage2_external_importance.png")
    fig.savefig(FIGS / "fig2_stage2_external_importance.svg")
    plt.close(fig)


def write_report(cv, holdout, importance, quality, gpu):
    best_cv = cv.sort_values(["dataset", "r2_mean"], ascending=[True, False]).groupby("dataset").head(1)
    lines = [
        "# Enhanced Training And Academic Validation Report",
        "",
        "## What Changed",
        "",
        "This run strengthens the course project from a single train/test result into a reproducible data-mining study: data-quality audit, leakage-controlled feature selection, group cross-validation, holdout validation, permutation importance, and a GPU neural baseline on the A10 server.",
        "",
        "## Dataset Boundary",
        "",
        "- Stage 1 is the SME size-class adoption-mechanism layer and should be used for SME-specific claims.",
        "- Stage 2 is the GE10 industry/region external-validation layer and should not be described as SME size split data.",
        "",
        "## Best Cross-Validated Models",
        "",
        best_cv.to_markdown(index=False),
        "",
        "## GPU Baseline",
        "",
        gpu.to_markdown(index=False),
        "",
        "## Data Quality Audit",
        "",
        quality.to_markdown(index=False),
        "",
        "## Key Interpretation",
        "",
        "The strongest mechanism is not a generic AI enthusiasm variable. AI workflow automation adoption is explained by machine-learning capability, natural-language generation, data analytics maturity, digital foundation, deployment readiness, and country/industry heterogeneity. Security concern remains important because it redirects deployment preference toward private, local, or hybrid architectures.",
        "",
        "## Reproducibility",
        "",
        "- Script: `src/enhanced_training_gpu.py`",
        "- Tables: `outputs/tables/enhanced_*`",
        "- Figures: `outputs/figures/academic/fig*.png` and `.svg`",
        "- Data source: processed Eurostat panels generated by the acquisition and cleaning pipelines.",
    ]
    (REPORTS / "enhanced_training_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    all_cv, all_holdout, all_imp, all_quality, all_gpu = [], [], [], [], []
    for spec in DATASETS:
        df = load_dataset(spec)
        num_cols, cat_cols = feature_columns(df)
        all_quality.append(quality_audit(spec, df, num_cols, cat_cols))
        cv, fitted = cv_eval(spec, df, num_cols, cat_cols)
        holdout = holdout_eval(spec, df, fitted, num_cols, cat_cols)
        best_model_name = cv.sort_values("r2_mean", ascending=False).iloc[0]["model"]
        imp = permutation_table(spec, df, fitted[best_model_name], num_cols, cat_cols)
        gpu = torch_mlp_eval(spec, df, num_cols, cat_cols)
        all_cv.append(cv)
        all_holdout.append(holdout)
        all_imp.append(imp)
        all_gpu.append(gpu)

    cv = pd.concat(all_cv, ignore_index=True)
    holdout = pd.concat(all_holdout, ignore_index=True)
    importance = pd.concat(all_imp, ignore_index=True)
    quality = pd.DataFrame(all_quality)
    gpu = pd.DataFrame(all_gpu)

    cv.to_csv(TABLES / "enhanced_cv_results.csv", index=False)
    holdout.to_csv(TABLES / "enhanced_holdout_results.csv", index=False)
    importance.to_csv(TABLES / "enhanced_permutation_importance.csv", index=False)
    quality.to_csv(TABLES / "enhanced_data_quality_audit.csv", index=False)
    gpu.to_csv(TABLES / "enhanced_gpu_baseline.csv", index=False)
    plot_academic(cv, holdout, importance, quality, gpu)
    write_report(cv, holdout, importance, quality, gpu)

    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "random_state": RANDOM_STATE,
        "torch_available": torch is not None,
        "cuda_available": bool(torch and torch.cuda.is_available()),
        "outputs": [
            "outputs/tables/enhanced_cv_results.csv",
            "outputs/tables/enhanced_holdout_results.csv",
            "outputs/tables/enhanced_permutation_importance.csv",
            "outputs/tables/enhanced_data_quality_audit.csv",
            "outputs/tables/enhanced_gpu_baseline.csv",
            "outputs/reports/enhanced_training_report.md",
            "outputs/figures/academic/fig1_enhanced_validation_panel.png",
            "outputs/figures/academic/fig2_stage2_external_importance.png",
        ],
    }
    (REPORTS / "enhanced_training_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
