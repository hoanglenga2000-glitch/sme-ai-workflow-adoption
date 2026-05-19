from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from fastapi import FastAPI
    from pydantic import BaseModel, Field
except Exception as exc:  # pragma: no cover
    raise RuntimeError("FastAPI dependencies are missing. Install requirements.txt first.") from exc

from agent_tools.agent_answer import agent_answer
from agent_tools.audit_data_file import audit_data_file
from agent_tools.cite_source import cite_source
from agent_tools.explain_prediction import explain_prediction
from agent_tools.predict_adoption import predict_adoption
from agent_tools.query_indicator import query_indicator
from agent_tools.recommend_deployment import recommend_deployment
from agent_tools.render_chart import render_chart

app = FastAPI(title="SME AI Workflow Adoption Research Agent", version="1.0.0")


class IndicatorRequest(BaseModel):
    country: str | None = None
    industry: str | None = None
    year: int | None = None
    indicator: str
    stage: str = "stage2"


class FeatureRequest(BaseModel):
    features: dict[str, Any] = Field(default_factory=dict)
    stage: str = "champion"


class ClaimRequest(BaseModel):
    claim: str


class ChartRequest(BaseModel):
    query_spec: dict[str, Any]
    stage: str = "stage2"


class AgentRequest(BaseModel):
    question: str


class AuditRequest(BaseModel):
    path: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/query_indicator")
def api_query_indicator(req: IndicatorRequest) -> dict:
    return query_indicator(req.country, req.industry, req.year, req.indicator, req.stage)


@app.post("/predict")
def api_predict(req: FeatureRequest) -> dict:
    return predict_adoption(req.features, req.stage)


@app.post("/explain")
def api_explain(req: FeatureRequest) -> dict:
    return explain_prediction(req.features, req.stage)


@app.post("/recommend")
def api_recommend(req: FeatureRequest) -> dict:
    return recommend_deployment(req.features)


@app.post("/cite")
def api_cite(req: ClaimRequest) -> dict:
    return cite_source(req.claim)


@app.post("/chart")
def api_chart(req: ChartRequest) -> dict:
    return render_chart(req.query_spec, req.stage)


@app.post("/agent_answer")
def api_agent_answer(req: AgentRequest) -> dict:
    return agent_answer(req.question)


@app.post("/audit_data_file")
def api_audit(req: AuditRequest) -> dict:
    return audit_data_file(req.path)
