# Reproducibility

Suggested CPU-first checks:

```bash
python src/acquisition/download_sources.py
python src/pipeline.py
python src/acquisition/download_stage2_large_sources.py
python src/pipeline_stage2_large.py
python src/evaluation/validate_research_quality.py
python -m unittest discover -s 10_Agent系统/tests -p "test_*.py"
```

The A10 server is historical and is not required for public reproduction.
