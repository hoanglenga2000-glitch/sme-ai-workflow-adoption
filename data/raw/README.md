# Raw Data Notice

本目录不上传大体积 Eurostat 官方原始下载文件。公开仓库保留：

- `data/processed/`：清洗后的建模面板；
- `data/samples/`：轻量样本数据；
- `data_sources.md`：数据来源说明；
- `src/acquisition/`：重新下载官方数据的脚本。

如需复现原始数据获取过程，请运行：

```bash
python src/acquisition/download_sources.py
python src/acquisition/download_stage2_large_sources.py
```

原始文件体积较大，结课 GitHub 展示版不随仓库提交。
