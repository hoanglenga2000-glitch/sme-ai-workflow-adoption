from __future__ import annotations

import json
import unittest
from pathlib import Path


AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent


class NoLeakageTest(unittest.TestCase):
    def test_stage1_target_equivalents_not_in_top_features(self) -> None:
        metrics = json.loads((AGENT_ROOT / "reports" / "model_metrics.json").read_text(encoding="utf-8"))
        stage1 = next(item for item in metrics["stages"] if item["stage"] == "stage1")
        feature_names = [row["feature"] for row in stage1["models"][stage1["best_model"]]["top_features"]]
        banned = {"E_AI_TPA", "target_any_ai", "adoption_gap_vs_any_ai", "efficiency_need_proxy", "security_x_efficiency"}
        self.assertTrue(banned.isdisjoint(feature_names))

    def test_stage2_target_not_in_features(self) -> None:
        metrics = json.loads((AGENT_ROOT / "reports" / "model_metrics.json").read_text(encoding="utf-8"))
        stage2 = next(item for item in metrics["stages"] if item["stage"] == "stage2")
        for model_name, payload in stage2["models"].items():
            feature_names = [row["feature"] for row in payload["top_features"]]
            self.assertNotIn("ai_industry__E_AI_TPA", feature_names, model_name)


if __name__ == "__main__":
    unittest.main()
