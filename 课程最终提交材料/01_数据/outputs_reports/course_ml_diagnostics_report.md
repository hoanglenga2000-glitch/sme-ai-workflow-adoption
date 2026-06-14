# Course ML Diagnostics Report

## OLS Summary
| dataset            |    n |       r2 |   adj_r2 |      aic |      bic |   features |   significant_05 |
|:-------------------|-----:|---------:|---------:|---------:|---------:|-----------:|-----------------:|
| Stage 1 SME规模层  |  544 | 0.918556 | 0.917028 |  2541.49 |  2588.78 |         10 |                3 |
| Stage 2 行业验证层 | 5814 | 0.71197  | 0.711474 | 31945.9  | 32019.3  |         10 |                6 |

## Algorithm Comparison
| dataset            | model_cn     |   r2_mean |    r2_std |   mae_mean |   train_r2_mean |   feature_count | validation            |
|:-------------------|:-------------|----------:|----------:|-----------:|----------------:|----------------:|:----------------------|
| Stage 1 SME规模层  | 多元线性回归 |  0.872915 | 0.0420702 |    1.77004 |        0.918791 |              10 | GroupKFold by country |
| Stage 1 SME规模层  | 岭回归       |  0.87435  | 0.038579  |    1.77302 |        0.918183 |              10 | GroupKFold by country |
| Stage 1 SME规模层  | 随机森林     |  0.860725 | 0.0459256 |    1.79781 |        0.965951 |              10 | GroupKFold by country |
| Stage 1 SME规模层  | ExtraTrees   |  0.862998 | 0.0561124 |    1.74246 |        0.986368 |              10 | GroupKFold by country |
| Stage 2 行业验证层 | 多元线性回归 |  0.697377 | 0.038194  |    2.1046  |        0.713152 |              10 | GroupKFold by country |
| Stage 2 行业验证层 | 岭回归       |  0.697422 | 0.0381678 |    2.10506 |        0.713152 |              10 | GroupKFold by country |
| Stage 2 行业验证层 | 随机森林     |  0.683067 | 0.0363018 |    2.14408 |        0.908042 |              10 | GroupKFold by country |
| Stage 2 行业验证层 | ExtraTrees   |  0.707334 | 0.0298398 |    2.10597 |        0.968314 |              10 | GroupKFold by country |

## Top OLS Coefficients
| dataset            | feature                    | feature_label    |   coef_std |   std_err |         t |      p_value | significant_05   | direction   |
|:-------------------|:---------------------------|:-----------------|-----------:|----------:|----------:|-------------:|:-----------------|:------------|
| Stage 1 SME规模层  | ai__E_AI_TML               | 机器学习能力     |  7.58848   | 0.280219  | 27.0805   | 3.14938e-102 | True             | positive    |
| Stage 2 行业验证层 | ai_industry__E_AI_TML      | 行业机器学习能力 |  4.19339   | 0.0802728 | 52.2392   | 0            | True             | positive    |
| Stage 2 行业验证层 | ai_industry__E_AI_TNLG     | 行业自然语言生成 |  1.2319    | 0.0780994 | 15.7735   | 6.4658e-55   | True             | positive    |
| Stage 1 SME规模层  | cloud__E_CC_PDEV           | 云开发能力       |  1.14245   | 0.20573   |  5.55314  | 4.43258e-08  | True             | positive    |
| Stage 1 SME规模层  | cloud__E_CC_DA             | 云数据分析       | -0.959787  | 0.403013  | -2.38153  | 0.0175909    | True             | negative    |
| Stage 1 SME规模层  | data_maturity_index        | 数据成熟度       |  0.553852  | 0.351084  |  1.57755  | 0.115262     | False            | positive    |
| Stage 2 行业验证层 | digital_foundation_index   | 数字基础         |  0.515099  | 0.0732515 |  7.03192  | 2.27158e-12  | True             | positive    |
| Stage 2 行业验证层 | governance_maturity_proxy  | 治理成熟度       |  0.439613  | 0.0667065 |  6.59026  | 4.77781e-11  | True             | positive    |
| Stage 1 SME规模层  | deployment_readiness_index | 部署准备度       |  0.439318  | 0.242031  |  1.81513  | 0.0700659    | False            | positive    |
| Stage 2 行业验证层 | deployment_readiness_index | 部署准备度       |  0.332153  | 0.117086  |  2.83683  | 0.00457221   | True             | positive    |
| Stage 1 SME规模层  | ai__E_AI_TNLG              | 自然语言生成     | -0.31683   | 0.204932  | -1.54602  | 0.122693     | False            | negative    |
| Stage 1 SME规模层  | digital_foundation_index   | 数字基础         |  0.141623  | 0.222111  |  0.637621 | 0.523994     | False            | positive    |
| Stage 2 行业验证层 | ict_constraint_index       | ICT人才约束      |  0.121933  | 0.0518669 |  2.35089  | 0.0187617    | True             | positive    |
| Stage 1 SME规模层  | governance_maturity_proxy  | 治理成熟度       | -0.115461  | 0.174056  | -0.663353 | 0.507391     | False            | negative    |
| Stage 2 行业验证层 | data_maturity_index        | 数据成熟度       |  0.0629472 | 0.058228  |  1.08105  | 0.279722     | False            | positive    |
| Stage 2 行业验证层 | market_digitization_index  | 市场数字化       | -0.0568277 | 0.0528442 | -1.07538  | 0.282249     | False            | negative    |

Interpretation: OLS is used for mechanism direction and significance; linear/tree models are compared with country-group cross-validation for generalization.