from __future__ import annotations

import json
import hashlib
import os
import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from pandas.api.types import is_numeric_dtype

AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent
ARTIFACTS = AGENT_ROOT / "training" / "artifacts"
REPORTS = AGENT_ROOT / "reports"
ARTIFACTS.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)
NO_EVIDENCE_LABEL = "无法确认"


@dataclass
class StageConfig:
    name: str
    csv_path: Path
    target: str
    group_col: str
    time_col: str
    industry_col: str | None
    drop_cols: set[str]
    required_cols: list[str]
    description: str
    cv_splits: int = 5
    preferred_models: list[str] | None = None


STAGE_CONFIGS = {
    "stage1": StageConfig(
        name="stage1",
        csv_path=ROOT / "data" / "processed" / "eurostat_ai_panel.csv",
        target="target_workflow_automation",
        group_col="geo",
        time_col="year",
        industry_col=None,
        drop_cols={
            "target_workflow_automation",
            "E_AI_TPA",
            "target_any_ai",
            "adoption_gap_vs_any_ai",
            "efficiency_need_proxy",
            "security_x_efficiency",
        },
        required_cols=["geo", "year", "size_emp"],
        description="SME mechanism interpretation layer",
        cv_splits=5,
        preferred_models=["ridge", "random_forest", "hist_gradient_boosting"],
    ),
    "stage2": StageConfig(
        name="stage2",
        csv_path=ROOT / "data" / "processed" / "stage2_industry_panel.csv",
        target="target_workflow_automation",
        group_col="geo",
        time_col="year",
        industry_col="nace_r2",
        drop_cols={"target_workflow_automation", "ai_industry__E_AI_TPA"},
        required_cols=["geo", "year", "size_emp", "nace_r2"],
        description="GE10 industry and region external validation layer",
        cv_splits=2,
        preferred_models=["ridge", "extra_trees", "hist_gradient_boosting"],
    ),
}


def load_stage_frame(stage: str) -> tuple[StageConfig, pd.DataFrame]:
    config = STAGE_CONFIGS[stage]
    df = pd.read_csv(config.csv_path)
    missing = [col for col in config.required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"{stage} missing required columns: {missing}")
    return config, df


def feature_columns(df: pd.DataFrame, config: StageConfig) -> list[str]:
    blacklist = set(config.drop_cols)
    for col in df.columns:
        if col.startswith("target_"):
            blacklist.add(col)
    cols = []
    for col in df.columns:
        if col in blacklist:
            continue
        if df[col].notna().mean() < 0.15:
            continue
        cols.append(col)
    return cols


def build_preprocessor(df: pd.DataFrame, features: list[str]) -> tuple[ColumnTransformer, list[str], list[str]]:
    categorical = [col for col in features if not is_numeric_dtype(df[col])]
    numeric = [col for col in features if is_numeric_dtype(df[col])]
    prep = ColumnTransformer(
        [
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), numeric),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
                    ]
                ),
                categorical,
            ),
        ],
        sparse_threshold=0.0,
    )
    return prep, numeric, categorical


def available_optional_models() -> dict[str, Callable[[], object]]:
    models: dict[str, Callable[[], object]] = {}
    try:
        from xgboost import XGBRegressor

        models["xgboost"] = lambda: XGBRegressor(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            random_state=42,
            tree_method="hist",
        )
    except Exception:
        pass
    try:
        from lightgbm import LGBMRegressor

        models["lightgbm"] = lambda: LGBMRegressor(
            n_estimators=500,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=42,
            verbosity=-1,
        )
    except Exception:
        pass
    try:
        from catboost import CatBoostRegressor

        models["catboost"] = lambda: CatBoostRegressor(
            iterations=500,
            depth=6,
            learning_rate=0.05,
            random_seed=42,
            verbose=False,
        )
    except Exception:
        pass
    return models


def model_factories() -> dict[str, Callable[[], object]]:
    factories: dict[str, Callable[[], object]] = {
        "ridge": lambda: Ridge(alpha=1.0),
        "random_forest": lambda: RandomForestRegressor(n_estimators=400, random_state=42, min_samples_leaf=3, n_jobs=-1),
        "extra_trees": lambda: ExtraTreesRegressor(n_estimators=400, random_state=42, min_samples_leaf=3, n_jobs=-1),
        "hist_gradient_boosting": lambda: HistGradientBoostingRegressor(max_iter=250, learning_rate=0.04, random_state=42, l2_regularization=0.05),
    }
    factories.update(available_optional_models())
    return factories


def build_pipeline(df: pd.DataFrame, features: list[str], model: object) -> Pipeline:
    prep, _, _ = build_preprocessor(df, features)
    return Pipeline([("prep", prep), ("model", model)])


def evaluate_group_kfold(df: pd.DataFrame, config: StageConfig, features: list[str], model_name: str, model_factory: Callable[[], object]) -> dict:
    selected = list(dict.fromkeys(features + [config.target, config.group_col]))
    data = df[selected].dropna(subset=[config.target]).copy()
    X = data[features]
    y = data[config.target]
    groups = data[config.group_col]
    splitter = GroupKFold(n_splits=min(config.cv_splits, groups.nunique()))
    fold_metrics = []
    oof_pred = np.zeros(len(data), dtype=float)
    for fold, (train_idx, test_idx) in enumerate(splitter.split(X, y, groups), start=1):
        train_x = X.iloc[train_idx]
        train_y = y.iloc[train_idx]
        test_x = X.iloc[test_idx]
        test_y = y.iloc[test_idx]
        pipe = build_pipeline(data, features, model_factory())
        pipe.fit(train_x, train_y)
        pred = pipe.predict(test_x)
        oof_pred[test_idx] = pred
        fold_metrics.append(
            {
                "fold": fold,
                "r2": float(r2_score(test_y, pred)),
                "mae": float(mean_absolute_error(test_y, pred)),
                "rows": int(len(test_idx)),
            }
        )
    final_pipe = build_pipeline(data, features, model_factory())
    final_pipe.fit(X, y)
    overall = {
        "model": model_name,
        "validation": "group_kfold",
        "rows": int(len(data)),
        "group_count": int(groups.nunique()),
        "r2_mean": float(np.mean([m["r2"] for m in fold_metrics])),
        "r2_std": float(np.std([m["r2"] for m in fold_metrics])),
        "mae_mean": float(np.mean([m["mae"] for m in fold_metrics])),
        "mae_std": float(np.std([m["mae"] for m in fold_metrics])),
        "fold_metrics": fold_metrics,
    }
    return {"metrics": overall, "pipeline": final_pipe, "data": data, "oof_pred": oof_pred}


def evaluate_time_holdout(df: pd.DataFrame, config: StageConfig, features: list[str], model_factory: Callable[[], object]) -> dict | None:
    if config.time_col not in df.columns:
        return None
    years = sorted(pd.Series(df[config.time_col].dropna().unique()).tolist())
    if len(years) < 3:
        return None
    cutoff = years[-2]
    selected = list(dict.fromkeys(features + [config.target, config.time_col]))
    data = df[selected].dropna(subset=[config.target]).copy()
    train = data[data[config.time_col] <= cutoff]
    test = data[data[config.time_col] > cutoff]
    if train.empty or test.empty:
        return None
    pipe = build_pipeline(data, features, model_factory())
    pipe.fit(train[features], train[config.target])
    pred = pipe.predict(test[features])
    return {
        "validation": "time_holdout",
        "train_year_max": int(cutoff),
        "test_year_min": int(test[config.time_col].min()),
        "rows_train": int(len(train)),
        "rows_test": int(len(test)),
        "r2": float(r2_score(test[config.target], pred)),
        "mae": float(mean_absolute_error(test[config.target], pred)),
    }


def evaluate_industry_holdout(df: pd.DataFrame, config: StageConfig, features: list[str], model_factory: Callable[[], object]) -> dict | None:
    if not config.industry_col or config.industry_col not in df.columns:
        return None
    selected = list(dict.fromkeys(features + [config.target, config.industry_col]))
    data = df[selected].dropna(subset=[config.target]).copy()
    counts = data[config.industry_col].value_counts()
    held_out = counts.idxmax()
    train = data[data[config.industry_col] != held_out]
    test = data[data[config.industry_col] == held_out]
    if train.empty or test.empty:
        return None
    pipe = build_pipeline(data, features, model_factory())
    pipe.fit(train[features], train[config.target])
    pred = pipe.predict(test[features])
    return {
        "validation": "industry_holdout",
        "held_out_industry": held_out,
        "rows_train": int(len(train)),
        "rows_test": int(len(test)),
        "r2": float(r2_score(test[config.target], pred)),
        "mae": float(mean_absolute_error(test[config.target], pred)),
    }


def top_feature_importance(pipe: Pipeline, data: pd.DataFrame, features: list[str], target: str, top_n: int = 15) -> list[dict]:
    perm = permutation_importance(pipe, data[features], data[target], scoring="r2", n_repeats=8, random_state=42, n_jobs=1)
    table = pd.DataFrame({"feature": features, "importance_mean": perm.importances_mean, "importance_std": perm.importances_std})
    table = table.sort_values("importance_mean", ascending=False).head(top_n)
    return table.round(6).to_dict(orient="records")


def save_bundle(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, path)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def file_sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dataset_fingerprint(paths: list[Path]) -> dict:
    return {
        str(path.relative_to(ROOT).as_posix()): {
            "sha256": file_sha256(path),
            "bytes": path.stat().st_size,
        }
        for path in paths
        if path.exists()
    }


def audit_manifest(manifest_path: Path) -> dict:
    records = []
    hash_bad = 0
    missing = 0
    hash_ok = 0
    skipped = 0
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        raw_path = record.get("path")
        expected_sha = record.get("sha256")
        if not raw_path or str(raw_path) == "None" or not expected_sha:
            skipped += 1
            records.append(
                {
                    "source_id": record.get("source_id"),
                    "path": raw_path,
                    "exists": False,
                    "expected_sha256": expected_sha,
                    "actual_sha256": None,
                    "ok": None,
                    "status": "skipped_no_hash_path",
                }
            )
            continue
        rel_path = Path(str(raw_path).replace("\\", "/"))
        data_path = ROOT / rel_path
        exists = data_path.exists()
        actual_sha = file_sha256(data_path) if exists else None
        ok = bool(exists and expected_sha and actual_sha == expected_sha)
        hash_ok += int(ok)
        missing += int(not exists)
        hash_bad += int(exists and expected_sha and actual_sha != expected_sha)
        records.append(
            {
                "source_id": record.get("source_id"),
                "path": rel_path.as_posix(),
                "exists": exists,
                "expected_sha256": expected_sha,
                "actual_sha256": actual_sha,
                "ok": ok,
            }
        )
    return {
        "manifest": str(manifest_path.relative_to(ROOT).as_posix()),
        "records": len(records),
        "hash_ok": hash_ok,
        "hash_bad": hash_bad,
        "missing": missing,
        "skipped": skipped,
        "ok": hash_bad == 0 and missing == 0,
        "items": records,
    }


def audit_all_manifests() -> dict:
    manifests = [ROOT / "data" / "raw" / "manifest.jsonl", ROOT / "data" / "raw" / "manifest_stage2.jsonl"]
    audits = [audit_manifest(path) for path in manifests if path.exists()]
    return {"ok": all(item["ok"] for item in audits), "manifests": audits}


def leakage_audit(stage: str, features: list[str]) -> dict:
    banned = set(STAGE_CONFIGS[stage].drop_cols)
    if stage == "stage1":
        banned.update({"E_AI_TPA", "target_any_ai", "adoption_gap_vs_any_ai", "efficiency_need_proxy", "security_x_efficiency"})
    if stage == "stage2":
        banned.update({"ai_industry__E_AI_TPA"})
    leaked = sorted(banned.intersection(features))
    return {"stage": stage, "ok": not leaked, "leaked_features": leaked, "banned_features": sorted(banned)}


def git_commit_sha() -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception:
        return None


def runtime_snapshot() -> dict:
    snapshot = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "git_commit": git_commit_sha(),
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
    }
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        snapshot["gpu_summary"] = result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
    except Exception as exc:
        snapshot["gpu_summary"] = f"unavailable: {exc}"
    return snapshot


def academic_score(metrics: dict) -> float:
    score = float(metrics.get("r2_mean", 0.0))
    time_holdout = metrics.get("time_holdout") or {}
    industry_holdout = metrics.get("industry_holdout") or {}
    if "r2" in time_holdout:
        score += 0.20 * float(time_holdout["r2"])
    if "r2" in industry_holdout:
        score += 0.10 * float(industry_holdout["r2"])
    score -= 0.05 * float(metrics.get("r2_std", 0.0))
    score -= 0.02 * float(metrics.get("mae_mean", 0.0))
    return score
