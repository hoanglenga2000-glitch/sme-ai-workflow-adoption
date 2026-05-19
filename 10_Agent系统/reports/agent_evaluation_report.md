# Agent Evaluation Report

This report summarizes the model-side and agent-side evaluation contract.

## stage1
- best_model: `ridge`
- group_kfold_r2_mean: 0.8680
- group_kfold_mae_mean: 1.8342
- time_holdout_r2: 0.9312
- token strategy: return features, metrics, and evidence file paths only; never inject raw tables into prompts.
- hallucination guard: no evidence means `无法确认`.

## stage2
- best_model: `extra_trees`
- group_kfold_r2_mean: 0.7137
- group_kfold_mae_mean: 2.0525
- time_holdout_r2: 0.7019
- industry_holdout_r2: 0.9521
- token strategy: return features, metrics, and evidence file paths only; never inject raw tables into prompts.
- hallucination guard: no evidence means `无法确认`.

## Agent Metrics Contract
- numeric_accuracy: values must match source CSV/JSON exactly
- citation_accuracy: every claim must point to repository files
- tool_success_rate: tools must return schema-valid JSON
- token_budget_proxy: no tool returns more than 20 rows or 5 evidence chunks
- latency_targets_seconds: indicator query <= 2, prediction <= 3, chart render <= 6

