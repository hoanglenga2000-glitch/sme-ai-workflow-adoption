# Stage 2 Large-Scale Data Mining Results

Official stage-2 source rows profiled: 12,770,332; non-null observations: 10,453,354; source files: 17.

Rows scanned in feature extraction: 12,341,630; rows kept after indicator filtering: 856,880.

Integrated GE10 industry panel rows: 5,814; modeling rows: 5,814; features after coverage/leakage control: 66.

## Model Metrics

Best model: `extra_trees`.

- ridge: R2=0.746, MAE=1.919, n_test=1454
- random_forest: R2=0.801, MAE=1.642, n_test=1454
- extra_trees: R2=0.833, MAE=1.457, n_test=1454
- hist_gradient_boosting: R2=0.823, MAE=1.561, n_test=1454

## Top Features

| feature                     |   importance_mean |   importance_std |
|:----------------------------|------------------:|-----------------:|
| ai_industry__E_AI_TML       |            0.4381 |           0.0235 |
| ai_industry__E_AI_TNLG      |            0.0851 |           0.0051 |
| geo                         |            0.0445 |           0.0037 |
| ai_industry__E_AI_CC        |            0.0171 |           0.0018 |
| digital_foundation_index    |            0.0132 |           0.0015 |
| nace_r2                     |            0.0076 |           0.0011 |
| year                        |            0.0075 |           0.0012 |
| ai_industry__E_AI_CC1SI_DA  |            0.007  |           0.0012 |
| deployment_readiness_index  |            0.0048 |           0.0008 |
| ai_industry__E_AI_DA        |            0.0046 |           0.0007 |
| isoc_cicce_usen2__E_CC_PDEV |            0.0038 |           0.0004 |
| isoc_cicce_usen2__E_CC1_S   |            0.0032 |           0.0005 |
| isoc_ec_eseln2__E_AWSFOR    |            0.003  |           0.0004 |
| ai_industry__E_AI_PITS      |            0.003  |           0.0007 |
| isoc_cicce_usen2__E_CC1_SI  |            0.0029 |           0.0004 |
| isoc_e_diin2__E_DI3_VHI     |            0.0029 |           0.0004 |
| isoc_ec_eseln2__E_AWS_CMP   |            0.0021 |           0.0002 |
| isoc_ec_eseln2__E_AESELL    |            0.002  |           0.0004 |
| isoc_e_diin2__E_DI4_VHI     |            0.0019 |           0.0004 |
| isoc_cicce_usen2__E_CC      |            0.0017 |           0.0002 |

## SME Persona Clusters

|   persona_cluster |   target_workflow_automation |   security_concern_index |   deployment_readiness_index |   data_maturity_index |   digital_foundation_index |   market_digitization_index |   ict_constraint_index |   governance_maturity_proxy |    n |
|------------------:|-----------------------------:|-------------------------:|-----------------------------:|----------------------:|---------------------------:|----------------------------:|-----------------------:|----------------------------:|-----:|
|                 2 |                        17.18 |                    15.37 |                        68.96 |                 57.79 |                      55.46 |                       34.61 |                  29.7  |                       42.21 |  659 |
|                 4 |                        11.93 |                    17.05 |                        60.23 |                nan    |                      53.4  |                       34.93 |                  40.9  |                       15.97 |  290 |
|                 5 |                         4.98 |                    14.31 |                        49.85 |                 40.74 |                      37.38 |                       30.09 |                  25.31 |                       29.84 | 1828 |
|                 1 |                         4.4  |                    14.4  |                        48.48 |                 47.11 |                      46.24 |                       59.86 |                  21.84 |                       25.85 |  527 |
|                 0 |                         4.21 |                    15.08 |                        36.73 |                 43.31 |                      39.45 |                       31.48 |                  16.27 |                        9.29 |  774 |
|                 3 |                         2.04 |                    13.13 |                        29.07 |                 33.14 |                      19.24 |                       28.27 |                  27.09 |                       17.56 | 1736 |
