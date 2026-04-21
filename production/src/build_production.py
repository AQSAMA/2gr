#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.shared import Pt, Inches, Cm
from docx.oxml.ns import qn
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
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


def collect_figure_md_files() -> list[Path]:
    files = sorted(FIGURES_DIR.glob("*.md"), key=lambda p: p.name)
    return files


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

    for fig_md in collect_figure_md_files():
        fig_text = fig_md.read_text(encoding="utf-8")
        fig_text = rewrite_local_figure_links(fig_text)
        parts.append(fig_text.strip())

    merged = "\n\n".join(parts).strip() + "\n"
    merged = normalize_page_breaks(merged)

    out_path = ASSEMBLED_DIR / "comprehensive_research.md"
    out_path.write_text(merged, encoding="utf-8")
    shutil.copy2(out_path, METHOD_A_DIR / "comprehensive_research.md")
    shutil.copy2(out_path, METHOD_B_DIR / "comprehensive_research.md")
    return out_path


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

        h1 = re.match(r"^#\s+(.+)$", line)
        h2 = re.match(r"^##\s+(.+)$", line)
        img = re.match(r"^!\[([^\]]*)\]\(([^\)]+)\)", line.strip())

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
    doc = Document()

    section = doc.sections[0]
    section.left_margin = Cm(3)
    section.right_margin = Cm(2)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(14)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.first_line_indent = Inches(0.5)

    for kind, data in iter_markdown_blocks(text):
        if kind == "h1":
            p = doc.add_paragraph(data)
            p.style = doc.styles["Heading 1"]
            p.paragraph_format.first_line_indent = Inches(0)
            continue
        if kind == "h2":
            p = doc.add_paragraph(data)
            p.style = doc.styles["Heading 2"]
            p.paragraph_format.first_line_indent = Inches(0)
            continue
        if kind == "paragraph":
            p = doc.add_paragraph(data)
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.first_line_indent = Inches(0.5)
            continue
        if kind == "image":
            _, rel_path = data.split("|||", 1)
            img_path = (md_path.parent / rel_path).resolve()
            if img_path.exists():
                p = doc.add_paragraph()
                p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                run = p.add_run()
                run.add_picture(str(img_path), width=Inches(6.3))
            continue
        if kind == "pagebreak":
            doc.add_page_break()

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
    body: list[str] = []

    for kind, data in iter_markdown_blocks(text):
        if kind == "h1":
            body.append(f"\\section*{{{escape_latex(data)}}}")
        elif kind == "h2":
            body.append(f"\\subsection*{{{escape_latex(data)}}}")
        elif kind == "paragraph":
            body.append(escape_latex(data) + "\n")
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
        elif kind == "pagebreak":
            body.append("\\newpage")

    tex = (
        "\\documentclass[12pt,a4paper]{article}\n"
        "\\usepackage[left=3cm,right=2cm,top=2cm,bottom=2cm]{geometry}\n"
        "\\usepackage{setspace}\n"
        "\\usepackage{graphicx}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{mathptmx}\n"
        "\\setstretch{1.5}\n"
        "\\setlength{\\parindent}{0.5in}\n"
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
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=3 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
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

    story = []
    for kind, data in iter_markdown_blocks(text):
        if kind == "h1":
            story.append(Paragraph(data, h1))
        elif kind == "h2":
            story.append(Paragraph(data, h2))
        elif kind == "paragraph":
            story.append(Paragraph(data, body))
        elif kind == "image":
            _, rel_path = data.split("|||", 1)
            img_path = (md_path.parent / rel_path).resolve()
            if img_path.exists():
                width = _fit_image_width(img_path)
                img = Image(str(img_path), width=width, preserveAspectRatio=True, hAlign="CENTER")
                story.append(Spacer(1, 8))
                story.append(img)
                story.append(Spacer(1, 8))
        elif kind == "pagebreak":
            story.append(PageBreak())

    doc.build(story)


def build_pdf_xhtml2pdf(md_path: Path, out_pdf: Path, out_html: Path) -> None:
    css = (PROD_ROOT / "templates" / "print.css").read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")
    html_body = markdown2.markdown(md_text, extras=["tables", "fenced-code-blocks", "cuddled-lists"])
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


def build_with_pandoc(md_path: Path, out_docx: Path, out_tex: Path) -> None:
    pypandoc.convert_file(
        str(md_path),
        to="docx",
        format="md",
        outputfile=str(out_docx),
        extra_args=["--resource-path", str(md_path.parent)],
    )
    pypandoc.convert_file(
        str(md_path),
        to="latex",
        format="md",
        outputfile=str(out_tex),
        extra_args=["--resource-path", str(md_path.parent)],
    )


def run_method_a(md_path: Path) -> None:
    build_docx(md_path, METHOD_A_DIR / "research_method_a.docx")
    build_tex(md_path, METHOD_A_DIR / "research_method_a.tex")
    build_pdf_reportlab(md_path, METHOD_A_DIR / "research_method_a.pdf")


def run_method_b(md_path: Path) -> None:
    build_with_pandoc(md_path, METHOD_B_DIR / "research_method_b.docx", METHOD_B_DIR / "research_method_b.tex")
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
