# Research-grade PPT revision report

## 1. 学术审稿式诊断

上一版 PPT 的数据和模型基础是真实的，但叙事仍偏“课程材料堆叠”：页面标题较多是章节名，图表旁的解释层不足，观众看到 R²、OLS 和 GPU 结果后，未必能立刻理解它们如何支撑“AI 流程自动化采纳机制”。本次重构不是简单美化，而是把每一页改成一个 research claim，并给每个图表补上 What the chart shows / Why it matters / Decision it supports。

## 2. 工具与环境核验

- 用户指定读取 `/home/oai/skills/slides/SKILL.md`：当前 Windows/Codex Desktop 环境中该路径不存在。
- 已读取并采用可用的 Presentations 插件 skill：`C:\Users\景浩伟\.codex-api-gateway\plugins\cache\openai-primary-runtime\presentations\26.430.10722\skills\presentations\SKILL.md`。
- 已按 Presentations 插件要求改用 artifact-tool slide modules 生成 PPTX，并导出 preview PNG 与 layout JSON。
- 已读取 imagegen skill，并使用 `assets/imagegen_research_visuals/prompts.jsonl` 中的统一研究风格 imagegen 视觉资产；图表和关键文字均来自 deterministic 数据脚本与可编辑 PPT 文本，不依赖图片内小字。

## 3. 数据可信度复核

- Stage 1 manifest：10 个成功源文件 SHA256 复算通过；失败状态记录 0 条，不进入训练。
- Stage 2 manifest：17 个压缩官方源文件 SHA256 复算通过。
- Stage 2 官方源画像：12,770,332 行，10,453,354 个非空观测；机制筛选保留 856,880 行。
- Stage 1 建模面板：544 行，36 个 geo，2021-2025，重复 panel key = 0。
- Stage 2 建模面板：5814 行，36 个 geo，50 个 NACE，重复 panel key = 0。

## 4. 指标口径修正

早期 `research_quality_validation.md` 中存在较宽松模型分数，本次 PPT 统一采用 `outputs/reports/enhanced_training_report.md` 的严格 GroupKFold 结果：

- Stage 1 SME size-class：RandomForest, GroupKFold by country, R²=0.850, MAE=1.790。
- Stage 2 GE10 industry/region：ExtraTrees, GroupKFold by country, R²=0.724, MAE=1.967。
- A10 GPU MLP baseline：Stage 1 R²=0.806; Stage 2 R²=0.662。

重要边界：Stage 1 是 SME 规模层机制样本；Stage 2 是 GE10 行业/区域外部验证，不作为 SME 规模分层替代。

## 5. 叙事重构

新的 claim spine：

1. AI 流程自动化采纳不是技术选择，而是组织决策。
2. 中小企业想要自动化，但受风险承受能力约束。
3. 研究问题是“什么条件下会采纳”。
4. 数据可信度来自官方来源、哈希校验和复现流程。
5. 数字生命周期把海量官方数据收敛为建模面板。
6. 机制框架是效率需求 × 安全顾虑 × 部署准备度。
7. 模型策略把解释、预测、泛化和深度学习基线分开。
8. OLS 解释机制方向，树模型负责非线性预测。
9. GroupKFold 说明模型学习跨地区机制。
10. A10 MLP 未超过树模型，说明表格学习器更适合该类官方统计。
11. 特征重要性支持机制故事。
12. 部署偏好是风险-效率权衡结果。
13. 客户画像把模型结果转为部署策略。
14. ai.zhjjq.tech 是研究落地操作层。
15. 项目贡献官方数据、机器学习、解释机制和部署策略的复现桥梁。

## 6. 视觉系统

- 白底、黑/灰文字、唯一强调色 deep academic blue `#0B1F3A`。
- 一页一个核心观点，一个主 proof object，最多三条解释。
- 禁用科技蓝渐变、3D 伪科技、随机 icon 和文字墙。
- 图表由 `scripts_render_rebuilt_charts.py` 重新渲染，风格统一且保留 `.svg` 源图。

## 7. 输出文件

- PPTX: `D:\桌面\codex\机械挖掘学习汇报\github_upload\sme-ai-workflow-adoption\08_Research_Grade_Deck\中小企业AI流程自动化采纳机制研究_Research_Grade_学术答辩版.pptx`
- PDF: `D:\桌面\codex\机械挖掘学习汇报\github_upload\sme-ai-workflow-adoption\08_Research_Grade_Deck\中小企业AI流程自动化采纳机制研究_Research_Grade_学术答辩版.pdf`
- Speaker notes: `D:\桌面\codex\机械挖掘学习汇报\github_upload\sme-ai-workflow-adoption\08_Research_Grade_Deck\speaker_notes\slide_by_slide_speaker_notes.md`
- Source notes: `D:\桌面\codex\机械挖掘学习汇报\github_upload\sme-ai-workflow-adoption\08_Research_Grade_Deck\source_notes.json`
- Verified metrics: `D:\桌面\codex\机械挖掘学习汇报\github_upload\sme-ai-workflow-adoption\08_Research_Grade_Deck\verified_metrics.json`

## 8. 参考来源

- Eurostat SDMX2.1 API guide: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines/sdmx2-1/data-query
- Eurostat Statistics Explained, Use of AI in enterprises: https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/106920.pdf
- Eurostat `isoc_eb_ai`: https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table?lang=en
- Eurostat `isoc_eb_ain2`: https://doi.org/10.2908/ISOC_EB_AIN2
- scikit-learn GroupKFold: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html
- NIST AI RMF 1.0: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10

## 9. QA verification

- Presentations artifact-tool export succeeded: 15 slides, PPTX bytes recorded in `artifact_build_manifest.json`.
- `check_layout_quality.mjs` on all `layout_json/*.layout.json`: 0 errors, 0 warnings.
- PowerPoint COM opened the final PPTX successfully and exported the PDF preview.
- Office PNG export produced 15 slides at 1920x1080; `office_visual_qa.json` reports all slides nonblank.
- Final preview contact sheets: `contact_sheet.png` from artifact-tool and `office_contact_sheet.png` from PowerPoint.

## 10. Deliverable map

- Final PPTX: `08_Research_Grade_Deck/中小企业AI流程自动化采纳机制研究_Research_Grade_学术答辩版.pptx`
- PDF preview: `08_Research_Grade_Deck/中小企业AI流程自动化采纳机制研究_Research_Grade_学术答辩版.pdf`
- Speaker notes: `08_Research_Grade_Deck/speaker_notes/slide_by_slide_speaker_notes.md`
- Data/metric evidence: `08_Research_Grade_Deck/verified_metrics.json`, `08_Research_Grade_Deck/source_notes.json`
- Layout and visual QA: `08_Research_Grade_Deck/layout_json/`, `08_Research_Grade_Deck/office_visual_qa.json`
