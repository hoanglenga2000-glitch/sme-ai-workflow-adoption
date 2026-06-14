from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_tools.common import evidence_payload, time_call, write_jsonable


def recommend_deployment(features: dict) -> dict:
    efficiency = float(features.get("efficiency_need_proxy", features.get("target_any_ai", 0)) or 0)
    security = float(features.get("security_concern_index", 0) or 0)
    readiness = float(features.get("deployment_readiness_index", 0) or 0)
    if readiness >= 60 and security <= 18:
        mode = "API_or_SaaS"
        rationale = "readiness is high and security friction is manageable"
    elif security >= 20 and readiness >= 40:
        mode = "hybrid"
        rationale = "security is meaningful, but internal readiness supports a mixed rollout"
    elif security >= 20:
        mode = "local"
        rationale = "security pressure dominates the decision"
    elif efficiency >= 15:
        mode = "SaaS"
        rationale = "high efficiency demand benefits from faster external adoption"
    else:
        mode = "API"
        rationale = "moderate readiness and moderate constraints favor incremental integration"
    return {
        "status": "ok",
        "recommended_mode": mode,
        "rationale": rationale,
        "inputs": {
            "efficiency_need_proxy": efficiency,
            "security_concern_index": security,
            "deployment_readiness_index": readiness,
        },
        "evidence_files": evidence_payload(
            [
                "09_Agent训练规划/项目总结与Agent训练路线.md",
                "outputs/reports/stage2_large_model_results.md",
            ]
        ),
    }


if __name__ == "__main__":
    sample = {"efficiency_need_proxy": 18, "security_concern_index": 12, "deployment_readiness_index": 68}
    print(write_jsonable(time_call(recommend_deployment, sample)))
