#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.oxml.ns import qn
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, CondPageBreak
import markdown2
from xhtml2pdf import pisa
import pypandoc


REPO_ROOT = Path(__file__).resolve().parents[2]
PROD_ROOT = REPO_ROOT / "production"
CONTENT_DIR = REPO_ROOT / "content"
FIGURES_DIR = REPO_ROOT / "figures"
REFERENCES_FILE = REPO_ROOT / "references.md"
ASSEMBLED_DIR = PROD_ROOT / "assembled"
METHOD_A_DIR = PROD_ROOT / "method_a_python"
METHOD_B_DIR = PROD_ROOT / "method_b_hybrid"
PROD_FIGURES_DIR = PROD_ROOT / "figures"

CONTENT_FILES = [
    "00_abstract.md",
    "01_introduction.md",
    "02_literature_review.md",
    "03_methodology.md",
    "04_results.md",
    "05_discussion.md",
    "06_recommendations_conclusion.md",
]


CHAPTER_INSERTIONS = [
    ("# I. INTRODUCTION", "Chapter One"),
    ("# III. METHODOLOGY (ORIGINAL CROSS-SECTIONAL STUDY)", "Chapter Two"),
    ("# IV. RESULTS", "Chapter Three"),
    ("# V. DISCUSSION", "Chapter Four"),
    ("# VI. RECOMMENDATIONS", "Chapter Five"),
]


def ensure_dirs() -> None:
    for d in [ASSEMBLED_DIR, METHOD_A_DIR, METHOD_B_DIR, PROD_FIGURES_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def copy_figure_assets() -> None:
    for png in FIGURES_DIR.glob("*.png"):
        shutil.copy2(png, PROD_FIGURES_DIR / png.name)
        shutil.copy2(png, ASSEMBLED_DIR / png.name)


def normalize_page_breaks(text: str) -> str:
    return text.replace(
        '<div style="page-break-after: always;"></div>',
        '<div class="page-break"></div>',
    )


def inject_chapter_title_pages(text: str) -> str:
    for heading, chapter_name in CHAPTER_INSERTIONS:
        marker = f"\n\n[[CHAPTER_TITLE:{chapter_name}]]\n\n{heading}"
        text = text.replace(f"\n\n{heading}", marker, 1)
    return text


def transform_inline_figure_links(text: str) -> str:
    pattern = re.compile(r"\[([^\]]+\.(?:png|jpg|jpeg|webp))\]\(([^)]+\.(?:png|jpg|jpeg|webp))\)")
    out_lines: list[str] = []

    def friendly_label(raw_path: str) -> str:
        filename = Path(unquote(raw_path.strip())).name
        stem = Path(filename).stem
        return stem.replace("_", " ").strip() or "figure"

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("!"):
            out_lines.append(line)
            continue

        matches = list(pattern.finditer(line))
        if not matches:
            out_lines.append(line)
            continue

        cleaned = pattern.sub(lambda _: "the corresponding figure below", line)
        out_lines.append(cleaned)
        out_lines.append("")
        for m in matches:
            out_lines.append(f"![{friendly_label(m.group(2))}]({m.group(2)})")
        out_lines.append("")

    return "\n".join(out_lines)


def rewrite_local_figure_links(md: str) -> str:
    def repl(match: re.Match[str]) -> str:
        alt = match.group(1)
        path = match.group(2)
        if "/" not in path:
            return f"![{alt}](../figures/{path})"
        return match.group(0)

    return re.sub(r"!\[([^\]]*)\]\(([^\)]+)\)", repl, md)


def assemble_markdown() -> Path:
    parts: list[str] = []

    for name in CONTENT_FILES:
        text = (CONTENT_DIR / name).read_text(encoding="utf-8")
        parts.append(text.strip())

    parts.append("# VIII. REFERENCES")
    parts.append(REFERENCES_FILE.read_text(encoding="utf-8").strip())

    merged = "\n\n".join(parts).strip() + "\n"
    merged = normalize_page_breaks(merged)
    merged = inject_chapter_title_pages(merged)
    merged = transform_inline_figure_links(merged)

    out_path = ASSEMBLED_DIR / "comprehensive_research.md"
    out_path.write_text(merged, encoding="utf-8")
    shutil.copy2(out_path, METHOD_A_DIR / "comprehensive_research.md")
    shutil.copy2(out_path, METHOD_B_DIR / "comprehensive_research.md")
    return out_path


def normalize_blocks(blocks: list[tuple[str, str]]) -> list[tuple[str, str]]:
    normalized: list[tuple[str, str]] = []
    for i, (kind, data) in enumerate(blocks):
        next_kind = blocks[i + 1][0] if i + 1 < len(blocks) else None
        if kind == "pagebreak":
            if not normalized:
                continue
            prev_kind = normalized[-1][0]
            if prev_kind == "pagebreak":
                continue
            if next_kind in {"pagebreak", "chaptertitle"}:
                continue
        normalized.append((kind, data))

    while normalized and normalized[-1][0] == "pagebreak":
        normalized.pop()
    return normalized


def iter_markdown_blocks(text: str) -> Iterable[tuple[str, str]]:
    paragraph_lines: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()

        if line.strip() == '<div class="page-break"></div>':
            if paragraph_lines:
                yield ("paragraph", " ".join(paragraph_lines).strip())
                paragraph_lines = []
            yield ("pagebreak", "")
            continue

        chapter_title = re.match(r"^\[\[CHAPTER_TITLE:(.+)\]\]$", line.strip())
        if chapter_title:
            if paragraph_lines:
                yield ("paragraph", " ".join(paragraph_lines).strip())
                paragraph_lines = []
            yield ("chaptertitle", chapter_title.group(1).strip())
            continue

        h1 = re.match(r"^#\s+(.+)$", line)
        h2 = re.match(r"^##\s+(.+)$", line)
        img = re.match(r"^!\[([^\]]*)\]\(([^\)]+)\)", line.strip())
        ordered_item = re.match(r"^\s*\d+\.\s+.+$", line)

        if h1:
            if paragraph_lines:
                yield ("paragraph", " ".join(paragraph_lines).strip())
                paragraph_lines = []
            yield ("h1", h1.group(1).strip())
            continue
        if h2:
            if paragraph_lines:
                yield ("paragraph", " ".join(paragraph_lines).strip())
                paragraph_lines = []
            yield ("h2", h2.group(1).strip())
            continue
        if img:
            if paragraph_lines:
                yield ("paragraph", " ".join(paragraph_lines).strip())
                paragraph_lines = []
            yield ("image", f"{img.group(1)}|||{img.group(2)}")
            continue
        if ordered_item:
            if paragraph_lines:
                yield ("paragraph", " ".join(paragraph_lines).strip())
                paragraph_lines = []
            yield ("paragraph", line.strip())
            continue

        if not line.strip():
            if paragraph_lines:
                yield ("paragraph", " ".join(paragraph_lines).strip())
                paragraph_lines = []
            continue

        paragraph_lines.append(line)

    if paragraph_lines:
        yield ("paragraph", " ".join(paragraph_lines).strip())


def build_docx(md_path: Path, out_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    blocks = normalize_blocks(list(iter_markdown_blocks(text)))
    doc = Document()

    section = doc.sections[0]
    section.left_margin = Cm(1.5)
    section.right_margin = Cm(1.5)
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(14)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.first_line_indent = Inches(0.5)
    heading_1 = doc.styles["Heading 1"]
    heading_1.font.name = "Times New Roman"
    heading_1._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    heading_1.font.size = Pt(18)
    heading_2 = doc.styles["Heading 2"]
    heading_2.font.name = "Times New Roman"
    heading_2._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    heading_2.font.size = Pt(16)

    started = False
    chapter_just_emitted = False
    last_emitted_pagebreak = False
    in_references = False
    for kind, data in blocks:
        if kind == "chaptertitle":
            if started and not last_emitted_pagebreak:
                doc.add_page_break()
            p = doc.add_paragraph(data)
            p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.line_spacing = 1.0
            run = p.runs[0]
            run.font.name = "Times New Roman"
            run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
            run.font.size = Pt(36)
            run.bold = True
            doc.add_page_break()
            started = True
            chapter_just_emitted = True
            last_emitted_pagebreak = True
            continue
        if kind == "h1":
            if started and not chapter_just_emitted and not last_emitted_pagebreak:
                doc.add_page_break()
            p = doc.add_paragraph(data)
            p.style = doc.styles["Heading 1"]
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            in_references = data.strip().upper() == "VIII. REFERENCES"
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
            continue
        if kind == "h2":
            p = doc.add_paragraph(data)
            p.style = doc.styles["Heading 2"]
            p.paragraph_format.first_line_indent = Inches(0)
            p.paragraph_format.keep_with_next = True
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
            continue
        if kind == "paragraph":
            p = doc.add_paragraph(data)
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.widow_control = True
            if in_references:
                p.paragraph_format.first_line_indent = Inches(0)
                p.paragraph_format.space_after = Pt(8)
            else:
                p.paragraph_format.first_line_indent = Inches(0.5)
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
            continue
        if kind == "image":
            _, rel_path = data.split("|||", 1)
            img_path = (md_path.parent / rel_path).resolve()
            if img_path.exists():
                p = doc.add_paragraph()
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                run = p.add_run()
                run.add_picture(str(img_path), width=Inches(6.3))
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
            continue
        if kind == "pagebreak":
            if not last_emitted_pagebreak:
                doc.add_page_break()
                started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = True

    doc.save(out_path)


def escape_latex(text: str) -> str:
    table = {
        "\\": r"\\textbackslash{}",
        "&": r"\\&",
        "%": r"\\%",
        "$": r"\\$",
        "#": r"\\#",
        "_": r"\\_",
        "{": r"\\{",
        "}": r"\\}",
        "~": r"\\textasciitilde{}",
        "^": r"\\textasciicircum{}",
    }
    return "".join(table.get(ch, ch) for ch in text)


def build_tex(md_path: Path, out_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    blocks = normalize_blocks(list(iter_markdown_blocks(text)))
    body: list[str] = []
    started = False
    chapter_just_emitted = False
    last_emitted_pagebreak = False

    for kind, data in blocks:
        if kind == "chaptertitle":
            if started and not last_emitted_pagebreak:
                body.append("\\newpage")
            body.append("\\begin{center}\\vspace*{0.42\\textheight}")
            body.append("{\\LARGE \\textbf{" + escape_latex(data) + "}}")
            body.append("\\end{center}")
            body.append("\\newpage")
            started = True
            chapter_just_emitted = True
            last_emitted_pagebreak = True
        elif kind == "h1":
            if started and not chapter_just_emitted and not last_emitted_pagebreak:
                body.append("\\newpage")
            body.append("\\Needspace{5\\baselineskip}")
            body.append(f"\\section*{{{escape_latex(data)}}}")
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
        elif kind == "h2":
            body.append("\\Needspace{5\\baselineskip}")
            body.append(f"\\subsection*{{{escape_latex(data)}}}")
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
        elif kind == "paragraph":
            body.append(escape_latex(data) + "\n")
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
        elif kind == "image":
            alt, rel_path = data.split("|||", 1)
            rel = rel_path.replace('\\', '/')
            body.append(
                "\\begin{figure}[h!]\n"
                "\\centering\n"
                f"\\includegraphics[width=0.9\\textwidth]{{{escape_latex(rel)}}}\n"
                f"\\caption*{{{escape_latex(alt)}}}\n"
                "\\end{figure}"
            )
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
        elif kind == "pagebreak":
            if not last_emitted_pagebreak:
                body.append("\\newpage")
                started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = True

    tex = (
        "\\documentclass[12pt,a4paper]{article}\n"
        "\\usepackage[left=1.5cm,right=1.5cm,top=1.5cm,bottom=1.5cm]{geometry}\n"
        "\\usepackage{setspace}\n"
        "\\usepackage{graphicx}\n"
        "\\usepackage{needspace}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{mathptmx}\n"
        "\\setstretch{1.5}\n"
        "\\setlength{\\parindent}{0.5in}\n"
        "\\clubpenalty=10000\n"
        "\\widowpenalty=10000\n"
        "\\displaywidowpenalty=10000\n"
        "\\begin{document}\n\n"
        + "\n\n".join(body)
        + "\n\n\\end{document}\n"
    )
    out_path.write_text(tex, encoding="utf-8")


def _fit_image_width(img_path: Path, max_width_cm: float = 16.0) -> float:
    try:
        img = ImageReader(str(img_path))
        iw, ih = img.getSize()
        if iw <= 0 or ih <= 0:
            return max_width_cm * cm
        ratio = ih / iw
        width_cm = max_width_cm
        height_cm = width_cm * ratio
        if height_cm > 20:
            scale = 20 / height_cm
            width_cm *= scale
        return width_cm * cm
    except Exception:
        return max_width_cm * cm


def build_pdf_reportlab(md_path: Path, out_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    blocks = normalize_blocks(list(iter_markdown_blocks(text)))
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Times-Bold",
        fontSize=18,
        leading=24,
        spaceBefore=10,
        spaceAfter=8,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=16,
        leading=22,
        spaceBefore=8,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=14,
        leading=21,
        firstLineIndent=0.5 * 72,
        spaceBefore=2,
        spaceAfter=4,
    )
    refs = ParagraphStyle(
        "Refs",
        parent=body,
        firstLineIndent=0,
        leftIndent=0,
        spaceBefore=1,
        spaceAfter=8,
    )

    story = []
    started = False
    chapter_just_emitted = False
    last_emitted_pagebreak = False
    in_references = False
    for kind, data in blocks:
        if kind == "chaptertitle":
            if started and not last_emitted_pagebreak:
                story.append(PageBreak())
            chapter_style = ParagraphStyle(
                "ChapterTitle",
                parent=styles["Heading1"],
                fontName="Times-Bold",
                fontSize=36,
                leading=42,
                alignment=1,
                spaceBefore=260,
                spaceAfter=260,
            )
            story.append(Paragraph(data, chapter_style))
            story.append(PageBreak())
            started = True
            chapter_just_emitted = True
            last_emitted_pagebreak = True
        elif kind == "h1":
            if started and not chapter_just_emitted and not last_emitted_pagebreak:
                story.append(PageBreak())
            story.append(CondPageBreak(h1.leading + (4 * body.leading)))
            story.append(Paragraph(data, h1))
            in_references = data.strip().upper() == "VIII. REFERENCES"
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
        elif kind == "h2":
            story.append(CondPageBreak(h2.leading + (4 * body.leading)))
            story.append(Paragraph(data, h2))
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
        elif kind == "paragraph":
            story.append(Paragraph(data, refs if in_references else body))
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
        elif kind == "image":
            _, rel_path = data.split("|||", 1)
            img_path = (md_path.parent / rel_path).resolve()
            if img_path.exists():
                width = _fit_image_width(img_path)
                img_reader = ImageReader(str(img_path))
                iw, ih = img_reader.getSize()
                if iw > 0:
                    height = width * (ih / iw)
                else:
                    height = 8 * cm
                img = Image(str(img_path), width=width, height=height, hAlign="CENTER")
                story.append(Spacer(1, 8))
                story.append(img)
                story.append(Spacer(1, 8))
            started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = False
        elif kind == "pagebreak":
            if not last_emitted_pagebreak:
                story.append(PageBreak())
                started = True
            chapter_just_emitted = False
            last_emitted_pagebreak = True

    doc.build(story)


def build_pdf_xhtml2pdf(md_path: Path, out_pdf: Path, out_html: Path) -> None:
    css = (PROD_ROOT / "templates" / "print.css").read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")
    md_text = re.sub(
        r"\[\[CHAPTER_TITLE:(.+?)\]\]",
        r'<div class="page-break"></div><div class="chapter-title">\1</div><div class="page-break"></div>',
        md_text,
    )
    html_body = markdown2.markdown(md_text, extras=["tables", "fenced-code-blocks", "cuddled-lists"])
    html_body = re.sub(
        r'(<img[^>]+src=")([^":]+?)(")',
        lambda m: (
            m.group(1)
            + str((md_path.parent / unquote(m.group(2))).resolve())
            + m.group(3)
        ),
        html_body,
    )
    html = (
        "<html><head><meta charset='utf-8'><style>"
        + css
        + "</style></head><body>"
        + html_body
        + "</body></html>"
    )

    out_html.write_text(html, encoding="utf-8")
    with out_pdf.open("wb") as f:
        pisa.CreatePDF(src=html, dest=f, path=str(md_path.parent))


def build_with_pandoc(md_path: Path, out_tex: Path) -> None:
    md_text = md_path.read_text(encoding="utf-8")
    md_text = re.sub(r"\[\[CHAPTER_TITLE:(.+?)\]\]", r"\n\n# \1\n\n<div class=\"page-break\"></div>\n\n", md_text)
    tmp_md = METHOD_B_DIR / "_pandoc_input.md"
    tmp_md.write_text(md_text, encoding="utf-8")
    pypandoc.convert_file(
        str(tmp_md),
        to="latex",
        format="md",
        outputfile=str(out_tex),
        extra_args=["--resource-path", str(md_path.parent)],
    )
    tmp_md.unlink(missing_ok=True)


def run_method_a(md_path: Path) -> None:
    build_docx(md_path, METHOD_A_DIR / "research_method_a.docx")
    build_tex(md_path, METHOD_A_DIR / "research_method_a.tex")
    build_pdf_reportlab(md_path, METHOD_A_DIR / "research_method_a.pdf")


def run_method_b(md_path: Path) -> None:
    build_docx(md_path, METHOD_B_DIR / "research_method_b.docx")
    build_with_pandoc(md_path, METHOD_B_DIR / "research_method_b.tex")
    build_pdf_xhtml2pdf(md_path, METHOD_B_DIR / "research_method_b.pdf", METHOD_B_DIR / "research_method_b.html")


def main() -> None:
    ensure_dirs()
    copy_figure_assets()
    md_path = assemble_markdown()
    run_method_a(md_path)
    run_method_b(md_path)
    print("Production pipeline completed.")
    print(f"Comprehensive markdown: {md_path}")
    print(f"Method A outputs: {METHOD_A_DIR}")
    print(f"Method B outputs: {METHOD_B_DIR}")


if __name__ == "__main__":
    main()
