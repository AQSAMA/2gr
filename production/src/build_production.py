#!/usr/bin/env python3
"""Method A (Python) production path.

Produces three publishing-ready outputs from the assembled Markdown
manuscript at ``production/assembled/comprehensive_research.md``:

    research_method_a.docx  - Microsoft Word document. PRIMARY deliverable.
    research_method_a.pdf   - Reportlab PDF (companion).
    research_method_a.tex   - Standalone LaTeX source (companion).

This is an independent build (NOT a copy of the Typst output). The visual
style is intentionally plain (no page borders, no decorative coloring), but
the document structure mirrors the Typst pipeline:

    * a formal cover page (logo, university header, title, students,
      supervisor, month/year),
    * preliminary pages with lower-roman page numbers (Certification,
      Dedication, Acknowledgment, Table of Contents, List of Figures,
      List of Abbreviations),
    * main matter from the Abstract onward with arabic page numbers,
    * page headers carrying the page number plus the chapter name as a
      running head once each chapter starts.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import unquote

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors as rl_colors
from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    Image,
    LongTable,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    TableStyle,
)


# ---------------------------------------------------------------------------
# Repository layout (kept stable - imported by build_typst.py and
# build_typst_content.py).
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
PROD_ROOT = REPO_ROOT / "production"
CONTENT_DIR = REPO_ROOT / "content"
FIGURES_DIR = REPO_ROOT / "figures"
REFERENCES_FILE = REPO_ROOT / "references.md"
ASSEMBLED_DIR = PROD_ROOT / "assembled"
METHOD_A_DIR = PROD_ROOT / "method_a_python"
PROD_FIGURES_DIR = PROD_ROOT / "figures"

CONTENT_FILES = [
    "00_cover.md",
    "00_abstract.md",
    "01_introduction.md",
    "02_literature_review.md",
    "03_methodology.md",
    "04_results.md",
    "05_discussion.md",
    "06_recommendations_conclusion.md",
]

APPENDIX_FILES: list[str] = []

CHAPTER_INSERTIONS = [
    ("# I. INTRODUCTION", "Chapter One", "Introduction"),
    ("# III. METHODOLOGY (ORIGINAL CROSS-SECTIONAL STUDY)", "Chapter Two", "Materials and Methods"),
    ("# IV. RESULTS", "Chapter Three", "Results"),
    ("# V. DISCUSSION", "Chapter Four", "Discussion"),
    ("# VI. RECOMMENDATIONS", "Chapter Five", "Conclusions and Suggestions"),
]


# ---------------------------------------------------------------------------
# Manuscript metadata (single source of truth shared with build_typst_content).
# ---------------------------------------------------------------------------
TITLE = "Psychiatric Medication Use and Public Acceptance in Iraq"
STUDENTS = [
    "Abdul Rahman Wakaa Ali",
    "Ali Basem Hammoud",
    "Shifa Safi Aboud",
    "Zainab Mashal Nayef",
]
SUPERVISOR = "Hameed Adnan"
SUPERVISOR_DEGREE = "Supervisor's Degree"
UNIVERSITY = "University of Al-Maarif"
COLLEGE = "College of Pharmacy"
DEPARTMENT = "Department of Clinical Pharmacy"
MONTH_YEAR = "May, 2026"

LOGO_CANDIDATES = (
    "University_logo.png",
    "university logo.png",
    "university_logo.png",
    "University logo.png",
    "University Logo.png",
    "almaarif logo.png",
    "al-maarif logo.png",
)

# These constants stay available for the Typst-content builder, which is
# styled. The Method A DOCX/PDF/TEX themselves do NOT use them - the
# Method A path keeps its plain visual style (no decorative borders,
# no decorative coloring).
NAVY_HEX = "102A43"
GOLD_HEX = "B58B2A"
INK_HEX = "111827"


def find_university_logo() -> Optional[Path]:
    """Locate the university logo PNG in the repo root or figures/."""
    search_dirs = (REPO_ROOT, FIGURES_DIR)
    for directory in search_dirs:
        for filename in LOGO_CANDIDATES:
            candidate = directory / filename
            if candidate.exists():
                return candidate
    for directory in search_dirs:
        for candidate in sorted(directory.glob("*.png")):
            lowered = candidate.name.lower()
            if "logo" in lowered or "maarif" in lowered:
                return candidate
    return None


# ---------------------------------------------------------------------------
# Markdown assembly (shared by Method A, Method B and typst_content).
# ---------------------------------------------------------------------------
def ensure_dirs() -> None:
    for d in [ASSEMBLED_DIR, METHOD_A_DIR, PROD_FIGURES_DIR]:
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
    for heading, chapter_number, chapter_name in CHAPTER_INSERTIONS:
        marker = f"\n\n[[CHAPTER_TITLE:{chapter_number}|||{chapter_name}]]\n\n{heading}"
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


def normalize_figure_captions(text: str) -> str:
    out_lines: list[str] = []
    image_pattern = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
    caption_pattern = re.compile(r"^\*\*Caption:\*\*\s*(.+?)\s*$")
    figure_no = 0
    last_image_out_idx: Optional[int] = None
    last_caption_consumed = True

    def build_image_line(caption: str, path: str) -> str:
        return f"![{caption}]({path})"

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        img_match = image_pattern.match(line.strip())
        cap_match = caption_pattern.match(line.strip())

        if img_match:
            figure_no += 1
            alt = img_match.group(1).strip() or "Figure"
            path = img_match.group(2).strip()
            normalized_caption = f"Figure {figure_no}. {alt}"
            out_lines.append(build_image_line(normalized_caption, path))
            last_image_out_idx = len(out_lines) - 1
            last_caption_consumed = False
            continue

        if cap_match and last_image_out_idx is not None and not last_caption_consumed:
            caption_text = cap_match.group(1).strip()
            image_line = out_lines[last_image_out_idx]
            existing = image_pattern.match(image_line)
            if existing:
                path = existing.group(2).strip()
                current_label = existing.group(1).strip()
                num_match = re.match(r"^Figure\s+(\d+)\.\s*", current_label)
                if num_match:
                    figure_number = num_match.group(1)
                    normalized_caption = f"Figure {figure_number}. {caption_text}"
                    out_lines[last_image_out_idx] = build_image_line(normalized_caption, path)
                    last_caption_consumed = True
                    continue

        out_lines.append(line)
        if line.strip():
            last_image_out_idx = None
            last_caption_consumed = True

    return "\n".join(out_lines)


def assemble_markdown() -> Path:
    parts: list[str] = []

    for name in CONTENT_FILES:
        text = (CONTENT_DIR / name).read_text(encoding="utf-8")
        parts.append(text.strip())

    for name in APPENDIX_FILES:
        appendix_path = CONTENT_DIR / name
        if appendix_path.exists():
            parts.append(appendix_path.read_text(encoding="utf-8").strip())

    parts.append("# VIII. REFERENCES")
    parts.append(REFERENCES_FILE.read_text(encoding="utf-8").strip())

    merged = "\n\n".join(parts).strip() + "\n"
    merged = normalize_page_breaks(merged)
    merged = inject_chapter_title_pages(merged)
    merged = transform_inline_figure_links(merged)
    merged = normalize_figure_captions(merged)

    out_path = ASSEMBLED_DIR / "comprehensive_research.md"
    out_path.write_text(merged, encoding="utf-8")
    shutil.copy2(out_path, METHOD_A_DIR / "comprehensive_research.md")
    return out_path


# ---------------------------------------------------------------------------
# Markdown table parsing helpers (shared by all renderers).
# ---------------------------------------------------------------------------
_TABLE_LINE_RE = re.compile(r"^\s*\|.*\|\s*$")


def _split_table_row(line: str) -> list[str]:
    """Split a markdown table row into stripped cell values."""
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|"):
        inner = inner[:-1]
    return [cell.strip() for cell in inner.split("|")]


def _is_table_separator_cells(cells: list[str]) -> bool:
    """A separator row contains only dashes (with optional leading/trailing colons)."""
    if not cells:
        return False
    pattern = re.compile(r"^:?-{3,}:?$")
    return all(pattern.fullmatch(cell.strip()) for cell in cells if cell.strip() != "")


def _table_alignments(separator_cells: list[str]) -> list[str]:
    """Return one of 'left', 'center', 'right' per separator cell."""
    out: list[str] = []
    for cell in separator_cells:
        c = cell.strip()
        left = c.startswith(":")
        right = c.endswith(":")
        if left and right:
            out.append("center")
        elif right:
            out.append("right")
        else:
            out.append("left")
    return out


def _extract_markdown_tables(text: str) -> tuple[str, list[str]]:
    """Replace markdown tables in ``text`` with placeholders.

    Returns the rewritten text plus a list of JSON-encoded table payloads.
    Each payload contains ``headers``, ``rows`` and ``aligns`` so renderers
    can reproduce the table without re-parsing markdown.
    """
    lines = text.splitlines()
    tables: list[str] = []
    out_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _TABLE_LINE_RE.match(line) and i + 1 < len(lines) and _TABLE_LINE_RE.match(lines[i + 1]):
            sep_cells = _split_table_row(lines[i + 1])
            if _is_table_separator_cells(sep_cells):
                headers = _split_table_row(line)
                aligns = _table_alignments(sep_cells)
                # Pad alignments to header length if separator was shorter.
                while len(aligns) < len(headers):
                    aligns.append("left")
                rows: list[list[str]] = []
                j = i + 2
                while j < len(lines) and _TABLE_LINE_RE.match(lines[j]):
                    rows.append(_split_table_row(lines[j]))
                    j += 1
                payload = json.dumps(
                    {"headers": headers, "rows": rows, "aligns": aligns},
                    ensure_ascii=False,
                )
                tables.append(payload)
                out_lines.append(f"<<<MD_TABLE_{len(tables) - 1}>>>")
                i = j
                continue
        out_lines.append(line)
        i += 1
    return "\n".join(out_lines), tables


def iter_markdown_blocks(text: str) -> Iterable[tuple[str, str]]:
    text, tables = _extract_markdown_tables(text)
    paragraph_lines: list[str] = []
    for raw in text.splitlines():
        line = raw.rstrip()

        if line.strip() == '<div class="page-break"></div>':
            if paragraph_lines:
                yield ("paragraph", " ".join(paragraph_lines).strip())
                paragraph_lines = []
            yield ("pagebreak", "")
            continue

        table_marker = re.match(r"^<<<MD_TABLE_(\d+)>>>$", line.strip())
        if table_marker:
            if paragraph_lines:
                yield ("paragraph", " ".join(paragraph_lines).strip())
                paragraph_lines = []
            idx = int(table_marker.group(1))
            if 0 <= idx < len(tables):
                yield ("table", tables[idx])
            continue

        front_matter = re.match(r"^\[\[FRONT_MATTER:(.+)\]\]$", line.strip())
        if front_matter:
            if paragraph_lines:
                yield ("paragraph", " ".join(paragraph_lines).strip())
                paragraph_lines = []
            yield ("frontmatter", front_matter.group(1).strip())
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


def clean_inline_markdown(value: str) -> str:
    """Strip light Markdown formatting (bold/italic/code/links) from a run."""
    value = value.replace("\u00a0", " ")
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def collect_thesis_blocks(md_path: Path) -> list[tuple[str, str]]:
    """Return main-matter blocks from the assembled manuscript.

    The cover-content placeholders in ``content/00_cover.md`` are skipped
    (everything before the ``# ABSTRACT`` heading) because the cover and
    preliminary pages are produced programmatically.
    """
    blocks: list[tuple[str, str]] = []
    skip_cover = True

    for kind, data in iter_markdown_blocks(md_path.read_text(encoding="utf-8")):
        if skip_cover:
            if kind == "h1" and data.strip().upper() == "ABSTRACT":
                skip_cover = False
            else:
                continue

        if kind == "chaptertitle":
            blocks.append(("chapter", data))
            continue
        if kind == "h1":
            blocks.append(("h1", clean_inline_markdown(data)))
            continue
        if kind == "h2":
            blocks.append(("h2", clean_inline_markdown(data)))
            continue
        if kind == "paragraph":
            text = clean_inline_markdown(data)
            if text:
                blocks.append(("paragraph", text))
            continue
        if kind == "image":
            caption, rel_path = data.split("|||", 1)
            blocks.append(("image", f"{clean_inline_markdown(caption)}|||{rel_path}"))
            continue
        if kind == "table":
            blocks.append(("table", data))
            continue
        if kind == "pagebreak":
            blocks.append(("pagebreak", ""))
            continue

    return blocks


# ---------------------------------------------------------------------------
# DOCX low-level OOXML helpers (used by both Method A and typst_content).
# ---------------------------------------------------------------------------
def set_run_font(run, size: float | None = None, bold: bool | None = None,
                 color: str | None = None, italic: bool | None = None) -> None:
    from docx.shared import RGBColor
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


def set_paragraph_border(paragraph, color: str = GOLD_HEX, size: str = "8") -> None:
    """Add a four-edge border around a paragraph (used by build_typst_content,
    NOT by the plain Method A DOCX)."""
    p_pr = paragraph._p.get_or_add_pPr()
    borders = p_pr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        p_pr.append(borders)
    for edge in ("top", "left", "bottom", "right"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "4")
        element.set(qn("w:color"), color)
        borders.append(element)


def set_section_page_numbering(section, fmt: str, start: int | None) -> None:
    sect_pr = section._sectPr
    pg_num = sect_pr.find(qn("w:pgNumType"))
    if pg_num is None:
        pg_num = OxmlElement("w:pgNumType")
        sect_pr.append(pg_num)
    pg_num.set(qn("w:fmt"), fmt)
    if start is not None:
        pg_num.set(qn("w:start"), str(start))
    elif pg_num.get(qn("w:start")) is not None:
        # Continue numbering across sections by removing any inherited start.
        del pg_num.attrib[qn("w:start")]


def add_field_run(paragraph, instruction: str, default_text: str = " ") -> None:
    """Insert a Word field run (PAGE / TOC / SEQ).

    Word refreshes the field on first open (or when the user presses F9 /
    right-clicks -> Update Field).
    """
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    run._r.append(fld_begin)

    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    run._r.append(instr)

    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    run._r.append(fld_sep)

    result = OxmlElement("w:t")
    result.set(qn("xml:space"), "preserve")
    result.text = default_text
    run._r.append(result)

    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_end)


def configure_section(
    section,
    *,
    numbered: bool,
    number_format: str = "decimal",
    start: int | None = None,
    running_head: str = "",
    suppress_first_page_header: bool = False,
) -> None:
    """Apply margins, page numbering, and the page header to a Word section.

    No page borders or decorative styling are applied; this keeps the plain
    visual style of the Method A DOCX.
    """
    section.left_margin = Cm(1.5)
    section.right_margin = Cm(1.5)
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)

    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    section.different_first_page_header_footer = suppress_first_page_header

    for paragraph in section.header.paragraphs:
        paragraph.clear()
    if section.different_first_page_header_footer:
        for paragraph in section.first_page_header.paragraphs:
            paragraph.clear()

    if numbered:
        set_section_page_numbering(section, number_format, start)

        head = section.header.paragraphs[0]
        head.alignment = WD_ALIGN_PARAGRAPH.LEFT
        head.paragraph_format.first_line_indent = Inches(0)
        if running_head:
            run = head.add_run(running_head)
            set_run_font(run, size=10)

        page_para = section.header.add_paragraph()
        page_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        page_para.paragraph_format.first_line_indent = Inches(0)
        marker = page_para.add_run()
        set_run_font(marker, size=10)
        add_field_run(page_para, "PAGE")

        if section.different_first_page_header_footer:
            # Chapter title pages still show the page number, but no
            # running head.
            first_page = section.first_page_header.paragraphs[0]
            first_page.alignment = WD_ALIGN_PARAGRAPH.CENTER
            first_page.paragraph_format.first_line_indent = Inches(0)
            add_field_run(first_page, "PAGE")
    else:
        # Cover page: clean header, no number.
        set_section_page_numbering(section, "decimal", None)


def setup_docx_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(14)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.first_line_indent = Inches(0.5)

    for style_name, size in (("Heading 1", 18), ("Heading 2", 16)):
        style = doc.styles[style_name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = True


# ---------------------------------------------------------------------------
# DOCX content helpers
# ---------------------------------------------------------------------------
def _add_centered_paragraph(
    doc: Document,
    text: str = "",
    size: float = 14,
    bold: bool = False,
    italic: bool = False,
    space_before: float | None = None,
    space_after: float | None = None,
):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Inches(0)
    if space_before is not None:
        paragraph.paragraph_format.space_before = Pt(space_before)
    if space_after is not None:
        paragraph.paragraph_format.space_after = Pt(space_after)
    if text:
        run = paragraph.add_run(text)
        set_run_font(run, size=size, bold=bold, italic=italic)
    return paragraph


def _add_front_title(doc: Document, title: str) -> None:
    """Plain centered front-matter section title (no border, no color)."""
    paragraph = _add_centered_paragraph(doc, title, size=20, bold=True)
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(14)


def _add_body_paragraph(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph(text)
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.first_line_indent = Inches(0.5)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def _add_reference_paragraph(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph(text)
    paragraph.paragraph_format.first_line_indent = Inches(-0.5)
    paragraph.paragraph_format.left_indent = Inches(0.5)
    paragraph.paragraph_format.space_before = Pt(3)
    paragraph.paragraph_format.space_after = Pt(5)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for run in paragraph.runs:
        set_run_font(run, size=12)


def _docx_alignment_for(align: str):
    if align == "right":
        return WD_ALIGN_PARAGRAPH.RIGHT
    if align == "center":
        return WD_ALIGN_PARAGRAPH.CENTER
    return WD_ALIGN_PARAGRAPH.LEFT


def _set_table_full_width(table) -> None:
    """Force a python-docx table to span 100% of the text-area width.

    Sets ``tblW`` to ``pct=5000`` (100% in Word's 1/50ths-of-a-percent units)
    and distributes the same percentage across every cell so columns stay
    even regardless of content. Also pins ``tblLayout`` to ``fixed`` so Word
    honors the column widths instead of shrinking to content.
    """
    tbl = table._tbl
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = OxmlElement("w:tblPr")
        tbl.insert(0, tblPr)

    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    tblW.set(qn("w:type"), "pct")
    tblW.set(qn("w:w"), "5000")

    tblLayout = tblPr.find(qn("w:tblLayout"))
    if tblLayout is None:
        tblLayout = OxmlElement("w:tblLayout")
        tblPr.append(tblLayout)
    tblLayout.set(qn("w:type"), "fixed")

    table.autofit = False
    table.allow_autofit = False

    cols = len(table.columns)
    if cols == 0:
        return
    per_col_pct = str(5000 // cols)
    for row in table.rows:
        for cell in row.cells:
            tc = cell._tc
            tcPr = tc.find(qn("w:tcPr"))
            if tcPr is None:
                tcPr = OxmlElement("w:tcPr")
                tc.insert(0, tcPr)
            tcW = tcPr.find(qn("w:tcW"))
            if tcW is None:
                tcW = OxmlElement("w:tcW")
                tcPr.append(tcW)
            tcW.set(qn("w:type"), "pct")
            tcW.set(qn("w:w"), per_col_pct)


def _add_markdown_table(
    doc: Document,
    payload: str,
    *,
    body_size: float = 10.0,
    header_size: float = 10.0,
) -> None:
    """Render a markdown-table JSON payload as a Word table.

    Cells use Times New Roman with sensible defaults for academic tables
    (10pt body, bold headers, alignment carried from the markdown spec).
    """
    try:
        data = json.loads(payload)
    except (TypeError, ValueError):
        return
    headers: list[str] = data.get("headers", [])
    rows: list[list[str]] = data.get("rows", [])
    aligns: list[str] = data.get("aligns", [])
    if not headers and not rows:
        return
    col_count = max(len(headers), max((len(r) for r in rows), default=0))
    if col_count == 0:
        return

    table = doc.add_table(rows=1 + len(rows), cols=col_count)
    table.style = "Table Grid"
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _set_table_full_width(table)

    def _set_cell(cell, value: str, *, bold: bool, size: float, align: str) -> None:
        cell.text = ""
        paragraph = cell.paragraphs[0]
        paragraph.alignment = _docx_alignment_for(align)
        paragraph.paragraph_format.first_line_indent = Inches(0)
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 1.15
        run = paragraph.add_run(clean_inline_markdown(value))
        set_run_font(run, size=size, bold=bold)

    header_row = table.rows[0]
    for col in range(col_count):
        value = headers[col] if col < len(headers) else ""
        align = aligns[col] if col < len(aligns) else "left"
        _set_cell(header_row.cells[col], value, bold=True, size=header_size, align=align)

    for r_idx, row in enumerate(rows, start=1):
        for col in range(col_count):
            value = row[col] if col < len(row) else ""
            align = aligns[col] if col < len(aligns) else "left"
            _set_cell(table.rows[r_idx].cells[col], value, bold=False, size=body_size, align=align)

    # A short trailing paragraph keeps tables visually separated from the
    # next block without forcing a page break.
    spacer = doc.add_paragraph()
    spacer.paragraph_format.first_line_indent = Inches(0)
    spacer.paragraph_format.space_after = Pt(6)


def _add_figure_caption(doc: Document, caption_text: str) -> None:
    cleaned = re.sub(r"^Figure\s+\d+\.\s*", "", caption_text).strip()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(8)
    label = p.add_run("Figure ")
    set_run_font(label, size=12, bold=True)
    add_field_run(p, r"SEQ Figure \* ARABIC", default_text="0")
    tail = p.add_run(f". {cleaned}")
    set_run_font(tail, size=12)


def _add_cover_page(doc: Document) -> None:
    """Plain cover page: logo, institutional header, title, students,
    supervisor, month/year. No frame, no decorative coloring."""
    logo_path = find_university_logo()
    if logo_path is not None:
        holder = doc.add_paragraph()
        holder.alignment = WD_ALIGN_PARAGRAPH.CENTER
        holder.paragraph_format.first_line_indent = Inches(0)
        holder.paragraph_format.space_after = Pt(2)
        run = holder.add_run()
        run.add_picture(str(logo_path), width=Inches(0.95))

    for line in [
        "Republic of Iraq",
        "Ministry of Higher Education and Scientific Research",
        UNIVERSITY,
        COLLEGE,
    ]:
        _add_centered_paragraph(doc, line, size=14, bold=True)

    _add_centered_paragraph(
        doc, TITLE, size=22, bold=True,
        space_before=20, space_after=18,
    )

    _add_centered_paragraph(doc, "A Project Submitted to", size=14)
    _add_centered_paragraph(
        doc,
        f"The {COLLEGE}, {UNIVERSITY}, {DEPARTMENT}, in Partial Fulfillment "
        "for the Bachelor of Pharmacy",
        size=13,
    )

    _add_centered_paragraph(doc, "By", size=14, bold=True, space_before=12)
    for student in STUDENTS:
        _add_centered_paragraph(doc, student, size=18, bold=True)

    _add_centered_paragraph(doc, "Supervised by:", size=14, bold=True, space_before=12)
    _add_centered_paragraph(doc, SUPERVISOR, size=18, bold=True)
    _add_centered_paragraph(doc, SUPERVISOR_DEGREE, size=14)
    _add_centered_paragraph(doc, MONTH_YEAR, size=14, space_before=14)


ABBREVIATIONS = [
    ("AOR", "Adjusted Odds Ratio"),
    ("CI", "Confidence Interval"),
    ("LLR", "Likelihood Ratio Test"),
    ("MLE", "Maximum Likelihood Estimation"),
    ("OR", "Odds Ratio"),
    ("PTSD", "Post-Traumatic Stress Disorder"),
    ("RRR", "Relative Risk Ratio"),
    ("Q6/Q7/Q8/Q9/Q11/Q12/Q13/Q31",
     "Survey question item codes used in analysis and reporting"),
    ("R\u00b2",
     "Coefficient of determination, reported as pseudo R\u00b2 in logistic "
     "model fit summaries"),
]


def _add_preliminary_pages(doc: Document) -> None:
    # 1. Certification of the Supervisor
    _add_front_title(doc, "Certification of the Supervisor")
    _add_body_paragraph(
        doc,
        f"I certify that this project entitled \u201c{TITLE}\u201d was prepared "
        f"by the fifth-year students {', '.join(STUDENTS)} under my supervision at "
        f"the {COLLEGE}/{UNIVERSITY} in partial fulfillment of the graduation "
        "requirements for the Bachelor Degree in Pharmacy.",
    )
    sig = doc.add_paragraph()
    sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    sig.paragraph_format.first_line_indent = Inches(0)
    sig.paragraph_format.space_before = Pt(18)
    sig_run = sig.add_run(f"Supervisor's name: {SUPERVISOR}")
    set_run_font(sig_run, size=14, bold=True)
    doc.add_page_break()

    # 2. Dedication
    _add_front_title(doc, "Dedication")
    _add_body_paragraph(
        doc,
        "We dedicate this work to our families, whose patience made long study "
        "days easier, and to every Iraqi patient who deserves safe, respectful, "
        "and evidence-based mental health care. We also dedicate it to the "
        "teachers and pharmacists who taught us that science becomes meaningful "
        "when it serves people with honesty and compassion.",
    )
    doc.add_page_break()

    # 3. Acknowledgment
    _add_front_title(doc, "Acknowledgment")
    _add_body_paragraph(
        doc,
        f"We thank Dr. {SUPERVISOR} for his supervision, guidance, and careful "
        f"advice throughout this project. We are also grateful to the {COLLEGE} "
        f"at {UNIVERSITY}, to the participants who gave their time to answer the "
        "survey, and to our colleagues who supported the data collection and "
        "revision process.",
    )
    doc.add_page_break()

    # 4. Table of Contents (Word TOC field)
    _add_front_title(doc, "Table of Contents")
    note = doc.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    note.paragraph_format.first_line_indent = Inches(0)
    note_run = note.add_run("Right-click and choose Update Field, or press F9 in Word, to refresh.")
    set_run_font(note_run, size=10, italic=True)
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    add_field_run(p, r'TOC \o "1-2" \h \z \u', default_text="(Update field in Word.)")
    doc.add_page_break()

    # 5. List of Figures
    _add_front_title(doc, "List of Figures")
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    add_field_run(p, r'TOC \h \z \c "Figure"', default_text="(Update field in Word.)")
    doc.add_page_break()

    # 6. List of Abbreviations
    _add_front_title(doc, "List of Abbreviations")
    for short, long in ABBREVIATIONS:
        para = doc.add_paragraph()
        para.paragraph_format.first_line_indent = Inches(0)
        para.paragraph_format.space_after = Pt(2)
        run_short = para.add_run(f"{short}: ")
        set_run_font(run_short, size=14, bold=True)
        run_long = para.add_run(long)
        set_run_font(run_long, size=14)


def _add_chapter_title_page(doc: Document, chapter_number: str, chapter_name: str) -> None:
    """Plain centered chapter title page with em-dash rules above and below.

    Matches the original Method A style: no decorative coloring, no frame.
    """
    spacer = doc.add_paragraph()
    spacer.paragraph_format.first_line_indent = Inches(0)
    spacer.paragraph_format.space_before = Inches(3.0)

    rule_top = doc.add_paragraph()
    rule_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rule_top.paragraph_format.first_line_indent = Inches(0)
    rule_top.paragraph_format.space_after = Pt(8)
    rule_top_run = rule_top.add_run("\u2500" * 12)
    set_run_font(rule_top_run, size=18)

    _add_centered_paragraph(
        doc, chapter_number, size=32, bold=True,
        space_before=4, space_after=8,
    )
    _add_centered_paragraph(
        doc, chapter_name, size=18, bold=True,
        space_before=0, space_after=10,
    )

    rule_bottom = doc.add_paragraph()
    rule_bottom.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rule_bottom.paragraph_format.first_line_indent = Inches(0)
    rule_bottom_run = rule_bottom.add_run("\u2500" * 12)
    set_run_font(rule_bottom_run, size=18)


# ---------------------------------------------------------------------------
# DOCX builder
# ---------------------------------------------------------------------------
def build_docx(md_path: Path, out_path: Path) -> None:
    blocks = collect_thesis_blocks(md_path)
    doc = Document()
    setup_docx_styles(doc)

    # Section 0: cover. No page numbers, no decorations.
    configure_section(doc.sections[0], numbered=False)
    _add_cover_page(doc)

    # Section 1: preliminary pages. Lower-roman numerals starting at i.
    prelim = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_section(
        prelim,
        numbered=True,
        number_format="lowerRoman",
        start=1,
    )
    _add_preliminary_pages(doc)

    # Section 2: main matter starting at the Abstract. Decimal restart at 1.
    main_section = doc.add_section(WD_SECTION.NEW_PAGE)
    configure_section(
        main_section,
        numbered=True,
        number_format="decimal",
        start=1,
        running_head="",
    )

    in_references = False
    chapter_just_emitted = False
    started = False

    for kind, data in blocks:
        if kind == "chapter":
            chapter_number, chapter_name = (data.split("|||", 1) + [""])[:2]
            chapter_section = doc.add_section(WD_SECTION.NEW_PAGE)
            configure_section(
                chapter_section,
                numbered=True,
                number_format="decimal",
                start=None,
                running_head=chapter_name,
                suppress_first_page_header=True,
            )
            _add_chapter_title_page(doc, chapter_number, chapter_name)
            doc.add_page_break()
            chapter_just_emitted = True
            started = True
            continue

        if kind == "h1":
            if started and not chapter_just_emitted:
                doc.add_page_break()
            paragraph = doc.add_paragraph(data)
            paragraph.style = doc.styles["Heading 1"]
            paragraph.paragraph_format.first_line_indent = Inches(0)
            paragraph.paragraph_format.space_after = Pt(8)
            in_references = data.strip().upper() == "VIII. REFERENCES"
            chapter_just_emitted = False
            started = True
            continue

        if kind == "h2":
            paragraph = doc.add_paragraph(data)
            paragraph.style = doc.styles["Heading 2"]
            paragraph.paragraph_format.first_line_indent = Inches(0)
            chapter_just_emitted = False
            started = True
            continue

        if kind == "paragraph":
            if in_references:
                _add_reference_paragraph(doc, data)
            else:
                _add_body_paragraph(doc, data)
            chapter_just_emitted = False
            started = True
            continue

        if kind == "image":
            caption, rel_path = data.split("|||", 1)
            img_path = (md_path.parent / rel_path).resolve()
            if img_path.exists():
                holder = doc.add_paragraph()
                holder.alignment = WD_ALIGN_PARAGRAPH.CENTER
                holder.paragraph_format.first_line_indent = Inches(0)
                holder.paragraph_format.space_before = Pt(6)
                run = holder.add_run()
                run.add_picture(str(img_path), width=Inches(6.1))
                _add_figure_caption(doc, caption)
            chapter_just_emitted = False
            started = True
            continue

        if kind == "table":
            _add_markdown_table(doc, data)
            chapter_just_emitted = False
            started = True
            continue

        if kind == "pagebreak":
            doc.add_page_break()
            chapter_just_emitted = False
            started = True

    doc.save(out_path)


# ---------------------------------------------------------------------------
# LaTeX builder
# ---------------------------------------------------------------------------
def escape_latex(text: str) -> str:
    table = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(table.get(ch, ch) for ch in text)


def _latex_table_block(payload: str) -> str:
    """Render a markdown-table JSON payload as a LaTeX longtable."""
    try:
        data = json.loads(payload)
    except (TypeError, ValueError):
        return ""
    headers: list[str] = data.get("headers", [])
    rows: list[list[str]] = data.get("rows", [])
    aligns: list[str] = data.get("aligns", [])
    col_count = max(len(headers), max((len(r) for r in rows), default=0))
    if col_count == 0:
        return ""
    align_map = {"left": "l", "center": "c", "right": "r"}
    spec = "".join(align_map.get(aligns[i] if i < len(aligns) else "left", "l") for i in range(col_count))

    def cells(row: list[str]) -> str:
        padded = row + [""] * (col_count - len(row))
        return " & ".join(escape_latex(clean_inline_markdown(c)) for c in padded[:col_count])

    lines: list[str] = []
    lines.append("\\begin{center}")
    lines.append("\\small")
    lines.append("\\begin{tabular}{" + spec + "}")
    lines.append("\\hline")
    if headers:
        header_cells = [f"\\textbf{{{escape_latex(clean_inline_markdown(h))}}}" for h in headers]
        while len(header_cells) < col_count:
            header_cells.append("")
        lines.append(" & ".join(header_cells) + " \\\\")
        lines.append("\\hline")
    for row in rows:
        lines.append(cells(row) + " \\\\")
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    lines.append("\\end{center}")
    return "\n".join(lines)


def _latex_cover_block() -> list[str]:
    students_block = " \\\\ \n".join(escape_latex(s) for s in STUDENTS)
    logo_path = find_university_logo()
    logo_line = ""
    if logo_path is not None:
        try:
            rel = logo_path.relative_to(REPO_ROOT)
        except ValueError:
            rel = logo_path
        logo_line = (
            f"\\includegraphics[height=2.2cm]{{{escape_latex(str(rel).replace(chr(92), '/'))}}}\\\\[6pt]\n"
        )
    return [
        "\\begin{titlepage}",
        "\\thispagestyle{empty}",
        "\\begin{center}",
        logo_line,
        "{\\large\\bfseries Republic of Iraq}\\\\",
        "{\\large\\bfseries Ministry of Higher Education and Scientific Research}\\\\",
        f"{{\\large\\bfseries {escape_latex(UNIVERSITY)}}}\\\\",
        f"{{\\large\\bfseries {escape_latex(COLLEGE)}}}\\\\[28pt]",
        "{\\Large\\bfseries " + escape_latex(TITLE) + "}\\\\[22pt]",
        "{A Project Submitted to}\\\\",
        f"{{The {escape_latex(COLLEGE)}, {escape_latex(UNIVERSITY)}, {escape_latex(DEPARTMENT)},"
        " in Partial Fulfillment for the Bachelor of Pharmacy}}\\\\[14pt]",
        "{\\bfseries By}\\\\[6pt]",
        f"{{\\Large\\bfseries {students_block}}}\\\\[14pt]",
        "{\\bfseries Supervised by:}\\\\[4pt]",
        f"{{\\Large\\bfseries {escape_latex(SUPERVISOR)}}}\\\\",
        f"{{\\large {escape_latex(SUPERVISOR_DEGREE)}}}\\\\[14pt]",
        f"{{{escape_latex(MONTH_YEAR)}}}",
        "\\end{center}",
        "\\end{titlepage}",
    ]


def _latex_preliminary_block() -> list[str]:
    students = ", ".join(escape_latex(s) for s in STUDENTS)
    abbrev_lines = " \\\\ \n".join(
        f"\\textbf{{{escape_latex(short)}}}: {escape_latex(long)}"
        for short, long in ABBREVIATIONS
    )
    return [
        "\\pagenumbering{roman}",
        "\\setcounter{page}{1}",
        "\\section*{Certification of the Supervisor}",
        "\\addcontentsline{toc}{section}{Certification of the Supervisor}",
        "I certify that this project entitled ``" + escape_latex(TITLE) + "'' was prepared by the fifth-year students "
        + students
        + f" under my supervision at the {escape_latex(COLLEGE)}/{escape_latex(UNIVERSITY)} "
        "in partial fulfillment of the graduation requirements for the Bachelor Degree in Pharmacy.",
        "",
        f"\\begin{{flushright}}\\textbf{{Supervisor's name: {escape_latex(SUPERVISOR)}}}\\end{{flushright}}",
        "\\newpage",
        "\\section*{Dedication}",
        "\\addcontentsline{toc}{section}{Dedication}",
        "We dedicate this work to our families, whose patience made long study days easier, "
        "and to every Iraqi patient who deserves safe, respectful, and evidence-based mental health care. "
        "We also dedicate it to the teachers and pharmacists who taught us that science becomes meaningful "
        "when it serves people with honesty and compassion.",
        "\\newpage",
        "\\section*{Acknowledgment}",
        "\\addcontentsline{toc}{section}{Acknowledgment}",
        f"We thank Dr.\\ {escape_latex(SUPERVISOR)} for his supervision, guidance, and careful advice throughout this project. "
        f"We are also grateful to the {escape_latex(COLLEGE)} at {escape_latex(UNIVERSITY)}, "
        "to the participants who gave their time to answer the survey, "
        "and to our colleagues who supported the data collection and revision process.",
        "\\newpage",
        "\\tableofcontents",
        "\\newpage",
        "\\listoffigures",
        "\\newpage",
        "\\section*{List of Abbreviations}",
        "\\addcontentsline{toc}{section}{List of Abbreviations}",
        abbrev_lines,
    ]


def build_tex(md_path: Path, out_path: Path) -> None:
    blocks = collect_thesis_blocks(md_path)

    body: list[str] = []
    body.extend(_latex_cover_block())
    body.extend(_latex_preliminary_block())

    body.append("\\newpage")
    body.append("\\pagenumbering{arabic}")
    body.append("\\setcounter{page}{1}")

    chapter_just_emitted = False
    started = False

    for kind, data in blocks:
        if kind == "chapter":
            chapter_number, chapter_name = (data.split("|||", 1) + [""])[:2]
            body.append("\\newpage")
            body.append("\\thispagestyle{plain}")
            body.append("\\begin{center}\\vspace*{0.30\\textheight}")
            body.append("{\\Large\\bfseries\\rule{4cm}{0.4pt}}\\\\[10pt]")
            body.append("{\\Huge\\bfseries " + escape_latex(chapter_number) + "}\\\\[8pt]")
            body.append("{\\Large\\bfseries " + escape_latex(chapter_name) + "}\\\\[10pt]")
            body.append("{\\Large\\bfseries\\rule{4cm}{0.4pt}}")
            body.append("\\end{center}")
            body.append("\\newpage")
            chapter_just_emitted = True
            started = True
            continue
        if kind == "h1":
            if started and not chapter_just_emitted:
                body.append("\\newpage")
            body.append(f"\\section*{{{escape_latex(data)}}}")
            body.append(f"\\addcontentsline{{toc}}{{section}}{{{escape_latex(data)}}}")
            chapter_just_emitted = False
            started = True
            continue
        if kind == "h2":
            body.append(f"\\subsection*{{{escape_latex(data)}}}")
            chapter_just_emitted = False
            started = True
            continue
        if kind == "paragraph":
            body.append(escape_latex(data) + "\n")
            chapter_just_emitted = False
            started = True
            continue
        if kind == "image":
            alt, rel_path = data.split("|||", 1)
            rel = rel_path.replace("\\", "/")
            body.append(
                "\\begin{figure}[h!]\n"
                "\\centering\n"
                f"\\includegraphics[width=0.9\\textwidth]{{{escape_latex(rel)}}}\n"
                f"\\caption{{{escape_latex(alt)}}}\n"
                "\\end{figure}"
            )
            chapter_just_emitted = False
            started = True
            continue
        if kind == "table":
            block = _latex_table_block(data)
            if block:
                body.append(block)
            chapter_just_emitted = False
            started = True
            continue
        if kind == "pagebreak":
            body.append("\\newpage")
            chapter_just_emitted = False
            started = True
            continue

    tex = (
        "\\documentclass[12pt,a4paper]{article}\n"
        "\\usepackage[a4paper,margin=1.5cm]{geometry}\n"
        "\\usepackage{setspace}\n"
        "\\usepackage{graphicx}\n"
        "\\usepackage[T1]{fontenc}\n"
        "\\usepackage[utf8]{inputenc}\n"
        "\\usepackage{mathptmx}\n"
        "\\usepackage{fancyhdr}\n"
        "\\usepackage{titlesec}\n"
        "\\setstretch{1.5}\n"
        "\\setlength{\\parindent}{0.5in}\n"
        "\\pagestyle{fancy}\n"
        "\\fancyhf{}\n"
        "\\fancyhead[C]{\\thepage}\n"
        "\\fancyhead[L]{\\leftmark}\n"
        "\\renewcommand{\\headrulewidth}{0.4pt}\n"
        "\\begin{document}\n\n"
        + "\n".join(body)
        + "\n\n\\end{document}\n"
    )
    out_path.write_text(tex, encoding="utf-8")


# ---------------------------------------------------------------------------
# Reportlab PDF builder (cover -> roman prelim -> arabic main, plain style).
# ---------------------------------------------------------------------------
class _PdfState:
    """Mutable state shared between flowables and onPage callbacks."""

    def __init__(self) -> None:
        self.section_starts: dict[str, int] = {}
        self.chapter: str = ""

    def reset(self) -> None:
        self.section_starts = {}
        self.chapter = ""


_pdf_state = _PdfState()


class _SetChapterFlowable(Flowable):
    """A zero-size flowable that updates the running-head state during draw."""

    def __init__(self, chapter: str) -> None:
        Flowable.__init__(self)
        self.chapter = chapter

    def wrap(self, _w, _h):
        return 0, 0

    def draw(self) -> None:
        _pdf_state.chapter = self.chapter


def _record_section(name: str, doc) -> None:
    if name not in _pdf_state.section_starts:
        _pdf_state.section_starts[name] = doc.page


def _draw_page_label(canvas, doc, label: str, running_head: str = "") -> None:
    pw, ph = doc.pagesize
    canvas.saveState()
    canvas.setFont("Times-Roman", 10)
    canvas.drawCentredString(pw / 2, ph - 1.0 * cm, label)
    if running_head:
        canvas.drawString(1.8 * cm, ph - 1.0 * cm, running_head)
    canvas.restoreState()


def _on_cover(canvas, doc) -> None:
    _record_section("cover", doc)
    # Cover page: no page number, no decorations.


def _on_prelim(canvas, doc) -> None:
    _record_section("prelim", doc)
    rel = doc.page - _pdf_state.section_starts["prelim"] + 1
    _draw_page_label(canvas, doc, _to_roman_lower(rel))


def _on_main(canvas, doc) -> None:
    _record_section("main", doc)
    rel = doc.page - _pdf_state.section_starts["main"] + 1
    _draw_page_label(canvas, doc, str(rel), running_head=_pdf_state.chapter)


def _on_main_chapter(canvas, doc) -> None:
    _record_section("main", doc)
    rel = doc.page - _pdf_state.section_starts["main"] + 1
    _draw_page_label(canvas, doc, str(rel))


def _to_roman_lower(value: int) -> str:
    pairs = [
        (1000, "m"), (900, "cm"), (500, "d"), (400, "cd"),
        (100, "c"), (90, "xc"), (50, "l"), (40, "xl"),
        (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"),
    ]
    out: list[str] = []
    n = max(value, 1)
    for arabic, roman in pairs:
        while n >= arabic:
            out.append(roman)
            n -= arabic
    return "".join(out)


def _build_pdf_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles: dict[str, ParagraphStyle] = {}
    styles["body"] = ParagraphStyle(
        "Body",
        parent=base["BodyText"],
        fontName="Times-Roman",
        fontSize=14,
        leading=21,
        firstLineIndent=0.5 * 72,
        spaceBefore=2,
        spaceAfter=4,
        alignment=4,  # justify
    )
    styles["refs"] = ParagraphStyle(
        "Refs",
        parent=styles["body"],
        fontSize=12,
        leading=16,
        firstLineIndent=0,
        leftIndent=0.5 * 72,
        spaceBefore=1,
        spaceAfter=8,
    )
    styles["h1"] = ParagraphStyle(
        "H1",
        parent=base["Heading1"],
        fontName="Times-Bold",
        fontSize=18,
        leading=24,
        spaceBefore=12,
        spaceAfter=8,
    )
    styles["h2"] = ParagraphStyle(
        "H2",
        parent=base["Heading2"],
        fontName="Times-Bold",
        fontSize=16,
        leading=22,
        spaceBefore=8,
        spaceAfter=6,
    )
    styles["centered_big"] = ParagraphStyle(
        "CenteredBig",
        parent=base["Normal"],
        fontName="Times-Bold",
        fontSize=22,
        leading=28,
        alignment=1,
    )
    styles["centered_lg"] = ParagraphStyle(
        "CenteredLg",
        parent=base["Normal"],
        fontName="Times-Bold",
        fontSize=18,
        leading=24,
        alignment=1,
    )
    styles["centered_md"] = ParagraphStyle(
        "CenteredMd",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=14,
        leading=20,
        alignment=1,
    )
    styles["centered_md_bold"] = ParagraphStyle(
        "CenteredMdBold",
        parent=styles["centered_md"],
        fontName="Times-Bold",
    )
    styles["front_title"] = ParagraphStyle(
        "FrontTitle",
        parent=base["Normal"],
        fontName="Times-Bold",
        fontSize=20,
        leading=26,
        alignment=1,
        spaceBefore=10,
        spaceAfter=14,
    )
    styles["chapter_number"] = ParagraphStyle(
        "ChapterNumber",
        parent=base["Normal"],
        fontName="Times-Bold",
        fontSize=32,
        leading=40,
        alignment=1,
    )
    styles["chapter_name"] = ParagraphStyle(
        "ChapterName",
        parent=base["Normal"],
        fontName="Times-Bold",
        fontSize=18,
        leading=24,
        alignment=1,
    )
    styles["chapter_rule"] = ParagraphStyle(
        "ChapterRule",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=18,
        leading=22,
        alignment=1,
    )
    styles["caption"] = ParagraphStyle(
        "FigureCaption",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=12,
        leading=16,
        alignment=1,
        spaceBefore=4,
        spaceAfter=10,
    )
    styles["abbr"] = ParagraphStyle(
        "Abbr",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=14,
        leading=20,
        spaceAfter=2,
    )
    return styles


def _pdf_cover_story(styles: dict[str, ParagraphStyle]) -> list:
    story: list = []
    logo_path = find_university_logo()
    if logo_path is not None:
        try:
            reader = ImageReader(str(logo_path))
            iw, ih = reader.getSize()
            target_h = 2.0 * cm
            target_w = target_h * (iw / ih if ih else 1)
            story.append(Image(str(logo_path), width=target_w, height=target_h, hAlign="CENTER"))
            story.append(Spacer(1, 4))
        except Exception:
            pass
    for line in [
        "Republic of Iraq",
        "Ministry of Higher Education and Scientific Research",
        UNIVERSITY,
        COLLEGE,
    ]:
        story.append(Paragraph(line, styles["centered_md_bold"]))
    story.append(Spacer(1, 18))
    story.append(Paragraph(TITLE, styles["centered_big"]))
    story.append(Spacer(1, 18))
    story.append(Paragraph("A Project Submitted to", styles["centered_md"]))
    story.append(Paragraph(
        f"The {COLLEGE}, {UNIVERSITY}, {DEPARTMENT}, in Partial Fulfillment for the Bachelor of Pharmacy",
        styles["centered_md"],
    ))
    story.append(Spacer(1, 14))
    story.append(Paragraph("By", styles["centered_md_bold"]))
    for student in STUDENTS:
        story.append(Paragraph(student, styles["centered_lg"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Supervised by:", styles["centered_md_bold"]))
    story.append(Paragraph(SUPERVISOR, styles["centered_lg"]))
    story.append(Paragraph(SUPERVISOR_DEGREE, styles["centered_md"]))
    story.append(Spacer(1, 14))
    story.append(Paragraph(MONTH_YEAR, styles["centered_md"]))
    return story


def _pdf_preliminary_story(styles: dict[str, ParagraphStyle]) -> list:
    story: list = []
    students_text = ", ".join(STUDENTS)

    def front(title: str) -> Paragraph:
        return Paragraph(title, styles["front_title"])

    story.append(front("Certification of the Supervisor"))
    story.append(Paragraph(
        f"I certify that this project entitled \u201c{TITLE}\u201d was prepared "
        f"by the fifth-year students {students_text} under my supervision at the "
        f"{COLLEGE}/{UNIVERSITY} in partial fulfillment of the graduation "
        "requirements for the Bachelor Degree in Pharmacy.",
        styles["body"],
    ))
    sig_style = ParagraphStyle(
        "Sig", parent=styles["body"],
        firstLineIndent=0, alignment=2,
        fontName="Times-Bold",
        spaceBefore=14,
    )
    story.append(Paragraph(f"Supervisor's name: {SUPERVISOR}", sig_style))
    story.append(PageBreak())

    story.append(front("Dedication"))
    story.append(Paragraph(
        "We dedicate this work to our families, whose patience made long study "
        "days easier, and to every Iraqi patient who deserves safe, respectful, "
        "and evidence-based mental health care. We also dedicate it to the "
        "teachers and pharmacists who taught us that science becomes meaningful "
        "when it serves people with honesty and compassion.",
        styles["body"],
    ))
    story.append(PageBreak())

    story.append(front("Acknowledgment"))
    story.append(Paragraph(
        f"We thank Dr. {SUPERVISOR} for his supervision, guidance, and careful "
        f"advice throughout this project. We are also grateful to the {COLLEGE} "
        f"at {UNIVERSITY}, to the participants who gave their time to answer the "
        "survey, and to our colleagues who supported the data collection and "
        "revision process.",
        styles["body"],
    ))
    story.append(PageBreak())

    story.append(front("Table of Contents"))
    story.append(Paragraph(
        "(See the auto-generated DOCX or compiled Typst PDF for the live, "
        "field-driven Table of Contents.)",
        styles["body"],
    ))
    story.append(PageBreak())

    story.append(front("List of Figures"))
    story.append(Paragraph(
        "(See the auto-generated DOCX or compiled Typst PDF for the live, "
        "field-driven List of Figures.)",
        styles["body"],
    ))
    story.append(PageBreak())

    story.append(front("List of Abbreviations"))
    for short, long in ABBREVIATIONS:
        story.append(Paragraph(f"<b>{short}:</b> {long}", styles["abbr"]))
    return story


def _pdf_chapter_title_story(chapter_number: str, chapter_name: str,
                             styles: dict[str, ParagraphStyle]) -> list:
    rule = "\u2500" * 12
    return [
        Spacer(1, 220),
        Paragraph(rule, styles["chapter_rule"]),
        Spacer(1, 8),
        Paragraph(chapter_number, styles["chapter_number"]),
        Spacer(1, 6),
        Paragraph(chapter_name, styles["chapter_name"]),
        Spacer(1, 10),
        Paragraph(rule, styles["chapter_rule"]),
    ]


def _pdf_table_flowable(payload: str, *, max_width_cm: float = 18.0):
    """Build a ReportLab LongTable flowable from a markdown-table payload."""
    try:
        data = json.loads(payload)
    except (TypeError, ValueError):
        return None
    headers: list[str] = data.get("headers", [])
    rows: list[list[str]] = data.get("rows", [])
    aligns: list[str] = data.get("aligns", [])
    col_count = max(len(headers), max((len(r) for r in rows), default=0))
    if col_count == 0:
        return None

    base = getSampleStyleSheet()
    cell_style = ParagraphStyle(
        "TableCell",
        parent=base["Normal"],
        fontName="Times-Roman",
        fontSize=9,
        leading=11,
    )
    head_style = ParagraphStyle(
        "TableHead",
        parent=cell_style,
        fontName="Times-Bold",
    )

    def pad(row: list[str]) -> list[str]:
        return list(row) + [""] * (col_count - len(row))

    table_data: list[list] = []
    if headers:
        table_data.append([Paragraph(clean_inline_markdown(c), head_style) for c in pad(headers)])
    for row in rows:
        table_data.append([Paragraph(clean_inline_markdown(c), cell_style) for c in pad(row)])

    col_width = (max_width_cm * cm) / col_count
    table = LongTable(table_data, colWidths=[col_width] * col_count, repeatRows=1 if headers else 0)
    style_cmds = [
        ("GRID", (0, 0), (-1, -1), 0.4, rl_colors.Color(0.78, 0.83, 0.90)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if headers:
        style_cmds.append(("BACKGROUND", (0, 0), (-1, 0), rl_colors.Color(0.95, 0.96, 0.99)))
    for col in range(col_count):
        align = aligns[col] if col < len(aligns) else "left"
        rl_align = {"left": "LEFT", "center": "CENTER", "right": "RIGHT"}.get(align, "LEFT")
        style_cmds.append(("ALIGN", (col, 0), (col, -1), rl_align))
    table.setStyle(TableStyle(style_cmds))
    return table


def _fit_image(img_path: Path, max_width_cm: float = 16.0) -> tuple[float, float]:
    try:
        reader = ImageReader(str(img_path))
        iw, ih = reader.getSize()
        if iw <= 0 or ih <= 0:
            return max_width_cm * cm, max_width_cm * cm * 0.6
        ratio = ih / iw
        width = max_width_cm * cm
        height = width * ratio
        if height > 20 * cm:
            height = 20 * cm
            width = height / ratio
        return width, height
    except Exception:
        return max_width_cm * cm, max_width_cm * cm * 0.6


def build_pdf_reportlab(md_path: Path, out_path: Path) -> None:
    blocks = collect_thesis_blocks(md_path)
    _pdf_state.reset()

    margin = 1.5 * cm
    pagesize = A4
    pw, ph = pagesize
    frame = Frame(
        margin, margin,
        pw - 2 * margin, ph - 2 * margin,
        leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=22,
        id="main_frame",
    )

    page_templates = [
        PageTemplate(id="cover", frames=[frame], onPage=_on_cover),
        PageTemplate(id="prelim", frames=[frame], onPage=_on_prelim),
        PageTemplate(id="main_chapter", frames=[frame], onPage=_on_main_chapter),
        PageTemplate(id="main", frames=[frame], onPage=_on_main),
    ]

    doc = BaseDocTemplate(
        str(out_path),
        pagesize=pagesize,
        leftMargin=margin, rightMargin=margin,
        topMargin=margin, bottomMargin=margin,
        pageTemplates=page_templates,
        title=TITLE,
        author=", ".join(STUDENTS),
    )

    styles = _build_pdf_styles()
    story: list = [NextPageTemplate("cover")]
    story.extend(_pdf_cover_story(styles))

    story.append(NextPageTemplate("prelim"))
    story.append(PageBreak())
    story.extend(_pdf_preliminary_story(styles))

    story.append(NextPageTemplate("main"))
    story.append(PageBreak())
    story.append(_SetChapterFlowable(""))

    in_references = False
    chapter_just_emitted = False
    started = False

    for kind, data in blocks:
        if kind == "chapter":
            chapter_number, chapter_name = (data.split("|||", 1) + [""])[:2]
            story.append(_SetChapterFlowable(""))
            story.append(NextPageTemplate("main_chapter"))
            story.append(PageBreak())
            story.extend(_pdf_chapter_title_story(chapter_number, chapter_name, styles))
            story.append(_SetChapterFlowable(chapter_name))
            story.append(NextPageTemplate("main"))
            story.append(PageBreak())
            chapter_just_emitted = True
            started = True
            continue
        if kind == "h1":
            if started and not chapter_just_emitted:
                story.append(PageBreak())
            story.append(Paragraph(data, styles["h1"]))
            in_references = data.strip().upper() == "VIII. REFERENCES"
            chapter_just_emitted = False
            started = True
            continue
        if kind == "h2":
            story.append(Paragraph(data, styles["h2"]))
            chapter_just_emitted = False
            started = True
            continue
        if kind == "paragraph":
            target = styles["refs"] if in_references else styles["body"]
            story.append(Paragraph(data, target))
            chapter_just_emitted = False
            started = True
            continue
        if kind == "image":
            caption, rel_path = data.split("|||", 1)
            img_path = (md_path.parent / rel_path).resolve()
            if img_path.exists():
                width, height = _fit_image(img_path)
                story.append(Spacer(1, 6))
                story.append(Image(str(img_path), width=width, height=height, hAlign="CENTER"))
                story.append(Paragraph(caption, styles["caption"]))
            chapter_just_emitted = False
            started = True
            continue
        if kind == "table":
            tbl = _pdf_table_flowable(data)
            if tbl is not None:
                story.append(Spacer(1, 4))
                story.append(tbl)
                story.append(Spacer(1, 4))
            chapter_just_emitted = False
            started = True
            continue
        if kind == "pagebreak":
            story.append(PageBreak())
            chapter_just_emitted = False
            started = True

    doc.build(story)


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------
def run_method_a(md_path: Path) -> None:
    build_docx(md_path, METHOD_A_DIR / "research_method_a.docx")
    build_tex(md_path, METHOD_A_DIR / "research_method_a.tex")
    build_pdf_reportlab(md_path, METHOD_A_DIR / "research_method_a.pdf")


def main() -> None:
    ensure_dirs()
    copy_figure_assets()
    md_path = assemble_markdown()
    run_method_a(md_path)
    print("Production pipeline completed.")
    print(f"Comprehensive markdown: {md_path}")
    print(f"Method A outputs: {METHOD_A_DIR}")


if __name__ == "__main__":
    main()
