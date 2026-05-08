#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from build_production import (
    ASSEMBLED_DIR,
    FIGURES_DIR,
    METHOD_A_DIR,
    REPO_ROOT,
    assemble_markdown,
    copy_figure_assets,
    ensure_dirs as ensure_production_dirs,
    iter_markdown_blocks,
)

TYPST_CONTENT_DIR = REPO_ROOT / "typst_content"
TYPST_OUTPUT_DIR = TYPST_CONTENT_DIR / "output"
TYPST_SOURCE = TYPST_CONTENT_DIR / "research.typ"
TYPST_PDF = TYPST_OUTPUT_DIR / "research.pdf"
TYPST_DOCX = TYPST_OUTPUT_DIR / "research.docx"

TITLE = "Psychiatric Medication Use and Public Acceptance in Iraq"
STUDENTS = [
    "Abdul Rahman Wakaa Ali",
    "Ali Basem Hammoud",
    "Shifa Safi Aboud",
    "Zainab Mashal Nayef",
]
SUPERVISOR = "Hameed Adnan"
UNIVERSITY = "University of Al-Maarif"
COLLEGE = "College of Pharmacy"
MONTH_YEAR = "May, 2026"


def typst_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


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
            else:
                continue

        if kind == "chaptertitle":
            chapter_number, chapter_name = (data.split("|||", 1) + [""])[:2]
            if chapter_number == "Chapter One":
                target = main_calls
                target.append("#start-main-numbering()")
            target.append(f"#chapter-page({typst_string(chapter_number)}, {typst_string(chapter_name)})")
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
            fn = "refp" if in_references else "p"
            target.append(f"#{fn}({typst_string(text)})")
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

#set page(paper: "a4", margin: 1.5cm, background: page-border)
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
#let p(s) = par(first-line-indent: 1.27cm, justify: true)[#s]
#let refp(s) = block(above: 3pt, below: 5pt)[
  #set text(size: 12pt)
  #par(first-line-indent: 0pt, hanging-indent: 0.5in, justify: true)[#s]
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
]

#let start-main-numbering() = [
  #pagebreak(weak: true)
  #set page(numbering: "1", number-align: top + center)
  #counter(page).update(1)
]

// Cover page: unnumbered. Certification begins on the second page.
#set page(numbering: none)
#align(center)[
  #text(size: 15pt, weight: "bold", fill: navy)[Republic of Iraq] \\
  #text(size: 15pt, weight: "bold", fill: navy)[Ministry of Higher Education and Scientific Research] \\
  #text(size: 15pt, weight: "bold", fill: navy)[{UNIVERSITY}] \\
  #text(size: 15pt, weight: "bold", fill: navy)[{COLLEGE}]
  #v(0.55cm)
  #box(width: 88%, inset: 12pt, stroke: 1pt + gold, fill: pale)[
    #text(size: 24pt, weight: "bold", fill: navy)[{TITLE}]
  ]
  #v(0.45cm)
  #text(size: 14pt)[A Project Submitted to] \\
  #text(size: 13pt)[The {COLLEGE}, {UNIVERSITY}, Department of Clinical Pharmacy, in Partial Fulfillment for the Bachelor of Pharmacy]
  #v(0.45cm)
  #text(size: 14pt, weight: "bold")[By] \\
  #text(size: 20pt, weight: "bold", fill: navy)[{student_lines}]
  #v(0.35cm)
  #text(size: 14pt, weight: "bold")[Supervised by:] \\
  #text(size: 20pt, weight: "bold", fill: navy)[{SUPERVISOR}] \\
  #text(size: 16pt)[Supervisor's Degree]
  #v(0.25cm)
  #text(size: 14pt)[{MONTH_YEAR}]
]

// Roman-numbered preliminary pages.
#pagebreak()
#set page(numbering: "i", number-align: top + center)
#counter(page).update(1)
#front-title[Certification of the Supervisor]
#p("I certify that this project entitled “{TITLE}” was prepared by the fifth-year students {students} under my supervision at the {COLLEGE}/{UNIVERSITY} in partial fulfillment of the graduation requirements for the Bachelor Degree in Pharmacy.")
#align(right)[#text(weight: "bold")[Supervisor's name: {SUPERVISOR}]]
#v(0.2cm)
#align(right)[Date:]
#v(0.35cm)
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
#front-title[List of Tables]
#p("No manuscript tables are currently embedded as formal Typst tables in this editable source. Statistical results are reported in the text and figures.")
#v(0.4cm)
#front-title[List of Abbreviations]
#par(first-line-indent: 0pt)[AOR: Adjusted Odds Ratio \\
CI: Confidence Interval \\
LLR: Likelihood Ratio Test \\
MLE: Maximum Likelihood Estimation \\
OR: Odds Ratio \\
PTSD: Post-Traumatic Stress Disorder \\
RRR: Relative Risk Ratio \\
Q6/Q7/Q8/Q9/Q11/Q12/Q13: Survey question item codes used in analysis and reporting \\
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


def convert_typst_docx_with_pandoc() -> bool:
    pandoc = shutil.which("pandoc")
    if pandoc is None:
        print("WARNING: pandoc is not installed; Typst-to-DOCX conversion was skipped.")
        return False
    try:
        result = subprocess.run(
            [pandoc, str(TYPST_SOURCE), "-f", "typst", "-t", "docx", "-o", str(TYPST_DOCX)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=300,
        )
    except subprocess.TimeoutExpired as exc:
        print("WARNING: Pandoc Typst-to-DOCX conversion timed out; falling back if possible.")
        _print_process_output(exc.stdout)
        _print_process_output(exc.stderr)
        return False
    if result.returncode != 0:
        print("WARNING: Pandoc could not convert typst_content/research.typ to DOCX; falling back if possible.")
        _print_process_output(result.stdout)
        _print_process_output(result.stderr)
        return False
    print(f"Typst content DOCX: {TYPST_DOCX}")
    return True


def copy_docx_output() -> bool:
    source_docx = METHOD_A_DIR / "research_method_a.docx"
    if not source_docx.exists():
        print("WARNING: Method A DOCX was not found; typst_content DOCX fallback was skipped.")
        return False
    shutil.copy2(source_docx, TYPST_DOCX)
    print(f"Typst content DOCX fallback copied from Method A: {TYPST_DOCX}")
    return True

def run_typst_content(md_path: Path | None = None) -> None:
    ensure_dirs()
    if md_path is None:
        ensure_production_dirs()
        copy_figure_assets()
        md_path = ASSEMBLED_DIR / "comprehensive_research.md"
        if not md_path.exists():
            md_path = assemble_markdown()
    source_path = write_typst_source(md_path)
    print(f"Editable Typst source: {source_path}")
    compile_typst_pdf()
    if not convert_typst_docx_with_pandoc():
        copy_docx_output()


def main() -> None:
    run_typst_content()


if __name__ == "__main__":
    main()
