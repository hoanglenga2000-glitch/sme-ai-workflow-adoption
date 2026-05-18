# 中小企业 AI 流程自动化采纳机制研究：项目总结与 Agent 训练路线

> 当前文档用于承接下一阶段工作：在已有真实数据、清洗代码、模型结果、学术图表和答辩 PPT 的基础上，继续利用 A10 GPU 服务器构建一个可查询、可解释、可复现实验的研究型 AI Agent。

## 1. 项目当前状态

本项目围绕“基于中小企业 AI 流程自动化采纳机制研究：效率需求、安全顾虑与部署偏好的实证分析”展开，目标不是单纯做一个 PPT，而是形成一套可复现的数据挖掘案例：

- 研究问题：中小企业在什么条件下更可能采纳 AI 流程自动化工具？
- 核心机制：效率需求、数据/安全顾虑、部署准备度共同影响 AI 自动化采纳。
- 课程关联：特征提取、数据清洗、因子构造、多元回归、随机森林、ExtraTrees、MLP 深度学习基线、交叉验证、特征重要性、客户画像聚类。
- 数字生命周期：数据采集 → 哈希校验 → 清洗整合 → 特征工程 → 机器学习建模 → 可解释分析 → 部署策略建议 → 产品落地。

目前仓库已经推送到 GitHub：

- 仓库地址：https://github.com/hoanglenga2000-glitch/sme-ai-workflow-adoption.git
- 最近一次已知提交：`ef5d98f Add research-grade academic defense deck`
- 注意：GitHub token、服务器密码等敏感信息不能写入仓库或文档。后续连接仓库应使用 `gh auth login`、环境变量 `GITHUB_TOKEN`、GitHub Actions Secrets 或服务器本地 `.env`。

## 2. 已完成的主要任务

### 2.1 数据获取与来源整理

已建立源数据目录和数据来源说明，重点使用 Eurostat 官方统计数据，保证数据真实、可查询、可复现。

主要目录：

- `01_源数据/`：镜像保存的原始数据与 manifest。
- `data/raw/`：标准源数据目录。
- `data/raw/manifest.jsonl`：Stage 1 数据下载与哈希校验记录。
- `data/raw/manifest_stage2.jsonl`：Stage 2 大规模数据下载与哈希校验记录。
- `docs/data_sources.md`、`data_sources.md`：数据来源说明。

已验证结果：

- Stage 1 manifest：14 条记录，其中 10 个成功下载文件完成哈希校验，未发现 hash 错误。
- Stage 2 manifest：17 个压缩源文件全部完成哈希校验，未发现 hash 错误。
- Stage 2 官方源数据总行数：12,770,332 行。
- Stage 2 非空观测值：10,453,354 条。
- 机制相关过滤后保留观测：856,880 条。

### 2.2 数据清洗、特征工程与模型训练

已建立清洗与训练代码：

- `src/pipeline.py`
- `src/pipeline_multisource.py`
- `src/pipeline_stage2_large.py`
- `src/cleaning/profile_stage2_sources.py`
- `03_清洗与训练代码/` 中保存了课程提交用代码副本。

已生成清洗后数据：

- `02_清洗后数据/`
- `data/processed/`
- `data/samples/`

关键建模样本：

- Stage 1：544 行，36 个国家/地区，偏 SME size-class 机制分析，适合做“中小企业机制层”解释。
- Stage 2：5,814 行，36 个国家/地区，50 个 NACE 行业，用于 GE10 行业/区域外部验证。注意：Stage 2 不是 SME size split，不能把 Stage 2 结论直接说成 SME 专属结论。

### 2.3 已完成模型与指标

当前严格核验指标来自 `08_Research_Grade_Deck/verified_metrics.json`：

| 模型/阶段 | 验证方式 | R2 | MAE | 解释 |
|---|---:|---:|---:|---|
| Stage 1 Random Forest | 国家组留出/GroupKFold 思路 | 0.8495 | 1.7900 | 对 SME 采纳机制的预测解释力较强 |
| Stage 2 ExtraTrees | 行业/国家外部验证 | 0.7238 | 1.9671 | 在更大范围官方统计数据上仍有较强泛化 |
| Stage 1 GPU MLP | A10 加速深度学习基线 | 0.8060 | 未列入主表 | 深度学习能跑通，但没有超过树模型 |
| Stage 2 GPU MLP | A10 加速深度学习基线 | 0.6621 | 未列入主表 | 结构化统计数据上 MLP 不是最优解 |

重要解释：

- 树模型优于 MLP，并不说明 GPU 没价值，而是说明当前数据是典型结构化表格统计数据，Random Forest、ExtraTrees、HistGradientBoosting 等模型更适合。
- A10 GPU 的价值应放在深度学习基线、FT-Transformer/TabTransformer 对比实验、嵌入构建、批量特征检索、超参数搜索和 Agent 服务推理加速上，而不是盲目训练大语言模型。
- Stage 1 与 Stage 2 的边界必须清楚：Stage 1 支撑 SME 机制解释，Stage 2 支撑跨行业/跨国家的外部验证。

### 2.4 图表、报告与 PPT 资产

已完成学术图表、课程报告和研究型答辩 PPT。

主要目录：

- `05_学术图表/`：数据挖掘图表、SVG/PNG 图。
- `06_结课报告/`：Word/PDF 课程报告。
- `07_PPT正式版/`：上一版正式 PPT。
- `08_Research_Grade_Deck/`：研究级重构 PPT。

最新研究级 PPT 文件：

- `08_Research_Grade_Deck/中小企业AI流程自动化采纳机制研究_Research_Grade_学术答辩版.pptx`
- `08_Research_Grade_Deck/中小企业AI流程自动化采纳机制研究_Research_Grade_学术答辩版.pdf`
- `08_Research_Grade_Deck/revision_report.md`
- `08_Research_Grade_Deck/speaker_notes/slide_by_slide_speaker_notes.md`

已完成质量检查：

- 15 页 PPT 全部完成非空渲染检查。
- 已导出 PDF 和 Office PNG 预览图。
- 布局 QA 检查结果：0 errors，0 warnings。

## 3. 当前研究结论的可靠边界

本项目现在可以严谨表达以下结论：

1. AI 流程自动化采纳不是单纯技术问题，而是效率收益、安全风险和部署准备度之间的组织决策问题。
2. 在 SME 机制层数据中，机器学习能力、数字基础、部署准备度等变量对 AI 自动化采纳具有重要解释力。
3. 在更大规模 Eurostat 行业/区域官方数据中，树模型仍能保持较好泛化，说明模型捕捉到的是跨国家、跨行业的结构性机制，而不是简单记忆样本。
4. GPU MLP 能作为深度学习课程基线，但在当前结构化官方统计数据上不是最优模型。
5. SaaS、API、本地化、混合部署不应被看作单纯技术偏好，而应被解释为企业在效率需求、安全顾虑和治理成熟度之间权衡后的结果。

不能过度表达的内容：

- 不能说 Stage 2 是“中小企业专属样本”，因为 Stage 2 是 GE10 行业/区域外部验证层。
- 不能说模型已经代表所有中国中小企业，因为主要公开数据来自 Eurostat，问卷数据与国内产品场景应作为机制映射和案例落地，而不是无限外推。
- 不能把 1000 多万原始行数直接等同于训练样本数。严谨说法是：官方源数据扫描 12,770,332 行，经指标过滤、面板整合、缺失控制和泄漏控制后，形成 5,814 行严格建模样本。

## 4. 是否建议使用简单 Transformer 框架训练 Agent？

结论：不建议把 1000 多万条表格统计数据直接拿去训练一个 Transformer 大模型。更推荐“表格机器学习模型 + 检索增强 RAG + 工具调用 Agent”的组合。

原因如下：

1. 当前数据主要是官方统计表格，不是自然语言语料。直接训练 Transformer 语言模型会浪费 token、成本高，而且不一定提高预测准确率。
2. 已有结果表明，Random Forest、ExtraTrees 等树模型在结构化数据上优于 GPU MLP。下一步应优先加强表格模型，而不是盲目微调大语言模型。
3. 研究要求强调数据真实性和可解释性。Agent 应该通过工具查询真实数据、调用模型预测、引用来源和生成图表，而不是把数据“记忆”在模型参数里。
4. 低成本高准确率的路线是：让 LLM 负责理解问题和组织回答，让可复现代码负责取数、预测、解释和画图。

推荐架构：

```text
真实数据源
  ↓
数据湖 / 原始数据区
  ↓
清洗数据 / 特征仓库
  ↓
表格模型注册表
  ↓
检索索引与来源文档
  ↓
工具调用型 Research Agent
  ↓
报告生成 / 图表生成 / 部署策略推荐
```

如果要使用 Transformer，建议只用于以下场景：

- 自然语言问答界面：理解老师或用户提出的问题。
- RAG 检索：从数据来源说明、模型报告、PPT 讲稿、论文段落中检索证据。
- 小规模 LoRA/指令微调：基于已验证结果构造“问题 → 工具调用 → 有来源答案”的训练样本。
- Tabular Transformer 对比实验：例如 FT-Transformer、TabTransformer，作为课程深度学习拓展基线，而不是替代所有树模型。

## 5. 下一阶段 Agent 的目标

建议把下一阶段定义为“SME AI Workflow Adoption Research Agent”，即一个面向本研究的可复现实验 Agent，而不是聊天机器人。

Agent 应具备以下能力：

1. 数据来源审计：回答每个数据来自哪里、是否哈希校验、对应哪个文件。
2. 指标查询：按国家、行业、年份、指标查询清洗后的统计数据。
3. 模型预测：输入企业/行业画像，预测 AI 自动化采纳强度或部署倾向。
4. 可解释分析：输出关键变量贡献、特征重要性、回归系数解释。
5. 图表生成：根据查询结果生成学术图表。
6. 部署建议：根据效率需求、安全顾虑、部署准备度，推荐 SaaS/API/本地化/混合部署。
7. 证据引用：每个结论尽量链接到源数据、清洗代码或模型报告。

## 6. A10 GPU 服务器的合理使用方式

A10 服务器应该用于加速以下任务：

- PyTorch MLP、FT-Transformer、TabTransformer、TabNet 等深度学习表格模型训练。
- 大规模特征矩阵处理和批量推理。
- Optuna / Ray Tune 等超参数搜索。
- 文档、报告、字段说明的 embedding 构建。
- RAG 检索索引构建。
- Agent 后端模型服务推理。

不建议用于：

- 从零训练大语言模型。
- 把 1000 多万统计表格行直接拼成 prompt。
- 把未清洗、未解释、无标签的原始表格直接拿去微调 LLM。

## 7. 推荐实验路线

### 7.1 表格预测模型增强

优先补充以下模型：

- LightGBM
- XGBoost
- CatBoost
- HistGradientBoosting
- FT-Transformer
- TabTransformer
- TabNet

验证方式：

- GroupKFold by country，避免国家层面信息泄漏。
- 时间切分验证，例如用较早年份训练、较晚年份测试。
- 行业留出验证，例如按 NACE 类别留出。
- 消融实验：分别去掉效率、安全、部署准备度变量，观察 R2/MAE 下降。
- 稳健性分析：不同缺失率阈值、不同标准化方式、不同目标变量定义下结果是否稳定。

### 7.2 Agent 检索与问答数据集

构建一个小而高质量的指令数据集，而不是追求无意义的大规模。

样本来源：

- `docs/data_sources.md`
- `outputs/reports/*.md`
- `outputs/tables/*.csv`
- `08_Research_Grade_Deck/source_notes.json`
- `08_Research_Grade_Deck/verified_metrics.json`
- Eurostat 指标说明与数据字典

样本格式建议：

```json
{
  "question": "为什么 Stage 2 不能直接说成中小企业样本？",
  "tool_calls": [
    {
      "tool": "read_metric",
      "args": {"file": "08_Research_Grade_Deck/verified_metrics.json"}
    }
  ],
  "answer": "Stage 2 是 GE10 行业/区域外部验证层，建模样本为 5,814 行、50 个 NACE 行业，不能直接解释为 SME size-class 样本。SME 专属机制解释应主要依赖 Stage 1。",
  "citations": [
    "08_Research_Grade_Deck/verified_metrics.json",
    "outputs/reports/stage2_large_model_results.md"
  ]
}
```

### 7.3 Agent 工具设计

建议实现以下工具：

- `query_indicator(country, industry, year, indicator)`：查询指标值。
- `predict_adoption(features)`：调用最佳表格模型预测采纳强度。
- `explain_prediction(features)`：返回 SHAP、Permutation Importance 或局部解释。
- `recommend_deployment(features)`：推荐 SaaS/API/本地/混合部署。
- `render_chart(query_spec)`：生成图表。
- `cite_source(claim)`：返回支持该结论的源文件、报告和数据表。
- `audit_data_file(path)`：检查文件哈希、缺失率、字段覆盖。

## 8. 准确率与 token 消耗优化

为了同时保证准确率和 token 成本，建议采用以下原则：

1. 不把大表直接塞进 prompt。所有大数据查询通过工具完成。
2. LLM 只接收小规模结构化结果，例如 Top 10 特征、模型指标、数据切片摘要。
3. 建立 feature store，让模型输入固定为结构化 JSON。
4. 对来源文档建立 embedding 索引，回答时只检索 3-5 段最相关证据。
5. 常用指标和模型结果做缓存，避免重复读取和重复推理。
6. 让 Agent 输出固定 JSON，再由报告层转成中文自然语言，减少跑偏。
7. 所有回答强制带 `evidence_files` 字段，没有证据就标记为“无法确认”。

## 9. 后续目录建议

建议下一阶段新增：

```text
10_Agent系统/
  README.md
  configs/
    agent.yaml
    model_registry.yaml
  data_index/
    source_catalog.parquet
    feature_catalog.parquet
  training/
    train_lgbm.py
    train_catboost.py
    train_ft_transformer.py
    evaluate_models.py
  agent_tools/
    query_indicator.py
    predict_adoption.py
    explain_prediction.py
    recommend_deployment.py
    cite_source.py
  rag/
    build_index.py
    evaluate_rag.py
  reports/
    agent_evaluation_report.md
    model_comparison_report.md
  tests/
    test_no_data_leakage.py
    test_citation_accuracy.py
    test_prediction_schema.py
```

## 10. 评估标准

机器学习模型评估：

- GroupKFold R2 / MAE
- 时间外推 R2 / MAE
- 行业留出 R2 / MAE
- 特征重要性稳定性
- SHAP/Permutation Importance 一致性
- 数据泄漏检查
- 缺失值敏感性分析

Agent 评估：

- 数值准确率：回答中的指标是否与 CSV/JSON 完全一致。
- 引用准确率：结论是否能追溯到真实文件。
- 幻觉率：无来源结论占比。
- 工具调用成功率：工具调用是否返回正确 schema。
- token 成本：每个问题平均输入/输出 token。
- 延迟：普通查询、模型预测、图表生成分别统计耗时。
- 稳定性：同一问题多次回答是否一致。

## 11. 安全与协作规范

必须遵守：

- 不要把 GitHub token、服务器 root 密码、SSH 私钥写入任何 Markdown、代码、日志或 commit。
- 如果 token 已经出现在聊天记录中，应视为已暴露，建议在 GitHub 后台立即 revoke 并重新生成最小权限 token。
- GitHub 连接使用 `gh auth login` 或服务器环境变量。
- 服务器连接使用本地 SSH config、密钥或安全密码管理方式。
- `.env` 必须加入 `.gitignore`。
- 训练日志可以记录模型参数和指标，但不能记录密钥。

## 12. 给下一位 Agent 的执行 Prompt

下面这段可以直接复制给下一位 Agent，让它继续完成训练系统。

```text
你现在接手一个已经建立好的研究项目：

项目名称：中小企业 AI 流程自动化采纳机制研究
GitHub 仓库：https://github.com/hoanglenga2000-glitch/sme-ai-workflow-adoption.git
核心目标：基于真实官方数据和已有清洗训练结果，构建一个可复现、可解释、低 token 成本的 SME AI Workflow Adoption Research Agent。

请严格遵守：
1. 不要编造数据，不要生成假指标。所有数据、模型结果、图表必须能追溯到仓库文件或官方来源。
2. 不要把 GitHub token、服务器密码、SSH 私钥写入任何文件或提交记录。认证使用 gh auth login、环境变量、SSH config 或 GitHub Secrets。
3. 先完整审查仓库结构，重点查看：
   - data/raw/manifest.jsonl
   - data/raw/manifest_stage2.jsonl
   - docs/data_sources.md
   - outputs/reports/stage2_source_profile.md
   - outputs/reports/stage2_large_model_results.md
   - 08_Research_Grade_Deck/verified_metrics.json
   - src/pipeline.py
   - src/pipeline_multisource.py
   - src/pipeline_stage2_large.py
4. 先验证数据真实性：
   - 检查 manifest 中的哈希记录。
   - 统计源数据行数、非空观测数、过滤后样本数。
   - 明确 Stage 1 与 Stage 2 的研究边界。
5. 不要直接把 1000 多万表格行训练成大语言模型。推荐架构是：
   表格机器学习模型 + RAG 检索 + 工具调用 Agent。
6. A10 GPU 应用于：
   - PyTorch MLP、FT-Transformer、TabTransformer、TabNet 等表格深度学习基线；
   - embedding/RAG 索引构建；
   - 超参数搜索和批量推理；
   - 不要从零训练 LLM。

请完成以下任务：

A. 新建 `10_Agent系统/` 目录，建立清晰工程结构：
   - configs/
   - training/
   - agent_tools/
   - rag/
   - reports/
   - tests/

B. 建立模型增强训练流水线：
   - 复用已有清洗后数据。
   - 训练 LightGBM、XGBoost、CatBoost、HistGradientBoosting。
   - 如果 GPU 环境可用，补充 FT-Transformer 或 TabTransformer。
   - 使用 GroupKFold by country、时间留出、行业留出验证。
   - 输出 `reports/model_comparison_report.md` 和机器可读 `model_metrics.json`。

C. 建立 Agent 工具：
   - query_indicator
   - predict_adoption
   - explain_prediction
   - recommend_deployment
   - render_chart
   - cite_source
   每个工具必须有输入/输出 schema 和测试用例。

D. 建立 RAG 检索：
   - 只索引经过验证的报告、来源说明、数据字典和模型结果。
   - 回答必须返回 evidence_files。
   - 没有证据的结论必须标记为“无法确认”。

E. 建立评估体系：
   - Agent 数值准确率
   - 引用准确率
   - 工具调用成功率
   - 幻觉率
   - 平均 token 成本
   - 平均延迟

F. 输出最终文件：
   - `10_Agent系统/README.md`
   - `10_Agent系统/reports/model_comparison_report.md`
   - `10_Agent系统/reports/agent_evaluation_report.md`
   - 可运行训练脚本
   - 可运行 Agent 工具脚本
   - 测试结果

G. 最后提交到 GitHub：
   - 先运行测试和关键脚本。
   - 检查 `git status`，不要提交临时文件、锁文件、密钥文件。
   - commit message 使用英文简洁描述。
   - push 到 main。

研究表达边界：
- Stage 1 支撑 SME 机制解释。
- Stage 2 支撑 GE10 行业/区域外部验证，不要说成 SME 专属样本。
- 树模型优于 MLP 是当前结构化官方统计数据的实证结果。
- Agent 的价值是把真实数据、模型预测、可解释分析和部署建议连接起来，而不是凭空聊天。
```

## 13. 下一步建议

下一阶段最有价值的不是“训练一个更大的模型”，而是把现有研究变成一个可信的研究型 Agent 系统：

- 预测靠表格模型。
- 解释靠 SHAP/Permutation Importance/回归系数。
- 证据靠 RAG 和文件引用。
- 汇报靠自动图表与结构化报告生成。
- 产品落地连接 `ai.zhjjq.tech`，体现 AI 工作站如何根据企业画像给出部署策略。

这样既能体现机器学习课程的模型训练与数据挖掘要求，也能体现数字生命周期、真实数据治理、企业部署价值和 A10 GPU 的合理使用。
