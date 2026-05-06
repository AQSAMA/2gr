# Production Pipeline

This folder contains a self-contained production pipeline that keeps source research text unchanged and generates publication-ready outputs using one unified Python production path.

## Input sources used
- `/home/runner/work/2gr/2gr/content/*.md`
- `/home/runner/work/2gr/2gr/references.md`
- `/home/runner/work/2gr/2gr/figures/*.png`

## Outputs
- `assembled/comprehensive_research.md`
- `method_a_python/research_method_a.pdf`
- `method_a_python/research_method_a.docx`
- `method_a_python/research_method_a.tex`

## Run
```bash
cd /home/runner/work/2gr/2gr
python -m pip install -r production/requirements.txt
python production/src/build_production.py
```

## Cover and front-matter behavior
- Front-matter pages are authored in `content/00_cover.md` as the single source for cover-related material.
- DOCX outputs still allow field refresh for navigation lists when needed in final formatting.

## Refresh instructions after each content update
1. Re-run the build command:
   ```bash
   python production/src/build_production.py
   ```
2. Open the generated DOCX file in Word (`production/method_a_python/research_method_a.docx`).
3. Select all (`Ctrl+A`) and update fields (`F9`) to refresh:
   - Table of Contents
   - List of Figures
   - List of Tables
4. Save the document after field refresh if you need a final submission copy.

## Caption normalization
- Figure captions are normalized and ordered automatically during assembly.
- Captions are exported in consistent `Figure N. ...` format so ToC/LoF generation remains stable across runs.
## Operations (CI/CD)
The workflow in `.github/workflows/production.yml` runs on every `push` and `pull_request`, executes `python production/src/build_production.py`, and uploads the generated outputs as run artifacts in the Actions **Artifacts** panel.

When a tag push (for example `v1.0.0`) or a published GitHub Release event occurs, the same build runs again and DOCX/PDF/TEX/MD outputs are uploaded as Release assets on the matching tag/release page.

CI only builds and publishes artifacts/assets; it does not commit generated binary files back to the repository.

## Notes
- The pipeline does not modify any file in `content/`, `sources/`, `figures/`, or other repository paths.
- Page size/margins, Times New Roman style target, and line spacing are applied in generated outputs.
