# Multi-Source Model Results: SME AI Workflow Automation Adoption

Verified official sources: 10 Eurostat datasets; raw bytes: 41,504,788; manifest rows including failed Census attempts: 14.

Long-form official observations after feature selection: 134,367; country-year-size panel rows: 2,323; modeling rows: 544; feature count: 67.

Latest year in integrated panel: 2025. Target remains official AI workflow automation / decision-assistance adoption (`E_AI_TPA`).

## Why This Is Stronger Than A Single Dataset

The model now connects AI adoption with cloud deployment, digital intensity, data analytics, big-data capability, e-commerce market digitization, ICT specialists, ICT training and ICT recruitment constraints. This directly operationalizes the research mechanism: efficiency demand, security concern, deployment preference, organizational digital foundation and capability constraints.

## Model Metrics

Best model: `ridge`.

- ridge: R2=0.889, MAE=1.636, n_test=136

- random_forest: R2=0.799, MAE=1.888, n_test=136

- extra_trees: R2=0.827, MAE=1.773, n_test=136

- hist_gradient_boosting: R2=0.780, MAE=1.934, n_test=136

## Top Predictive Factors

| feature                      |   importance_mean |   importance_std |
|:-----------------------------|------------------:|-----------------:|
| ai__E_AI_TML                 |            0.8754 |           0.0833 |
| security_concern_index       |            0.1256 |           0.0173 |
| geo                          |            0.0791 |           0.0143 |
| data_analytics__E_DASANY     |            0.078  |           0.013  |
| data_maturity_index          |            0.0645 |           0.0113 |
| ai__E_AI_BLEG                |            0.0582 |           0.0106 |
| data_analytics__E_DAOWN      |            0.0446 |           0.0086 |
| digital_intensity__E_DI3_VHI |            0.0243 |           0.0051 |
| cloud__E_CC_PDEV             |            0.0209 |           0.0045 |
| cloud__E_CC_DA               |            0.0199 |           0.0067 |
| data_analytics__E_DASWEB     |            0.0199 |           0.0055 |
| ai__E_AI_PITS                |            0.0138 |           0.0046 |
| market_digitization_index    |            0.0134 |           0.0054 |
| ai__E_AI_PBAM                |            0.0119 |           0.0059 |
| ecommerce_value__E_ETURN     |            0.0116 |           0.0041 |
| deployment_readiness_index   |            0.0107 |           0.0033 |
| cloud__E_CC                  |            0.0091 |           0.0046 |
| ai__E_AI_BCST                |            0.009  |           0.0033 |

## SME Persona Clusters

|   persona_cluster |   target_workflow_automation |   target_any_ai |   security_concern_index |   deployment_readiness_index |   data_maturity_index |   digital_foundation_index |   market_digitization_index |   ict_capability_index |   ict_constraint_index |   governance_maturity_proxy |   n |
|------------------:|-----------------------------:|----------------:|-------------------------:|-----------------------------:|----------------------:|---------------------------:|----------------------------:|-----------------------:|-----------------------:|----------------------------:|----:|
|                 3 |                        13.36 |           36.87 |                    17.08 |                        54.72 |                 55.95 |                      52.39 |                       38.98 |                 nan    |                 nan    |                       39.54 |  27 |
|                 4 |                         9.57 |           26.23 |                    16.79 |                        64.41 |                nan    |                      52.31 |                       40.35 |                  34.6  |                  28.99 |                       17.85 |  19 |
|                 1 |                         6.68 |           17.45 |                    12.86 |                        48.54 |                 47.4  |                      43.4  |                       38.71 |                  22.06 |                  24.02 |                       33.58 |  60 |
|                 2 |                         4.4  |           14.51 |                    15.03 |                        37.35 |                 39.93 |                      36.97 |                       35.67 |                  18.49 |                  21.6  |                       22.59 | 116 |
|                 0 |                         2.05 |            6.39 |                    13.62 |                        27.46 |                 34.83 |                      24.02 |                       32.23 |                  11.24 |                  22.2  |                       18.26 | 187 |

## Deployment Strategy Translation

- High workflow automation + high deployment readiness: prioritize API/hybrid integration and process orchestration.

- High AI interest but weak cloud/data foundation: prioritize SaaS templates and guided onboarding.

- High security/legal concern: prioritize private cloud/local deployment, audit logs, permission controls and NIST-style governance.

- ICT skill constraint cluster: prioritize low-code workflow automation and managed service support.
