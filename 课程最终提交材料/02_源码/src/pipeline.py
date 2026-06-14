#!/usr/bin/env python3
"""Lightweight end-to-end mining pipeline using installed pandas/sklearn only."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "eurostat" / "isoc_eb_ai_sdmx.csv"
PROCESSED = ROOT / "data" / "processed"
FIGDATA = ROOT / "outputs" / "figures"
TAB = ROOT / "outputs" / "tables"
REP = ROOT / "outputs" / "reports"
for p in [PROCESSED, FIGDATA, TAB, REP, ROOT / "data" / "samples"]:
    p.mkdir(parents=True, exist_ok=True)

INDICATOR_LABELS = {
    "E_AI_TANY": "Any AI technology adoption",
    "E_AI_TPA": "AI workflow automation / decision assistance",
    "E_AI_TNLG": "Natural language generation / code generation",
    "E_AI_TML": "Machine learning for data analysis",
    "E_AI_PBAM": "Business administration or management use",
    "E_AI_PITS": "ICT security use",
    "E_AI_CC": "AI plus cloud computing services",
    "E_AI_DA": "AI plus data analytics",
    "E_AI_CC1SI_DA": "AI + cloud + data analytics",
    "E_AI_BCDP": "Barrier: data protection and privacy concerns",
    "E_AI_BLEG": "Barrier: unclear legal consequences",
    "E_AI_BEC": "Barrier: ethical considerations",
    "E_AI_BDDT": "Barrier: data availability or quality",
    "E_AI_BLE": "Barrier: lack of expertise",
    "E_AI_BCST": "Barrier: high costs",
    "E_AI_BINC": "Barrier: incompatibility with existing systems",
    "E_AI_BNU": "Barrier: AI not useful for enterprise",
    "E_AI_EC": "Ever considered using AI",
    "E_AI_BIAS": "Governance: bias checking measures",
}
COUNTRY_LABELS = {"EU27_2020":"EU-27","EA":"Euro area","BE":"Belgium","BG":"Bulgaria","CZ":"Czechia","DK":"Denmark","DE":"Germany","EE":"Estonia","IE":"Ireland","EL":"Greece","ES":"Spain","FR":"France","HR":"Croatia","IT":"Italy","CY":"Cyprus","LV":"Latvia","LT":"Lithuania","LU":"Luxembourg","HU":"Hungary","MT":"Malta","NL":"Netherlands","AT":"Austria","PL":"Poland","PT":"Portugal","RO":"Romania","SI":"Slovenia","SK":"Slovakia","FI":"Finland","SE":"Sweden","NO":"Norway","BA":"Bosnia and Herzegovina","ME":"Montenegro","MK":"North Macedonia","AL":"Albania","RS":"Serbia","TR":"T?rkiye"}
MODEL_SIZES = ["10-49", "50-249", "10-249", "GE250"]
SME_SIZES = ["10-49", "50-249", "10-249"]


def load_long() -> pd.DataFrame:
    df = pd.read_csv(RAW)
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={"time_period": "year", "obs_value": "value"})
    df = df[df["indic_is"].isin(INDICATOR_LABELS)].copy()
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["indicator_label"] = df["indic_is"].map(INDICATOR_LABELS)
    df["country"] = df["geo"].map(COUNTRY_LABELS).fillna(df["geo"])
    return df.dropna(subset=["year", "value"])


def build_panel(df: pd.DataFrame) -> pd.DataFrame:
    keep = df[df["size_emp"].isin(MODEL_SIZES)].copy()
    panel = keep.pivot_table(index=["geo", "country", "year", "size_emp"], columns="indic_is", values="value", aggfunc="mean").reset_index()
    panel.columns.name = None
    panel = panel.dropna(subset=["E_AI_TPA", "E_AI_TANY"], how="all")
    groups = {
        "security_concern_index": ["E_AI_BCDP", "E_AI_BLEG", "E_AI_BEC", "E_AI_BDDT", "E_AI_BLE", "E_AI_BCST", "E_AI_BINC"],
        "efficiency_need_proxy": ["E_AI_TPA", "E_AI_TNLG", "E_AI_TML", "E_AI_PBAM", "E_AI_DA"],
        "deployment_readiness_index": ["E_AI_CC", "E_AI_CC1SI_DA", "E_AI_DA"],
        "governance_maturity_proxy": ["E_AI_BIAS", "E_AI_PITS"],
    }
    for name, cols in groups.items():
        panel[name] = panel[[c for c in cols if c in panel]].mean(axis=1)
    panel["target_workflow_automation"] = panel["E_AI_TPA"]
    panel["target_any_ai"] = panel["E_AI_TANY"]
    panel["is_sme"] = panel["size_emp"].isin(SME_SIZES).astype(int)
    panel["adoption_gap_vs_any_ai"] = panel["target_any_ai"] - panel["target_workflow_automation"]
    panel["security_x_efficiency"] = panel["security_concern_index"] * panel["efficiency_need_proxy"]
    return panel


def feature_pipeline(features: list[str]) -> ColumnTransformer:
    numeric = [c for c in features if c not in ["size_emp", "geo"]]
    categorical = [c for c in ["size_emp", "geo"] if c in features]
    return ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])


def fit_models(panel: pd.DataFrame) -> dict:
    target = "target_workflow_automation"
    features = ["year", "size_emp", "geo", "target_any_ai", "E_AI_TNLG", "E_AI_TML", "E_AI_PBAM", "E_AI_PITS", "E_AI_CC", "E_AI_DA", "security_concern_index", "deployment_readiness_index", "governance_maturity_proxy", "E_AI_BLE", "E_AI_BCST", "E_AI_BDDT", "E_AI_BCDP", "E_AI_BLEG", "security_x_efficiency"]
    features = [f for f in features if f in panel.columns]
    data = panel[features + [target]].dropna(subset=[target]).copy()
    X, y = data[features], data[target]
    train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=0.25, random_state=42)
    models = {
        "ridge": Ridge(alpha=1.0),
        "random_forest": RandomForestRegressor(n_estimators=700, random_state=42, min_samples_leaf=3, n_jobs=-1),
        "hist_gradient_boosting": HistGradientBoostingRegressor(max_iter=300, learning_rate=0.04, random_state=42, l2_regularization=0.05),
    }
    results, fitted = {}, {}
    for name, model in models.items():
        pipe = Pipeline([("prep", feature_pipeline(features)), ("model", model)])
        pipe.fit(train_x, train_y)
        pred = pipe.predict(test_x)
        results[name] = {"r2": float(r2_score(test_y, pred)), "mae": float(mean_absolute_error(test_y, pred)), "n_test": int(len(test_y))}
        fitted[name] = pipe
    best_name = max(results, key=lambda n: results[n]["r2"])
    best = fitted[best_name]
    perm = permutation_importance(best, test_x, test_y, scoring="r2", n_repeats=25, random_state=42, n_jobs=-1)
    imp = pd.DataFrame({"feature": features, "importance_mean": perm.importances_mean, "importance_std": perm.importances_std}).sort_values("importance_mean", ascending=False)
    imp.to_csv(TAB / "feature_importance.csv", index=False)
    payload = {"best_model": best_name, "metrics": results, "features": features, "model_rows": int(len(data))}
    (REP / "model_metrics.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**payload, "importance": imp}


def cluster_personas(panel: pd.DataFrame) -> pd.DataFrame:
    cols = ["target_workflow_automation", "target_any_ai", "security_concern_index", "deployment_readiness_index", "governance_maturity_proxy", "E_AI_BLE", "E_AI_BCST"]
    cols = [c for c in cols if c in panel.columns]
    data = panel[panel["size_emp"].isin(SME_SIZES)][["geo", "country", "year", "size_emp"] + cols].dropna(subset=["target_workflow_automation"]).copy()
    mat = data[cols].fillna(data[cols].median(numeric_only=True))
    z = StandardScaler().fit_transform(mat)
    data["persona_cluster"] = KMeans(n_clusters=4, random_state=42, n_init=50).fit_predict(z)
    data.to_csv(PROCESSED / "sme_persona_assignments.csv", index=False)
    summary = data.groupby("persona_cluster")[cols].mean().round(2)
    summary["n"] = data.groupby("persona_cluster").size()
    summary = summary.sort_values("target_workflow_automation", ascending=False)
    summary.to_csv(TAB / "sme_persona_clusters.csv")
    return summary


def export_chart_data(df: pd.DataFrame, panel: pd.DataFrame, importance: pd.DataFrame, personas: pd.DataFrame) -> None:
    trend = df[(df["geo"] == "EU27_2020") & (df["size_emp"].isin(["10-49", "50-249", "GE250"]))]
    trend = trend[trend["indic_is"].isin(["E_AI_TANY", "E_AI_TPA", "E_AI_TNLG", "E_AI_TML", "E_AI_BCDP", "E_AI_BLEG", "E_AI_CC"])]
    trend[["year", "size_emp", "indic_is", "indicator_label", "value"]].to_csv(FIGDATA / "01_eu_ai_adoption_trends.csv", index=False)
    latest_year = int(panel["year"].max())
    latest = panel[(panel["year"] == latest_year) & (panel["size_emp"] == "10-249") & (~panel["geo"].isin(["EU27_2020", "EA"]))]
    latest.sort_values("target_workflow_automation", ascending=False).head(25).to_csv(FIGDATA / "02_sme_workflow_automation_country_rank.csv", index=False)
    heat = panel[(panel["geo"] == "EU27_2020") & (panel["size_emp"].isin(["10-49", "50-249", "GE250"]))]
    heat.to_csv(FIGDATA / "03_size_lifecycle_heatmap_data.csv", index=False)
    importance.to_csv(FIGDATA / "04_model_feature_importance_data.csv", index=False)
    personas.to_csv(FIGDATA / "05_sme_persona_clusters_data.csv")


def write_report(df: pd.DataFrame, panel: pd.DataFrame, model: dict, personas: pd.DataFrame) -> None:
    latest_year = int(panel["year"].max())
    eu = panel[(panel["geo"] == "EU27_2020") & (panel["year"] == latest_year)]
    lines = ["# Model Results: SME AI Workflow Automation Adoption\n"]
    lines.append(f"Data source: Eurostat `isoc_eb_ai`, official API SDMX-CSV. Filtered long-form observations: {len(df):,}; panel rows: {len(panel):,}; modeling rows: {model['model_rows']:,}.\n")
    lines.append(f"Latest year: {latest_year}. Target: `E_AI_TPA`, percentage of enterprises using AI technologies automating workflows or assisting decision making.\n")
    lines.append("## Data Mining And Digital Lifecycle\n")
    lines.append("- Acquisition: official API download, timestamp and SHA256 manifest.\n- Cleaning: SDMX data normalized to long and panel forms.\n- Feature engineering: efficiency proxy, security concern index, deployment readiness index, governance maturity proxy, interaction term `security_x_efficiency`.\n- Modeling: Ridge, Random Forest, HistGradientBoosting regression; KMeans persona clustering.\n- Evaluation: R2, MAE, permutation importance; all result tables exported.\n- Deployment/governance: outputs support SaaS/API/local/hybrid deployment recommendations and NIST-style risk feedback.\n")
    lines.append("## Model Metrics\n")
    lines.append(f"Best model: `{model['best_model']}`.\n")
    for name, m in model["metrics"].items():
        lines.append(f"- {name}: R2={m['r2']:.3f}, MAE={m['mae']:.3f}, n_test={m['n_test']}\n")
    lines.append("## Top Predictive Factors\n")
    lines.append(model["importance"].head(12).round(4).to_markdown(index=False) + "\n")
    lines.append("## EU Latest Size-Class Snapshot\n")
    cols = ["size_emp", "target_workflow_automation", "target_any_ai", "security_concern_index", "deployment_readiness_index", "governance_maturity_proxy", "adoption_gap_vs_any_ai"]
    if not eu.empty:
        lines.append(eu[cols].round(2).sort_values("size_emp").to_markdown(index=False) + "\n")
    lines.append("## SME Persona Clusters\n")
    lines.append(personas.to_markdown() + "\n")
    lines.append("## Chart Data Files\n")
    for f in sorted(FIGDATA.glob("*.csv")):
        lines.append(f"- `{f.relative_to(ROOT)}`\n")
    (REP / "model_results.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = load_long()
    panel = build_panel(df)
    df.to_csv(PROCESSED / "eurostat_ai_long.csv", index=False)
    panel.to_csv(PROCESSED / "eurostat_ai_panel.csv", index=False)
    df.head(1000).to_csv(ROOT / "data" / "samples" / "eurostat_ai_long_sample.csv", index=False)
    panel.head(500).to_csv(ROOT / "data" / "samples" / "eurostat_ai_panel_sample.csv", index=False)
    model = fit_models(panel)
    personas = cluster_personas(panel)
    export_chart_data(df, panel, model["importance"], personas)
    write_report(df, panel, model, personas)
    printable = {k: v for k, v in model.items() if k != "importance"}
    printable.update({"rows_long": len(df), "rows_panel": len(panel), "persona_clusters": len(personas)})
    print(json.dumps(printable, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
