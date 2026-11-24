#!/usr/bin/env python3
"""0단계 보고서 Markdown → PDF (그림 포함). pandoc(→ docx) + LibreOffice(→ pdf), 한글 글꼴 Noto Sans CJK KR.
사용: python build_report_pdf.py   (결과: prelim/PRELIM_STAGE0_REPORT.pdf)
"""
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

P = Path("/storage/bigdata/EmoBrain_response/prelim")
SRC = P / "PRELIM_STAGE0_REPORT.md"
OUT = P / "PRELIM_STAGE0_REPORT.pdf"
FONT = "Noto Sans CJK KR"
PAGEBREAK = '\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n'
# 표 열 너비 (구분선의 '-' 개수 비율로 정해짐): 머리글 첫 칸 → 구분선
WIDTHS = {"| # | 질문 | 답 |": "|--|------|-------------|---------|",
          "| 라벨 | 설명 비율 | 주된 방향 |": "|------|---|-------|",
          "| 항목 | 방법 |": "|---|---------|",
          "| 데이터 | 피험자 | 블록 |": "|-----|---|---|--|---|---|-----|",
          "| 단계 | 입력 → 감정 | 묻는 것 |": "|----|--------|--------|",
          "| 네트워크 | Horikawa | MindCaptioning |": "|----|---|---|"}


def reference_docx(tmp):
    ref = tmp / "ref.docx"
    ref.write_bytes(subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"], check=True, stdout=subprocess.PIPE).stdout)
    out = tmp / "ref_kr.docx"
    with zipfile.ZipFile(ref) as zin, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":   # A4, 여백 2cm (pandoc 은 기준 문서의 sectPr 를 그대로 씀)
                d = data.decode("utf8")
                if "<w:sectPr" not in d:
                    d = d.replace("</w:body>", '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134" w:header="567" w:footer="567" w:gutter="0"/></w:sectPr></w:body>')
                data = d.encode("utf8")
            if item.filename in ("word/styles.xml", "word/theme/theme1.xml"):
                s = data.decode("utf8")
                s = re.sub(r"<w:rFonts [^>]*/>", f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:eastAsia="{FONT}" w:cs="{FONT}"/>', s)
                s = re.sub(r'(<a:(?:latin|ea) typeface=")[^"]*(")', rf"\g<1>{FONT}\g<2>", s)
                data = s.encode("utf8")
            zout.writestr(item, data)
    return out


def prepare_markdown(tmp):
    lines = SRC.read_text().split("\n")
    out = []
    for i, line in enumerate(lines):
        m = re.match(r"!\[(.*)\]\((fig_[^)]+\.png)\)$", line.strip())
        if m:   # 그림: 절대 경로 + 쪽 너비
            line = f"![{m.group(1)}]({P / m.group(2)}){{width=17cm}}"   # % 는 pandoc 2.2 에서 비율이 깨짐
        if re.match(r"^\|[-| ]+\|$", line) and i > 0:
            for head, sep in WIDTHS.items():
                if lines[i - 1].startswith(head):
                    line = sep
        if re.match(r"^\s*(- |\d+\. )", line) and out and out[-1].strip() and not re.match(r"^\s*(- |\d+\. )", out[-1]):
            out.append("")   # 문단 바로 뒤 목록은 빈 줄이 있어야 목록으로 읽힌다 (pandoc 2.2)
        if line.startswith("## ") and not line.startswith(("## 한눈에", "## 핵심 해석", "## 다음 단계")):
            out.append(PAGEBREAK)
        out.append(line)
    md = tmp / "report.md"; md.write_text("\n".join(out))
    return md


TEXT_W = 17 * 360000   # 본문 폭 17cm (EMU)
A4 = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" '
      'w:left="1134" w:header="567" w:footer="567" w:gutter="0"/></w:sectPr>')


def set_a4(docx):
    """pandoc 2.2 는 기준 문서의 쪽 설정을 쓰지 않아, 만들어진 docx 의 본문 끝 쪽 설정을 A4·여백 2cm 로 바꾼다."""
    tmpf = docx.with_suffix(".a4.docx")
    with zipfile.ZipFile(docx) as zin, zipfile.ZipFile(tmpf, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/document.xml":
                d = data.decode("utf8")
                d = re.sub(r"<w:sectPr>.*?</w:sectPr>(?=</w:body>)", "", d, flags=re.S)
                d = d.replace("</w:body>", A4 + "</w:body>")
                # 그림을 본문 폭(17cm)에 맞춰 비율 그대로 키운다 (pandoc 2.2 가 약 14.8cm 로 줄여 넣음)
                def fit(m):
                    cx, cy = int(m.group(2)), int(m.group(3)); k = TEXT_W / cx
                    return f'{m.group(1)}cx="{TEXT_W}" cy="{int(cy * k)}"'
                d = re.sub(r'(<(?:wp:extent|a:ext) )cx="(\d+)" cy="(\d+)"', fit, d)
                data = d.encode("utf8")
            zout.writestr(item, data)
    tmpf.replace(docx)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="emo_pdf_"))
    try:
        ref = reference_docx(tmp); md = prepare_markdown(tmp); docx = tmp / "PRELIM_STAGE0_REPORT.docx"
        subprocess.run(["pandoc", str(md), "-f", "markdown", "-o", str(docx), "--reference-doc", str(ref),
                        "--resource-path", str(P), "--columns=10"], check=True)
        set_a4(docx)
        # LibreOffice 6.4 는 명령줄 PDF 옵션이 없어 임시 사용자 설정으로 지정: 그림 무손실, 해상도 줄이지 않음
        prof = tmp / "lo_profile" / "user"; prof.mkdir(parents=True, exist_ok=True)
        (prof / "registrymodifications.xcu").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<oor:items xmlns:oor="http://openoffice.org/2001/registry" '
            'xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n'
            '<item oor:path="/org.openoffice.Office.Common/Filter/PDF/Export"><prop oor:name="UseLosslessCompression" oor:op="fuse"><value>true</value></prop></item>\n'
            '<item oor:path="/org.openoffice.Office.Common/Filter/PDF/Export"><prop oor:name="ReduceImageResolution" oor:op="fuse"><value>false</value></prop></item>\n'
            '</oor:items>\n')
        subprocess.run(["soffice", f"-env:UserInstallation=file://{tmp}/lo_profile", "--headless", "--convert-to", "pdf",
                        "--outdir", str(tmp), str(docx)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600)
        shutil.copy(tmp / "PRELIM_STAGE0_REPORT.pdf", OUT)
        print("저장:", OUT)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
