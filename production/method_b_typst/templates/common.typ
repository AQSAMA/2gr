// Shared rendering helpers for Method B Typst designs.
// Design files import this helper and pass their own colors and frontmatter style.

#let manuscript_title = "Psychiatric Medication Use and Public Acceptance in Iraq"
#let running_header = "Psychiatric Medication Use and Public Acceptance in Iraq"

#let navigation-frontmatter(accent: rgb("#1f2937")) = {
  align(center)[#text(size: 28pt, weight: "bold", fill: accent)[Table of Contents]]
  outline(title: none, depth: 2)
  pagebreak()
  align(center)[#text(size: 28pt, weight: "bold", fill: accent)[List of Figures]]
  outline(title: none, target: figure.where(kind: image))
  pagebreak()
  align(center)[#text(size: 28pt, weight: "bold", fill: accent)[List of Tables]]
  outline(title: none, target: figure.where(kind: table))
  pagebreak()
}

#let render-blocks(
  blocks,
  accent: rgb("#1f2937"),
  light-accent: rgb("#eef2ff"),
  chapter-frame: true,
  frontmatter-frame: false,
) = {
  let in-references = false

  for block in blocks {
    if block.kind == "pagebreak" {
      pagebreak()
    } else if block.kind == "frontmatter" {
      pagebreak(weak: true)
      align(center + horizon)[
        #if frontmatter-frame {
          box(width: 82%, inset: 24pt, stroke: 1pt + accent, radius: 8pt)[
            #align(center)[#text(size: 28pt, weight: "bold", fill: accent)[#block.title]]
          ]
        } else {
          text(size: 28pt, weight: "bold", fill: accent)[#block.title]
        }
      ]
      pagebreak()
    } else if block.kind == "chaptertitle" {
      pagebreak(weak: true)
      align(center + horizon)[
        #if chapter-frame {
          box(width: 84%, inset: 28pt, stroke: 1.2pt + accent, radius: 6pt, fill: light-accent)[
            #align(center)[
              #text(size: 32pt, weight: "bold", fill: accent)[#block.chapter]
              #v(8pt)
              #text(size: 19pt, weight: "bold", fill: accent)[#block.title]
            ]
          ]
        } else {
          align(center)[
            #line(length: 4.5cm, stroke: 0.8pt + accent)
            #v(10pt)
            #text(size: 32pt, weight: "bold", fill: accent)[#block.chapter]
            #v(6pt)
            #text(size: 19pt, weight: "bold", fill: accent)[#block.title]
            #v(10pt)
            #line(length: 4.5cm, stroke: 0.8pt + accent)
          ]
        }
      ]
      pagebreak()
    } else if block.kind == "references_start" {
      in-references = true
    } else if block.kind == "h1" {
      heading(level: 1, outlined: true)[#block.text]
    } else if block.kind == "h2" {
      heading(level: 2, outlined: true)[#block.text]
    } else if block.kind == "paragraph" {
      if in-references {
        par(first-line-indent: 0pt, justify: true)[#block.text]
      } else {
        par(first-line-indent: 1.27cm, justify: true)[#block.text]
      }
    } else if block.kind == "image" {
      figure(
        image(block.path, width: 90%),
        caption: [#block.caption],
      )
    }
  }
}
