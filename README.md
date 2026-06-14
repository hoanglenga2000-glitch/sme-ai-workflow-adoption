# 企业 AI 部署偏好与治理机制研究

机器学习课程结课 GitHub 展示仓库  
学生：南京工业大学｜信管2301｜景浩伟｜202321054012

本仓库是课程结课提交使用的公开版材料，已经按“最终展示内容”整理：保留最终提交 PDF/PPT、复现代码、必要数据面板、结果表、图表和 Agent 原型；删除历史 PPT 版本、构建预览图、大体积原始下载文件、缓存文件和重复副本。

## 提交入口

老师检查时优先看：

| 路径 | 内容 |
|---|---|
| `课程最终提交材料/01_数据` | processed、samples、raw manifest、模型结果表、报告和图表。 |
| `课程最终提交材料/02_源码` | 数据下载、清洗、建模、图表生成、Agent 原型、测试和复现说明。 |
| `课程最终提交材料/03_小组汇报PPT和报告` | 小组最终 PPT/PDF、证据映射、预览总览图、16 页最终课程报告 DOCX/PDF。 |
| `课程最终提交材料/04_个人作业总结` | 平时作业汇总、个人任务报告、第一次到第十次个人作业 PDF。 |
| `课程最终提交材料/提交说明与质量核验.md` | 页数、字体颜色、目录完整性、AI痕迹词、研究口径和测试结果核验。 |

## 项目复现材料

| 路径 | 内容 |
|---|---|
| `src/` | 数据下载、清洗、建模、诊断和图表生成代码。 |
| `configs/` | 默认实验配置。 |
| `notebooks/` | 快速演示 Notebook。 |
| `data/processed/` | 清洗后的建模面板。 |
| `data/samples/` | 轻量样本数据，便于快速查看结构。 |
| `data/raw/` | 原始数据说明和 manifest。大体积官方下载文件不随仓库上传。 |
| `outputs/tables/` | 模型指标、回归结果、VIF、特征重要性等结果表。 |
| `outputs/reports/` | 数据质量、训练结果和复现实验报告。 |
| `outputs/figures/` | 报告与 PPT 使用的核心图表。 |
| `10_Agent系统/` | 研究 Agent 原型、RAG 索引、评估报告和测试。 |

## 研究主题

本项目把机器学习课程中的数据挖掘流程落到公开企业 ICT 数据：数据获取、清洗、特征工程、建模、解释、可视化与复现实验。研究主线是“企业 AI 部署偏好与治理机制”，中小企业是重点解释场景，行业/区域面板用于外部验证。

## 核心结果

| 层次 | 作用 | 数据形态 | 模型 | 验证结果 |
|---|---|---:|---|---:|
| Stage 1 | SME 机制解释 | 553 panel rows, 544 modeling rows, 36 geo groups | Ridge | GroupKFold R2=0.8680, MAE=1.8342 |
| Stage 2 | 行业/区域外部验证 | 5,814 modeling rows, 36 geo groups, 50 industries | ExtraTrees | GroupKFold R2=0.7245, MAE=1.9646 |

说明：项目不直接在千万级样本上训练模型。官方源数据经过扫描、筛选、聚合后形成可复现建模面板。Stage 2 使用 GE10 行业/区域口径，不写成 SME-only 结论。

## 快速运行

```bash
pip install -r requirements.txt
python src/pipeline.py
python src/pipeline_multisource.py
python src/pipeline_stage2_large.py
python src/course_ml_diagnostics.py
python src/render_academic_figures.py
python -m unittest discover -s "10_Agent系统/tests" -p "test_*.py"
```

如需重新下载官方原始数据，可运行 `src/acquisition/download_sources.py` 和 `src/acquisition/download_stage2_large_sources.py`。原始下载文件体积较大，公开仓库只保留清洗后数据、样本数据和来源说明。

## 公开边界

仓库不包含 `.env`、API key、模型二进制、私密问卷/访谈材料、投稿论文定稿包或本地缓存。结论表述不写“机器学习证明因果”，Stage 2 不表述为 SME-only。
