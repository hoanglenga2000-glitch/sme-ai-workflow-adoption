# 企业 AI 部署偏好与治理机制研究

Enterprise AI Deployment Preferences and Governance Mechanisms: a reproducible machine learning coursework case built on official enterprise ICT data.

本仓库是明日课堂展示使用的公开版机器学习案例。它保留课程展示、公开数据、复现代码、结果表、图表、Agent 原型和提交材料；投稿论文、问卷/访谈私密材料、期刊定稿包和模型二进制不进入公开仓库。

## Research Scope

本项目把课程中的数据挖掘与机器学习流程落到真实公开数据：数据获取、生命周期治理、清洗、特征工程、建模、解释、可视化与复现实验。

研究主线是企业 AI 部署偏好与治理机制。中小企业是重要样本场景，但不是全部研究边界。Stage 1 用企业规模组数据解释 SME 机制，Stage 2 用行业/区域数据做外部验证。

## Locked Public Metrics

| Layer | Role | Data shape | Model | Main validation result |
|---|---|---:|---|---:|
| Stage 1 | SME mechanism interpretation | 553 panel rows, 544 modeling rows, 36 geo groups, 2021, 2023-2025 | Ridge | GroupKFold R2=0.8680, MAE=1.8342 |
| Stage 2 | Industry / region external validation | 5,814 modeling rows, 36 geo groups, 50 industries, 2021, 2023-2025 | ExtraTrees | Long-run GroupKFold R2=0.7245, MAE=1.9646 |

Source data chain:

`12,770,332 raw official rows -> 12,341,630 scanned rows -> 856,880 feature-filtered rows -> 5,814 modeling-panel rows`

Correct wording: the project does not directly train on ten-million-level samples. The official source rows are profiled, filtered, and aggregated into reproducible modeling panels.

## Repository Structure

| Path | Purpose |
|---|---|
| `01_源数据` | Public mirror of verified official source files and manifests. |
| `02_清洗后数据` | Processed Stage 1 / Stage 2 modeling panels. |
| `03_清洗与训练代码` | Course mirror of acquisition, cleaning, modeling, diagnostics, and figure scripts. |
| `04_分析结果表格` | Public result tables and reports. |
| `05_学术图表` | Public course figures and visual material. |
| `06_结课报告` | Course report material. |
| `07_PPT正式版`, `08_Research_Grade_Deck`, `11_PPT最终核验版` | Historical presentation versions. |
| `12_机械学习完整案例展示PPT` | Final public presentation package for tomorrow's display. |
| `data/` | Standard reproducibility data path. |
| `src/` | Standard reproducibility code path. |
| `outputs/` | Standard reproducibility results path. |
| `10_Agent系统` | Research Agent prototype, evaluation reports, and tests. |
| `提交材料` | Classroom submission material. |

## Run The Core Pipeline

```bash
python src/acquisition/download_sources.py
python src/pipeline.py
python src/pipeline_multisource.py
python src/acquisition/download_stage2_large_sources.py
python src/pipeline_stage2_large.py
python src/enhanced_training_gpu.py
python src/course_ml_diagnostics.py
python src/render_academic_figures.py
python src/build_academic_image_brief.py
python src/build_course_report_docx.py
python -m unittest discover -s "10_Agent系统/tests" -p "test_*.py"
```

The historical A10 GPU run is retained as a training log and deep-learning baseline only. The current public display uses the locked GroupKFold metrics above.

## Why This Fits The Course

The case covers a complete machine learning workflow:

1. Official source acquisition with manifests and SHA256 hashes.
2. Data cleaning, profiling, filtering, aggregation, and leakage control.
3. Supervised learning with interpretable tabular models.
4. GroupKFold validation by country to reduce geographic leakage.
5. Feature importance and mechanism interpretation.
6. Agent prototype that answers with evidence constraints instead of unsupported claims.
7. A clean GitHub evidence base that separates public coursework artifacts from private manuscript material.

## Boundaries

Do not describe Stage 2 as SME-only. Do not write that machine learning proves causality. Do not describe questionnaire material as a per-sample raw database. Questionnaire and interview evidence are private auxiliary materials, not the public repository's main evidence base.

The public GitHub repository intentionally excludes `.joblib`, `.pkl`, `.env`, private submission packages, questionnaire/interview records, tokens, passwords, SSH keys, and server credentials.
