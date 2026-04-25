# Production and Submission Plan

This plan is written for manual execution through GitHub Copilot PR prompts.

## 1) Front-matter and chapter title pages

The current pipeline builds the manuscript body from `content/*.md`, `references.md`, and figure assets, then generates DOCX/PDF outputs. To support your missing pages and chapter title style request, make the output pipeline generate a dedicated front-matter block before Chapter One and style each chapter title page with centered text, chapter number, chapter name in smaller font, and a horizontal line above and below the title block.

Recommended production order in generated DOCX/PDF is:

Cover Page, Certification of Supervisor, Dedication, Acknowledgment, Table of Contents, List of Figures, List of Tables, List of Abbreviations, then Chapter One onward.

## 2) Question IDs (Q11, Q13, Q20) in manuscript text

Q-style variable names are currently used in results/discussion text. Keep them in analysis-facing sections, but define each one the first time it appears, for example: "Q13 (belief that modern psychiatric medicines are safer than older ones)." Then either continue with the label or switch to full wording for readability.

## 3) Automatic ToC / LoF / LoT in production

Use automatic generation in the DOCX stage whenever possible.

- In a DOCX-first workflow, generate heading styles (`Heading 1/2`) and figure/table captions using Word fields or python-docx compatible structures.
- If moving to LaTeX/Pandoc for final PDF, use generated `\tableofcontents`, `\listoffigures`, and `\listoftables`.
- Do not type ToC/LoF/LoT manually unless you are doing a one-time emergency submission.

## 4) What to do now to make List of Figures easy later

Start now with strict caption discipline.

- Every figure must have one explicit caption line in markdown figure files.
- Captions should follow a consistent pattern such as `Figure X. ...`.
- Keep figure titles human-readable and avoid only filenames.
- Keep figure numbering stable and sequential in final assembled manuscript order.

## 5) APA 7 checks

The current `references.md` is close to a journal-style bibliography but not fully APA 7 in all entries. For final APA 7 compliance, add a validation step in production that checks:

- Author formatting and initials consistency.
- Journal/book title casing and italics rules.
- Volume(issue), page range formatting.
- DOI URL format (`https://doi.org/...`) consistency.
- Non-standard placeholders such as "ahead of print" style lines.

## 6) Page numbering strategy

Use section-aware page numbering in DOCX export:

- Front matter in lowercase Roman numerals (i, ii, iii...).
- Main body in Arabic numerals (1, 2, 3...).
- Restart numbering at Chapter One.

## 7) GitHub Actions release strategy

Yes, release artifacts are better than storing generated binaries in the repo.

Recommended architecture:

- Source of truth: `content/`, `references.md`, `figures/`, and `production/src/`.
- CI job runs the production pipeline on push/PR.
- On tagged release (or manual workflow dispatch), upload DOCX/PDF/TEX as release assets.
- Keep only source files under version control; avoid committing generated binaries except when explicitly needed.

## 8) Will CI delete existing production code?

Not by default. A GitHub Action only changes repository files if you explicitly script commit/push steps. If the workflow only builds and uploads artifacts, it will not modify tracked source files in your branch.

## 9) Suggested PR split

Use multiple PRs for safer review:

- PR 1: Front-matter templates + chapter title page styling + page numbering sections.
- PR 2: Automatic ToC/LoF/LoT and caption normalization.
- PR 3: GitHub Action for build/test/release artifacts and optional cleanup policy for generated files.
- PR 4: APA 7 lint/check script and optional citation normalization utility.

## 10) Copilot prompts you can paste

### Prompt A (front matter + chapter pages)

Implement manuscript front-matter generation in `production/src/build_production.py` and related templates.

Requirements:
1. Add generated pages before Chapter One in this exact order: Cover Page, Certification of the Supervisor, Dedication, Acknowledgment, Table of Contents, List of Figures, List of Tables, List of Abbreviations.
2. Add chapter title pages that are centered vertically and horizontally and contain:
   - "Chapter X" line,
   - chapter name in a smaller font below it,
   - short horizontal line above and below the title block.
3. Preserve the existing content assembly logic and do not modify source manuscript files in `content/`.
4. Keep Times New Roman output formatting and current margins unless explicitly set elsewhere.
5. Add tests or smoke checks where practical.

### Prompt B (automatic ToC/LoF/LoT + captions)

Add automatic Table of Contents, List of Figures, and List of Tables support to the production pipeline.

Requirements:
1. Ensure headings and caption structures are exported in a way Word/Pandoc can build ToC/LoF/LoT automatically.
2. Add a caption normalization pass so figure captions are consistent and ordered.
3. Do not hardcode ToC/LoF/LoT entries manually.
4. Update documentation in `production/README.md` with exact build and refresh instructions.

### Prompt C (GitHub Action build + release assets)

Create a GitHub Actions workflow under `.github/workflows/production.yml`.

Requirements:
1. On push and pull_request: run the production build (`python production/src/build_production.py`) and upload outputs as workflow artifacts.
2. On tag/release event: publish DOCX/PDF/TEX outputs as GitHub Release assets.
3. Do not commit generated binaries back to the repository from CI.
4. Cache dependencies and fail fast on build errors.
5. Add a short operations section in `production/README.md` describing trigger behavior and where artifacts appear.

### Prompt D (APA 7 validator)

Add an APA 7 reference checker script (for `references.md`) and integrate it into CI.

Requirements:
1. Create a script in `production/src/` that scans entries and flags likely APA 7 issues (author punctuation, DOI format, title casing, year placement, volume/issue/page patterns).
2. Output warnings with line numbers and suggested fixes.
3. Add a CI step that runs the checker and reports warnings without blocking releases initially.
4. Document how to run it locally.
