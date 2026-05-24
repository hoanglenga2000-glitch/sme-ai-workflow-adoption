# A10 Validation Summary

Validation date: 2026-05-19

Environment:
- Host: [REDACTED]
- GPU: NVIDIA A10, 23028 MiB, driver 580.126.09
- Runtime: historical GPU environment; internal host paths are not included in the public submission.
- Python: 3.10.12
- Optuna: 4.8.0, ready for A10 sweeps

Champion:
- Stage: stage2
- Model: extra_trees
- Historical A10 academic score is not used as the final public display metric.
- Final public GroupKFold R2 mean: 0.7245
- GroupKFold MAE mean: 1.9646
- Time holdout R2: 0.7019150547187023
- Industry holdout R2: 0.9521096639989431
- Leakage audit: passed
- Manifest hash audit: passed

Agent evaluation:
- Case count: 6
- Tool success rate: 1.0
- Citation accuracy proxy: 1.0
- Hallucination rate: 0.0
- Average latency: 0.0603 seconds

Verification:
- `training/train_champion.py --force`: passed
- `rag/build_index.py`: passed
- `evaluation/evaluate_agent.py`: passed
- `python -m unittest discover -s tests -p "test_*.py"`: 8 tests passed
- `python -m compileall -q`: passed

Security:
- No GitHub token, SSH password, or server credential is stored in project files.
