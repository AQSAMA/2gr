# College Guideline vs AGENTS.md/outline.md: Conflict Map and Fix Plan

## Scope
This note identifies where the provided college instructions differ from the repository's governing documents (`AGENTS.md` and `outline.md`) and gives a practical correction path that preserves current manuscript consistency.

## Confirmed Conflicts (Status Updated)

### 1) Margins specification conflict
- College sheet says all margins are 1.5 cm.
- `AGENTS.md` previously specified 3 cm binding edge and 2 cm on other edges.
- `AGENTS.md` keeps final margin enforcement at Word stage under college-alignment controls.

**Applied Fix:** `AGENTS.md` now uses 1.5 cm on all sides and explicitly restates this in Word-stage controls.

### 2) Front-matter list mismatch (List of Abbreviations)
- College sheet includes "List of Abbreviations" in project arrangement.
- `AGENTS.md` deferred front matter list does not include it.
- `outline.md` front-matter deferred section also omits it.

**Applied Fix:** "List of Abbreviations" has been added as a deferred front-matter item in both `AGENTS.md` and `outline.md`.

### 3) Chapter-title hierarchy mismatch (operational vs final output)
- College sheet frames chapter-based output directly.
- `outline.md` uses internal Roman-structure sections (I–VIII) and maps them to final chapter order.
- This is not a scientific conflict, but can look inconsistent during review if mapping is not preserved in final document.

**Fix:** Keep current drafting structure, then enforce chapter labels during final export exactly as listed in the college format.

## Non-Conflicts (Already Aligned)

- Main text chapter order for survey/research projects is aligned.
- Page numbering rule (Roman preliminary pages, Arabic from Introduction onward) is aligned.
- Thesis length target (20–25 pages excluding references) is aligned.
- APA reference style is aligned.
- Line spacing (1.5), paragraph indentation by tab/first-line indent, and Times New Roman body size are aligned at final formatting stage.
- Table title above table and figure title below figure are already recognized in governance-level polishing instructions.

## Potentially Misread Items (Not Real Conflicts)

- College says "minimum 20 references". `AGENTS.md` says around 50 when appropriate and does not force reduction. This is stricter than minimum and remains compliant.
- College includes front matter in final arrangement. `AGENTS.md` marks front matter as deferred in current phase only, not removed.

## Recommended Correction Sequence

1. Keep current manuscript content unchanged for now (to avoid breaking source-scoping and results provenance rules).
2. Patch governance files only:
   - Add "List of Abbreviations" to deferred front matter in `AGENTS.md` and `outline.md`.
   - Standardize margin policy to 1.5 cm on all sides to match college instructions.
3. At export stage, apply final college formatting package in Word (page numbering, margins, heading sizes, tab indents, caption placement).
4. Add a brief "format compliance" checklist before submission.

## Impact on Existing Drafts

If your chapters were written according to `AGENTS.md` + `outline.md`, they remain methodologically consistent. The main updates were governance-level formatting alignment items rather than data or scientific-content changes.
