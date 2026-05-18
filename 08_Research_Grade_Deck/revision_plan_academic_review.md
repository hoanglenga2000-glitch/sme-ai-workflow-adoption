# 学术审稿式诊断与重构计划

## 0. 执行前置核验
- 用户要求读取 `/home/oai/skills/slides/SKILL.md`：当前 Windows/Codex Desktop 环境不存在该路径；已改用可用的 `Presentations` 插件 skill 与本地 presentation-builder 规范。
- 当前仓库已包含官方数据、清洗数据、训练脚本、模型结果表、学术图表、Word 报告和上一版 PPT。
- 数据证据主要来自 Eurostat 官方 SDMX-CSV；BTOS 403 仅作为获取日志，不进入训练。

## 1. 对当前 PPT 的审稿式诊断
### 研究问题
- 现有 PPT 覆盖了题目，但开头更像“项目说明”，没有把核心张力先立起来。
- 新版必须用第一组页面先回答：AI workflow adoption 为什么不是技术选择，而是组织决策？

### 数据来源可信度
- 数据来源可信：Eurostat 官方 API、manifest、SHA256、清洗/训练表都存在。
- 现有 PPT 对 Stage 1/Stage 2 边界有说明，但需要更尖锐地避免误读：Stage 1 是 SME size-class mechanism layer；Stage 2 是 GE10 industry/region external validation，不是 SME 分规模替代。

### 模型指标来源
- 指标有来源：`outputs/tables/enhanced_cv_results.csv`、`enhanced_gpu_baseline.csv`、`course_ols_coefficients.csv`、`course_vif_diagnostics.csv`。
- 问题在于上一版仍较多“R² 数字展示”，解释层不足：为什么 GroupKFold 重要、为什么树模型强于 MLP、为什么特征重要性支持机制框架，需要写成结论句。

### 图表解释力
- 现有图表来自真实结果，但多页呈现为“图表 + 卡片”，更像课程展示。
- 新版每张图必须附 interpretation layer：What it shows / Why it matters / Decision supported。

### 每页 research claim
- 上一版标题多数是章节名，如“模型比较”“数据质量审计”。
- 新版标题必须是 claim，例如：`Country-group validation suggests the model learns mechanisms, not leakage.`

### 视觉质量
- 上一版可读、干净，但仍有课程模板感：顶部深色栏、右侧卡片反复出现，页面节奏不够高级。
- 新版将采用研究机构风格：白底/黑灰/一个 deep academic blue 强调色、大留白、少卡片、严格网格、少文字。

## 2. 新叙事结构
1. The real problem: AI workflow adoption is an organizational decision problem.
2. Core tension: SMEs want efficiency but fear governance and deployment risk.
3. Research question and mechanism: Efficiency × Security × Deployment Readiness.
4. Data credibility: Eurostat official data, hash validation, reproducible pipeline.
5. Data lifecycle: Collection → Cleaning → Feature Engineering → Modeling → Interpretation → Deployment.
6. Model strategy: OLS for mechanism, RF/ExtraTrees for nonlinear prediction, GroupKFold for generalization, GPU MLP as baseline.
7. Key results: GroupKFold R², OLS direction, feature importance, MLP comparison.
8. Deployment implication: SaaS/API/Local/Hybrid as risk-efficiency outcomes.
9. Product landing: ai.zhjjq.tech AI workstation operating model.
10. Contribution: official data + ML + explainable mechanism + deployment strategy.

## 3. 设计系统
- 画布：16:9，白底为主。
- 色彩：#0B1F3A deep academic blue 为唯一强调色；黑/灰作为主体。
- 字体：优先 Inter / IBM Plex Sans / Aptos / Microsoft YaHei fallback。
- 版式：一页一个核心观点，一个主视觉中心，最多三个 supporting points。
- 图表：不拉伸，按 contain/crop 保持比例；每页只有一个主 proof object。
- 禁止：随机 icon、科技蓝渐变、3D 假科技、文字墙、图表堆叠。

## 4. 新版 slide claim spine
1. AI workflow adoption is an organizational decision, not a technology checkbox.
2. SMEs face a three-way tension: efficiency gains, security risk, and deployment readiness.
3. The study asks when SMEs are likely to adopt AI workflow automation.
4. The dataset is credible because every used source is official, hashed, and reproducible.
5. The data lifecycle turns 12.77M official rows into an auditable modeling panel.
6. The mechanism framework links efficiency demand, security concern, and deployment readiness.
7. The model strategy separates explanation, prediction, generalization, and deep-learning baseline roles.
8. OLS identifies the direction of mechanisms before nonlinear models optimize prediction.
9. Country-group validation shows the model learns cross-country adoption mechanisms, not random leakage.
10. Tree models outperform the GPU MLP because structured official statistics favor tabular nonlinear learners.
11. Feature importance supports the proposed mechanism rather than a generic AI enthusiasm story.
12. Security concern redirects deployment choice from SaaS toward API, local, or hybrid architectures.
13. Customer personas convert model results into enterprise deployment decisions.
14. ai.zhjjq.tech becomes the operating layer for applying the research to real AI office workflows.
15. The project contributes a reproducible bridge from public data to deployable AI workflow strategy.

## 5. 质量门槛
- 所有最终页运行 out-of-bounds 与 overlap QA。
- 渲染 1920×1080 slide previews 与 contact sheet。
- 导出 PPTX 与 PDF，PowerPoint 必须能打开。
- 附 slide-by-slide speaker notes 与 revision report。
