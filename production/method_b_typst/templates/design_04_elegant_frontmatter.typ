#import "common.typ": render-blocks, navigation-frontmatter

#let burgundy = rgb("#6b1f2a")
#let render-manuscript(blocks) = render-blocks(
  blocks,
  accent: burgundy,
  light-accent: rgb("#fbf1f3"),
  chapter-frame: true,
  frontmatter-frame: true,
)

#let document(body) = {
  set document(title: "Psychiatric Medication Use and Public Acceptance in Iraq")
  set page(paper: "a4", margin: 1.5cm, numbering: "1", number-align: center)
  set text(font: ("Times New Roman", "Times"), size: 14pt, fill: rgb("#201517"))
  set par(leading: 0.55em, spacing: 0.35em, justify: true)
  show heading.where(level: 1): it => block(above: 12pt, below: 8pt, inset: (left: 8pt), stroke: (left: 2pt + burgundy))[#text(size: 18pt, weight: "bold", fill: burgundy)[#it.body]]
  show heading.where(level: 2): it => block(above: 8pt, below: 6pt)[#text(size: 16pt, weight: "bold", fill: burgundy)[#it.body]]
  show figure: it => block(above: 10pt, below: 12pt)[#align(center)[#it]]
  navigation-frontmatter(accent: burgundy)
  body
}
