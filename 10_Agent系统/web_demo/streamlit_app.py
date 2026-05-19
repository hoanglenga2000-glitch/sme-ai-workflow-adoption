from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    import streamlit as st
except Exception as exc:  # pragma: no cover
    raise RuntimeError("Streamlit is missing. Install requirements.txt first.") from exc

from agent_tools.agent_answer import agent_answer
from agent_tools.predict_adoption import predict_adoption
from agent_tools.query_indicator import query_indicator
from agent_tools.recommend_deployment import recommend_deployment


st.set_page_config(page_title="SME AI Research Agent", page_icon="AI", layout="wide")

st.markdown(
    """
    <style>
    :root {
      --ink: #14213d;
      --paper: #f7f3ea;
      --accent: #0f766e;
      --line: #d8d2c4;
    }
    .main { background: var(--paper); }
    h1, h2, h3 { color: var(--ink); letter-spacing: 0; }
    .stButton button { border-radius: 6px; border: 1px solid var(--accent); }
    .metric-card { border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: #fffdf8; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("SME AI Workflow Adoption Research Agent")
st.caption("Evidence-first academic agent: tabular prediction, source-linked retrieval, and bounded tool outputs.")

left, right = st.columns([0.45, 0.55])
with left:
    st.subheader("Prediction Input")
    geo = st.text_input("Country code", value="DE")
    nace = st.text_input("NACE industry", value="C26")
    year = st.number_input("Year", min_value=2021, max_value=2026, value=2025)
    security = st.slider("Security concern index", 0.0, 80.0, 12.0)
    readiness = st.slider("Deployment readiness index", 0.0, 100.0, 68.0)
    efficiency = st.slider("Efficiency need proxy", 0.0, 80.0, 18.0)
    features = {
        "geo": geo,
        "country": geo,
        "year": int(year),
        "size_emp": "GE10",
        "nace_r2": nace,
        "security_concern_index": security,
        "deployment_readiness_index": readiness,
        "efficiency_need_proxy": efficiency,
    }
    run = st.button("Run academic agent", type="primary")

with right:
    st.subheader("Research Answer")
    question = st.text_area("Question", value="Why is Stage 2 not an SME-only sample?")
    if run:
        pred = predict_adoption(features)
        rec = recommend_deployment(features)
        ans = agent_answer(question)
        indicator = query_indicator(geo, nace, int(year), "ai_industry__E_AI_TML")
        st.metric("Predicted adoption intensity", pred.get("prediction"))
        st.metric("Recommended deployment", rec.get("recommended_mode"))
        st.write(ans.get("answer"))
        st.markdown("**Evidence files**")
        st.json(ans.get("evidence_files", []))
        with st.expander("Tool payloads"):
            st.code(json.dumps({"prediction": pred, "recommendation": rec, "indicator": indicator, "answer": ans}, ensure_ascii=False, indent=2), language="json")
    else:
        st.info("Run the agent to produce a source-linked academic answer.")

st.markdown("---")
st.caption("No large raw tables are passed to the language layer. All numerical claims must come from tools.")
