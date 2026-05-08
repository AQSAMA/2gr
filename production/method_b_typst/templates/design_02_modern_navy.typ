#import "common.typ": render-blocks, navigation-frontmatter, manuscript_title, running_header

#let navy = rgb("#0f2a44")
#let render-manuscript(blocks) = render-blocks(
  blocks,
  accent: navy,
  light-accent: rgb("#e8eef5"),
  chapter-frame: true,
  frontmatter-frame: true,
)

#let project(body) = {
  set document(title: manuscript_title)
  set page(
    paper: "a4",
    margin: 1.5cm,
    numbering: "1",
    number-align: center,
    header: align(right)[#text(size: 9pt, fill: navy)[#running_header]],
  )
  set text(font: ("Times New Roman", "Times"), size: 14pt, fill: rgb("#111827"))
  set par(leading: 0.55em, spacing: 0.35em, justify: true)
  show heading.where(level: 1): it => block(above: 12pt, below: 9pt)[#text(size: 18pt, weight: "bold", fill: navy)[#it.body]#linebreak()#line(length: 100%, stroke: 0.7pt + navy)]
  show heading.where(level: 2): it => block(above: 9pt, below: 6pt)[#text(size: 16pt, weight: "bold", fill: navy)[#it.body]]
  show figure: it => block(above: 10pt, below: 12pt, inset: 6pt, stroke: 0.4pt + rgb("#cbd5e1"))[#align(center)[#it]]
  navigation-frontmatter(accent: navy)
  body
}
