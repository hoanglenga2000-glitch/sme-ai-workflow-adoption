#!/usr/bin/env python3
"""Multi-source official data pipeline for SME AI workflow automation adoption."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "eurostat"
PROCESSED = ROOT / "data" / "processed"
FIGDATA = ROOT / "outputs" / "figures"
TAB = ROOT / "outputs" / "tables"
REP = ROOT / "outputs" / "reports"
for p in [PROCESSED, FIGDATA, TAB, REP, ROOT / "data" / "samples"]:
    p.mkdir(parents=True, exist_ok=True)

DATASETS = {
    "ai": {"file": "isoc_eb_ai_sdmx.csv", "keep": ["E_AI_TPA","E_AI_TANY","E_AI_TNLG","E_AI_TML","E_AI_PBAM","E_AI_PITS","E_AI_CC","E_AI_DA","E_AI_CC1SI_DA","E_AI_BCDP","E_AI_BLEG","E_AI_BEC","E_AI_BDDT","E_AI_BLE","E_AI_BCST","E_AI_BINC","E_AI_BNU","E_AI_EC","E_AI_BIAS"]},
    "cloud": {"file": "isoc_cicce_use_sdmx.csv", "keep": ["E_CC","E_CC1_SI","E_CC1_S","E_CC_PSEC","E_CC_PDEV","E_CC_DA","E_CC_PDB","E_CC_PFIL","E_CC_PCPU","E_CC_PCRM","E_CC_PERP"]},
    "digital_intensity": {"file": "isoc_e_dii_sdmx.csv", "keep": ["E_DI3_GELO","E_DI3_HI","E_DI3_VHI","E_DI4_GELO","E_DI4_HI","E_DI4_VHI"]},
    "data_analytics": {"file": "isoc_eb_das_sdmx.csv", "keep": ["E_DA","E_DASANY","E_DASGE3","E_DASWEB","E_DASCRM","E_DASERP","E_DASSDS","E_DAOWN","E_DAEXT"]},
    "big_data": {"file": "isoc_eb_bd_sdmx.csv", "keep": ["E_BDA","E_BDAML","E_BDANL","E_BDAINT","E_BDAEXT","E_BDBUY"]},
    "ecommerce_sales": {"file": "isoc_ec_esels_sdmx.csv", "keep": ["E_AESELL","E_ESELL","E_AWSELL","E_AWS_COWN","E_AWS_CMP","E_AWSDS","E_AWSFOR"]},
    "ecommerce_value": {"file": "isoc_ec_evals_sdmx.csv", "keep": []},
    "ict_specialists": {"file": "isoc_ske_itspe_sdmx.csv", "keep": ["E_ITSP"]},
    "ict_training": {"file": "isoc_ske_itts_sdmx.csv", "keep": ["E_ITT2","E_ITSPT2","E_ITUST2"]},
    "ict_recruitment": {"file": "isoc_ske_itrcrs_sdmx.csv", "keep": ["E_ITSPRCR2","E_ITSPVAC2","E_ITSPDLA","E_ITSPDLET","E_ITSPDLWE","E_ITSPDSAL"]},
}

COUNTRY_LABELS = {"EU27_2020":"EU-27","EA":"Euro area","BE":"Belgium","BG":"Bulgaria","CZ":"Czechia","DK":"Denmark","DE":"Germany","EE":"Estonia","IE":"Ireland","EL":"Greece","ES":"Spain","FR":"France","HR":"Croatia","IT":"Italy","CY":"Cyprus","LV":"Latvia","LT":"Lithuania","LU":"Luxembourg","HU":"Hungary","MT":"Malta","NL":"Netherlands","AT":"Austria","PL":"Poland","PT":"Portugal","RO":"Romania","SI":"Slovenia","SK":"Slovakia","FI":"Finland","SE":"Sweden","NO":"Norway","BA":"Bosnia and Herzegovina","ME":"Montenegro","MK":"North Macedonia","AL":"Albania","RS":"Serbia","TR":"T?rkiye"}
MODEL_SIZES = ["10-49", "50-249", "10-249", "GE250"]
SME_SIZES = ["10-49", "50-249", "10-249"]


def load_dataset(name: str, meta: dict) -> pd.DataFrame:
    p = RAW_DIR / meta["file"]
    df = pd.read_csv(p)
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={"time_period": "year", "obs_value": "value"})
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df[df["size_emp"].isin(MODEL_SIZES)].copy()
    if meta["keep"]:
        df = df[df["indic_is"].isin(meta["keep"])].copy()
    else:
        # e-commerce value has different measures; keep enterprise percentage variables if present.
        df = df[df["unit"].astype(str).str.contains("PC", na=False)].copy()
    df["dataset"] = name
    df["feature"] = name + "__" + df["indic_is"].astype(str)
    return df.dropna(subset=["year", "value"])


def build_multisource() -> tuple[pd.DataFrame, pd.DataFrame]:
    frames = [load_dataset(name, meta) for name, meta in DATASETS.items()]
    long = pd.concat(frames, ignore_index=True)
    long["country"] = long["geo"].map(COUNTRY_LABELS).fillna(long["geo"])
    panel = long.pivot_table(index=["geo", "country", "year", "size_emp"], columns="feature", values="value", aggfunc="mean").reset_index()
    panel.columns.name = None
    # Core targets from AI table.
    panel["target_workflow_automation"] = panel.get("ai__E_AI_TPA")
    panel["target_any_ai"] = panel.get("ai__E_AI_TANY")
    groups = {
        "security_concern_index": ["ai__E_AI_BCDP","ai__E_AI_BLEG","ai__E_AI_BEC","ai__E_AI_BDDT","ai__E_AI_BLE","ai__E_AI_BCST","ai__E_AI_BINC"],
        "efficiency_need_proxy": ["ai__E_AI_TPA","ai__E_AI_TNLG","ai__E_AI_TML","ai__E_AI_PBAM","data_analytics__E_DA","data_analytics__E_DASANY","big_data__E_BDA"],
        "deployment_readiness_index": ["cloud__E_CC","cloud__E_CC1_SI","cloud__E_CC1_S","cloud__E_CC_PDEV","cloud__E_CC_PSEC","ai__E_AI_CC","ai__E_AI_CC1SI_DA"],
        "data_maturity_index": ["data_analytics__E_DA","data_analytics__E_DASANY","data_analytics__E_DASGE3","big_data__E_BDA","big_data__E_BDAML","big_data__E_BDANL"],
        "digital_foundation_index": ["digital_intensity__E_DI3_GELO","digital_intensity__E_DI3_HI","digital_intensity__E_DI3_VHI","digital_intensity__E_DI4_GELO","digital_intensity__E_DI4_HI","digital_intensity__E_DI4_VHI"],
        "market_digitization_index": ["ecommerce_sales__E_AESELL","ecommerce_sales__E_ESELL","ecommerce_sales__E_AWSELL","ecommerce_sales__E_AWS_COWN","ecommerce_sales__E_AWS_CMP","ecommerce_sales__E_AWSDS"],
        "ict_capability_index": ["ict_specialists__E_ITSP","ict_training__E_ITT2","ict_training__E_ITSPT2","ict_training__E_ITUST2","ict_recruitment__E_ITSPRCR2"],
        "ict_constraint_index": ["ict_recruitment__E_ITSPVAC2","ict_recruitment__E_ITSPDLA","ict_recruitment__E_ITSPDLET","ict_recruitment__E_ITSPDLWE","ict_recruitment__E_ITSPDSAL"],
        "governance_maturity_proxy": ["ai__E_AI_BIAS", "ai__E_AI_PITS", "cloud__E_CC_PSEC"],
    }
    for name, cols in groups.items():
        available = [c for c in cols if c in panel.columns]
        panel[name] = panel[available].mean(axis=1) if available else np.nan
    panel["is_sme"] = panel["size_emp"].isin(SME_SIZES).astype(int)
    panel["adoption_gap_vs_any_ai"] = panel["target_any_ai"] - panel["target_workflow_automation"]
    panel["security_x_efficiency"] = panel["security_concern_index"] * panel["efficiency_need_proxy"]
    panel["deployment_x_data_maturity"] = panel["deployment_readiness_index"] * panel["data_maturity_index"]
    return long, panel


def make_supervised(panel: pd.DataFrame) -> dict:
    target = "target_workflow_automation"
    # Exclude direct AI adoption aggregates and target-derived gap/interaction variables
    # to avoid target leakage in the supervised prediction stage.
    engineered = ['security_concern_index','deployment_readiness_index','data_maturity_index','digital_foundation_index','market_digitization_index','ict_capability_index','ict_constraint_index','governance_maturity_proxy']
    leakage = {'ai__E_AI_TPA', 'ai__E_AI_TANY', 'ai__E_AI_EC'}
    raw_candidates = [c for c in panel.columns if "__" in c and c not in leakage]
    features = ["year", "size_emp", "geo"] + [c for c in engineered + raw_candidates if c in panel.columns]
    data = panel[features + [target]].dropna(subset=[target]).copy()
    # Use columns with enough observed information.
    keep = ["year", "size_emp", "geo"]
    for c in features:
        if c in keep: continue
        if data[c].notna().mean() >= 0.25:
            keep.append(c)
    features = keep
    X, y = data[features], data[target]
    train_x, test_x, train_y, test_y = train_test_split(X, y, test_size=0.25, random_state=42)
    numeric = [c for c in features if c not in ["size_emp", "geo"]]
    categorical = [c for c in ["size_emp", "geo"] if c in features]
    prep = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
        ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))]), categorical),
    ])
    models = {
        "ridge": Ridge(alpha=1.0),
        "random_forest": RandomForestRegressor(n_estimators=1000, random_state=42, min_samples_leaf=2, n_jobs=-1),
        "extra_trees": ExtraTreesRegressor(n_estimators=1000, random_state=42, min_samples_leaf=2, n_jobs=-1),
        "hist_gradient_boosting": HistGradientBoostingRegressor(max_iter=600, learning_rate=0.03, random_state=42, l2_regularization=0.03),
    }
    results, fitted = {}, {}
    for name, model in models.items():
        pipe = Pipeline([("prep", prep), ("model", model)])
        pipe.fit(train_x, train_y)
        pred = pipe.predict(test_x)
        results[name] = {"r2": float(r2_score(test_y, pred)), "mae": float(mean_absolute_error(test_y, pred)), "n_test": int(len(test_y))}
        fitted[name] = pipe
    best_name = max(results, key=lambda k: results[k]["r2"])
    best = fitted[best_name]
    perm = permutation_importance(best, test_x, test_y, scoring="r2", n_repeats=30, random_state=42, n_jobs=-1)
    imp = pd.DataFrame({"feature": features, "importance_mean": perm.importances_mean, "importance_std": perm.importances_std}).sort_values("importance_mean", ascending=False)
    imp.to_csv(TAB / "feature_importance_multisource.csv", index=False)
    payload = {"best_model": best_name, "metrics": results, "features": features, "model_rows": int(len(data)), "feature_count": len(features)}
    (REP / "model_metrics_multisource.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**payload, "importance": imp}


def make_personas(panel: pd.DataFrame) -> pd.DataFrame:
    cols = ["target_workflow_automation","target_any_ai","security_concern_index","deployment_readiness_index","data_maturity_index","digital_foundation_index","market_digitization_index","ict_capability_index","ict_constraint_index","governance_maturity_proxy"]
    cols = [c for c in cols if c in panel.columns]
    data = panel[panel["size_emp"].isin(SME_SIZES)][["geo","country","year","size_emp"] + cols].dropna(subset=["target_workflow_automation"]).copy()
    mat = data[cols].copy()
    mat = mat.fillna(mat.median(numeric_only=True))
    z = StandardScaler().fit_transform(mat)
    data["persona_cluster"] = MiniBatchKMeans(n_clusters=5, random_state=42, n_init=25, batch_size=128).fit_predict(z)
    data.to_csv(PROCESSED / "sme_persona_assignments_multisource.csv", index=False)
    summary = data.groupby("persona_cluster")[cols].mean().round(2)
    summary["n"] = data.groupby("persona_cluster").size()
    summary = summary.sort_values("target_workflow_automation", ascending=False)
    summary.to_csv(TAB / "sme_persona_clusters_multisource.csv")
    return summary


def export_chart_data(long: pd.DataFrame, panel: pd.DataFrame, importance: pd.DataFrame, personas: pd.DataFrame) -> None:
    panel.to_csv(PROCESSED / "eurostat_multisource_panel.csv", index=False)
    long.to_csv(PROCESSED / "eurostat_multisource_long.csv", index=False)
    long.head(3000).to_csv(ROOT / "data" / "samples" / "eurostat_multisource_long_sample.csv", index=False)
    panel.head(1000).to_csv(ROOT / "data" / "samples" / "eurostat_multisource_panel_sample.csv", index=False)
    latest = panel[(panel["year"] == panel["year"].max()) & (panel["size_emp"] == "10-249") & (~panel["geo"].isin(["EU27_2020", "EA"]))]
    latest.sort_values("target_workflow_automation", ascending=False).head(30).to_csv(FIGDATA / "06_multisource_country_rank.csv", index=False)
    trend = panel[(panel["geo"] == "EU27_2020") & (panel["size_emp"].isin(["10-49","50-249","GE250"]))]
    trend.to_csv(FIGDATA / "07_multisource_lifecycle_trend.csv", index=False)
    importance.head(40).to_csv(FIGDATA / "08_multisource_feature_importance.csv", index=False)
    personas.to_csv(FIGDATA / "09_multisource_persona_clusters.csv")


def write_report(long: pd.DataFrame, panel: pd.DataFrame, model: dict, personas: pd.DataFrame) -> None:
    manifest_rows = sum(1 for _ in (ROOT / "data" / "raw" / "manifest.jsonl").open(encoding="utf-8"))
    ok_sources = [json.loads(line) for line in (ROOT / "data" / "raw" / "manifest.jsonl").open(encoding="utf-8") if json.loads(line).get("ok")]
    total_bytes = sum(x["bytes"] for x in ok_sources)
    latest_year = int(panel["year"].max())
    lines = ["# Multi-Source Model Results: SME AI Workflow Automation Adoption\n"]
    lines.append(f"Verified official sources: {len(ok_sources)} Eurostat datasets; raw bytes: {total_bytes:,}; manifest rows including failed Census attempts: {manifest_rows}.\n")
    lines.append(f"Long-form official observations after feature selection: {len(long):,}; country-year-size panel rows: {len(panel):,}; modeling rows: {model['model_rows']:,}; feature count: {model['feature_count']}.\n")
    lines.append(f"Latest year in integrated panel: {latest_year}. Target remains official AI workflow automation / decision-assistance adoption (`E_AI_TPA`).\n")
    lines.append("## Why This Is Stronger Than A Single Dataset\n")
    lines.append("The model now connects AI adoption with cloud deployment, digital intensity, data analytics, big-data capability, e-commerce market digitization, ICT specialists, ICT training and ICT recruitment constraints. This directly operationalizes the research mechanism: efficiency demand, security concern, deployment preference, organizational digital foundation and capability constraints.\n")
    lines.append("## Model Metrics\n")
    lines.append(f"Best model: `{model['best_model']}`.\n")
    for name, m in model["metrics"].items():
        lines.append(f"- {name}: R2={m['r2']:.3f}, MAE={m['mae']:.3f}, n_test={m['n_test']}\n")
    lines.append("## Top Predictive Factors\n")
    lines.append(model["importance"].head(18).round(4).to_markdown(index=False) + "\n")
    lines.append("## SME Persona Clusters\n")
    lines.append(personas.to_markdown() + "\n")
    lines.append("## Deployment Strategy Translation\n")
    lines.append("- High workflow automation + high deployment readiness: prioritize API/hybrid integration and process orchestration.\n")
    lines.append("- High AI interest but weak cloud/data foundation: prioritize SaaS templates and guided onboarding.\n")
    lines.append("- High security/legal concern: prioritize private cloud/local deployment, audit logs, permission controls and NIST-style governance.\n")
    lines.append("- ICT skill constraint cluster: prioritize low-code workflow automation and managed service support.\n")
    (REP / "model_results_multisource.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    long, panel = build_multisource()
    model = make_supervised(panel)
    personas = make_personas(panel)
    export_chart_data(long, panel, model["importance"], personas)
    write_report(long, panel, model, personas)
    printable = {k: v for k, v in model.items() if k != "importance"}
    printable.update({"long_rows": len(long), "panel_rows": len(panel), "persona_clusters": len(personas)})
    print(json.dumps(printable, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
