# SME AI Workflow Automation Adoption Research

研究主题：基于中小企业 AI 流程自动化采纳机制研究：效率需求、安全顾虑与部署偏好的实证分析。

本项目将课程中的数据挖掘与机器学习流程落到真实公开数据：数据获取、生命周期治理、清洗、特征工程、建模、解释、可视化与复现实验。大体量原始数据保存在 A10 GPU 服务器，不直接下载到本地电脑；GitHub 仓库计划保存代码、数据来源、元数据、哈希、轻量样本和结果图表。

## 核心研究问题

1. 中小企业 AI/自动化采纳是否主要受效率压力、企业规模、行业和时间趋势影响？
2. 安全/治理能力是否会调节效率需求对 AI 功能需求强度的影响？
3. 哪些企业群体更适合云端 SaaS、API 接入、本地化部署或混合部署？
4. 从数字生命周期看，企业从识别需求、采集数据、建模决策、部署应用到治理反馈的关键风险点是什么？

## 数据源路线

- 官方主数据：U.S. Census Bureau Business Trends and Outlook Survey (BTOS) AI 相关表。
- 官方验证数据：Eurostat 企业 AI 技术使用数据，按国家、行业、规模等维度提供对照。
- 治理框架：NIST AI Risk Management Framework，用于构造治理/安全解释框架。
- 原问卷与 Kaggle 数据：仅作为辅助对照，不作为唯一证据来源。

## 运行入口

```bash
python3 src/acquisition/download_sources.py
python3 src/pipeline.py
```



## Current Verified Run (2026-05-18)

- Remote compute: A10 GPU server, Ubuntu 22.04, Python 3.10, PyTorch CUDA available.
- Verified official dataset: Eurostat `isoc_eb_ai` Artificial intelligence by size class of enterprise.
- Raw official file: `data/raw/eurostat/isoc_eb_ai_sdmx.csv` on server only, 7,143,934 bytes, SHA256 `58b0ca3c982d90449dbfe9f63900e6e485eb49db7fc53a71900d9c86e5061f20`.
- Filtered observations: 28,519 long-form rows; 553 country-year-size panel rows; 544 modeling rows.
- Best first-pass model: Ridge regression, R2=0.912, MAE=1.458 percentage points for workflow automation adoption.
- Outputs for PPT/report: `outputs/reports/model_results.md`, `outputs/tables/*.csv`, `outputs/figures/*.svg`.

## Why This Fits The Course

The project follows a complete data mining lifecycle: source verification, acquisition manifest, data cleaning, feature construction, supervised learning, clustering, interpretation, visualization, and deployment-strategy translation. The target variable is not a generic AI score; it is the official Eurostat indicator for enterprises using AI to automate workflows or assist decision making, which directly matches the research topic.


## Multi-Source Verified Run (2026-05-18)

The current main result uses 10 verified Eurostat official datasets: AI adoption, cloud computing, digital intensity, data analytics, big data, e-commerce sales, e-commerce value, ICT specialists, ICT training, and ICT recruitment constraints.

- Verified raw official data: 10 successful Eurostat API files, about 39.5 MB raw CSV.
- Feature-selected long-form observations: 134,367.
- Integrated country-year-size panel rows: 2,323.
- Supervised modeling rows: 544.
- Predictors after leakage control: 67.
- Leakage-control rule: the model excludes the target `E_AI_TPA`, direct aggregate AI adoption `E_AI_TANY`, ever-considered AI `E_AI_EC`, and target-derived gap/interaction variables from the supervised feature set.
- Best leakage-controlled model: Ridge regression, R2=0.889, MAE=1.636 percentage points.

This is the recommended version for the final course report because it is both richer and more defensible than the earlier single-table model.
