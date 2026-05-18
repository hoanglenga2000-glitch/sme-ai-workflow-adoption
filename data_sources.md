# Data Sources And Provenance

本文件记录数据来源、下载 URL、下载时间、文件哈希、用途与限制。所有来源均要求可追溯，禁止伪造数据。

## Primary Official Data

### U.S. Census Bureau - Business Trends and Outlook Survey (BTOS)

- Source page: https://www.census.gov/data/experimental-data-products/business-trends-and-outlook-survey.html
- Use: AI adoption, business conditions, size/sector/time variation, AI supplement/core AI questions.
- Role: 主实证数据，用于构造 AI 采纳与效率压力、规模、行业差异之间的机器学习模型。

### Eurostat - ICT usage and e-commerce in enterprises / AI technologies

- API base: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/
- Candidate dataset code: `isoc_eb_ai` or related enterprise AI datasets, subject to API metadata verification.
- Use: 国际对照，验证企业规模、行业和 AI 技术使用之间的共性关系。

## Governance / Lifecycle Framework

### NIST AI Risk Management Framework

- Source: https://www.nist.gov/itl/ai-risk-management-framework
- Use: 支撑安全顾虑、治理实践和数字生命周期解释，不作为训练样本。

## Auxiliary Data

### Kaggle Global AI Adoption & Workforce Impact Dataset

- Source: https://www.kaggle.com/datasets/mohankrishnathalla/global-ai-adoption-and-workforce-impact-dataset
- Use: 辅助参考。只有在实际通过 Kaggle API 下载并记录哈希后才进入模型。

## Download Manifest

下载脚本会自动生成 `data/raw/manifest.jsonl`，包括 URL、local path、timestamp、SHA256、size bytes、status。


## Verified Acquisition Status On A10 Server

### Eurostat `isoc_eb_ai`

- Status: downloaded successfully through official Eurostat SDMX API.
- Dataset label from API metadata: Artificial intelligence by size class of enterprise.
- URL: https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_eb_ai?format=SDMX-CSV
- Download timestamp UTC: 2026-05-18T04:04:22Z.
- Bytes: 7,143,934.
- SHA256: 58b0ca3c982d90449dbfe9f63900e6e485eb49db7fc53a71900d9c86e5061f20.
- Research role: primary real public data for training and analysis.
- Key variables: enterprise size class, country, year, AI technology type, barriers to AI use, cloud/data analytics/governance indicators, observed percentage of enterprises.

### Census BTOS AI files

- Status: server-side direct requests returned HTTP 403 and were recorded in `data/raw/manifest.jsonl`.
- Research role: high-value supplementary source, but not used in the first verified model until an allowed download path or manually supplied official file is available.
- Integrity rule: do not treat failed HTML responses as XLSX data; a failed streamed attempt was removed from raw data.

## Source Links For Report Citation

- Eurostat API endpoint: https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_eb_ai?format=SDMX-CSV
- Eurostat Statistics Explained PDF on enterprise AI use: https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/106920.pdf
- NIST AI RMF landing page: https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF 1.0 publication: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10


## Multi-Source Eurostat Data Lake

Successful official Eurostat datasets on the A10 server:

1. `isoc_eb_ai`: Artificial intelligence by size class of enterprise.
2. `isoc_cicce_use`: Cloud computing services by size class of enterprise.
3. `isoc_e_dii`: Digital Intensity by size class of enterprise.
4. `isoc_eb_das`: Data analytics by size class of enterprise.
5. `isoc_eb_bd`: Big data analysis by size class of enterprise.
6. `isoc_ec_esels`: E-commerce sales of enterprises by size class of enterprise.
7. `isoc_ec_evals`: Value of e-commerce sales by size class of enterprise.
8. `isoc_ske_itspe`: Enterprises that employ ICT specialists by size class of enterprise.
9. `isoc_ske_itts`: Enterprises that provided ICT skills training by size class of enterprise.
10. `isoc_ske_itrcrs`: Enterprises that recruited or tried to recruit ICT specialists by size class.

Each file is downloaded by `src/acquisition/download_sources.py`; `data/raw/manifest.jsonl` records URL, title, HTTP status, bytes, SHA256 and timestamp. Raw files remain on the A10 server and are excluded from git by default.
