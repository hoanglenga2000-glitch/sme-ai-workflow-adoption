from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_tools.common import evidence_payload, load_stage_dataframe, time_call, write_jsonable


def query_indicator(country: str | None, industry: str | None, year: int | None, indicator: str, stage: str = "stage2") -> dict:
    df = load_stage_dataframe(stage)
    data = df.copy()
    if country:
        data = data[data["geo"] == country]
    if industry and "nace_r2" in data.columns:
        data = data[data["nace_r2"] == industry]
    if year is not None:
        data = data[data["year"] == year]
    if indicator not in data.columns:
        return {
            "status": "error",
            "message": f"indicator `{indicator}` not found",
            "evidence_files": evidence_payload([f"data/processed/{'stage2_industry_panel.csv' if stage == 'stage2' else 'eurostat_ai_panel.csv'}"]),
        }
    rows = data[[col for col in ["geo", "nace_r2", "year", "size_emp", indicator] if col in data.columns]].head(20)
    return {
        "status": "ok",
        "stage": stage,
        "indicator": indicator,
        "row_count": int(len(rows)),
        "rows": rows.to_dict(orient="records"),
        "evidence_files": evidence_payload([f"data/processed/{'stage2_industry_panel.csv' if stage == 'stage2' else 'eurostat_ai_panel.csv'}"]),
    }


if __name__ == "__main__":
    print(write_jsonable(time_call(query_indicator, "DE", "C26", 2025, "ai_industry__E_AI_TML")))
