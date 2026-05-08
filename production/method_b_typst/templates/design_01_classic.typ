#import "common.typ": render-blocks, navigation-frontmatter, manuscript_title, running_header

#let render-manuscript(blocks) = render-blocks(
  blocks,
  accent: rgb("#1f2937"),
  light-accent: rgb("#f8fafc"),
  chapter-frame: false,
  frontmatter-frame: false,
)

#let project(body) = {
  set document(title: manuscript_title)
  set page(paper: "a4", margin: 1.5cm, numbering: "1", number-align: center)
  set text(font: ("Times New Roman", "Times"), size: 14pt, fill: rgb("#111827"))
  set par(leading: 0.55em, spacing: 0.4em, justify: true)
  show heading.where(level: 1): it => block(above: 10pt, below: 8pt)[#text(size: 18pt, weight: "bold")[#it.body]]
  show heading.where(level: 2): it => block(above: 8pt, below: 6pt)[#text(size: 16pt, weight: "bold")[#it.body]]
  show figure: it => block(above: 10pt, below: 10pt)[#align(center)[#it]]
  navigation-frontmatter(accent: rgb("#1f2937"))
  body
}
