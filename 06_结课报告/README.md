# 结课报告说明

本目录保存机器学习课程结课报告相关材料。公开展示口径以仓库根目录 `README.md`、`DATA_CARD.md`、`MODEL_CARD.md` 和 `12_机械学习完整案例展示PPT` 为准。

## 课程案例主题

企业 AI 部署偏好与治理机制研究：效率需求、安全顾虑与部署准备度的混合证据分析。

中小企业是 Stage 1 的重要样本场景；Stage 2 是行业/区域外部验证层，不应写成 SME-only。

## 核心事实

- Stage 1：553 行面板，544 行可建模样本，36 个 geo，Ridge，GroupKFold R2=0.8680，MAE=1.8342。
- Stage 2：5,814 行建模面板，36 个 geo，50 个行业，ExtraTrees，长跑 GroupKFold R2=0.7245，MAE=1.9646。
- 源数据链：12,770,332 行官方源数据 -> 12,341,630 行程序扫描 -> 856,880 行特征过滤 -> 5,814 行建模面板。

## 推荐复现入口

```bash
python src/acquisition/download_sources.py
python src/pipeline.py
python src/acquisition/download_stage2_large_sources.py
python src/pipeline_stage2_large.py
python -m unittest discover -s "10_Agent系统/tests" -p "test_*.py"
```

历史 A10 GPU 基线可作为课程训练日志和模型对照，不作为当前公开展示的主结果。
