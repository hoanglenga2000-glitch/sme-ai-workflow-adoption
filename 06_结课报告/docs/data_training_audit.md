# Data And Training Audit

## Research Topic

SME AI workflow automation adoption mechanism: empirical analysis of efficiency demand, security concern, and deployment preference.

## Data Authenticity

The final training data are derived from official Eurostat SDMX-CSV sources. The repository stores reproducible metadata and processed modeling panels:

- `data/raw/manifest.jsonl`
- `data/raw/manifest_stage2.jsonl`
- `data/processed/eurostat_multisource_panel.csv`
- `data/processed/stage2_industry_panel.csv`

The verified raw Eurostat files are stored in GitHub under `data/raw/eurostat/` and `data/raw/eurostat_stage2/`, with SHA256 values recorded in the manifests. The processed modeling panels are also committed for classroom review and reruns.

Primary source verification references:

- Eurostat SDMX2.1 API guide: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines/sdmx2-1/data-query
- Eurostat `isoc_eb_ai` Data Browser page: https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table?lang=en
- Eurostat `isoc_eb_ain2` Data Browser page: https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ain2/default/table?lang=en
- NIST AI RMF 1.0 governance reference: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- scikit-learn GroupKFold method reference: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html

## Empirical Layers

| Layer | Purpose | Unit | Modeling rows | Main use |
|---|---|---|---:|---|
| Stage 1 | SME mechanism modeling | country-year-size class | 544 | SME-specific claims |
| Stage 2 | External validation | country-year-NACE GE10 industry | 5,814 | industry/region validation |

Stage 2 must not be described as SME-size-specific evidence because its industry tables use `GE10`. It strengthens external validity rather than replacing Stage 1.

## Large-Scale Source Profile

The Stage 2 extraction uses 17 official Eurostat source files:

- Raw source rows profiled: 12,770,332
- Non-null observations profiled: 10,453,354
- Rows retained after indicator filtering: 856,880
- Integrated GE10 industry/region panel: 5,814 rows x 80 columns

This is a data-mining pipeline: raw official tables are verified, profiled, filtered by theoretically relevant indicators, aggregated into panel features, and then used for supervised learning and interpretation.

## Enhanced Training Results

The enhanced pipeline uses country-group cross-validation to avoid overly optimistic random splits.

| Dataset | Best model | Validation | R2 | MAE |
|---|---|---|---:|---:|
| Stage 1 SME size class | RandomForest | GroupKFold by geo | 0.850 | 1.790 |
| Stage 2 GE10 validation | ExtraTrees | GroupKFold by geo | 0.724 | 1.967 |

The A10 GPU was used for a PyTorch MLP baseline:

| Dataset | Device | Split | R2 | MAE |
|---|---|---|---:|---:|
| Stage 1 SME size class | NVIDIA A10 / CUDA | country-group holdout | 0.806 | 2.523 |
| Stage 2 GE10 validation | NVIDIA A10 / CUDA | country-group holdout | 0.662 | 2.529 |

Interpretation: the GPU neural baseline confirms that the project used the A10 server, while tree and linear tabular models generalize better under group validation. This is a defensible research finding for structured enterprise panel data.

## Leakage Control

The enhanced script excludes:

- direct target fields such as `E_AI_TPA`
- aggregate AI adoption fields such as `E_AI_TANY`
- ever-considered AI fields such as `E_AI_EC`
- target-derived variables containing `target`, `workflow_gap`, `adoption_gap` or `gap_vs_any_ai`

This produces more conservative and more defensible metrics than the earlier random-holdout report.

## Key Files

- `src/enhanced_training_gpu.py`
- `src/render_academic_figures.py`
- `src/pipeline_stage2_large.py`
- `src/build_academic_image_brief.py`
- `src/build_course_report_docx.py`
- `outputs/reports/enhanced_training_report.md`
- `outputs/reports/stage2_source_profile.md`
- `outputs/tables/enhanced_cv_results.csv`
- `outputs/tables/enhanced_gpu_baseline.csv`
- `outputs/tables/enhanced_permutation_importance.csv`
- `outputs/figures/academic/fig1a_model_comparison_ppt.png`
- `outputs/figures/academic/fig1b_sme_importance_ppt.png`
- `outputs/figures/academic/fig1c_gpu_baseline_ppt.png`
