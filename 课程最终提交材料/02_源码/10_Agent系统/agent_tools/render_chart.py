from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_tools.common import evidence_payload, load_stage_dataframe, save_chart, time_call, write_jsonable


def render_chart(query_spec: dict, stage: str = "stage2") -> dict:
    df = load_stage_dataframe(stage)
    indicator = query_spec["indicator"]
    country = query_spec.get("country")
    if country:
        df = df[df["geo"] == country]
    if indicator not in df.columns:
        return {
            "status": "error",
            "message": f"indicator `{indicator}` not found",
            "evidence_files": evidence_payload([f"data/processed/{'stage2_industry_panel.csv' if stage == 'stage2' else 'eurostat_ai_panel.csv'}"]),
        }
    chart_df = df.groupby("year", as_index=False)[indicator].mean().sort_values("year")
    chart_path = save_chart(chart_df, "year", indicator, query_spec.get("title", indicator), f"{stage}_{indicator}_trend.png")
    return {
        "status": "ok",
        "chart_path": chart_path,
        "rows_used": int(len(chart_df)),
        "evidence_files": evidence_payload([f"data/processed/{'stage2_industry_panel.csv' if stage == 'stage2' else 'eurostat_ai_panel.csv'}"]),
    }


if __name__ == "__main__":
    print(write_jsonable(time_call(render_chart, {"indicator": "ai_industry__E_AI_TML", "country": "DE", "title": "Germany ML capability trend"})))
