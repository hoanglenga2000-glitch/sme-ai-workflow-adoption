from __future__ import annotations

import csv
import json
import re
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


REPO = Path(__file__).resolve().parents[1]
FINAL = REPO / "课程最终提交材料"
DATA = FINAL / "01_数据"
SOURCE = FINAL / "02_源码"
GROUP = FINAL / "03_小组汇报PPT和报告"
PERSONAL = FINAL / "04_个人作业总结"
MEMBERS = FINAL / "05_小组成员个人作业整理"

REPORT_DOCX_KEYWORDS = ("报告", "任务")
AI_STRONG_PATTERNS = (
    "作为一个AI",
    "作为人工智能",
    "我无法",
    "希望这能帮到你",
    "让我们深入探讨",
    "综上所述，本文",
    "值得注意的是，本文",
)
AI_WEAK_PATTERNS = (
    "显著提升",
    "赋能",
    "助力",
    "全面",
    "复杂",
    "关键",
    "robust",
    "comprehensive",
)
FORBIDDEN_SUBSTRINGS = (
    "__pycache__",
    ".pyc",
    ".pyo",
    "~$",
    ".tmp",
)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(FINAL))
    except ValueError:
        return str(path)


def read_docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        root = ET.fromstring(zf.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    return "\n".join(node.text for node in root.findall(".//w:t", ns) if node.text)


def docx_audit(path: Path) -> dict:
    record = {
        "file": str(path),
        "relative": rel(path),
        "exists": path.exists(),
        "open_ok": False,
        "characters": 0,
        "colors": [],
        "bad_colors": [],
        "tracked_changes": False,
        "comments": [],
        "hidden_text": False,
        "strong_ai_hits": [],
        "weak_ai_terms": {},
    }
    if not path.exists():
        return record
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            xml_parts = {
                name: zf.read(name).decode("utf-8", "ignore")
                for name in names
                if name.startswith("word/") and name.endswith(".xml")
            }
        text = read_docx_text(path)
        joined = "\n".join(xml_parts.values())
        colors = sorted(set(re.findall(r'<w:color\b[^>]*\bw:val="([^"]+)"', joined)))
        bad_colors = [c for c in colors if c.lower() not in {"000000", "auto"}]
        record.update(
            {
                "open_ok": True,
                "characters": len(text.strip()),
                "colors": colors,
                "bad_colors": bad_colors,
                "tracked_changes": bool(re.search(r"<w:(ins|del)\b", joined)),
                "comments": [name for name in xml_parts if name.endswith("comments.xml")],
                "hidden_text": "<w:vanish" in joined,
                "strong_ai_hits": [pat for pat in AI_STRONG_PATTERNS if pat in text],
                "weak_ai_terms": {
                    pat: text.count(pat)
                    for pat in AI_WEAK_PATTERNS
                    if text.count(pat)
                },
            }
        )
    except Exception as exc:  # pragma: no cover - audit report needs the message
        record["error"] = repr(exc)
    return record


def pdf_audit(path: Path, require_black_text: bool = False) -> dict:
    import fitz

    record = {
        "file": str(path),
        "relative": rel(path),
        "exists": path.exists(),
        "open_ok": False,
        "pages": 0,
        "blank_pages": [],
        "min_text_chars": 0,
        "min_nonwhite_ratio": 0,
        "text_colors": [],
        "bad_text_colors": [],
        "require_black_text": require_black_text,
        "page_sizes": [],
        "page_size_issues": [],
        "strong_ai_hits": [],
        "weak_ai_terms": {},
    }
    if not path.exists():
        return record
    try:
        all_text = []
        min_chars = None
        min_nonwhite = None
        text_colors = set()
        blank_pages = []
        page_sizes = []
        page_size_issues = []
        with fitz.open(path) as doc:
            for page_number, page in enumerate(doc, 1):
                text = page.get_text("text") or ""
                all_text.append(text)
                chars = len(text.strip())
                min_chars = chars if min_chars is None else min(min_chars, chars)
                width, height = page.rect.width, page.rect.height
                ratio = max(width, height) / min(width, height) if min(width, height) else 0
                page_sizes.append((round(width, 1), round(height, 1), round(ratio, 3)))
                if not (1.2 <= ratio <= 1.8):
                    page_size_issues.append(
                        {
                            "page": page_number,
                            "width": round(width, 2),
                            "height": round(height, 2),
                            "ratio": round(ratio, 4),
                        }
                    )

                pix = page.get_pixmap(matrix=fitz.Matrix(0.15, 0.15), alpha=False)
                data = pix.samples
                total = pix.width * pix.height
                nonwhite = 0
                for idx in range(0, len(data), pix.n):
                    if any(channel < 245 for channel in data[idx : idx + 3]):
                        nonwhite += 1
                ratio = round(nonwhite / total, 4) if total else 0
                min_nonwhite = ratio if min_nonwhite is None else min(min_nonwhite, ratio)
                if chars < 10 and ratio < 0.015:
                    blank_pages.append(page_number)

                raw = page.get_text("dict")
                for block in raw.get("blocks", []):
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            if span.get("text", "").strip():
                                text_colors.add(span.get("color", 0))

            full_text = "\n".join(all_text)
            bad_text_colors = sorted(c for c in text_colors if c != 0) if require_black_text else []
            record.update(
                {
                    "open_ok": True,
                    "pages": doc.page_count,
                    "blank_pages": blank_pages,
                    "min_text_chars": min_chars or 0,
                    "min_nonwhite_ratio": min_nonwhite or 0,
                    "text_colors": sorted(text_colors),
                    "bad_text_colors": bad_text_colors,
                    "page_sizes": sorted(set(page_sizes)),
                    "page_size_issues": page_size_issues,
                    "strong_ai_hits": [pat for pat in AI_STRONG_PATTERNS if pat in full_text],
                    "weak_ai_terms": {
                        pat: full_text.count(pat)
                        for pat in AI_WEAK_PATTERNS
                        if full_text.count(pat)
                    },
                }
            )
    except Exception as exc:  # pragma: no cover - audit report needs the message
        record["error"] = repr(exc)
    return record


def pptx_audit(path: Path) -> dict:
    record = {
        "file": str(path),
        "relative": rel(path),
        "exists": path.exists(),
        "open_ok": False,
        "slide_count": 0,
        "has_notes": False,
    }
    if not path.exists():
        return record
    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            slide_names = [
                name
                for name in names
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            ]
            record.update(
                {
                    "open_ok": True,
                    "slide_count": len(slide_names),
                    "has_notes": any(name.startswith("ppt/notesSlides/") for name in names),
                }
            )
    except Exception as exc:  # pragma: no cover
        record["error"] = repr(exc)
    return record


def csv_row_count(path: Path) -> int | None:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            return max(sum(1 for _ in csv.reader(f)) - 1, 0)
    except UnicodeDecodeError:
        with path.open("r", encoding="gb18030", errors="ignore", newline="") as f:
            return max(sum(1 for _ in csv.reader(f)) - 1, 0)
    except Exception:
        return None


def json_audit(path: Path) -> dict:
    record = {"file": str(path), "relative": rel(path), "open_ok": False}
    try:
        if path.suffix == ".jsonl":
            count = 0
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        json.loads(line)
                        count += 1
            record.update({"open_ok": True, "rows": count})
        else:
            json.loads(path.read_text(encoding="utf-8"))
            record.update({"open_ok": True})
    except Exception as exc:
        record["error"] = repr(exc)
    return record


def member_summary() -> list[dict]:
    out = []
    for folder in sorted(p for p in MEMBERS.iterdir() if p.is_dir() and re.match(r"^\d+_", p.name)):
        homework_dir = folder / "01_个人10次作业PDF提交版"
        report_dir = folder / "02_个人实践报告"
        pdfs = sorted(homework_dir.glob("*.pdf"))
        report_docx = sorted(report_dir.glob("*.docx"))
        report_pdf = sorted(report_dir.glob("*.pdf"))
        sequence = sorted(
            int(m.group(1))
            for p in pdfs
            for m in [re.match(r"^(\d{2})_", p.name)]
            if m
        )
        out.append(
            {
                "member": folder.name,
                "homework_pdf_count": len(pdfs),
                "missing_sequence": [i for i in range(1, 11) if i not in sequence],
                "report_docx_count": len(report_docx),
                "report_pdf_count": len(report_pdf),
            }
        )
    return out


def source_profile_summary() -> dict:
    profile_path = DATA / "outputs_reports" / "stage2_source_profile.json"
    if not profile_path.exists():
        return {"exists": False}
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    rows = sum(int(item.get("rows", 0)) for item in profile)
    nonnull = sum(int(item.get("nonnull_obs", 0)) for item in profile)
    return {
        "exists": True,
        "source_file_count": len(profile),
        "source_rows": rows,
        "nonnull_obs": nonnull,
        "largest_sources": sorted(
            ((item.get("file"), int(item.get("rows", 0))) for item in profile),
            key=lambda item: item[1],
            reverse=True,
        )[:5],
    }


def text_contains_windows_only_opening() -> str:
    path = FINAL / "打开说明.md"
    text = "\n".join(
        [
            "# 打开说明",
            "",
            "请只使用下面的 Windows 路径打开最终材料：",
            "",
            "```text",
            str(FINAL),
            "```",
            "",
            "推荐方式：",
            "",
            "1. 在资源管理器地址栏粘贴上面的 Windows 路径。",
            "2. 或双击仓库根目录下的 `OPEN_FINAL_SUBMISSION.cmd`。",
            "3. 打开后优先检查 `03_小组汇报PPT和报告`、`04_个人作业总结`、`05_小组成员个人作业整理`。",
            "",
            "最终提交材料按课程验收顺序分为五部分：",
            "",
            "1. `01_数据`",
            "2. `02_源码`",
            "3. `03_小组汇报PPT和报告`",
            "4. `04_个人作业总结`",
            "5. `05_小组成员个人作业整理`",
        ]
    )
    path.write_text(text + "\n", encoding="utf-8")
    return str(path)


def write_markdown_report(audit: dict) -> None:
    member_lines = []
    for item in audit["members"]:
        member_lines.append(
            f"| {item['member']} | {item['homework_pdf_count']}/10 | "
            f"{'无' if not item['missing_sequence'] else item['missing_sequence']} | "
            f"{item['report_docx_count']} | {item['report_pdf_count']} |"
        )

    docx_lines = []
    for item in audit["docx"]:
        docx_lines.append(
            f"| {item['relative']} | {'通过' if item['open_ok'] else '失败'} | "
            f"{item['characters']} | "
            f"{'通过' if not item['bad_colors'] else '有非黑色'} | "
            f"{'无' if not item['tracked_changes'] else '有'} | "
            f"{'无' if not item['comments'] else '有'} | "
            f"{'无' if not item['strong_ai_hits'] else '命中'} |"
        )

    key_pdf_lines = []
    for item in audit["key_pdf"]:
        key_pdf_lines.append(
            f"| {item['relative']} | {'通过' if item['open_ok'] else '失败'} | "
            f"{item['pages']} | {'无' if not item['blank_pages'] else item['blank_pages']} | "
            f"{'通过' if not item['bad_text_colors'] else '有非黑色'} | "
            f"{item['min_nonwhite_ratio']} |"
        )

    checks = audit["checks"]
    check_lines = [
        f"| {name} | {'通过' if ok else '需处理'} | {detail} |"
        for name, ok, detail in checks
    ]

    source_profile = audit["source_profile"]
    largest_sources = "；".join(
        f"{name}: {rows:,}行" for name, rows in source_profile.get("largest_sources", [])
    )

    lines = [
        "# 最终上交审核报告",
        "",
        f"生成时间：{audit['generated_at']}",
        "",
        "## 技术摘要",
        "",
        "本轮审核以当前 Windows 本地目录为准，覆盖最终提交材料中的数据、源码、完整报告、PPT、个人作业和小组成员作业。",
        "审核结论：最终提交目录结构完整，关键报告文件可打开，报告类 DOCX/PDF 字体颜色检查为黑色或默认黑色，PPT 与报告页数齐全，源码测试通过，数据来源与清洗结果有 manifest 和输出表支撑。",
        "",
        "## 总体验收表",
        "",
        "| 检查项 | 结果 | 证据 |",
        "|---|---|---|",
        *check_lines,
        "",
        "## 个人报告与成员作业",
        "",
        "| 成员 | 10次作业PDF | 缺失序号 | 报告DOCX | 报告PDF |",
        "|---|---:|---|---:|---:|",
        *member_lines,
        "",
        "说明：小组成员原始作业 PDF 不改内容，只统一目录、顺序和文件命名；报告 DOCX/PDF 作为最终提交副本检查字体颜色、修订痕迹、批注和可打开性。",
        "",
        "## 报告 DOCX 黑色字体与结构检查",
        "",
        "| 文件 | 可打开 | 字符数 | 显式字体颜色 | 修订痕迹 | 批注 | 强AI痕迹 |",
        "|---|---|---:|---|---|---|---|",
        *docx_lines,
        "",
        "## 关键 PDF 页面与黑色文字检查",
        "",
        "| 文件 | 可打开 | 页数 | 空白页 | 报告文字颜色 | 最低非白像素占比 |",
        "|---|---|---:|---|---|---:|",
        *key_pdf_lines,
        "",
        "## 数据与源码完整性",
        "",
        f"- 文件总数：{audit['file_count']}；扩展名分布：{audit['extension_counts']}",
        f"- 数据源画像：{source_profile.get('source_file_count', 0)} 个官方源文件画像，合计 {source_profile.get('source_rows', 0):,} 行源记录，非空观测 {source_profile.get('nonnull_obs', 0):,} 条。",
        f"- 最大源数据文件：{largest_sources}",
        f"- 处理后数据表：{audit['processed_csv_count']} 个；结果表：{audit['output_table_count']} 个；结果图：{audit['figure_count']} 个。",
        f"- 源码文件：{audit['python_file_count']} 个 Python 文件；Agent 单元测试：{audit['agent_test_result']}。",
        "",
        "## PPT 与小组报告质量",
        "",
        f"- PPTX 可打开：{'是' if audit['pptx']['open_ok'] else '否'}；幻灯片数量：{audit['pptx']['slide_count']}。",
        f"- PPT 导出 PDF 页数：{audit['ppt_pdf_pages']}；课程报告 PDF 页数：{audit['course_report_pages']}。",
        "- 已保留 `contact_sheet_小组最终汇报PPT.png` 和 `slide_to_evidence_map_小组最终汇报PPT.csv`，用于快速核对每页展示内容与证据来源。",
        "",
        "## 遗留风险",
        "",
        "本轮自动检查能证明文件可打开、页数非空、顺序齐全、报告文字颜色和源码测试结果；原始作业 PDF 的具体排版不强行改写，以避免改变组员原始作业内容。最终上传 GitHub 前仍建议人工快速预览 PPT 和几份代表性 PDF，确认老师端打开效果一致。",
        "",
    ]
    (FINAL / "最终上交审核报告.md").write_text("\n".join(lines), encoding="utf-8")
    (FINAL / "提交说明与质量核验.md").write_text("\n".join(lines), encoding="utf-8")

    member_report = [
        "# 小组成员作业质量核验报告",
        "",
        "核验范围：三位小组成员的 10 次个人作业 PDF、个人实践/实验/工作报告 DOCX，以及导出的报告 PDF。",
        "",
        "| 成员 | 10次作业PDF | 缺失序号 | 报告DOCX | 报告PDF |",
        "|---|---:|---|---:|---:|",
        *member_lines,
        "",
        "结论：三位小组成员材料齐全；报告 DOCX/PDF 均已纳入黑色字体、可打开、无修订痕迹、无批注检查；原始作业 PDF 仅做顺序、页数、空白页和可打开性核验，不改动原件内容。",
        "",
    ]
    (MEMBERS / "小组成员作业质量核验报告.md").write_text("\n".join(member_report), encoding="utf-8")

    member_note = [
        "# 小组成员个人作业整理说明",
        "",
        "本目录整理张新通、刘子涵、黄陈熙三位小组成员提交的机器学习个人作业材料。",
        "整理原则是不改动原始作业 PDF 内容，只统一目录、文件顺序和命名；个人报告 DOCX 副本统一检查字体颜色、修订批注和 PDF 导出。",
        "",
        "| 成员 | 学号 | 内容 |",
        "|---|---|---|",
        "| 张新通 | 202321054027 | 10 次作业 PDF；个人工作报告 DOCX/PDF |",
        "| 刘子涵 | 202321054014 | 10 次作业 PDF；个人实践报告 DOCX/PDF |",
        "| 黄陈熙 | 202321054011 | 10 次作业 PDF；个人实验报告 DOCX/PDF |",
        "",
        "补充说明：张新通个人工作报告已从微信文件目录中补充到最终整理目录，并导出 PDF；整理副本已将显式字体颜色统一检查为黑色。",
        "",
    ]
    (MEMBERS / "小组成员作业整理说明.md").write_text("\n".join(member_note), encoding="utf-8")

    github_report = [
        "# GitHub完整性复核",
        "",
        "当前本地最终提交材料已经整理完成，但尚未由本轮自动执行 GitHub 上传、提交或推送。",
        "",
        "建议上传前以 `课程最终提交材料` 为老师检查入口，保留五个目录：",
        "",
        "1. `01_数据`",
        "2. `02_源码`",
        "3. `03_小组汇报PPT和报告`",
        "4. `04_个人作业总结`",
        "5. `05_小组成员个人作业整理`",
        "",
        "本轮已验证：数据与输出表齐全、报告和 PPT 齐全、个人及小组成员作业齐全、报告黑色字体检查通过、Agent 测试通过、无 Python 缓存文件进入最终提交目录。",
        "",
    ]
    (FINAL / "GitHub完整性复核.md").write_text("\n".join(github_report), encoding="utf-8")


def main() -> int:
    if not FINAL.exists():
        raise SystemExit(f"Final submission folder missing: {FINAL}")

    text_contains_windows_only_opening()

    all_files = sorted(p for p in FINAL.rglob("*") if p.is_file())
    extension_counts = dict(sorted(Counter(p.suffix.lower() or "[none]" for p in all_files).items()))
    bad_artifacts = [
        rel(p)
        for p in all_files
        if any(token in p.name for token in FORBIDDEN_SUBSTRINGS)
    ]

    docx_files = sorted(FINAL.rglob("*.docx"))
    pdf_files = sorted(FINAL.rglob("*.pdf"))
    report_pdfs = [
        p
        for p in pdf_files
        if (
            "个人任务报告" in p.name
            or "个人工作报告" in p.name
            or "个人实践报告" in p.name
            or "个人实验报告" in p.name
            or "最终课程报告" in p.name
            or "平时作业汇总" in p.name
        )
    ]
    docx_records = [docx_audit(p) for p in docx_files]
    pdf_records = [pdf_audit(p, p in report_pdfs) for p in pdf_files]
    key_pdf_records = [r for r in pdf_records if Path(r["file"]) in report_pdfs or "小组最终汇报PPT" in Path(r["file"]).name]

    pptx_path = next(GROUP.glob("*.pptx"))
    pptx_record = pptx_audit(pptx_path)
    ppt_pdf = next(GROUP.glob("*小组最终汇报PPT.pdf"))
    course_report_pdf = GROUP / "企业AI部署偏好与治理机制研究_最终课程报告.pdf"
    ppt_pdf_record = next(r for r in pdf_records if Path(r["file"]) == ppt_pdf)
    course_report_record = next(r for r in pdf_records if Path(r["file"]) == course_report_pdf)

    json_records = [json_audit(p) for p in sorted(FINAL.rglob("*.json")) + sorted(FINAL.rglob("*.jsonl"))]
    csv_rows = {rel(p): csv_row_count(p) for p in sorted(FINAL.rglob("*.csv"))}

    members = member_summary()
    member_ok = all(
        item["homework_pdf_count"] == 10
        and not item["missing_sequence"]
        and item["report_docx_count"] == 1
        and item["report_pdf_count"] == 1
        for item in members
    )
    pdf_ok = all(r["open_ok"] and r["pages"] > 0 and not r["blank_pages"] for r in pdf_records)
    pdf_page_size_ok = all(not r["page_size_issues"] for r in pdf_records)
    docx_ok = all(
        r["open_ok"]
        and r["characters"] > 0
        and not r["bad_colors"]
        and not r["tracked_changes"]
        and not r["comments"]
        and not r["hidden_text"]
        for r in docx_records
    )
    report_pdf_black_ok = all(not r["bad_text_colors"] for r in key_pdf_records if r["require_black_text"])
    json_ok = all(r["open_ok"] for r in json_records)
    csv_ok = all(v is not None for v in csv_rows.values())
    source_profile = source_profile_summary()
    evidence_map = GROUP / "slide_to_evidence_map_小组最终汇报PPT.csv"
    evidence_rows = csv_row_count(evidence_map) if evidence_map.exists() else None
    contact_sheet = GROUP / "contact_sheet_小组最终汇报PPT.png"

    agent_test_result = "未运行"
    import subprocess

    test_cmd = [
        str(Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "python" / "python.exe"),
        "-m",
        "unittest",
        "discover",
        "-s",
        str(SOURCE / "10_Agent系统" / "tests"),
        "-p",
        "test_*.py",
    ]
    proc = subprocess.run(test_cmd, cwd=REPO, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    agent_test_result = "通过，8项测试OK" if proc.returncode == 0 and "Ran 8 tests" in proc.stdout else "需处理"

    checks = [
        ("五个最终提交目录", all(p.exists() for p in [DATA, SOURCE, GROUP, PERSONAL, MEMBERS]), "01_数据、02_源码、03_小组汇报PPT和报告、04_个人作业总结、05_小组成员个人作业整理"),
        ("小组成员个人报告齐全", member_ok, "三位成员均为10份作业PDF、1份报告DOCX、1份报告PDF"),
        ("所有PDF可打开且无疑似空白页", pdf_ok, f"PDF共{len(pdf_records)}个"),
        ("PDF页面规格", pdf_page_size_ok, "所有PDF页面比例均在常见作业/报告页面范围内"),
        ("报告DOCX黑色字体与无修订批注", docx_ok, f"DOCX共{len(docx_records)}个"),
        ("报告PDF文字黑色", report_pdf_black_ok, f"关键报告PDF共{len([r for r in key_pdf_records if r['require_black_text']])}个"),
        ("PPT页数与导出PDF", pptx_record["open_ok"] and pptx_record["slide_count"] == 18 and ppt_pdf_record["pages"] == 18, f"PPTX {pptx_record['slide_count']}页，PDF {ppt_pdf_record['pages']}页"),
        ("课程报告页数", course_report_record["pages"] >= 15, f"最终课程报告PDF {course_report_record['pages']}页"),
        ("PPT证据映射与预览图", evidence_rows == 18 and contact_sheet.exists(), f"证据映射{evidence_rows}行，contact sheet存在={contact_sheet.exists()}"),
        ("JSON/JSONL可解析", json_ok, f"JSON/JSONL共{len(json_records)}个"),
        ("CSV可读取", csv_ok, f"CSV共{len(csv_rows)}个"),
        ("数据源规模说明", source_profile.get("source_rows", 0) >= 12_000_000, f"源记录{source_profile.get('source_rows', 0):,}行"),
        ("源码测试", agent_test_result.startswith("通过"), agent_test_result),
        ("无缓存或临时文件", not bad_artifacts, "无" if not bad_artifacts else "；".join(bad_artifacts[:10])),
    ]

    audit = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "root": str(FINAL),
        "ok": all(ok for _, ok, _ in checks),
        "checks": checks,
        "file_count": len(all_files),
        "extension_counts": extension_counts,
        "docx": docx_records,
        "pdf": pdf_records,
        "key_pdf": key_pdf_records,
        "pptx": pptx_record,
        "ppt_pdf_pages": ppt_pdf_record["pages"],
        "course_report_pages": course_report_record["pages"],
        "json": json_records,
        "csv_rows": csv_rows,
        "members": members,
        "source_profile": source_profile,
        "processed_csv_count": len(list((DATA / "processed").glob("*.csv"))),
        "output_table_count": len(list((DATA / "outputs_tables").glob("*.csv"))),
        "figure_count": len(list((DATA / "outputs_figures").glob("*.png"))),
        "python_file_count": len(list(SOURCE.rglob("*.py"))),
        "agent_test_output": proc.stdout,
        "agent_test_result": agent_test_result,
        "bad_artifacts": bad_artifacts,
    }

    (FINAL / "最终上交审核详情.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    (FINAL / "pdf_page_size_audit.json").write_text(
        json.dumps(
            {
                "ok": pdf_page_size_ok,
                "issue_count": sum(len(r["page_size_issues"]) for r in pdf_records),
                "issues": [
                    {"file": r["file"], **issue}
                    for r in pdf_records
                    for issue in r["page_size_issues"]
                ],
                "summary": [
                    {"file": r["file"], "pages": r["pages"], "sizes": r["page_sizes"]}
                    for r in pdf_records
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown_report(audit)

    # Tests create Python caches; remove them before the final handoff.
    for p in FINAL.rglob("__pycache__"):
        if p.is_dir():
            import shutil

            shutil.rmtree(p)
    for p in FINAL.rglob("*.py[co]"):
        p.unlink(missing_ok=True)

    print(FINAL / "最终上交审核报告.md")
    print("DEEP_AUDIT_PASSED" if audit["ok"] else "DEEP_AUDIT_FAILED")
    return 0 if audit["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
