# Model Results: SME AI Workflow Automation Adoption

Data source: Eurostat `isoc_eb_ai`, official API SDMX-CSV. Filtered long-form observations: 28,519; panel rows: 553; modeling rows: 544.

Latest year: 2025. Target: `E_AI_TPA`, percentage of enterprises using AI technologies automating workflows or assisting decision making.

## Data Mining And Digital Lifecycle

- Acquisition: official API download, timestamp and SHA256 manifest.
- Cleaning: SDMX data normalized to long and panel forms.
- Feature engineering: efficiency proxy, security concern index, deployment readiness index, governance maturity proxy, interaction term `security_x_efficiency`.
- Modeling: Ridge, Random Forest, HistGradientBoosting regression; KMeans persona clustering.
- Evaluation: R2, MAE, permutation importance; all result tables exported.
- Deployment/governance: outputs support SaaS/API/local/hybrid deployment recommendations and NIST-style risk feedback.

## Model Metrics

Best model: `ridge`.

- ridge: R2=0.912, MAE=1.458, n_test=136

- random_forest: R2=0.836, MAE=1.722, n_test=136

- hist_gradient_boosting: R2=0.797, MAE=1.826, n_test=136

## Top Predictive Factors

| feature                    |   importance_mean |   importance_std |
|:---------------------------|------------------:|-----------------:|
| E_AI_TML                   |            0.4493 |           0.0483 |
| target_any_ai              |            0.3808 |           0.0477 |
| geo                        |            0.0839 |           0.0125 |
| deployment_readiness_index |            0.0252 |           0.0056 |
| E_AI_BLEG                  |            0.024  |           0.0063 |
| security_concern_index     |            0.0204 |           0.0054 |
| security_x_efficiency      |            0.02   |           0.0062 |
| E_AI_CC                    |            0.0174 |           0.0058 |
| E_AI_TNLG                  |            0.0169 |           0.0062 |
| governance_maturity_proxy  |            0.0088 |           0.0038 |
| size_emp                   |            0.0039 |           0.0019 |
| E_AI_BCDP                  |            0.0034 |           0.0022 |

## EU Latest Size-Class Snapshot

| size_emp   |   target_workflow_automation |   target_any_ai |   security_concern_index |   deployment_readiness_index |   governance_maturity_proxy |   adoption_gap_vs_any_ai |
|:-----------|-----------------------------:|----------------:|-------------------------:|-----------------------------:|----------------------------:|-------------------------:|
| 10-249     |                         4.8  |           18.99 |                    15.76 |                        12.69 |                        7.98 |                    14.19 |
| 10-49      |                         4.15 |           17.1  |                    15.57 |                        10.85 |                        6.49 |                    12.94 |
| 50-249     |                         8.68 |           30.4  |                    17.22 |                        23.74 |                       14.45 |                    21.72 |
| GE250      |                        24.44 |           55.06 |                    18.78 |                        49.65 |                       33.28 |                    30.63 |

## SME Persona Clusters

|   persona_cluster |   target_workflow_automation |   target_any_ai |   security_concern_index |   deployment_readiness_index |   governance_maturity_proxy |   E_AI_BLE |   E_AI_BCST |   n |
|------------------:|-----------------------------:|----------------:|-------------------------:|-----------------------------:|----------------------------:|-----------:|------------:|----:|
|                 3 |                        14.66 |           39.89 |                    17.13 |                        31.81 |                       16.21 |      29.48 |       11.73 |  21 |
|                 2 |                         7.85 |           22.95 |                    14.58 |                        16.36 |                       11.9  |      24.32 |       11.33 |  86 |
|                 1 |                         3.48 |           10.81 |                    16.13 |                         7.93 |                       16.09 |      21.49 |       19.44 |  77 |
|                 0 |                         2.61 |            7.86 |                    12.64 |                         5.42 |                        8.49 |      18.8  |       14.88 | 225 |

## Chart Data Files

- `outputs/figures/01_eu_ai_adoption_trends.csv`

- `outputs/figures/02_sme_workflow_automation_country_rank.csv`

- `outputs/figures/03_size_lifecycle_heatmap_data.csv`

- `outputs/figures/04_model_feature_importance_data.csv`

- `outputs/figures/05_sme_persona_clusters_data.csv`
