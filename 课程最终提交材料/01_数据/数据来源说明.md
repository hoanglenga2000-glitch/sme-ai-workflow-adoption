# Data Sources And Provenance

本文件记录数据来源、下载 URL、下载时间、文件哈希、用途与限制。所有来源均要求可追溯，禁止伪造数据。

## Primary Official Data

### Eurostat - ICT usage and e-commerce in enterprises / AI technologies

- API base: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/
- SDMX API base used by this project: https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/
- Main dataset code: `isoc_eb_ai`, Artificial intelligence by size class of enterprise.
- Use: 主实证数据。用于构造中小企业 AI 流程自动化采纳、效率需求、安全顾虑、部署准备度与数字基础变量。
- Integrity: all successful Eurostat files are recorded in `data/raw/manifest.jsonl` and `data/raw/manifest_stage2.jsonl` with URL, timestamp, bytes and SHA256.

### U.S. Census Bureau - Business Trends and Outlook Survey (BTOS)

- Source page: https://www.census.gov/data/experimental-data-products/business-trends-and-outlook-survey.html
- Intended use: potential supplementary validation for U.S. business AI adoption.
- Actual status: server-side requests returned HTTP 403. The failed records are kept in the manifest for transparency but are not used in training, charts, or conclusions.
- Integrity rule: failed HTML or 403 responses must never be treated as data.

## Governance / Lifecycle Framework

### NIST AI Risk Management Framework

- Source: https://www.nist.gov/itl/ai-risk-management-framework
- Use: 支撑安全顾虑、治理实践和数字生命周期解释，不作为训练样本。

## Auxiliary Data

### Kaggle Global AI Adoption & Workforce Impact Dataset

- Source: https://www.kaggle.com/datasets/mohankrishnathalla/global-ai-adoption-and-workforce-impact-dataset
- Use: 背景参考，不作为当前最终模型的训练样本。

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

- Eurostat SDMX2.1 API data-query guide: https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines/sdmx2-1/data-query
- Eurostat Data Browser, `isoc_eb_ai` Artificial intelligence by size class of enterprise: https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ai/default/table?lang=en
- Eurostat API endpoint, `isoc_eb_ai`: https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_eb_ai?format=SDMX-CSV
- Eurostat Data Browser, `isoc_eb_ain2` Artificial intelligence by NACE Rev. 2 activity: https://ec.europa.eu/eurostat/databrowser/view/isoc_eb_ain2/default/table?lang=en
- Eurostat API endpoint: https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_eb_ai?format=SDMX-CSV
- Eurostat Statistics Explained PDF on enterprise AI use: https://ec.europa.eu/eurostat/statistics-explained/SEPDF/cache/106920.pdf
- scikit-learn `GroupKFold` documentation: https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html
- NIST AI RMF landing page: https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF 1.0 publication: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- Nature final artwork guidance, used as figure-production quality reference: https://www.nature.com/nature/for-authors/final-submission


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

Each file is downloaded by `src/acquisition/download_sources.py`; `data/raw/manifest.jsonl` records URL, title, HTTP status, bytes, SHA256 and timestamp. For classroom review, the verified raw Eurostat files are also committed under `data/raw/` and mirrored under `01_源数据/`.


## Stage 2 Large-Scale Official Sources

Stage 2 adds 17 compressed Eurostat SDMX-CSV datasets. The download script is `src/acquisition/download_stage2_large_sources.py`; the profiling script is `src/cleaning/profile_stage2_sources.py`; the modeling script is `src/pipeline_stage2_large.py`.

The stage-2 source profile is stored in `outputs/reports/stage2_source_profile.md` and records 12,770,332 source rows with 10,453,354 non-null observations. Each downloaded raw file is recorded in `data/raw/manifest_stage2.jsonl` with URL, timestamp, byte size, and SHA256. The same source files are stored in GitHub under `data/raw/eurostat_stage2/` and mirrored under `01_源数据/data/raw/eurostat_stage2/`.

Important data semantics: industry-level AI datasets use `GE10` (enterprises with 10 persons employed or more). They are used for industry and regional validation. SME size-specific conclusions come from the size-class Eurostat datasets in stage 1.
