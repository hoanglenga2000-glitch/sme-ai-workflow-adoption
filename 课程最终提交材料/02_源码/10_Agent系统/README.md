# SME AI Workflow Adoption Research Agent

This directory turns the existing research repo into a reproducible agent system with:

- tabular model training built on verified Stage 1 and Stage 2 datasets
- low-token agent tools that query structured data instead of stuffing tables into prompts
- evidence-first retrieval over verified research artifacts
- evaluation scripts for accuracy, citation quality, latency, and token budget proxies

## Design principles

1. Keep prediction in tabular models, not in the LLM.
2. Keep evidence in indexed files, not in model weights.
3. Keep agent outputs structured and source-linked.
4. Use the A10 GPU only where it helps: optional deep tabular baselines, embedding/index builds, and batch inference.

## Layout

```text
10_Agent系统/
  configs/
  training/
  agent_tools/
  rag/
  api/
  web_demo/
  evaluation/
  reports/
  tests/
```

## Quick start

Run the enhanced training pipeline:

```bash
python 10_Agent系统/training/train_models.py
python 10_Agent系统/training/evaluate_models.py
python 10_Agent系统/training/train_champion.py
```

On the A10 server, use `--force` to rerun model training before champion selection:

```bash
python 10_Agent系统/training/train_champion.py --force
```

Build the lightweight evidence index:

```bash
python 10_Agent系统/rag/build_index.py
python 10_Agent系统/rag/evaluate_rag.py
```

Run validation:

```bash
python -m unittest discover -s 10_Agent系统/tests -p "test_*.py"
python 10_Agent系统/evaluation/evaluate_agent.py
```

Start the API after installing dependencies:

```bash
uvicorn 10_Agent系统.api.app:app --host 0.0.0.0 --port 8000
```

Start the academic demo:

```bash
streamlit run 10_Agent系统/web_demo/streamlit_app.py
```

## Outputs

- `reports/model_metrics.json`: machine-readable model metrics
- `reports/model_comparison_report.md`: human-readable model comparison
- `reports/agent_evaluation_report.md`: agent-side evaluation summary
- `reports/model_registry.json`: champion model metadata, hashes, manifest audit, and runtime snapshot
- `reports/agent_quality_eval.json`: curated academic agent quality evaluation
- `rag/evidence_index.json`: verified retrieval index
- `training/artifacts/*.joblib`: saved model bundles

## A10 usage

`train_ft_transformer.py` is intentionally optional. If `torch` is available on the A10 server, it will run a GPU-backed deep tabular baseline. If not, the main pipeline still completes with high-quality tree models.

For a clean A10 setup:

```bash
bash 10_Agent系统/scripts/a10_bootstrap.sh
```

The bootstrap script installs dependencies, records NVIDIA/CUDA status, and runs manifest hash auditing before training.

## Security

- never write GitHub tokens, SSH passwords, or private keys into this directory
- keep secrets in environment variables or the server runtime only
- all evidence returned by tools must map to real files in this repository
