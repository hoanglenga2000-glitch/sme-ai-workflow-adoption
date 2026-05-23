# 企业AI部署偏好与治理机制研究

Enterprise AI Deployment Preferences and Governance Mechanisms: Mixed Evidence on Efficiency Needs, Security Concerns, and Deployment Readiness

研究主题：企业 AI 部署偏好与治理机制研究：效率需求、安全顾虑与部署准备度的混合证据分析。中小企业是重要样本场景，不是全部研究边界。

本项目将课程中的数据挖掘与机器学习流程落到真实公开数据：数据获取、生命周期治理、清洗、特征工程、建模、解释、可视化与复现实验。当前最终口径以本地 CPU 可复现结果为准；A10 GPU 服务器仅作为历史加速与深度学习基线记录，不再作为复现依赖。GitHub 仓库保存源数据、清洗后数据、代码、数据来源、元数据、哈希、结果表格、学术图表和结课复现材料；投稿论文、补充材料和期刊定稿包暂时保留在本地私密区，不进入公开仓库。

## 核心研究问题

1. 企业 AI 部署偏好如何受到效率需求、安全顾虑与部署准备度共同影响？
2. 安全顾虑如何塑造本地化、人工确认、权限分级和日志审计等治理型部署偏好？
3. Stage 1 企业规模组机制解释层与 Stage 2 行业/区域外部验证层是否表现出一致机制？
4. 国家、行业、企业规模和数字基础如何形成异质性？

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



## Final Research Position (2026-05-19)

The current public repository is a reproducible research and coursework evidence base. Journal-oriented manuscripts and submission packages are maintained privately outside this public repository. Publicly shareable locked facts are:

- Current private journal target: management / digital transformation journal style, with `现代管理科学` as the preferred working target.
- Stage 1, SME mechanism interpretation layer: 553 panel rows, 544 modeling rows, 36 geo groups, 2021-2025.
- Stage 1 champion model: Ridge, country-level GroupKFold R2=0.8680, MAE=1.8342.
- Stage 2, industry / region external validation layer: 5,814 modeling rows, 36 geo groups, 50 industries, 2021-2025.
- Stage 2 champion model: ExtraTrees, country-level GroupKFold R2=0.7245 (long-run 500 trees x 3 seeds), MAE=1.9646.
- Stage 2 source scale: 17 verified Eurostat official files, 12,770,332 raw source rows, 856,880 feature-filtered rows, aggregated into a 5,814-row modeling panel.
- Agent validation: 54 evaluation cases, tool success 1.0, citation proxy 1.0, hallucination rate 0.0.
- Important wording rule: do not write that tens of millions of rows were directly trained. The accurate statement is that official source rows were filtered and aggregated into modeling panels.
- Important scope rule: Stage 2 is an industry / region external validation layer, not an SME-only sample.

## Why This Fits The Course

The project follows a complete data mining lifecycle: source verification, acquisition manifest, data cleaning, feature construction, supervised learning, clustering, interpretation, visualization, and deployment-strategy translation. The target variable is not a generic AI score; it is the official Eurostat indicator for enterprises using AI to automate workflows or assist decision making, which directly matches the research topic.


## Historical Multi-Source Run (2026-05-18)

The current main result uses 10 verified Eurostat official datasets: AI adoption, cloud computing, digital intensity, data analytics, big data, e-commerce sales, e-commerce value, ICT specialists, ICT training, and ICT recruitment constraints.

- Verified raw official data: 10 successful Eurostat API files, about 39.5 MB raw CSV.
- Feature-selected long-form observations: 134,367.
- Integrated country-year-size panel rows: 2,323.
- Supervised modeling rows: 544.
- Predictors after leakage control: 67.
- Leakage-control rule: the model excludes the target `E_AI_TPA`, direct aggregate AI adoption `E_AI_TANY`, ever-considered AI `E_AI_EC`, and target-derived gap/interaction variables from the supervised feature set.
- Best leakage-controlled model: Ridge regression, R2=0.889, MAE=1.636 percentage points.

This run is retained as a historical intermediate result. For journal-style writing, use the locked Stage 1 / Stage 2 results listed in this README and the private manuscript workspace, not historical intermediate scores.


## Historical Stage 2 Large-Scale Data Mining Run (2026-05-18)

The upgraded research run adds 17 larger official Eurostat datasets covering industry, regional, structural business statistics, and high-growth enterprise dimensions. The compressed raw stage-2 files are committed under `data/raw/eurostat_stage2/` and mirrored under `01_源数据/` for classroom verification.

- Stage-2 official source files: 17.
- Profiled source rows: 12,770,332.
- Non-null observations: 10,453,354.
- Rows scanned for feature extraction: 12,341,630.
- Rows retained after indicator filtering: 856,880.
- Integrated GE10 industry panel rows: 5,814.
- Modeling rows: 5,814.
- Leakage-controlled feature count: 66.
- Earlier random/less strict validation reported ExtraTreesRegressor R2=0.833, MAE=1.457 percentage points.

Interpretation note: stage-2 industry tables use `GE10` rather than SME size splits, so they complement rather than replace the SME size-class model. The final report presents Stage 1 as SME mechanism interpretation and Stage 2 as industry / region external validation.

## Historical A10 GPU Training Run (2026-05-18)

The enhanced run adds stricter validation and academic-style figures:

- Leakage-controlled feature selection excludes direct target fields and target-derived gap variables.
- Country-group 5-fold cross-validation is used to test cross-country generalization.
- A PyTorch MLP baseline is trained on the NVIDIA A10 GPU and evaluated with country-group holdout.
- Academic figures are rendered with `SciencePlots`/matplotlib style and exported as PNG + SVG.

Main enhanced results:

- Stage 1 SME size-class layer: best GroupKFold model = RandomForest, mean R²=0.850, MAE=1.790.
- Stage 2 GE10 industry/region validation layer: best GroupKFold model = ExtraTrees, mean R²=0.724, MAE=1.967.
- A10 GPU MLP baseline under country-group holdout: Stage 1 R²=0.806, Stage 2 R²=0.662.

These A10 results are retained as historical training logs only. The A10 server is no longer required, and the final reproducible results are the CPU-first journal package results listed above.

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
The A10 server is not a current dependency. GitHub includes verified raw Eurostat files and processed modeling panels so teachers, reviewers, or collaborators can inspect the public evidence chain directly. Journal manuscripts, submission drafts, supplementary materials, and private target-journal adaptation files are intentionally kept outside the public repository until the author decides otherwise.
