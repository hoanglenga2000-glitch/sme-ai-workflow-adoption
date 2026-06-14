from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import fitz


REPO = Path(__file__).resolve().parents[1]
FINAL = REPO / "课程最终提交材料"
DATA = FINAL / "01_数据"
SOURCE = FINAL / "02_源码"
GROUP = FINAL / "03_小组汇报PPT和报告"
MEMBERS = FINAL / "04_小组成员个人作业整理"
GROUP_REPORT = GROUP / "中小企业AI流程自动化采纳机制研究案例_小组课程汇报报告.pdf"
GROUP_REPORT_DOCX = GROUP / "中小企业AI流程自动化采纳机制研究案例_小组课程汇报报告.docx"
PPTX = GROUP / "中小企业AI流程自动化采纳机制研究案例_小组最终汇报PPT.pptx"
PPT_PDF = GROUP / "中小企业AI流程自动化采纳机制研究案例_小组最终汇报PPT.pdf"
GITHUB_URL_FILE = FINAL / "GitHub地址.txt"


def member_name_id(folder: Path) -> tuple[str, str]:
    parts = folder.name.split("_")
    if len(parts) >= 3:
        return parts[1], parts[2]
    match = re.search(r"(.+?)(20\d+)", folder.name)
    if match:
        return match.group(1).lstrip("0123456789_"), match.group(2)
    return folder.name, "未知学号"


def merge_homework(member_dir: Path) -> dict:
    name, sid = member_name_id(member_dir)
    homework_dir = member_dir / "01_个人10次作业PDF提交版"
    summary_dir = member_dir / "00_平时作业汇总PDF"
    summary_dir.mkdir(exist_ok=True)
    pdfs = sorted(homework_dir.glob("*.pdf"))
    out = summary_dir / f"信管2301{name}{sid}平时作业汇总.pdf"
    if out.exists():
        out.unlink()
    merged = fitz.open()
    for pdf in pdfs:
        with fitz.open(pdf) as src:
            merged.insert_pdf(src)
    merged.save(out)
    merged.close()
    with fitz.open(out) as doc:
        pages = doc.page_count
    return {
        "member": member_dir.name,
        "homework_source_count": len(pdfs),
        "summary_pdf": str(out),
        "summary_pages": pages,
        "summary_exists": out.exists(),
    }


def normalize_report_folder(member_dir: Path) -> dict:
    src = member_dir / "02_个人实践报告"
    dst = member_dir / "02_个人案例总结"
    if src.exists() and not dst.exists():
        src.rename(dst)
    elif src.exists() and dst.exists():
        for item in src.iterdir():
            target = dst / item.name
            if not target.exists():
                shutil.move(str(item), str(target))
        src.rmdir()
    docx_count = len(list(dst.glob("*.docx"))) if dst.exists() else 0
    pdf_count = len(list(dst.glob("*.pdf"))) if dst.exists() else 0
    return {
        "member": member_dir.name,
        "report_folder": str(dst),
        "report_docx_count": docx_count,
        "report_pdf_count": pdf_count,
        "report_ok": docx_count >= 1 and pdf_count >= 1,
    }


def pdf_pages(path: Path) -> tuple[int, list[int]]:
    blanks = []
    with fitz.open(path) as doc:
        for idx, page in enumerate(doc, 1):
            text = page.get_text("text").strip()
            pix = page.get_pixmap(matrix=fitz.Matrix(0.12, 0.12), alpha=False)
            data = pix.samples
            nonwhite = 0
            for i in range(0, len(data), pix.n):
                if any(channel < 245 for channel in data[i : i + 3]):
                    nonwhite += 1
            if len(text) < 10 and nonwhite / max(1, pix.width * pix.height) < 0.015:
                blanks.append(idx)
        return doc.page_count, blanks


def git_remote_url() -> str:
    proc = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=REPO,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def write_member_lists(summary: list[dict]) -> None:
    rows = []
    for member_dir in sorted(p for p in MEMBERS.iterdir() if p.is_dir() and re.match(r"^\d{2}_", p.name)):
        for file in sorted(member_dir.rglob("*")):
            if file.is_file():
                rows.append([member_dir.name, str(file.relative_to(MEMBERS)), file.suffix.lower(), file.stat().st_size])
    for name in ["小组成员作业文件清单.csv", "整理后文件完整清单.csv"]:
        with (MEMBERS / name).open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["成员", "相对路径", "扩展名", "大小bytes"])
            writer.writerows(rows)

    lines = [
        "# 小组成员个人材料核对",
        "",
        "每名成员按老师要求保留平时作业汇总PDF、个人10次作业PDF原件和个人案例总结。",
        "",
        "| 成员 | 平时作业汇总PDF | 10次作业PDF | 个人案例总结DOCX | 个人案例总结PDF | 结论 |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for item in summary:
        ok = item["summary_exists"] and item["homework_source_count"] == 10 and item["report_ok"]
        lines.append(
            f"| {item['member']} | {1 if item['summary_exists'] else 0} | {item['homework_source_count']} | "
            f"{item['report_docx_count']} | {item['report_pdf_count']} | {'通过' if ok else '需处理'} |"
        )
    (MEMBERS / "小组成员作业质量核验报告.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (MEMBERS / "小组成员作业整理说明.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (MEMBERS / "小组成员作业质量核验详情.json").write_text(
        json.dumps({"ok": all(item["ok"] for item in summary), "members": summary}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    member_dirs = sorted(p for p in MEMBERS.iterdir() if p.is_dir() and re.match(r"^\d{2}_", p.name))
    summary = []
    for member_dir in member_dirs:
        merged = merge_homework(member_dir)
        report = normalize_report_folder(member_dir)
        item = {**merged, **report}
        item["ok"] = item["summary_exists"] and item["homework_source_count"] == 10 and item["report_ok"]
        summary.append(item)
    write_member_lists(summary)

    github_url = git_remote_url()
    GITHUB_URL_FILE.write_text(
        f"共享文档GitHub地址填写：{github_url}\n",
        encoding="utf-8",
    )

    report_pages, report_blanks = pdf_pages(GROUP_REPORT)
    ppt_pages, ppt_blanks = pdf_pages(PPT_PDF)
    checks = [
        ["平时作业汇总PDF", all(item["summary_exists"] for item in summary), "四名成员均已生成平时作业汇总PDF"],
        ["每名成员个人案例总结", all(item["report_ok"] for item in summary), "四名成员均有个人案例总结DOCX/PDF"],
        ["小组案例数据", DATA.exists() and any(DATA.rglob("*.csv")), "数据目录存在且包含处理后数据/结果表"],
        ["小组案例代码", SOURCE.exists() and any(SOURCE.rglob("*.py")), "源码目录存在且包含Python代码"],
        ["小组案例PPT", PPTX.exists() and PPT_PDF.exists() and ppt_pages == 18 and not ppt_blanks, f"PPTX存在，PDF {ppt_pages}页"],
        ["小组案例15页以上PDF文档", GROUP_REPORT.exists() and report_pages >= 15 and not report_blanks, f"小组案例PDF {report_pages}页"],
        ["GitHub地址", bool(github_url), github_url],
    ]
    ok = all(item[1] for item in checks)
    detail = {
        "ok": ok,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "official_requirement": [
            "平时作业汇总+案例汇报+个人案例总结",
            "每组一个GitHub地址，放在共享文档一列",
            "提交成员平时作业汇总PDF、小组案例数据/代码/PPT、小组案例15页以上PDF文档、每个成员个人总结",
        ],
        "checks": checks,
        "members": summary,
        "github_url": github_url,
    }
    (FINAL / "15周最终提交要求核对.json").write_text(json.dumps(detail, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# 15周最终提交要求核对",
        "",
        "根据老师要求，本次最终提交应包括：平时作业汇总、案例汇报、个人案例总结；每组一个GitHub地址；小组案例数据、代码、PPT和15页以上PDF文档。",
        "",
        "| 要求 | 结果 | 说明 |",
        "|---|---|---|",
    ]
    for name, passed, desc in checks:
        lines.append(f"| {name} | {'通过' if passed else '需处理'} | {desc} |")
    lines.extend(
        [
            "",
            f"共享文档GitHub地址填写：`{github_url}`",
            "",
            "成员材料结构：每名成员均包含 `00_平时作业汇总PDF`、`01_个人10次作业PDF提交版`、`02_个人案例总结`。",
        ]
    )
    (FINAL / "15周最终提交要求核对.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (FINAL / "最终上交审核报告.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (FINAL / "提交说明与质量核验.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not ok:
        raise RuntimeError(json.dumps(detail, ensure_ascii=False, indent=2))
    print(json.dumps(detail, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
