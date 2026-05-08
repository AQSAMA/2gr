#import "common.typ": render-blocks, navigation-frontmatter, manuscript_title, running_header

#let render-manuscript(blocks) = render-blocks(
  blocks,
  accent: rgb("#374151"),
  light-accent: rgb("#ffffff"),
  chapter-frame: false,
  frontmatter-frame: false,
)

#let document_element = document
#let document(body) = {
  set document_element(title: manuscript_title)
  set page(paper: "a4", margin: 1.5cm, numbering: "1", number-align: center)
  set text(font: ("Times New Roman", "Times"), size: 14pt, fill: rgb("#111111"))
  set par(leading: 0.55em, spacing: 0.25em, justify: true)
  show heading.where(level: 1): it => block(above: 11pt, below: 7pt)[#text(size: 17pt, weight: "bold")[#it.body]]
  show heading.where(level: 2): it => block(above: 7pt, below: 5pt)[#text(size: 15pt, weight: "bold", style: "italic")[#it.body]]
  show figure: it => block(above: 8pt, below: 8pt)[#align(center)[#it]]
  navigation-frontmatter(accent: rgb("#374151"))
  body
}
