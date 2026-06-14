from __future__ import annotations

import sys
import unittest
from pathlib import Path


AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent
sys.path.insert(0, str(AGENT_ROOT))

from agent_tools.predict_adoption import predict_adoption


class PredictionSchemaTest(unittest.TestCase):
    def test_prediction_output_schema(self) -> None:
        payload = predict_adoption({"geo": "DE", "year": 2025, "size_emp": "GE10", "nace_r2": "C26"})
        self.assertIn(payload["status"], {"ok", "unavailable"})
        self.assertIn("prediction", payload)
        self.assertIn("evidence_files", payload)
        if payload["status"] == "ok":
            self.assertIsInstance(payload["prediction"], float)
        else:
            self.assertIsNone(payload["prediction"])
            self.assertIn("reproduce_command", payload)


if __name__ == "__main__":
    unittest.main()
