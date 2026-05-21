#!/usr/bin/env python3
"""Convert the comprehensive survey-results Markdown to Typst calls.

This module is consumed by ``build_typst_content.py`` to add a detailed
statistical-analysis appendix to the editable Typst document. It does
not touch the upstream analysis output file, the assembled manuscript
Markdown, or the Method A / Method B build paths.

The numeric content of the appendix is preserved exactly as written in
``analysis_pipeline/output/survey_data_results_comprehensive.md``; only
the visual formatting is upgraded (proper Typst tables, italicized
subtitle, structured bullets, smaller appendix typography).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_CODE_RE = re.compile(r"`([^`]+)`")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
_TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|?\s*$")

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


def _typst_string(value: str) -> str:
    """Encode a Python string as a Typst string literal."""
    return json.dumps(value, ensure_ascii=False)


def _escape_typst_markup(value: str) -> str:
    """Escape characters that have meaning in Typst markup mode."""
    return value.translate(_TYPST_MARKUP_ESCAPES)


def _strip_inline(text: str) -> str:
    """Remove markdown bold/code/link markers, keep human-readable text."""
    text = _BOLD_RE.sub(r"\1", text)
    text = _CODE_RE.sub(r"\1", text)
    text = _LINK_RE.sub(r"\1", text)
    text = text.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def _markup_with_bold(text: str) -> str:
    """Return a Typst markup string that preserves ``**bold**`` runs.

    The output is intended to be passed to a helper that calls
    ``eval(s, mode: "markup")``: bold spans are emitted as
    ``#strong[...]`` while every other character that has meaning in
    Typst markup is escaped so it renders verbatim.
    """
    placeholders: list[str] = []

    def stash(match: re.Match[str]) -> str:
        placeholders.append(_strip_inline(match.group(1)))
        return f"\x00{len(placeholders) - 1}\x00"

    staged = _BOLD_RE.sub(stash, text)
    # Inline ``code`` and links collapse to plain text in this appendix.
    staged = _CODE_RE.sub(r"\1", staged)
    staged = _LINK_RE.sub(r"\1", staged)
    staged = staged.replace("\u00a0", " ")
    staged = re.sub(r"\s+", " ", staged).strip()
    escaped = _escape_typst_markup(staged)

    def restore(match: re.Match[str]) -> str:
        return f"#strong[{placeholders[int(match.group(1))]}]"

    return re.sub(r"\x00(\d+)\x00", restore, escaped)


# ---------------------------------------------------------------------------
# Table parsing
# ---------------------------------------------------------------------------
def _split_table_row(line: str) -> List[str]:
    inner = line.strip().strip("|")
    return [cell.strip() for cell in inner.split("|")]


def _parse_table_alignments(separators: List[str]) -> List[str]:
    aligns: List[str] = []
    for sep in separators:
        marker = sep.strip()
        left = marker.startswith(":")
        right = marker.endswith(":")
        if left and right:
            aligns.append("center")
        elif right:
            aligns.append("right")
        else:
            aligns.append("left")
    return aligns


def _parse_table(lines: List[str], start: int) -> Tuple[dict, int]:
    headers = _split_table_row(lines[start])
    aligns = _parse_table_alignments(_split_table_row(lines[start + 1]))
    if len(aligns) < len(headers):
        aligns.extend(["left"] * (len(headers) - len(aligns)))

    rows: List[List[str]] = []
    idx = start + 2
    while idx < len(lines) and _TABLE_ROW_RE.match(lines[idx]):
        cells = _split_table_row(lines[idx])
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        else:
            cells = cells[: len(headers)]
        rows.append([_strip_inline(cell) for cell in cells])
        idx += 1

    return (
        {
            "headers": [_strip_inline(h) for h in headers],
            "aligns": aligns,
            "rows": rows,
        },
        idx,
    )


def _emit_table(table: dict) -> str:
    headers = table["headers"]
    aligns = table["aligns"]
    rows = table["rows"]

    headers_typst = "(" + ", ".join(_typst_string(h) for h in headers)
    if len(headers) == 1:
        headers_typst += ","
    headers_typst += ")"

    aligns_typst = "(" + ", ".join(aligns)
    if len(aligns) == 1:
        aligns_typst += ","
    aligns_typst += ")"

    if rows:
        row_chunks: List[str] = []
        for row in rows:
            chunk = "(" + ", ".join(_typst_string(c) for c in row)
            if len(row) == 1:
                chunk += ","
            chunk += ")"
            row_chunks.append(chunk)
        rows_typst = "(" + ", ".join(row_chunks) + ",)"
    else:
        rows_typst = "()"

    return f"#datatable({headers_typst}, {aligns_typst}, {rows_typst})"


# ---------------------------------------------------------------------------
# Block parser
# ---------------------------------------------------------------------------
def parse_to_typst_calls(md_text: str, *, drop_first_h1: bool = True) -> List[str]:
    """Convert the comprehensive analysis Markdown to Typst function calls.

    The first ``#`` heading is dropped by default because it duplicates
    the thesis title; the caller wraps the output with its own appendix
    section title.
    """
    lines = md_text.splitlines()
    calls: List[str] = []
    paragraph_lines: List[str] = []
    bullet_lines: List[str] = []
    first_h1_seen = False

    def flush_paragraph() -> None:
        if paragraph_lines:
            text = " ".join(paragraph_lines).strip()
            if text:
                calls.append(f"#para({_typst_string(_markup_with_bold(text))})")
            paragraph_lines.clear()

    def flush_bullets() -> None:
        if bullet_lines:
            items = [
                _typst_string(_markup_with_bold(item)) for item in bullet_lines
            ]
            joined = ", ".join(items)
            if len(items) == 1:
                joined += ","
            calls.append(f"#bullets(({joined}))")
            bullet_lines.clear()

    idx = 0
    while idx < len(lines):
        line = lines[idx].rstrip()

        # HTML page break.
        if line.strip() == '<div style="page-break-after: always;"></div>':
            flush_paragraph()
            flush_bullets()
            calls.append("#pagebreak(weak: true)")
            idx += 1
            continue

        m_h1 = re.match(r"^#\s+(.+)$", line)
        m_h2 = re.match(r"^##\s+(.+)$", line)
        m_h3 = re.match(r"^###\s+(.+)$", line)

        if m_h1:
            flush_paragraph()
            flush_bullets()
            text = _strip_inline(m_h1.group(1))
            if drop_first_h1 and not first_h1_seen:
                first_h1_seen = True
            else:
                calls.append(f"#h2({_typst_string(text)})")
            idx += 1
            continue

        if m_h2:
            flush_paragraph()
            flush_bullets()
            calls.append(f"#h2({_typst_string(_strip_inline(m_h2.group(1)))})")
            idx += 1
            continue

        if m_h3:
            flush_paragraph()
            flush_bullets()
            calls.append(f"#h3({_typst_string(_strip_inline(m_h3.group(1)))})")
            idx += 1
            continue

        # Markdown table.
        if (
            _TABLE_ROW_RE.match(line)
            and idx + 1 < len(lines)
            and _TABLE_SEP_RE.match(lines[idx + 1])
        ):
            flush_paragraph()
            flush_bullets()
            table, idx = _parse_table(lines, idx)
            calls.append(_emit_table(table))
            continue

        m_bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        if m_bullet:
            flush_paragraph()
            bullet_lines.append(m_bullet.group(1))
            idx += 1
            continue

        if not line.strip():
            flush_paragraph()
            flush_bullets()
            idx += 1
            continue

        # Default: extend the current paragraph.
        flush_bullets()
        paragraph_lines.append(line.strip())
        idx += 1

    flush_paragraph()
    flush_bullets()
    return calls


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
APPENDIX_TITLE = "Appendix A. Detailed Statistical Analysis Output"
APPENDIX_RUNNING_HEAD = "Appendix A"


def render_appendix_calls(md_path: Path) -> List[str]:
    """Read the survey-results Markdown and emit appendix Typst calls."""
    text = md_path.read_text(encoding="utf-8")

    subtitle: str | None = None
    match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    if match:
        subtitle = _strip_inline(match.group(1))

    calls: List[str] = [
        # The running head is updated *before* the section title so the
        # ``weak`` page break inside ``#section-title`` lands on a page
        # that already shows ``Appendix A`` in the header. Otherwise the
        # first appendix page would inherit the previous chapter's
        # running head until the next page boundary.
        f"#set-running-head({_typst_string(APPENDIX_RUNNING_HEAD)})",
        f"#section-title({_typst_string(APPENDIX_TITLE)})",
    ]
    if subtitle:
        calls.append(f"#appendix-subtitle({_typst_string(subtitle)})")
    calls.extend(parse_to_typst_calls(text, drop_first_h1=True))
    return calls
