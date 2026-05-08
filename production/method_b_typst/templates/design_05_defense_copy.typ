#import "common.typ": render-blocks, navigation-frontmatter

#let green = rgb("#1f5f4b")
#let render-manuscript(blocks) = render-blocks(
  blocks,
  accent: green,
  light-accent: rgb("#edf7f2"),
  chapter-frame: true,
  frontmatter-frame: false,
)

#let document(body) = {
  set document(title: "Psychiatric Medication Use and Public Acceptance in Iraq")
  set page(paper: "a4", margin: 1.5cm, numbering: "1", number-align: center, footer: align(center)[#text(size: 9pt, fill: green)[Defense copy — #counter(page).display()]])
  set text(font: ("Times New Roman", "Times"), size: 14pt, fill: rgb("#102017"))
  set par(leading: 0.55em, spacing: 0.35em, justify: true)
  show heading.where(level: 1): it => block(above: 12pt, below: 8pt, fill: rgb("#edf7f2"), inset: 6pt)[#text(size: 18pt, weight: "bold", fill: green)[#it.body]]
  show heading.where(level: 2): it => block(above: 8pt, below: 6pt)[#text(size: 16pt, weight: "bold", fill: green)[#it.body]]
  show figure: it => block(above: 10pt, below: 12pt, stroke: 0.5pt + green, inset: 6pt)[#align(center)[#it]]
  navigation-frontmatter(accent: green)
  body
}
