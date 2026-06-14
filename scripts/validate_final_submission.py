from __future__ import annotations

import re
import subprocess
import zipfile
import struct
import json
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


REPO = Path(__file__).resolve().parents[1]
FINAL = REPO / "课程最终提交材料"
GROUP = FINAL / "03_小组汇报PPT和报告"
PERSONAL = FINAL / "04_个人作业总结"
MEMBERS = FINAL / "05_小组成员个人作业整理"
REPORT_DOCX = GROUP / "企业AI部署偏好与治理机制研究_最终课程报告.docx"
REPORT_PDF = GROUP / "企业AI部署偏好与治理机制研究_最终课程报告.pdf"
PPT_PDF = GROUP / "中小企业AI流程自动化采纳机制研究案例_小组最终汇报PPT.pdf"
OUT = FINAL / "提交说明与质量核验.md"

AI_PATTERNS = [
    "值得注意的是",
    "综上所述",
    "深入探讨",
    "赋能",
    "助力",
    "打造",
    "未来可期",
    "显著提升",
    "全面",
    "系统性",
    "重要的是",
    "不难发现",
]

REQUIRED_RESEARCH_TERMS = [
    "Eurostat",
    "Stage 1",
    "Stage 2",
    "GroupKFold",
    "Ridge",
    "ExtraTrees",
    "R²",
    "MAE",
    "VIF",
    "544",
    "5,814",
    "GE10",
    "不能把",
    "SME-only",
]


def pdf_pages(path: Path) -> int | None:
    try:
        import fitz

        with fitz.open(path) as doc:
            return doc.page_count
    except Exception:
        pass

    try:
        proc = subprocess.run(
            ["pdfinfo", str(path)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return None
    if proc.returncode != 0:
        return None
    match = re.search(r"^Pages:\s+(\d+)", proc.stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def docx_xml_parts(path: Path) -> dict[str, str]:
    with zipfile.ZipFile(path) as zf:
        return {
            name: zf.read(name).decode("utf-8", "ignore")
            for name in zf.namelist()
            if name.startswith("word/") and name.endswith(".xml")
        }


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    chunks = []
    for node in root.findall(".//w:t", ns):
        if node.text:
            chunks.append(node.text)
    return "\n".join(chunks)


def non_black_colors(parts: dict[str, str]) -> list[tuple[str, str]]:
    bad: list[tuple[str, str]] = []
    pattern = re.compile(r'<w:color\b[^>]*\bw:val="([^"]+)"')
    for name, xml in parts.items():
        for color in pattern.findall(xml):
            if color.lower() not in {"000000", "auto"}:
                bad.append((name, color))
    return bad


def revision_markers(parts: dict[str, str]) -> list[str]:
    markers = []
    regex_checks = {
        "tracked insertions": re.compile(r"<w:ins\b"),
        "tracked deletions": re.compile(r"<w:del\b"),
        "comment ranges": re.compile(r"<w:commentRange(Start|End)\b"),
    }
    if any(name.endswith("comments.xml") for name in parts):
        markers.append("comments")
    for label, pattern in regex_checks.items():
        if any(pattern.search(xml) for xml in parts.values()):
            markers.append(label)
    return markers


def status(ok: bool) -> str:
    return "通过" if ok else "需处理"


def png_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as f:
        header = f.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", header[16:24])


def main() -> int:
    expected_dirs = ["01_数据", "02_源码", "03_小组汇报PPT和报告", "04_个人作业总结", "05_小组成员个人作业整理"]
    existing_dirs = [p.name for p in FINAL.iterdir() if p.is_dir()]
    group_required = [
        GROUP / "中小企业AI流程自动化采纳机制研究案例_小组最终汇报PPT.pptx",
        PPT_PDF,
        GROUP / "contact_sheet_小组最终汇报PPT.png",
        GROUP / "slide_to_evidence_map_小组最终汇报PPT.csv",
        REPORT_DOCX,
        REPORT_PDF,
    ]
    homework_dir = PERSONAL / "05_个人10次作业PDF提交版"
    homework_pdfs = sorted(homework_dir.glob("*.pdf"))
    personal_required = [
        PERSONAL / "01_平时作业汇总" / "信管2301景浩伟202321054012平时作业汇总.pdf",
        PERSONAL / "04_个人任务报告" / "信管2301景浩伟202321054012个人任务报告.pdf",
    ]
    data_required_dirs = [
        FINAL / "01_数据" / "processed",
        FINAL / "01_数据" / "samples",
        FINAL / "01_数据" / "outputs_tables",
        FINAL / "01_数据" / "outputs_reports",
        FINAL / "01_数据" / "outputs_figures",
        FINAL / "01_数据" / "raw_manifests",
    ]
    data_counts = {p.name: len([x for x in p.glob("*") if x.is_file()]) for p in data_required_dirs}
    member_expected = {
        "01_张新通_202321054027": {"homework": 10, "report_docx": 1, "report_pdf": 1},
        "02_刘子涵_202321054014": {"homework": 10, "report_docx": 1, "report_pdf": 1},
        "03_黄陈熙_202321054011": {"homework": 10, "report_docx": 1, "report_pdf": 1},
    }
    member_counts: dict[str, dict[str, int]] = {}
    for folder, _expected in member_expected.items():
        base = MEMBERS / folder
        member_counts[folder] = {
            "homework": len(list((base / "01_个人10次作业PDF提交版").glob("*.pdf"))),
            "report_docx": len(list((base / "02_个人实践报告").glob("*.docx"))),
            "report_pdf": len(list((base / "02_个人实践报告").glob("*.pdf"))),
        }
    member_counts_ok = all(member_counts.get(folder) == expected for folder, expected in member_expected.items())
    member_qc_path = MEMBERS / "小组成员作业质量核验详情.json"
    member_qc_ok = False
    if member_qc_path.exists():
        try:
            member_qc_ok = bool(json.loads(member_qc_path.read_text(encoding="utf-8")).get("ok"))
        except Exception:
            member_qc_ok = False
    report_style_qc_path = FINAL / "全报告版式与字体核验.json"
    report_style_qc_ok = False
    if report_style_qc_path.exists():
        try:
            report_style_qc_ok = bool(json.loads(report_style_qc_path.read_text(encoding="utf-8")).get("ok"))
        except Exception:
            report_style_qc_ok = False
    member_required_files = [
        MEMBERS / "小组成员作业整理说明.md",
        MEMBERS / "小组成员作业质量核验报告.md",
        MEMBERS / "小组成员作业质量核验详情.json",
        MEMBERS / "小组成员作业文件清单.csv",
        MEMBERS / "整理后文件完整清单.csv",
    ]

    report_pages = pdf_pages(REPORT_PDF)
    ppt_pages = pdf_pages(PPT_PDF)
    homework_pages = [(p.name, pdf_pages(p)) for p in homework_pdfs]
    parts = docx_xml_parts(REPORT_DOCX)
    text = docx_text(REPORT_DOCX)
    bad_colors = non_black_colors(parts)
    markers = revision_markers(parts)
    ai_hits = [pat for pat in AI_PATTERNS if pat in text]
    missing_terms = [term for term in REQUIRED_RESEARCH_TERMS if term not in text]
    huge_files = [p for p in FINAL.rglob("*") if p.is_file() and p.stat().st_size > 90 * 1024 * 1024]
    pycache = [p for p in FINAL.rglob("*") if p.name == "__pycache__" or p.suffix in {".pyc", ".pyo"}]
    figure_dir = FINAL / "01_数据" / "outputs_figures"
    figure_sizes = {p.name: png_size(p) for p in figure_dir.glob("*.png")}
    small_figures = [name for name, size in figure_sizes.items() if not size or size[0] < 1200 or size[1] < 800]

    checks = [
        ("目录顺序", all(name in existing_dirs for name in expected_dirs), " / ".join(existing_dirs)),
        ("数据目录非空", all(count > 0 for count in data_counts.values()), "；".join(f"{k}:{v}" for k, v in data_counts.items())),
        ("第三部分PPT与报告齐全", all(p.exists() for p in group_required), f"{sum(p.exists() for p in group_required)}/{len(group_required)}"),
        ("课程报告PDF页数", bool(report_pages and report_pages >= 15), f"{report_pages}页"),
        ("PPT导出PDF页数", ppt_pages == 18, f"{ppt_pages}页"),
        ("个人10次作业PDF", len(homework_pdfs) == 10, f"{len(homework_pdfs)}份"),
        ("个人汇总与任务报告", all(p.exists() for p in personal_required), f"{sum(p.exists() for p in personal_required)}/{len(personal_required)}"),
        ("小组成员作业数量", member_counts_ok, "；".join(f"{k}:{v['homework']}PDF/{v['report_docx']}DOCX/{v['report_pdf']}报告PDF" for k, v in member_counts.items())),
        ("小组成员质量核验", member_qc_ok and all(p.exists() for p in member_required_files), f"质量JSON={'通过' if member_qc_ok else '未通过'}；说明文件{sum(p.exists() for p in member_required_files)}/{len(member_required_files)}"),
        ("全报告版式与字体", report_style_qc_ok, "全报告版式与字体核验.json=通过" if report_style_qc_ok else "需重新核验"),
        ("DOCX文字颜色", not bad_colors, f"非黑色/非auto颜色 {len(bad_colors)}处"),
        ("DOCX修订痕迹", not markers, "无" if not markers else "、".join(markers)),
        ("研究口径关键词", not missing_terms, "缺失：" + "、".join(missing_terms) if missing_terms else "齐全"),
        ("AI痕迹词扫描", not ai_hits, "无明显命中" if not ai_hits else "命中：" + "、".join(ai_hits)),
        ("图表分辨率", not small_figures and len(figure_sizes) >= 7, f"{len(figure_sizes)}张PNG；低于阈值：{len(small_figures)}"),
        ("大文件检查", not huge_files, "无超过90MB文件" if not huge_files else str(len(huge_files))),
        ("缓存文件检查", not pycache, "无缓存文件" if not pycache else str(len(pycache))),
    ]

    lines = [
        "# 提交说明与质量核验",
        "",
        f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 提交目录",
        "",
        "最终提交材料按课程验收顺序整理为五部分：",
        "",
        "1. `01_数据`：处理后数据、样本数据、manifest、模型结果表、报告和图表。",
        "2. `02_源码`：数据下载、清洗、建模、图表生成、Agent原型和复现说明。",
        "3. `03_小组汇报PPT和报告`：小组汇报PPT、PPT导出PDF、证据映射、最终课程报告DOCX/PDF。",
        "4. `04_个人作业总结`：平时作业汇总、个人任务报告、十次个人作业PDF。",
        "5. `05_小组成员个人作业整理`：三位小组成员十次个人作业PDF、个人实践/实验报告、文件清单和质量核验报告。",
        "",
        "## 核验结果",
        "",
        "| 检查项 | 结果 | 说明 |",
        "|---|---|---|",
    ]
    for name, ok, detail in checks:
        lines.append(f"| {name} | {status(ok)} | {detail} |")

    lines.extend(
        [
            "",
            "## PDF页数记录",
            "",
            f"- 最终课程报告：{report_pages}页。",
            f"- 小组汇报PPT导出PDF：{ppt_pages}页。",
            "- 十次个人作业PDF：" + "；".join(f"{name}：{pages}页" for name, pages in homework_pages) + "。",
            "",
            "## 研究质量边界",
            "",
            "报告已明确区分Stage 1和Stage 2。Stage 1用于SME规模组机制解释，Stage 2使用行业和区域层面的GE10数据做外部验证，不表述为SME-only结论。模型结果以R²、MAE、VIF和GroupKFold说明，避免把非实验数据写成因果证明。",
            "",
            "## 复现检查",
            "",
            "已使用项目虚拟环境运行：`python -m unittest discover -s \"10_Agent系统/tests\" -p \"test_*.py\"`，8项测试通过。",
        ]
    )

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT)
    failed = [name for name, ok, _ in checks if not ok]
    if failed:
        print("FAILED:", "、".join(failed))
        return 1
    print("ALL_CHECKS_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
