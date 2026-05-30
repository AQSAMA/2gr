#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

from build_production import (
    ABBREVIATIONS,
    ASSEMBLED_DIR,
    COLLEGE,
    DEPARTMENT,
    FIGURES_DIR,
    METHOD_A_DIR,
    MONTH_YEAR,
    NAVY_HEX,
    REPO_ROOT,
    STUDENTS,
    SUPERVISOR,
    SUPERVISOR_DEGREE,
    TITLE,
    UNIVERSITY,
    add_field_run,
    assemble_markdown,
    configure_section,
    copy_figure_assets,
    ensure_dirs as ensure_production_dirs,
    find_university_logo,
    iter_markdown_blocks,
    set_paragraph_border,
    set_run_font,
    setup_docx_styles,
)

TYPST_CONTENT_DIR = REPO_ROOT / "typst_content"
TYPST_OUTPUT_DIR = TYPST_CONTENT_DIR / "output"
TYPST_SOURCE = TYPST_CONTENT_DIR / "research.typ"
TYPST_PDF = TYPST_OUTPUT_DIR / "research.pdf"
TYPST_DOCX = TYPST_OUTPUT_DIR / "research.docx"
SURVEY_RESULTS_SOURCE = TYPST_CONTENT_DIR / "survey_results.typ"
SURVEY_RESULTS_PDF = TYPST_OUTPUT_DIR / "survey_results.pdf"
SURVEY_RESULTS_DOCX = TYPST_OUTPUT_DIR / "survey_results.docx"
SURVEY_RESULTS_MD = REPO_ROOT / "survey_data_results.md"


def typst_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


_CITATION_PAREN_RE = re.compile(r"\([^()]*?\b(?:19|20)\d{2}[a-z]?[^()]*?\)")
_CITATION_NARRATIVE_RE = re.compile(
    r"\b[A-Z][\w'\u2019\u00C0-\u017F-]+"
    r"(?:\s+(?:et\s+al\.|(?:&|and)\s+[A-Z][\w'\u2019\u00C0-\u017F-]+))?"
    r"\s+\((?:19|20)\d{2}[a-z]?\)"
)

_TYPST_MARKUP_ESCAPES = str.maketrans({
    "\\": r"\\",
    "#": r"\#",
    "*": r"\*",
    "_": r"\_",
    "<": r"\<",
    ">": r"\>",
    "[": r"\[",
    "]": r"\]",
    "@": r"\@",
    "`": r"\`",
    "~": r"\~",
    "$": r"\$",
})


def _escape_typst_markup(value: str) -> str:
    """Escape characters that have meaning in Typst markup mode."""
    return value.translate(_TYPST_MARKUP_ESCAPES)


def bold_citations(value: str) -> str:
    """Wrap parenthetical and narrative citations in Typst bold markup.

    The cleaned text is intended for ``eval(s, mode: "markup")`` inside the
    ``p`` paragraph helper. Non-citation characters that have meaning in
    Typst markup (``<``, ``>``, ``[``, ``]``, ``*``, ``_``, ``#``, etc.) are
    escaped so that only the bold wrappers we inject are interpreted as
    markup. Citation text itself (parens, letters, ampersand, comma) does
    not contain any of these markup characters in this manuscript.
    """
    placeholders: list[str] = []

    def stash(match: re.Match[str]) -> str:
        placeholders.append(match.group(0))
        return f"\x00{len(placeholders) - 1}\x00"

    # Narrative form is matched first so that "Author et al. (YYYY)" is
    # captured as a single citation; otherwise the parenthetical regex
    # would consume just "(YYYY)" and leave the author run unbolded.
    staged = _CITATION_NARRATIVE_RE.sub(stash, value)
    staged = _CITATION_PAREN_RE.sub(stash, staged)
    escaped = _escape_typst_markup(staged)

    def restore(match: re.Match[str]) -> str:
        return f"#strong[{placeholders[int(match.group(1))]}]"

    return re.sub(r"\x00(\d+)\x00", restore, escaped)


def clean_text(value: str) -> str:
    value = value.replace("\u00a0", " ")
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def ensure_dirs() -> None:
    TYPST_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    TYPST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)



def _split_references(md_text: str) -> tuple[str, list[str]]:
    marker = "\n# VIII. REFERENCES\n"
    if marker not in md_text:
        return md_text, []
    before, after = md_text.split(marker, 1)
    references = [clean_text(line) for line in after.splitlines() if clean_text(line)]
    return before + marker, references


def collect_manuscript_calls(md_path: Path) -> tuple[list[str], list[str]]:
    """Return Typst calls for roman-numbered front matter and arabic main matter."""
    front_calls: list[str] = []
    main_calls: list[str] = []
    target = front_calls
    skip_cover = True
    in_references = False
    md_text, references = _split_references(md_path.read_text(encoding="utf-8"))

    for kind, data in iter_markdown_blocks(md_text):
        if skip_cover:
            if kind == "h1" and data.strip().upper() == "ABSTRACT":
                skip_cover = False
                target = main_calls
                # Switch to arabic numbering at the top level so the
                # ``#set page(...)`` rule actually applies to all
                # subsequent pages. (Putting these inside a content
                # function leaves the set-rule scoped to that function
                # and the rest of the document keeps the old format.)
                target.append("#pagebreak(weak: true)")
                target.append(
                    '#set page(numbering: "1", '
                    "header: regular-page-header, footer: page-number-footer)"
                )
                target.append("#counter(page).update(1)")
                target.append('#set-running-head("")')
            else:
                continue

        if kind == "chaptertitle":
            chapter_number, chapter_name = (data.split("|||", 1) + [""])[:2]
            target.append(f"#chapter-page({typst_string(chapter_number)}, {typst_string(chapter_name)})")
            target.append(f"#set-running-head({typst_string(chapter_name)})")
            continue

        if kind == "h1":
            text = clean_text(data)
            if text.upper() == "VIII. REFERENCES":
                in_references = True
            target.append(f"#section-title({typst_string(text)})")
            continue

        if kind == "h2":
            target.append(f"#h2({typst_string(clean_text(data))})")
            continue

        if kind == "paragraph":
            text = clean_text(data)
            if not text:
                continue
            if in_references:
                target.append(f"#refp({typst_string(text)})")
            else:
                target.append(f"#p({typst_string(bold_citations(text))})")
            continue

        if kind == "image":
            caption, rel_path = data.split("|||", 1)
            filename = Path(rel_path).name
            target.append(f"#fig({typst_string('../figures/' + filename)}, {typst_string(clean_text(caption))})")
            continue

        if kind == "pagebreak":
            target.append("#pagebreak()")
            continue

    if references:
        if not in_references:
            target.append(f"#section-title({typst_string('VIII. REFERENCES')})")
        for reference in references:
            target.append(f"#refp({typst_string(reference)})")

    return front_calls, main_calls

def render_typst_source(md_path: Path) -> str:
    front_calls, main_calls = collect_manuscript_calls(md_path)
    students = ", ".join(STUDENTS)
    student_lines = "\\\n".join(STUDENTS)

    logo_path = find_university_logo()
    logo_block = ""
    if logo_path is not None:
        logo_rel = Path("..") / logo_path.relative_to(REPO_ROOT)
        logo_block = f"  #image({typst_string(logo_rel.as_posix())}, width: 2.25cm)\n  #v(0.16cm)\n"

    preamble = f'''// Editable Typst source for the graduation project.
// Generated from content/*.md by production/src/build_typst_content.py.
// The design follows common university thesis conventions: bordered A4 pages,
// formal title page, compact front matter, automatic contents, and figure lists.

#set document(title: {typst_string(TITLE)}, author: {typst_string(students)})

#let navy = rgb("#102a43")
#let gold = rgb("#b58b2a")
#let ink = rgb("#111827")
#let pale = rgb("#f7f9fc")
#let page-border = rect(width: 100%, height: 100%, stroke: 0.8pt + navy)
#let running-head = state("running-head", "")
#let set-running-head(s) = running-head.update(s)
#let regular-page-header = context {{
  let head = running-head.get()
  if head != "" {{
    align(left)[#text(size: 9pt, fill: navy)[#head]]
  }}
}}
// Centered footer that prints the page number using whatever numbering
// format is active for the page (roman for preliminaries, arabic for the
// main matter). This is required because a custom ``header`` suppresses
// Typst's automatic page-number rendering, so without an explicit footer
// no number would be visible at all.
#let page-number-footer = context [
  #align(center)[
    #text(size: 10pt, fill: navy)[
      #counter(page).display(here().page-numbering())
    ]
  ]
]

#set text(font: ("Times New Roman", "Times"), size: 14pt, fill: ink)
#set par(leading: 0.55em, justify: true)

#show heading.where(level: 1): it => block(above: 10pt, below: 8pt)[
  #text(size: 18pt, weight: "bold", fill: navy)[#it.body]
  #linebreak()
  #line(length: 100%, stroke: 0.7pt + gold)
]
#show heading.where(level: 2): it => block(above: 8pt, below: 6pt)[
  #text(size: 16pt, weight: "bold", fill: navy)[#it.body]
]
#show figure: it => block(above: 10pt, below: 12pt, inset: 6pt, stroke: 0.35pt + rgb("#c9d4e5"))[#align(center)[#it]]

#let center-line(s, size: 14pt, weight: "regular", fill: ink) = align(center)[#text(size: size, weight: weight, fill: fill)[#s]]
// Body paragraph helper: evaluates the string as Typst markup so that
// citation runs wrapped in ``#strong[...]`` by the build script render in
// bold while the surrounding text stays normal weight.
#let p(s) = par(first-line-indent: 1.27cm, justify: true)[#eval(s, mode: "markup")]
// Reference paragraph: a normal first-line indent (no hanging indent)
// with comfortable spacing between entries so the bibliography reads as a
// list of paragraphs instead of a dense merged block.
#let refp(s) = block(above: 0pt, below: 14pt, breakable: true)[
  #set text(size: 12pt)
  #par(first-line-indent: 1.27cm, justify: true, leading: 0.6em)[#s]
]
#let h1(s) = heading(level: 1, outlined: true)[#s]
#let section-title(s) = [
  #pagebreak(weak: true)
  #h1(s)
]
#let h2(s) = heading(level: 2, outlined: true)[#s]
#let fig(path, caption-text) = figure(image(path, width: 90%), caption: [#caption-text])

#let front-title(s) = [
  #align(center)[
    #box(width: 80%, inset: 10pt, stroke: 0.7pt + gold, fill: pale)[
      #text(size: 22pt, weight: "bold", fill: navy)[#s]
    ]
  ]
]

#let chapter-page(chapter, title) = [
  #pagebreak(weak: true)
  // Hide both header and footer on the chapter title page so the page
  // counts toward the total but shows no running head and no number.
  #set page(header: none, footer: none)
  #align(center + horizon)[
    #box(width: 84%, inset: 28pt, stroke: 1pt + navy, fill: pale)[
      #align(center)[
        #text(size: 32pt, weight: "bold", fill: navy)[#chapter]
        #v(8pt)
        #line(length: 55%, stroke: 0.8pt + gold)
        #v(8pt)
        #text(size: 20pt, weight: "bold", fill: navy)[#title]
      ]
    ]
  ]
  #pagebreak()
  #set page(header: regular-page-header, footer: page-number-footer)
]

// ===== Cover page =====
// Numbered as roman page i so the cover counts toward the preliminary
// page total, but header and footer are suppressed so no number is
// visible on the cover itself.
#set page(paper: "a4", margin: 1.5cm, background: page-border, numbering: "i", header: none, footer: none)
#counter(page).update(1)
#align(center)[
{logo_block}  #text(size: 15pt, weight: "bold", fill: navy)[Republic of Iraq] \\
  #text(size: 15pt, weight: "bold", fill: navy)[Ministry of Higher Education and Scientific Research] \\
  #text(size: 15pt, weight: "bold", fill: navy)[{UNIVERSITY}] \\
  #text(size: 15pt, weight: "bold", fill: navy)[{COLLEGE}]
  #v(0.35cm)
  #box(width: 88%, inset: 12pt, stroke: 1pt + gold, fill: pale)[
    #text(size: 24pt, weight: "bold", fill: navy)[{TITLE}]
  ]
  #v(0.32cm)
  #text(size: 14pt)[A Project Submitted to] \\
  #text(size: 13pt)[The {COLLEGE}, {UNIVERSITY}, Department of Clinical Pharmacy, in Partial Fulfillment for the Bachelor of Pharmacy]
  #v(0.28cm)
  #text(size: 14pt, weight: "bold")[By] \\
  #text(size: 20pt, weight: "bold", fill: navy)[{student_lines}]
  #v(0.25cm)
  #text(size: 14pt, weight: "bold")[Supervised by:] \\
  #text(size: 20pt, weight: "bold", fill: navy)[{SUPERVISOR}] \\
  #text(size: 16pt)[Supervisor's Degree]
  #v(0.18cm)
  #text(size: 14pt)[{MONTH_YEAR}]
]

// ===== Roman-numbered preliminary pages =====
// Roman numbering continues from the cover (so this page is ii). The
// header and footer return so each preliminary page shows its number.
#pagebreak()
#set page(numbering: "i", header: regular-page-header, footer: page-number-footer)
#front-title[Dedication]
#p("We dedicate this work to our families, whose patience made long study days easier, and to every Iraqi patient who deserves safe, respectful, and evidence-based mental health care. We also dedicate it to the teachers and pharmacists who taught us that science becomes meaningful when it serves people with honesty and compassion.")
#v(0.35cm)
#front-title[Acknowledgment]
#p("We thank Dr. {SUPERVISOR} for his supervision, guidance, and careful advice throughout this project. We are also grateful to the College of Pharmacy at {UNIVERSITY}, to the participants who gave their time to answer the survey, and to our colleagues who supported the data collection and revision process.")

#pagebreak()
#front-title[Table of Contents]
#outline(title: none, depth: 2)

#pagebreak()
#front-title[List of Figures]
#outline(title: none, target: figure.where(kind: image))
#v(0.4cm)
#front-title[List of Abbreviations]
#par(first-line-indent: 0pt)[AOR: Adjusted Odds Ratio \\
CI: Confidence Interval \\
LLR: Likelihood Ratio Test \\
MLE: Maximum Likelihood Estimation \\
OR: Odds Ratio \\
PTSD: Post-Traumatic Stress Disorder \\
RRR: Relative Risk Ratio \\
Q6/Q7/Q8/Q9/Q11/Q12/Q13/Q31: Survey question item codes used in analysis and reporting \\
R²: Coefficient of determination, reported as pseudo R² in logistic model fit summaries]

'''
    return preamble + "\n".join(front_calls) + "\n\n" + "\n".join(main_calls) + "\n"


def write_typst_source(md_path: Path) -> Path:
    source = render_typst_source(md_path)
    TYPST_SOURCE.write_text(source, encoding="utf-8")
    return TYPST_SOURCE


def _print_process_output(output: str | bytes | None) -> None:
    if output is None:
        return
    if isinstance(output, bytes):
        output = output.decode(errors="replace")
    if output.strip():
        print(output.strip())


def compile_typst_pdf() -> bool:
    typst = shutil.which("typst")
    if typst is None:
        print("WARNING: typst is not installed; typst_content PDF compilation was skipped.")
        return False
    result = subprocess.run(
        [typst, "compile", "--root", str(REPO_ROOT), str(TYPST_SOURCE), str(TYPST_PDF)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=300,
    )
    if result.returncode != 0:
        print("WARNING: Typst failed for typst_content/research.typ; continuing with other outputs.")
        _print_process_output(result.stdout)
        _print_process_output(result.stderr)
        return False
    print(f"Typst content PDF: {TYPST_PDF}")
    return True


def compile_survey_results_pdf() -> bool:
    """Compile the standalone survey results Typst source to PDF."""
    typst = shutil.which("typst")
    if typst is None:
        print("WARNING: typst is not installed; survey_results PDF compilation was skipped.")
        return False
    if not SURVEY_RESULTS_SOURCE.exists():
        print("WARNING: survey_results.typ not found; skipping survey results PDF.")
        return False
    result = subprocess.run(
        [typst, "compile", "--root", str(REPO_ROOT), str(SURVEY_RESULTS_SOURCE), str(SURVEY_RESULTS_PDF)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=300,
    )
    if result.returncode != 0:
        print("WARNING: Typst failed for typst_content/survey_results.typ; continuing with other outputs.")
        _print_process_output(result.stdout)
        _print_process_output(result.stderr)
        return False
    print(f"Survey results PDF: {SURVEY_RESULTS_PDF}")
    return True


def collect_docx_blocks(md_path: Path) -> list[tuple[str, str]]:
    """Collect the same manuscript structure used by the editable Typst source."""
    blocks: list[tuple[str, str]] = []
    skip_cover = True
    in_references = False
    md_text, references = _split_references(md_path.read_text(encoding="utf-8"))

    for kind, data in iter_markdown_blocks(md_text):
        if skip_cover:
            if kind == "h1" and data.strip().upper() == "ABSTRACT":
                skip_cover = False
                blocks.append(("start_main", ""))
            else:
                continue

        if kind == "chaptertitle":
            chapter_number, chapter_name = (data.split("|||", 1) + [""])[:2]
            blocks.append(("chapter", f"{chapter_number}|||{chapter_name}"))
            continue

        if kind == "h1":
            text = clean_text(data)
            if text.upper() == "VIII. REFERENCES":
                in_references = True
            blocks.append(("section", text))
            continue

        if kind == "h2":
            blocks.append(("h2", clean_text(data)))
            continue

        if kind == "paragraph":
            text = clean_text(data)
            if text:
                blocks.append(("reference" if in_references else "paragraph", text))
            continue

        if kind == "image":
            caption, rel_path = data.split("|||", 1)
            blocks.append(("image", f"{clean_text(caption)}|||{Path(rel_path).name}"))
            continue

        if kind == "pagebreak":
            blocks.append(("pagebreak", ""))
            continue

    if references:
        if not in_references:
            blocks.append(("section", "VIII. REFERENCES"))
        for reference in references:
            blocks.append(("reference", reference))

    return blocks


def _set_run_font(run, size: int | float | None = None, bold: bool | None = None, color: str | None = None) -> None:
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


def _set_paragraph_border(paragraph, color: str = "B58B2A", size: str = "8") -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    borders = p_pr.find(qn("w:pBdr"))
    if borders is None:
        borders = OxmlElement("w:pBdr")
        p_pr.append(borders)
    for edge in ["top", "left", "bottom", "right"]:
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "4")
        element.set(qn("w:color"), color)
        borders.append(element)


def _set_page_border(section) -> None:
    sect_pr = section._sectPr
    borders = sect_pr.find(qn("w:pgBorders"))
    if borders is None:
        borders = OxmlElement("w:pgBorders")
        borders.set(qn("w:offsetFrom"), "page")
        sect_pr.append(borders)
    for edge in ["top", "left", "bottom", "right"]:
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "8")
        element.set(qn("w:space"), "18")
        element.set(qn("w:color"), "102A43")
        borders.append(element)


def _set_page_numbering(section, fmt: str, start: int | None = 1) -> None:
    sect_pr = section._sectPr
    pg_num = sect_pr.find(qn("w:pgNumType"))
    if pg_num is None:
        pg_num = OxmlElement("w:pgNumType")
        sect_pr.append(pg_num)
    pg_num.set(qn("w:fmt"), fmt)
    if start is None:
        # Remove any existing start attribute so the section continues
        # numbering from the previous section instead of restarting.
        if pg_num.get(qn("w:start")) is not None:
            del pg_num.attrib[qn("w:start")]
    else:
        pg_num.set(qn("w:start"), str(start))


def _add_field_run(paragraph, instruction: str, *, dirty: bool = False) -> None:
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    if dirty:
        fld_begin.set(qn("w:dirty"), "true")
    run._r.append(fld_begin)
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    run._r.append(instr)
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    run._r.append(fld_sep)
    result = OxmlElement("w:t")
    result.text = " "
    run._r.append(result)
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_end)


def _configure_section(
    section,
    *,
    numbered: bool,
    number_format: str = "decimal",
    start: int | None = 1,
    running_head: str = "",
    empty_first_page: bool = False,
) -> None:
    section.left_margin = Cm(1.5)
    section.right_margin = Cm(1.5)
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)
    _set_page_border(section)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    section.different_first_page_header_footer = empty_first_page

    # Always start with cleared headers; we add content selectively below.
    for paragraph in section.header.paragraphs:
        paragraph.clear()
    for paragraph in section.first_page_header.paragraphs:
        paragraph.clear()

    if numbered:
        _set_page_numbering(section, number_format, start)
        # Regular header: optional running head on the left and a centered
        # PAGE field that renders the page number in the section's format.
        header = section.header.paragraphs[0]
        header.alignment = WD_ALIGN_PARAGRAPH.LEFT
        if running_head:
            run = header.add_run(running_head)
            _set_run_font(run, size=9, color="102A43")
        page_paragraph = section.header.add_paragraph()
        page_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _add_field_run(page_paragraph, "PAGE")
        # When ``empty_first_page`` is requested the first-page header stays
        # empty (already cleared above) so cover/chapter title pages count
        # toward the page total but display no number or running head.


def _setup_docx_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.font.size = Pt(14)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.first_line_indent = Inches(0.5)

    for style_name, size in [("Heading 1", 18), ("Heading 2", 16)]:
        style = doc.styles[style_name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string("102A43")


def _center_paragraph(doc: Document, text: str = "", size: int | float = 14, bold: bool = False, color: str | None = None):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Inches(0)
    if text:
        run = paragraph.add_run(text)
        _set_run_font(run, size=size, bold=bold, color=color)
    return paragraph


def _front_title(doc: Document, title: str) -> None:
    paragraph = _center_paragraph(doc, title, size=22, bold=True, color="102A43")
    _set_paragraph_border(paragraph)
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(8)


def _add_body_paragraph(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph(text)
    paragraph.paragraph_format.line_spacing = 1.5
    paragraph.paragraph_format.first_line_indent = Inches(0.5)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY


def _add_reference_paragraph(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph(text)
    # Normal first-line indent (no hanging indent), with comfortable
    # spacing between successive references so the bibliography reads as a
    # list of paragraphs rather than a single dense block.
    paragraph.paragraph_format.first_line_indent = Inches(0.3)
    paragraph.paragraph_format.left_indent = Inches(0)
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(8)
    paragraph.paragraph_format.line_spacing = 1.15
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for run in paragraph.runs:
        _set_run_font(run, size=12)


def _add_cover_page(doc: Document) -> None:
    logo_path = find_university_logo()
    if logo_path is not None:
        paragraph = doc.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.first_line_indent = Inches(0)
        run = paragraph.add_run()
        run.add_picture(str(logo_path), width=Inches(0.9))
    for line in ["Republic of Iraq", "Ministry of Higher Education and Scientific Research", UNIVERSITY, COLLEGE]:
        _center_paragraph(doc, line, size=15, bold=True, color="102A43")
    title = _center_paragraph(doc, TITLE, size=24, bold=True, color="102A43")
    _set_paragraph_border(title)
    title.paragraph_format.space_before = Pt(8)
    title.paragraph_format.space_after = Pt(14)
    _center_paragraph(doc, "A Project Submitted to", size=14)
    _center_paragraph(
        doc,
        f"The {COLLEGE}, {UNIVERSITY}, Department of Clinical Pharmacy, in Partial Fulfillment for the Bachelor of Pharmacy",
        size=13,
    )
    doc.add_paragraph()
    _center_paragraph(doc, "By", size=14, bold=True)
    for student in STUDENTS:
        _center_paragraph(doc, student, size=20, bold=True, color="102A43")
    doc.add_paragraph()
    _center_paragraph(doc, "Supervised by:", size=14, bold=True)
    _center_paragraph(doc, SUPERVISOR, size=20, bold=True, color="102A43")
    _center_paragraph(doc, "Supervisor's Degree", size=16)
    doc.add_paragraph()
    _center_paragraph(doc, MONTH_YEAR, size=14)


def _add_preliminary_pages(doc: Document, figure_captions: list[str]) -> None:
    _front_title(doc, "Dedication")
    _add_body_paragraph(
        doc,
        "We dedicate this work to our families, whose patience made long study days easier, and to every Iraqi patient who deserves safe, respectful, and evidence-based mental health care. We also dedicate it to the teachers and pharmacists who taught us that science becomes meaningful when it serves people with honesty and compassion.",
    )
    _front_title(doc, "Acknowledgment")
    _add_body_paragraph(
        doc,
        f"We thank Dr. {SUPERVISOR} for his supervision, guidance, and careful advice throughout this project. We are also grateful to the {COLLEGE} at {UNIVERSITY}, to the participants who gave their time to answer the survey, and to our colleagues who supported the data collection and revision process.",
    )

    doc.add_page_break()
    _front_title(doc, "Table of Contents")
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.first_line_indent = Inches(0)
    # ``dirty=True`` tells Word the field needs to be regenerated, so the
    # TOC fills automatically on first open instead of staying blank.
    _add_field_run(paragraph, r'TOC \o "1-2" \h \z \u', dirty=True)

    doc.add_page_break()
    _front_title(doc, "List of Figures")
    for caption in figure_captions:
        paragraph = doc.add_paragraph(caption)
        paragraph.paragraph_format.first_line_indent = Inches(0)
    _front_title(doc, "List of Abbreviations")
    abbreviations = [
        "AOR: Adjusted Odds Ratio",
        "CI: Confidence Interval",
        "LLR: Likelihood Ratio Test",
        "MLE: Maximum Likelihood Estimation",
        "OR: Odds Ratio",
        "PTSD: Post-Traumatic Stress Disorder",
        "RRR: Relative Risk Ratio",
        "Q6/Q7/Q8/Q9/Q11/Q12/Q13/Q31: Survey question item codes used in analysis and reporting",
        "R²: Coefficient of determination, reported as pseudo R² in logistic model fit summaries",
    ]
    for item in abbreviations:
        paragraph = doc.add_paragraph(item)
        paragraph.paragraph_format.first_line_indent = Inches(0)


def _set_update_fields_on_open(doc: Document) -> None:
    """Tell Word to refresh all fields (TOC, PAGE, etc.) on open.

    Without this the TOC field can render as a blank gap until the user
    manually right-clicks and chooses *Update Field*.
    """
    settings = doc.settings.element
    update_fields = settings.find(qn("w:updateFields"))
    if update_fields is None:
        update_fields = OxmlElement("w:updateFields")
        settings.append(update_fields)
    update_fields.set(qn("w:val"), "true")


def build_typst_content_docx(md_path: Path, out_path: Path) -> None:
    blocks = collect_docx_blocks(md_path)
    figure_captions = [data.split("|||", 1)[0] for kind, data in blocks if kind == "image"]

    doc = Document()
    _setup_docx_styles(doc)
    _set_update_fields_on_open(doc)

    # Section 0: cover page only. Counts toward Roman numbering as page i
    # but the first-page header is empty so no number is displayed.
    _configure_section(
        doc.sections[0],
        numbered=True,
        number_format="lowerRoman",
        start=1,
        empty_first_page=True,
    )
    _add_cover_page(doc)

    # Section 1: remaining preliminary pages (Dedication, Acknowledgment,
    # Table of Contents, List of Figures, List of Abbreviations).
    # ``start=None`` lets numbering continue from the cover, so this
    # section starts at page ii.
    front_section = doc.add_section(WD_SECTION.NEW_PAGE)
    _configure_section(
        front_section,
        numbered=True,
        number_format="lowerRoman",
        start=None,
    )
    _add_preliminary_pages(doc, figure_captions)

    main_started = False
    in_references = False
    chapter_just_added = False

    for kind, data in blocks:
        if kind == "start_main" and not main_started:
            # Section 2: abstract and onwards. Restart at Arabic 1.
            section = doc.add_section(WD_SECTION.NEW_PAGE)
            _configure_section(
                section,
                numbered=True,
                number_format="decimal",
                start=1,
            )
            main_started = True
            chapter_just_added = False
            continue

        if kind == "chapter":
            chapter_number, chapter_name = (data.split("|||", 1) + [""])[:2]
            # New section per chapter so each can carry its own running
            # head, but ``start=None`` makes numbering continue across
            # chapters instead of restarting at 1 every time.
            section = doc.add_section(WD_SECTION.NEW_PAGE)
            _configure_section(
                section,
                numbered=True,
                number_format="decimal",
                start=None,
                running_head=chapter_name,
                empty_first_page=True,
            )
            paragraph = _center_paragraph(doc, chapter_number, size=32, bold=True, color="102A43")
            paragraph.paragraph_format.space_before = Inches(3)
            _center_paragraph(doc, chapter_name, size=20, bold=True, color="102A43")
            doc.add_page_break()
            chapter_just_added = True
            continue

        if kind == "section":
            if chapter_just_added:
                chapter_just_added = False
            else:
                doc.add_page_break()
            paragraph = doc.add_paragraph(data)
            paragraph.style = doc.styles["Heading 1"]
            paragraph.paragraph_format.first_line_indent = Inches(0)
            paragraph.paragraph_format.space_after = Pt(8)
            in_references = data.upper() == "VIII. REFERENCES"
            continue

        if kind == "h2":
            paragraph = doc.add_paragraph(data)
            paragraph.style = doc.styles["Heading 2"]
            paragraph.paragraph_format.first_line_indent = Inches(0)
            continue

        if kind == "paragraph":
            _add_body_paragraph(doc, data)
            continue

        if kind == "reference":
            _add_reference_paragraph(doc, data)
            continue

        if kind == "image":
            caption, filename = data.split("|||", 1)
            image_path = FIGURES_DIR / filename
            if image_path.exists():
                paragraph = doc.add_paragraph()
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.paragraph_format.first_line_indent = Inches(0)
                run = paragraph.add_run()
                run.add_picture(str(image_path), width=Inches(5.9))
            cap = doc.add_paragraph(caption)
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap.paragraph_format.first_line_indent = Inches(0)
            for run in cap.runs:
                _set_run_font(run, size=12, bold=True)
            continue

        if kind == "pagebreak":
            doc.add_page_break()
            chapter_just_added = False

    doc.save(out_path)
    print(f"Typst content DOCX: {out_path}")


def copy_docx_output() -> bool:
    source_docx = METHOD_A_DIR / "research_method_a.docx"
    if not source_docx.exists():
        print("WARNING: Method A DOCX was not found; typst_content DOCX fallback was skipped.")
        return False
    shutil.copy2(source_docx, TYPST_DOCX)
    print(f"Typst content DOCX emergency fallback copied from Method A: {TYPST_DOCX}")
    return True


# ---------------------------------------------------------------------------
# Standalone survey results DOCX helpers
# ---------------------------------------------------------------------------
def _clean_markdown_inline(value: str) -> str:
    """Remove Markdown formatting while preserving the original values."""
    value = value.replace("\\|", "|")
    value = re.sub(r"<div\s+style=[\"']page-break-after:\s*always;[\"']\s*>\s*</div>", "", value, flags=re.I)
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", value)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", value)
    value = value.replace(" to ", "–") if re.search(r"\d+\.\d+ to \d+\.\d+", value) else value
    return re.sub(r"\s+", " ", value).strip()


def _split_markdown_table_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [_clean_markdown_inline(cell.strip()) for cell in stripped.split("|")]


def _is_markdown_table_separator(line: str) -> bool:
    cells = _split_markdown_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def _parse_table_alignment(separator: str) -> list[str]:
    alignment: list[str] = []
    for cell in _split_markdown_table_row(separator):
        raw = cell.strip()
        if raw.startswith(":") and raw.endswith(":"):
            alignment.append("center")
        elif raw.endswith(":"):
            alignment.append("right")
        else:
            alignment.append("left")
    return alignment


def _collect_survey_markdown_blocks(md_text: str) -> list[tuple[str, object]]:
    """Parse the small Markdown subset used in survey_data_results.md."""
    blocks: list[tuple[str, object]] = []
    lines = md_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if re.fullmatch(r"<div\s+style=[\"']page-break-after:\s*always;[\"']\s*>\s*</div>", stripped, flags=re.I):
            blocks.append(("pagebreak", ""))
            i += 1
            continue
        if stripped.startswith("#"):
            marker, _, heading = stripped.partition(" ")
            level = min(len(marker), 3)
            blocks.append((f"h{level}", _clean_markdown_inline(heading)))
            i += 1
            continue
        if stripped.startswith("|") and i + 1 < len(lines) and _is_markdown_table_separator(lines[i + 1]):
            header = _split_markdown_table_row(line)
            align = _parse_table_alignment(lines[i + 1])
            rows: list[list[str]] = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(_split_markdown_table_row(lines[i]))
                i += 1
            blocks.append(("table", {"header": header, "align": align, "rows": rows}))
            continue
        if stripped.startswith("- "):
            items: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                items.append(_clean_markdown_inline(lines[i].strip()[2:]))
                i += 1
            blocks.append(("bullets", items))
            continue
        paragraph_lines = [stripped]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or nxt.startswith("#") or nxt.startswith("|") or nxt.startswith("- ") or re.fullmatch(r"<div\s+style=[\"']page-break-after:\s*always;[\"']\s*>\s*</div>", nxt, flags=re.I):
                break
            paragraph_lines.append(nxt)
            i += 1
        blocks.append(("paragraph", _clean_markdown_inline(" ".join(paragraph_lines))))
    return blocks


def _set_table_width_percent(table, percent: int = 100) -> None:
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:type"), "pct")
    tbl_w.set(qn("w:w"), str(percent * 50))


def _shade_cell(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = tc_pr.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        tc_pr.append(shading)
    shading.set(qn("w:fill"), fill)


def _set_cell_text(cell, text: str, *, bold: bool = False, size: float = 9.5, color: str | None = None, align: str = "left") -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.first_line_indent = Inches(0)
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.alignment = {
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }.get(align, WD_ALIGN_PARAGRAPH.LEFT)
    run = paragraph.add_run(text)
    _set_run_font(run, size=size, bold=bold, color=color)


def _add_survey_table(doc: Document, table_data: dict[str, object]) -> None:
    header = list(table_data["header"])
    rows = list(table_data["rows"])
    align = list(table_data["align"])
    col_count = len(header)
    table = doc.add_table(rows=1, cols=col_count)
    table.style = "Table Grid"
    table.autofit = False
    _set_table_width_percent(table, 100)

    section = doc.sections[-1]
    usable_width = section.page_width - section.left_margin - section.right_margin
    ratios = table_data.get("ratios")
    if isinstance(ratios, list) and len(ratios) == col_count and sum(ratios) > 0:
        ratio_total = sum(float(ratio) for ratio in ratios)
        widths = [int(usable_width * (float(ratio) / ratio_total)) for ratio in ratios]
    elif col_count >= 6:
        first_col_width = int(usable_width * 0.19)
        other_width = int((usable_width - first_col_width) / (col_count - 1))
        widths = [first_col_width] + [other_width] * (col_count - 1)
    elif col_count == 5:
        widths = [int(usable_width * 0.24)] + [int(usable_width * 0.19)] * 4
    elif col_count == 4:
        widths = [int(usable_width * 0.34), int(usable_width * 0.28), int(usable_width * 0.19), int(usable_width * 0.19)]
    elif col_count == 3:
        widths = [int(usable_width * 0.46), int(usable_width * 0.30), int(usable_width * 0.24)]
    else:
        widths = [int(usable_width / max(col_count, 1))] * col_count

    for col_index, width in enumerate(widths):
        for cell in table.columns[col_index].cells:
            cell.width = width

    for index, text in enumerate(header):
        cell = table.rows[0].cells[index]
        _shade_cell(cell, "F7F9FC")
        _set_cell_text(cell, text, bold=True, color="102A43", align=align[index] if index < len(align) else "left")
        cell.width = widths[index]

    for row_data in rows:
        row = table.add_row()
        for index, text in enumerate(row_data[:col_count]):
            cell = row.cells[index]
            _set_cell_text(cell, text, align=align[index] if index < len(align) else "left")
            cell.width = widths[index]

    for row in table.rows:
        row.height = Pt(18)
    caption = table_data.get("caption")
    if caption:
        _add_survey_caption(doc, str(caption))
    else:
        spacer = doc.add_paragraph()
        spacer.paragraph_format.first_line_indent = Inches(0)
        spacer.paragraph_format.space_after = Pt(6)


def _set_table_cell_fill(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = tc_pr.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        tc_pr.append(shading)
    shading.set(qn("w:fill"), fill)


def _add_survey_title_page(doc: Document) -> None:
    """Render the DOCX title page to mirror the standalone Typst title box."""
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Inches(2.45)
    spacer.paragraph_format.first_line_indent = Inches(0)

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    _set_table_width_percent(table, 88)
    cell = table.rows[0].cells[0]
    cell.width = int((doc.sections[-1].page_width - doc.sections[-1].left_margin - doc.sections[-1].right_margin) * 0.88)
    _set_table_cell_fill(cell, "F7F9FC")
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ["top", "left", "bottom", "right"]:
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "12")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), "102A43")
        borders.append(element)
    tc_pr.append(borders)

    for paragraph in cell.paragraphs:
        paragraph.clear()
    title = cell.paragraphs[0]
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.first_line_indent = Inches(0)
    title.paragraph_format.space_before = Pt(18)
    run = title.add_run("Survey Data Results")
    _set_run_font(run, size=20, bold=True, color="102A43")

    divider = cell.add_paragraph()
    divider.alignment = WD_ALIGN_PARAGRAPH.CENTER
    divider.paragraph_format.first_line_indent = Inches(0)
    divider.paragraph_format.space_before = Pt(7)
    divider.paragraph_format.space_after = Pt(7)
    _set_paragraph_border(divider, color="B58B2A", size="6")

    subtitle = cell.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.first_line_indent = Inches(0)
    run = subtitle.add_run("Psychiatric Medication Use and Public Acceptance in Iraq")
    _set_run_font(run, size=14, color="111827")

    sample = cell.add_paragraph()
    sample.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sample.paragraph_format.first_line_indent = Inches(0)
    sample.paragraph_format.space_after = Pt(18)
    run = sample.add_run("Unified Analysis (N = 877)")
    _set_run_font(run, size=12, color="111827")


def _add_survey_heading(doc: Document, text: str, level: int) -> None:
    paragraph = doc.add_paragraph(text)
    paragraph.paragraph_format.first_line_indent = Inches(0)
    if level == 1:
        paragraph.style = doc.styles["Heading 1"]
        paragraph.paragraph_format.space_before = Pt(18)
        paragraph.paragraph_format.space_after = Pt(10)
        _set_paragraph_border(paragraph, color="B58B2A", size="6")
        for run in paragraph.runs:
            _set_run_font(run, size=16, bold=True, color="102A43")
    elif level == 2:
        paragraph.style = doc.styles["Heading 2"]
        paragraph.paragraph_format.space_before = Pt(14)
        paragraph.paragraph_format.space_after = Pt(8)
        for run in paragraph.runs:
            _set_run_font(run, size=13, bold=True, color="102A43")
    else:
        paragraph.paragraph_format.space_before = Pt(10)
        paragraph.paragraph_format.space_after = Pt(6)
        for run in paragraph.runs:
            _set_run_font(run, size=11.5, bold=True, color="111827")


def _add_survey_paragraph(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph(_clean_markdown_inline(text.replace("\\.", ".")))
    paragraph.paragraph_format.first_line_indent = Inches(0)
    paragraph.paragraph_format.line_spacing = 1.15
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for run in paragraph.runs:
        _set_run_font(run, size=11)


def _add_survey_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        paragraph = doc.add_paragraph(style="List Bullet")
        paragraph.paragraph_format.first_line_indent = Inches(0)
        paragraph.paragraph_format.left_indent = Inches(0.25)
        paragraph.paragraph_format.line_spacing = 1.15
        paragraph.paragraph_format.space_after = Pt(2)
        run = paragraph.add_run(_clean_markdown_inline(item))
        _set_run_font(run, size=11)


def _add_survey_caption(doc: Document, caption: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Inches(0)
    paragraph.paragraph_format.space_before = Pt(2)
    paragraph.paragraph_format.space_after = Pt(8)
    run = paragraph.add_run(caption)
    _set_run_font(run, size=9.5, bold=False, color="111827")


def _strip_percent(value: str) -> str:
    return value.replace("%", "")


def _rename_predictor(value: str) -> str:
    return {
        "const": "Intercept",
        "Intercept": "Intercept",
        "Age_Binary": "Age (binary)",
        "Gender_Binary": "Gender (binary)",
        "Edu_Binary": "Education (binary)",
        "Married_Binary": "Marital status (binary)",
        "PriorUse_Binary": "Prior use (binary)",
        "Q11": "Q11 — Overprescription belief",
        "Q12": "Q12 — Dependence belief",
        "Q13": "Q13 — Modern safety belief",
        "Fear_Binary": "Fear (binary)",
    }.get(value, value)


def _table_from_survey_source(tables: list[dict[str, object]], index: int) -> dict[str, object]:
    try:
        return tables[index]
    except IndexError as exc:
        raise ValueError(f"survey_data_results.md is missing expected table #{index + 1}") from exc


def _build_typeset_survey_blocks(raw_blocks: list[tuple[str, object]]) -> list[tuple[str, object]]:
    """Build the same section order/content as typst_content/survey_results.typ.

    Numeric cells are read from survey_data_results.md tables; this function only
    renames labels and adds the explanatory prose/captions used by the Typst
    survey-results document.
    """
    tables = [data for kind, data in raw_blocks if kind == "table"]
    source_text = "\n".join(str(data) for kind, data in raw_blocks if kind in {"paragraph", "bullets"})

    model = _table_from_survey_source(tables, 0)
    model_rows = model["rows"]  # type: ignore[index]
    model_table = {
        "header": ["Block", "Predictors", "McFadden R²", "LLR p-value"],
        "align": ["left", "left", "right", "right"],
        "ratios": [2, 4, 1, 1],
        "rows": [
            ["Block 1 (Demographics)", "Age, Gender, Education, Marital status", model_rows[0][2], model_rows[0][3]],
            ["Block 2 (+ Prior Use)", "Block 1 + Prior medication use", model_rows[1][2], model_rows[1][3]],
            ["Block 3 (+ Beliefs & Fear)", "Block 2 + Q11, Q12, Q13, Fear", model_rows[2][2], model_rows[2][3]],
        ],
        "caption": "Hierarchical model fit statistics across sequential blocks.",
    }

    aor = _table_from_survey_source(tables, 1)
    aor_table = {
        "header": ["Predictor", "Adjusted OR (95% CI)", "p-value"],
        "align": ["left", "right", "right"],
        "ratios": [3, 2, 1],
        "rows": [[_rename_predictor(row[0]), row[1], row[2]] for row in aor["rows"]],  # type: ignore[index]
        "caption": "Adjusted odds ratios from the final hierarchical logistic regression (Block 3).",
    }

    multi = _table_from_survey_source(tables, 2)
    yes_rows = [row for row in multi["rows"] if row[0] == "Q8=1 vs ref"]  # type: ignore[index]
    unsure_rows = [row for row in multi["rows"] if row[0] == "Q8=2 vs ref"]  # type: ignore[index]
    yes_table = {
        "header": ["Predictor", "RRR (95% CI)", "p-value"],
        "align": ["left", "right", "right"],
        "ratios": [3, 2, 1],
        "rows": [[_rename_predictor(row[1]), row[2], row[3]] for row in yes_rows],
        "caption": "Relative risk ratios for Q8 = Yes vs. No.",
    }
    unsure_table = {
        "header": ["Predictor", "RRR (95% CI)", "p-value"],
        "align": ["left", "right", "right"],
        "ratios": [3, 2, 1],
        "rows": [[_rename_predictor(row[1]), row[2], row[3]] for row in unsure_rows],
        "caption": "Relative risk ratios for Q8 = Not Sure vs. No.",
    }

    contact = _table_from_survey_source(tables, 3)
    contact_names = {
        "Q11 (Doctors prescribe medications more than necessary)": "Q11 — Overprescription",
        "Q12 (Most medications cause psychological or physical dependence)": "Q12 — Dependence",
        "Q13 (Modern medications are safer than older ones)": "Q13 — Modern safety",
    }
    contact_table = {
        "header": ["Item", "User Mdn", "Non-user Mdn", "M-W p", "Cliff's d", "χ² p", "Cramér's V"],
        "align": ["left", "right", "right", "right", "right", "right", "right"],
        "ratios": [3, 1, 1, 1, 1, 1, 1],
        "rows": [[contact_names.get(row[0], row[0]), *row[1:7]] for row in contact["rows"]],  # type: ignore[index]
        "caption": "Comparison of core belief items between medication users and non-users.",
    }

    silhouette = _table_from_survey_source(tables, 4)
    silhouette_table = {
        "header": ["k", "Silhouette Score"],
        "align": ["center", "center"],
        "ratios": [1, 1],
        "rows": silhouette["rows"],  # type: ignore[index]
        "caption": "Silhouette scores for candidate cluster solutions.",
    }

    profiles = _table_from_survey_source(tables, 5)
    profile_table = {
        "header": ["Profile", "n", "Q11 Mean", "Q12 Mean", "Q13 Mean"],
        "align": ["center", "right", "right", "right", "right"],
        "ratios": [1, 1, 1, 1, 1],
        "rows": profiles["rows"],  # type: ignore[index]
        "caption": "Mean belief scores by cluster profile (k = 4).",
    }

    demographics = _table_from_survey_source(tables, 6)
    demographic_rows = [row for row in demographics["rows"] if row[2] != "0"]  # type: ignore[index]
    demo_table = {
        "header": ["Variable", "Category", "Count", "%"],
        "align": ["left", "left", "right", "right"],
        "ratios": [2, 2, 1, 1],
        "rows": demographic_rows,
        "caption": "Demographic characteristics of respondents (N = 877).",
    }

    likert = _table_from_survey_source(tables, 7)
    likert_names = {
        "Q11": "Q11 — Doctors prescribe medications more than necessary",
        "Q12": "Q12 — Most medications cause psychological or physical dependence",
        "Q13": "Q13 — Modern medications are safer than older ones",
    }
    likert_table = {
        "header": ["Question", "Disagree %", "Neutral %", "Agree %"],
        "align": ["left", "right", "right", "right"],
        "ratios": [3, 1, 1, 1],
        "rows": [[likert_names.get(row[0], row[0]), *[ _strip_percent(v) for v in row[1:] ]] for row in likert["rows"]],  # type: ignore[index]
        "caption": "Distribution of agreement on core belief items (collapsed Likert categories).",
    }

    corr = _table_from_survey_source(tables, 8)
    corr_table = {
        "header": ["Variable", "Q11", "Q12", "Q13", "Concern", "Accept.", "Recommend"],
        "align": ["left", "right", "right", "right", "right", "right", "right"],
        "ratios": [2, 1, 1, 1, 1, 1, 1],
        "rows": corr["rows"],  # type: ignore[index]
        "caption": "Spearman correlation matrix among primary belief and attitude variables.",
    }

    acceptance = _table_from_survey_source(tables, 9)
    acceptance_table = {
        "header": ["Prior Use", "Recommend Yes %", "Sample n"],
        "align": ["left", "right", "right"],
        "ratios": [2, 1, 1],
        "rows": [[row[0], _strip_percent(row[1]), row[2]] for row in acceptance["rows"]],  # type: ignore[index]
        "caption": "Recommendation willingness by prior psychiatric medication use.",
    }

    attitudes = _table_from_survey_source(tables, 10)
    attitude_names = {
        "Safety perception": "Safety perception (Q6)",
        "Acceptability": "Acceptability (Q7)",
        "Recommendation willingness": "Recommendation willingness (Q8)",
        "Social concerns": "Social concerns (Q9)",
    }
    attitude_table = {
        "header": ["Question", "Yes %", "Not Sure %", "No %"],
        "align": ["left", "right", "right", "right"],
        "ratios": [3, 1, 1, 1],
        "rows": [[attitude_names.get(row[0], row[0]), *[_strip_percent(v) for v in row[1:]]] for row in attitudes["rows"]],  # type: ignore[index]
        "caption": "Response distribution for general attitude items.",
    }

    instrument_table = {
        "header": ["Code", "Question (Arabic)", "Response Options"],
        "align": ["center", "left", "left"],
        "ratios": [1, 4, 3],
        "rows": [
            ["Q1", "العمر (Age)", "18–25 / 26–35 / 36–45 / 46–60 / > 60"],
            ["Q2", "الجنس (Gender)", "Male / Female"],
            ["Q4", "المستوى التعليمي (Educational level)", "Primary / Middle School / High School / Institute-Diploma / University / Postgraduate"],
            ["Q5", "الحالة الاجتماعية (Marital status)", "Single / Married / Divorced / Widowed"],
            ["Q6", "هل تعتقد أن الأدوية النفسية آمنة؟ (Do you believe psychiatric medications are safe?)", "Yes / No / Not sure"],
            ["Q7", "هل ترى أن استخدامها مقبول مثل أدوية الضغط والسكري؟ (Is their use acceptable like hypertension or diabetes drugs?)", "Yes / No / Not sure"],
            ["Q8", "هل تنصح شخصًا مقربًا باستخدامها إذا احتاج إليها؟ (Would you advise someone close to use them if needed?)", "Yes / No / Not sure"],
            ["Q9", "هل لديك تخوف من التعامل مع شخص يتناول أدوية نفسية؟ (Do you fear interacting with someone on psychiatric medication?)", "Yes / No / Not sure"],
            ["Q11", "الأطباء يصفون الأدوية أكثر مما يجب (Doctors prescribe medications more than necessary)", "5-point Likert: Strongly disagree to Strongly agree"],
            ["Q12", "معظم الأدوية تسبب اعتمادًا نفسيًا أو جسديًا (Most medications cause psychological or physical dependence)", "5-point Likert"],
            ["Q13", "الأدوية الحديثة أكثر أمانًا من القديمة (Modern medications are safer than older ones)", "5-point Likert"],
            ["Q15", "أعتقد أن الأدوية النفسية ضرورية لصحتي (I believe psychiatric medications are necessary for my health)", "5-point Likert"],
            ["Q16", "الأدوية النفسية تحافظ على استقراري (Psychiatric medications maintain my stability)", "5-point Likert"],
            ["Q17", "بدون الأدوية النفسية ستتدهور حالتي (Without psychiatric medications my condition would deteriorate)", "5-point Likert"],
            ["Q18", "الأدوية النفسية تسبب آثارًا جانبية مزعجة (Psychiatric medications cause unpleasant side effects)", "5-point Likert"],
            ["Q19", "أشعر بالقلق من التعود أو الإدمان على الأدوية النفسية (I worry about habituation or addiction to psychiatric medications)", "5-point Likert"],
            ["Q20", "الأدوية النفسية قد تضر بصحتي على المدى الطويل (Psychiatric medications may harm my long-term health)", "5-point Likert"],
            ["Q22", "أشعر بتحسن عند استخدام الأدوية النفسية (I feel better when using psychiatric medications)", "5-point Likert"],
            ["Q23", "الأدوية تجعلني أفقد السيطرة على حياتي (Medications make me lose control of my life)", "5-point Likert"],
            ["Q24", "الأدوية تساعدني أن أكون أكثر طبيعية (Medications help me be more normal)", "5-point Likert"],
            ["Q25", "الأدوية تسبب لي مشاكل (Medications cause me problems)", "5-point Likert"],
            ["Q26", "الأدوية تجعلني أثق بقدرتي على العلاج (Medications make me trust my ability to recover)", "5-point Likert"],
            ["Q27", "استخدام الأدوية يشعرني بالخوف (Using medications makes me feel afraid)", "5-point Likert"],
            ["Q28", "الأدوية النفسية تساعدني على أن أكون بحالة أفضل (Psychiatric medications help me be in a better state)", "5-point Likert"],
            ["Q29", "الأدوية النفسية تساعدني على أن أكون بحالة أفضل (Psychiatric medications help me be in a better state)", "5-point Likert"],
            ["Q30", "الأدوية تجعل حياتي أسوأ (Medications make my life worse)", "5-point Likert"],
            ["Q31", "هل تستخدم أو سبق أن استخدمت دواء نفسي؟ (Do you use or have you previously used psychiatric medication?)", "Yes / No"],
            ["Q32", "الأدوية تسبب لي قلقًا بشأن آثارها (Medications cause me anxiety about their effects)", "5-point Likert"],
        ],
        "caption": "Complete survey instrument with question codes and response formats.",
    }

    primary_n = re.search(r"Complete-case n \(primary hierarchical models\):\s*(\d+)", source_text)
    sensitivity_n = re.search(r"Complete-case n \(sensitivity model\):\s*(\d+)", source_text)
    sensitivity_r2 = re.search(r"McFadden pseudo R²:\s*([0-9.]+)", source_text)
    multi_n = re.search(r"Complete-case n:\s*(\d+)", source_text)
    loglike = re.search(r"Model log-likelihood:\s*([-0-9.]+)", source_text)
    users = re.search(r"Users \(Q31=1\):\s*(\d+)", source_text)
    non_users = re.search(r"Non-users \(Q31=0\):\s*(\d+)", source_text)

    return [
        ("h1", "Hierarchical Block Logistic Regression"),
        ("p", f"The primary outcome variable is recommendation willingness (Q8: Yes vs. No). Complete-case sample size for hierarchical models: n = {primary_n.group(1) if primary_n else '647'}."),
        ("h2", "Model Comparison"),
        ("p", "Three nested blocks were fitted sequentially to evaluate incremental explanatory contributions."),
        ("table", model_table),
        ("p", "Block 3 demonstrates a statistically significant improvement in model fit (LLR p < 0.0001), indicating that attitudinal variables (belief items Q11–Q13 and fear of psychiatric medication) substantially improve prediction of recommendation willingness beyond demographic and prior-use factors."),
        ("h2", "Final Model — Adjusted Odds Ratios (Block 3)"),
        ("table", aor_table),
        ("p", "Gender, belief that modern medications are safer (Q13), and fear of psychiatric medication emerged as statistically significant predictors. Fear halved the odds of recommending psychiatric medications (AOR = 0.504), while endorsement of modern medication safety nearly doubled them (AOR = 1.507 per unit increase)."),
        ("h2", "Sensitivity Model with Proximal Beliefs (Q6/Q7)"),
        ("p", f"A supplementary model adding safety perception (Q6) and acceptability (Q7) was fitted on a reduced sample (n = {sensitivity_n.group(1) if sensitivity_n else '406'}) because these items are conceptually proximate to the outcome and may inflate explanatory variance."),
        ("bullets", [f"McFadden pseudo R²: {sensitivity_r2.group(1) if sensitivity_r2 else '0.2440'}", "Fit type: MLE"]),
        ("p", "This model is reported separately to avoid conflation of proximal predictors with distal attitudinal measures."),
        ("pagebreak", ""),
        ("h1", "Multinomial Logistic Regression"),
        ("p", f"This model preserves the three-category structure of Q8 (No / Yes / Not sure) rather than collapsing hesitant respondents. Complete-case sample: n = {multi_n.group(1) if multi_n else '837'}. Model log-likelihood: {loglike.group(1) if loglike else '−748.910'}."),
        ("p", "The reference category is the lowest coded group (Q8 = No). Coefficients express relative risk ratios for endorsing \"Yes\" or \"Not sure\" compared with \"No.\""),
        ("h2", "Q8 = Yes vs. Reference (No)"),
        ("table", yes_table),
        ("h2", "Q8 = Not Sure vs. Reference (No)"),
        ("table", unsure_table),
        ("p", "Gender is significant across both outcome equations. The belief that modern medications are safer (Q13) is strongly predictive of endorsing \"Yes\" but not \"Not sure,\" suggesting that this belief discriminates between active recommendation and mere hesitation."),
        ("pagebreak", ""),
        ("h1", "Contact Hypothesis: Users vs. Non-Users on Core Beliefs"),
        ("p", f"This exploratory analysis examines whether personal experience with psychiatric medication (Q31) is associated with different belief profiles on items Q11–Q13. Users: n = {users.group(1) if users else '127'}; Non-users: n = {non_users.group(1) if non_users else '716'}."),
        ("table", contact_table),
        ("p", "Users endorsed significantly higher agreement with modern medication safety (Q13) and somewhat lower agreement with overprescription concern (Q11) compared with non-users. Effect sizes are small but consistent with contact hypothesis predictions."),
        ("pagebreak", ""),
        ("h1", "Exploratory Stigma Phenotypes (K-Means Clustering)"),
        ("p", "Standardised scores on Q11–Q13 were submitted to K-means clustering. Silhouette analysis favoured k = 4."),
        ("h2", "Cluster Selection"),
        ("table", silhouette_table),
        ("h2", "Profile Characterisation"),
        ("table", profile_table),
        ("p", "Profile 0 reflects uniformly high agreement across all three belief dimensions. Profile 3 shows high overprescription and dependence concern but low endorsement of modern safety — a pattern potentially indicative of generalised pharmacological scepticism. Profile 1 shows moderate-to-low scores on all items, while Profile 2 combines low overprescription concern with high dependence concern. These profiles warrant further investigation with confirmatory approaches."),
        ("pagebreak", ""),
        ("h1", "Demographics Summary"),
        ("table", demo_table),
        ("pagebreak", ""),
        ("h1", "Core Beliefs — Likert Distribution"),
        ("table", likert_table),
        ("h1", "Correlation Matrix: Primary Beliefs"),
        ("table", corr_table),
        ("h1", "Acceptance by Prior Use"),
        ("table", acceptance_table),
        ("h1", "General Attitudes Distribution"),
        ("table", attitude_table),
        ("pagebreak", ""),
        ("h1", "Notes for Manuscript Positioning"),
        ("bullets", [
            "Hierarchical and multinomial modelling are suitable main-text analyses because they preserve response structure and clarify incremental explanatory value.",
            "K-means profiling should be presented as an exploratory secondary analysis.",
            "For stronger latent construct validation in future work, ordinal EFA/CFA with polychoric correlations is recommended on appropriately scoped item blocks.",
        ]),
        ("pagebreak", ""),
        ("h1", "Survey Instrument — Full Question List"),
        ("p", "The following table presents all questions administered in the survey along with their response options."),
        ("table", instrument_table),
    ]


def build_survey_results_docx(md_path: Path = SURVEY_RESULTS_MD, out_path: Path = SURVEY_RESULTS_DOCX) -> None:
    """Build a DOCX replica of the standalone Typst survey results report.

    The writer does not convert the PDF. It reads survey_data_results.md,
    reshapes those result tables into the same typeset report structure used by
    typst_content/survey_results.typ, and then applies matching Word styles.
    """
    if not md_path.exists():
        print(f"WARNING: {md_path} was not found; survey results DOCX generation was skipped.")
        return

    raw_blocks = _collect_survey_markdown_blocks(md_path.read_text(encoding="utf-8"))
    report_blocks = _build_typeset_survey_blocks(raw_blocks)
    doc = Document()
    _setup_docx_styles(doc)
    _set_update_fields_on_open(doc)
    _configure_section(doc.sections[0], numbered=True, number_format="decimal", start=1)
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)

    _add_survey_title_page(doc)
    doc.add_page_break()
    _front_title(doc, "Contents")
    toc_para = doc.add_paragraph()
    toc_para.paragraph_format.first_line_indent = Inches(0)
    _add_field_run(toc_para, r'TOC \o "1-2" \h \z \u', dirty=True)
    doc.add_page_break()

    for kind, data in report_blocks:
        if kind == "h1":
            _add_survey_heading(doc, str(data), 1)
        elif kind == "h2":
            _add_survey_heading(doc, str(data), 2)
        elif kind == "h3":
            _add_survey_heading(doc, str(data), 3)
        elif kind == "p":
            _add_survey_paragraph(doc, str(data))
        elif kind == "bullets":
            _add_survey_bullets(doc, data)  # type: ignore[arg-type]
        elif kind == "table":
            _add_survey_table(doc, data)  # type: ignore[arg-type]
        elif kind == "pagebreak":
            doc.add_page_break()

    doc.save(out_path)
    print(f"Survey results DOCX: {out_path}")


def run_typst_content(md_path: Path | None = None) -> None:
    ensure_dirs()
    if md_path is None:
        ensure_production_dirs()
        copy_figure_assets()
        md_path = ASSEMBLED_DIR / "comprehensive_research.md"
        if not md_path.exists():
            md_path = assemble_markdown()
    if find_university_logo() is None:
        print("WARNING: university logo PNG was not found at repository root or in figures/; cover logo placement was skipped.")
    source_path = write_typst_source(md_path)
    print(f"Editable Typst source: {source_path}")
    compile_typst_pdf()
    compile_survey_results_pdf()
    build_survey_results_docx()
    try:
        build_typst_content_docx(md_path, TYPST_DOCX)
    except Exception as exc:
        print(f"WARNING: Typst content DOCX generation failed ({exc}); falling back if possible.")
        copy_docx_output()


def main() -> None:
    run_typst_content()


if __name__ == "__main__":
    main()
