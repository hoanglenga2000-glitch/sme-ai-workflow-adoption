"""Create a Chinese, submission-friendly mirror of the research project files.

The canonical pipeline still lives in ``data/``, ``src/`` and ``outputs/`` so
the code can run normally. This script copies the same real files into clearly
named Chinese folders for course review:

01_源数据 -> downloaded official Eurostat raw data and manifests
02_清洗后数据 -> processed modeling panels and samples
03_清洗与训练代码 -> acquisition, cleaning, training, diagnostics scripts
04_分析结果表格 -> model metrics, audits, coefficients, feature importance
05_学术图表 -> PNG/SVG academic figures
06_结课报告 -> markdown/docx reports
"""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TARGETS = {
    "01_源数据": [
        "data/raw/manifest.jsonl",
        "data/raw/manifest_stage2.jsonl",
        "data/raw/eurostat",
        "data/raw/eurostat_stage2",
    ],
    "02_清洗后数据": [
        "data/processed",
        "data/samples",
    ],
    "03_清洗与训练代码": [
        "src/acquisition",
        "src/cleaning",
        "src/pipeline.py",
        "src/pipeline_multisource.py",
        "src/pipeline_stage2_large.py",
        "src/enhanced_training_gpu.py",
        "src/course_ml_diagnostics.py",
        "src/render_academic_figures.py",
        "src/render_svg_charts.py",
        "src/build_academic_image_brief.py",
        "src/build_course_report_docx.py",
    ],
    "04_分析结果表格": [
        "outputs/tables",
        "outputs/reports",
    ],
    "05_学术图表": [
        "outputs/figures",
    ],
    "06_结课报告": [
        "docs",
        "README.md",
        "data_sources.md",
    ],
}


def copy_item(src: Path, dest_root: Path) -> None:
    if not src.exists():
        return
    rel = src.relative_to(ROOT)
    dest = dest_root / rel
    if src.is_dir():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def main() -> None:
    for folder, items in TARGETS.items():
        out = ROOT / folder
        preserved_files: list[tuple[str, bytes]] = []
        preserved_dirs: list[tuple[str, Path]] = []
        if folder == "06_结课报告" and out.exists():
            for pattern in ["*.docx", "*.pdf"]:
                for existing in out.glob(pattern):
                    preserved_files.append((existing.name, existing.read_bytes()))
        if folder == "05_学术图表" and out.exists():
            brief = out / "汇报图片稿_4K待审核"
            if brief.exists():
                tmp = ROOT / ".tmp_preserve_汇报图片稿_4K待审核"
                if tmp.exists():
                    shutil.rmtree(tmp)
                shutil.copytree(brief, tmp)
                preserved_dirs.append(("汇报图片稿_4K待审核", tmp))
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True, exist_ok=True)
        for item in items:
            copy_item(ROOT / item, out)
        for name, data in preserved_files:
            (out / name).write_bytes(data)
        for name, tmp in preserved_dirs:
            dest = out / name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(tmp, dest)
            shutil.rmtree(tmp)

    readme = ROOT / "中文目录说明.md"
    readme.write_text(
        "# 中文提交目录说明\n\n"
        "本仓库保留英文工程目录以保证代码可运行，同时提供中文目录便于课程提交和教师检查。\n\n"
        "| 中文目录 | 内容 |\n"
        "|---|---|\n"
        "| `01_源数据` | Eurostat 官方 SDMX-CSV 原始下载文件、压缩源文件、manifest 来源校验记录。 |\n"
        "| `02_清洗后数据` | 清洗、整合后的建模面板和抽样预览数据。 |\n"
        "| `03_清洗与训练代码` | 数据下载、清洗、特征工程、A10 GPU 训练、课程诊断、图表生成代码。 |\n"
        "| `04_分析结果表格` | 数据质量审计、交叉验证、GPU 基线、OLS、VIF、特征重要性等结果表。 |\n"
        "| `05_学术图表` | PNG/SVG 学术图表，供报告和PPT图片稿使用。 |\n"
        "| `06_结课报告` | 数据来源说明、训练审计、研究质量说明和最终结课报告。 |\n\n"
        "注意：`Stage 1 SME规模层` 用于中小企业规模组机制解释；`Stage 2 GE10行业/区域层` 用于外部验证，不表述为SME规模拆分。\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
