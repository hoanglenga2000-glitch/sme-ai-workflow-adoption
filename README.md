# SME AI Workflow Automation Adoption Research

研究主题：基于中小企业 AI 流程自动化采纳机制研究：效率需求、安全顾虑与部署偏好的实证分析。

本项目将课程中的数据挖掘与机器学习流程落到真实公开数据：数据获取、生命周期治理、清洗、特征工程、建模、解释、可视化与复现实验。A10 GPU 服务器用于加速训练与核验；GitHub 仓库保存源数据、清洗后数据、代码、数据来源、元数据、哈希、结果表格、学术图表和结课报告。

## 核心研究问题

1. 中小企业 AI/自动化采纳是否主要受效率压力、企业规模、行业和时间趋势影响？
2. 安全/治理能力是否会调节效率需求对 AI 功能需求强度的影响？
3. 哪些企业群体更适合云端 SaaS、API 接入、本地化部署或混合部署？
4. 从数字生命周期看，企业从识别需求、采集数据、建模决策、部署应用到治理反馈的关键风险点是什么？

## 数据源路线

- 官方主数据：Eurostat 企业 AI 技术使用、云计算、数字强度、数据分析、电子商务、ICT技能等数据，按国家、年份、企业规模组构建 SME 机制层。
- 官方验证数据：Eurostat 行业、区域、结构性商业统计和高增长企业数据，构建 GE10 行业/区域外部验证层。
- 未采用数据：U.S. Census Bureau BTOS AI 相关表曾尝试补充，但服务器访问出现 HTTP 403，因此不作为最终训练主体。
- 治理框架：NIST AI Risk Management Framework，用于构造治理/安全解释框架。
- 原问卷与 Kaggle 数据：仅作为辅助对照，不作为最终模型的唯一证据来源。

关键可查来源包括 Eurostat SDMX2.1 API 文档、Eurostat `isoc_eb_ai` / `isoc_eb_ain2` 官方数据浏览页、NIST AI RMF 1.0、scikit-learn GroupKFold 文档和 Nature 图表规范。完整链接见 `data_sources.md`。

## 运行入口

```bash
python3 src/acquisition/download_sources.py
python3 src/pipeline.py
python3 src/pipeline_multisource.py
python3 src/acquisition/download_stage2_large_sources.py
python3 src/pipeline_stage2_large.py
python3 src/evaluation/validate_research_quality.py
python3 src/enhanced_training_gpu.py
python3 src/course_ml_diagnostics.py
python3 src/render_academic_figures.py
python3 src/build_academic_image_brief.py
python3 src/build_course_report_docx.py
python scripts/整理中文提交目录.py
```



## Current Verified Run (2026-05-18)

- Remote compute: A10 GPU server, Ubuntu 22.04, Python 3.10, PyTorch CUDA available.
- Verified official dataset: Eurostat `isoc_eb_ai` Artificial intelligence by size class of enterprise.
- Raw official file: `data/raw/eurostat/isoc_eb_ai_sdmx.csv`, 7,143,934 bytes, SHA256 `58b0ca3c982d90449dbfe9f63900e6e485eb49db7fc53a71900d9c86e5061f20`.
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


## Stage 2 Large-Scale Data Mining Run (2026-05-18)

The upgraded research run adds 17 larger official Eurostat datasets covering industry, regional, structural business statistics, and high-growth enterprise dimensions. The compressed raw stage-2 files are committed under `data/raw/eurostat_stage2/` and mirrored under `01_源数据/` for classroom verification.

- Stage-2 official source files: 17.
- Profiled source rows: 12,770,332.
- Non-null observations: 10,453,354.
- Rows scanned for feature extraction: 12,341,630.
- Rows retained after indicator filtering: 856,880.
- Integrated GE10 industry panel rows: 5,814.
- Modeling rows: 5,814.
- Leakage-controlled feature count: 66.
- Best model: ExtraTreesRegressor, R2=0.833, MAE=1.457 percentage points.

Interpretation note: stage-2 industry tables use `GE10` rather than SME size splits, so they complement rather than replace the SME size-class model. The final report should present stage 1 as SME size-class adoption modeling and stage 2 as industry/region large-scale validation.

## Enhanced Training Run With A10 GPU (2026-05-18)

The enhanced run adds stricter validation and academic-style figures:

- Leakage-controlled feature selection excludes direct target fields and target-derived gap variables.
- Country-group 5-fold cross-validation is used to test cross-country generalization.
- A PyTorch MLP baseline is trained on the NVIDIA A10 GPU and evaluated with country-group holdout.
- Academic figures are rendered with `SciencePlots`/matplotlib style and exported as PNG + SVG.

Main enhanced results:

- Stage 1 SME size-class layer: best GroupKFold model = RandomForest, mean R²=0.850, MAE=1.790.
- Stage 2 GE10 industry/region validation layer: best GroupKFold model = ExtraTrees, mean R²=0.724, MAE=1.967.
- A10 GPU MLP baseline under country-group holdout: Stage 1 R²=0.806, Stage 2 R²=0.662.

These numbers are more conservative than the earlier random holdout results and should be preferred in the final academic discussion because they better reflect external generalization.

## What Is Stored In GitHub

- `data/raw/manifest*.jsonl`: source URL, timestamp, bytes and SHA256 hashes.
- `data/raw/eurostat/` and `data/raw/eurostat_stage2/`: verified Eurostat SDMX-CSV raw files.
- `data/processed/*.csv`: processed modeling panels and persona assignments, small enough for course review.
- `data/samples/*.csv`: lightweight samples for quick inspection.
- `outputs/tables/*.csv`: model metrics, feature importance, quality audit and GPU baseline.
- `outputs/reports/*.md`: reproducible result reports.
- `outputs/figures/academic/*`: publication-style figures for PPT/report.
- `src/build_academic_image_brief.py`: 16:9 4K 汇报图片稿与配套 PNG/SVG 学术图表生成脚本。
- `src/build_course_report_docx.py`: 机器学习结课 Word 报告生成脚本。
- `01_源数据` to `06_结课报告`: Chinese submission folders separating source data, cleaned data, code, results, figures and report.

The A10 server remains the accelerated compute environment; GitHub now includes the verified raw Eurostat files used by the final training run so the teacher can inspect the source data directly.
