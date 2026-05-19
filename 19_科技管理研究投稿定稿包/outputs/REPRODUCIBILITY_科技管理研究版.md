# 复现说明

## 环境
建议使用Python 3.10+，依赖pandas、numpy、matplotlib、scikit-learn、python-docx、openpyxl。本包不依赖A10服务器，CPU即可复现投稿材料。

## 一键生成投稿包
```bash
python 19_科技管理研究投稿定稿包/build_journal_submission_package.py
```

## 事实源
- `10_Agent系统/reports/final_research_registry_summary.json`
- `14_CPU研究增强包/outputs/cpu_research_upgrade_summary.json`
- `16_论文级实证增强包/outputs/*.csv`
- `17_投稿级研究完善包/tables/*.csv`
- `data/processed/eurostat_ai_panel.csv`
- `data/processed/stage2_industry_panel.csv`

## 安全边界
不提交`.joblib`、`.pkl`、`.env`、token、密码或服务器登录信息。A10相关内容仅作为历史训练记录，不作为当前投稿复现依赖。
