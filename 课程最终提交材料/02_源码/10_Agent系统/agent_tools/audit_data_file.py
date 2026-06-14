from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_tools.common import ROOT, evidence_payload, time_call, write_jsonable
from training.common import audit_all_manifests, file_sha256


def audit_data_file(path: str) -> dict:
    data_path = (ROOT / path).resolve()
    root = ROOT.resolve()
    if not data_path.is_relative_to(root):
        return {"status": "error", "message": "path must stay inside repository", "evidence_files": []}
    if not data_path.exists():
        return {"status": "error", "message": "file not found", "path": path, "evidence_files": []}
    payload = {
        "status": "ok",
        "path": str(data_path.relative_to(ROOT).as_posix()),
        "bytes": data_path.stat().st_size,
        "sha256": file_sha256(data_path),
        "evidence_files": evidence_payload([str(data_path.relative_to(ROOT).as_posix())]),
    }
    if data_path.suffix.lower() == ".csv":
        df = pd.read_csv(data_path, nrows=10000)
        payload["columns"] = list(df.columns)
        payload["sampled_rows"] = int(len(df))
        payload["missing_rate_sample"] = {col: round(float(df[col].isna().mean()), 6) for col in df.columns[:50]}
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?")
    parser.add_argument("--manifest-audit", action="store_true")
    args = parser.parse_args()
    if args.manifest_audit:
        print(write_jsonable(audit_all_manifests()))
        raise SystemExit(0)
    if not args.path:
        parser.error("path is required unless --manifest-audit is used")
    print(write_jsonable(time_call(audit_data_file, args.path)))


if __name__ == "__main__":
    main()
