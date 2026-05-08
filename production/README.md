# Production Pipeline

## English

The `production/` directory is the output factory for the research project. The scientific manuscript text stays in `content/*.md`, with references in `references.md` and figures in `figures/`. Production scripts assemble those sources into final deliverables without changing the scientific content files.

The main entry point is:

```bash
python production/src/build_all.py
```

Before running locally, install the Python dependencies:

```bash
python -m pip install -r production/requirements.txt
```

`build_all.py` runs two production paths in order. Method A (`production/method_a_python/`) is the existing Python path and produces DOCX, PDF, TEX, and a copy of the assembled Markdown. Method B (`production/method_b_typst/`) generates Typst files from the same assembled Markdown and, when Typst is installed, produces five PDF designs.

If optional tools such as Typst or Pandoc are missing, the build prints a warning and continues with the available outputs. Pandoc is not required for the current Python Method A path, but the warning makes the environment status clear for future conversion steps.

## Inputs

```text
content/*.md          Scientific manuscript source text
references.md         Master bibliography
figures/*.png         Figure assets used by the manuscript
outline.md            Structural blueprint that governs manuscript order
survey_data_results.md Source of primary survey result values
```

## Outputs

```text
production/assembled/comprehensive_research.md
production/method_a_python/research_method_a.docx
production/method_a_python/research_method_a.pdf
production/method_a_python/research_method_a.tex
production/method_b_typst/output/design_01_classic.pdf
production/method_b_typst/output/design_02_modern_navy.pdf
production/method_b_typst/output/design_03_minimal_journal.pdf
production/method_b_typst/output/design_04_elegant_frontmatter.pdf
production/method_b_typst/output/design_05_defense_copy.pdf
```

## Method A: Python

Method A remains the stable production path. It assembles `content/*.md`, appends `references.md`, copies figure assets, normalizes figure captions, and produces DOCX/PDF/TEX outputs in `production/method_a_python/`. Open the DOCX in Word and refresh fields if you need Word-generated navigation lists.

## Method B: Typst

Method B is located in `production/method_b_typst/`. Its directory roles are:

```text
templates/  Editable design files
generated/  Auto-generated Typst body and entry files; generally do not edit manually
output/     Final Typst PDF outputs
main.typ    Default classic-design Typst entry point
```

To adjust a Typst design, edit the matching template file, such as `production/method_b_typst/templates/design_03_minimal_journal.typ`, then rerun `python production/src/build_all.py`. The generated body stays synchronized with `production/assembled/comprehensive_research.md`, which is assembled from `content/*.md`.

## العربية

مجلد `production/` هو مصنع الإخراج النهائي للمشروع. يبقى النص العلمي الأصلي داخل `content/*.md`، وتبقى المراجع في `references.md`، والأشكال في `figures/`. تقوم سكربتات الإنتاج بتجميع هذه الملفات لإنتاج النسخ النهائية من دون تعديل ملفات المحتوى العلمي.

نقطة التشغيل الرئيسية هي:

```bash
python production/src/build_all.py
```

قبل التشغيل المحلي، ثبّت متطلبات بايثون:

```bash
python -m pip install -r production/requirements.txt
```

يشغّل `build_all.py` مسارين. Method A هو المسار الحالي باستخدام Python ويُنتج DOCX وPDF وTEX. Method B يستخدم Typst لإنشاء خمسة تصاميم PDF من نفس النص المجمّع. إذا لم تكن أدوات Typst أو Pandoc مثبتة، تظهر رسالة تحذير ويستمر البناء بالمسارات المتاحة.

لا تعدّل ملفات `production/method_b_typst/generated/` يدوياً لأنها تُنشأ تلقائياً. عدّل ملفات التصميم داخل `production/method_b_typst/templates/` فقط، ثم أعد تشغيل البناء. أما النتائج النهائية فتوجد في مجلد `output/`.

## Operations (CI/CD)

The workflow in `.github/workflows/production.yml` installs Python dependencies, Pandoc, and Typst, then runs `python production/src/build_all.py`. It uploads the assembled Markdown, Method A outputs, and Method B Typst PDF outputs as workflow artifacts. For tag builds or published releases, the same outputs are uploaded as release assets.

CI only builds and publishes artifacts/assets; it does not commit generated binary files back to the repository.
