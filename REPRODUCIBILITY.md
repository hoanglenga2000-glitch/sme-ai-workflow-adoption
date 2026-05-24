# Reproducibility

Suggested CPU-first checks:

```bash
python src/acquisition/download_sources.py
python src/pipeline.py
python src/acquisition/download_stage2_large_sources.py
python src/pipeline_stage2_large.py
python -m unittest discover -s "10_Agent系统/tests" -p "test_*.py"
```

Useful inspection files:

- `data/raw/manifest*.jsonl`
- `data/processed/eurostat_ai_panel.csv`
- `data/processed/stage2_industry_panel.csv`
- `outputs/reports/stage2_source_profile.json`
- `outputs/tables/enhanced_cv_results.csv`
- `outputs/tables/stage2_feature_importance.csv`
- `10_Agent系统/reports/agent_quality_eval.json`

The historical A10 run is not required for public reproduction. Public results should be read through the locked Stage 1 / Stage 2 GroupKFold metrics in `README.md`, `DATA_CARD.md`, and `MODEL_CARD.md`.
