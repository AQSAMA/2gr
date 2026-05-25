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
}

#let render-block(block, accent, light-accent, chapter-frame, frontmatter-frame, in-references) = {
  if block.kind == "pagebreak" {
    pagebreak()
  } else if block.kind == "toc" {
    navigation-frontmatter(accent: accent)
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
  } else if block.kind == "cover_h2" {
    v(1.5em, weak: true)
    align(center)[#heading(level: 2, outlined: false)[#block.text]]
  } else if block.kind == "cover_paragraph" {
    if block.text.starts-with("(Prepared for") or block.text.starts-with("(Automatically generated") or block.text.starts-with("(No manuscript") {
      align(center)[#text(style: "italic")[#block.text]]
      v(4em)
    } else {
      v(8em)
      align(center)[#text(size: 26pt, weight: "bold")[#block.text]]
      v(8em)
    }
  } else if block.kind == "h1" {
    v(1.5em, weak: true)
    heading(level: 1, outlined: true)[#block.text]
  } else if block.kind == "h2" {
    v(1.5em, weak: true)
    heading(level: 2, outlined: true)[#block.text]
  } else if block.kind == "paragraph" {
    if in-references {
      par(first-line-indent: 0pt, justify: true, hanging-indent: 0.5in)[#block.text]
    } else {
      par(first-line-indent: 1.27cm, justify: true)[#block.text]
    }
  } else if block.kind == "image" {
    figure(
      image(block.path, width: 90%),
      caption: [#block.caption],
    )
  } else if block.kind == "table" {
    let data = json(bytes(block.data))
    let columns = ()
    for _ in data.headers { columns.push(auto) }
    let align-map = ("left": left, "right": right, "center": center)
    let aligns = ()
    for a in data.alignments {
      aligns.push(align-map.at(a, default: left))
    }
    while aligns.len() < data.headers.len() { aligns.push(left) }
    let header-cells = ()
    let hi = 0
    for h in data.headers {
      let a = aligns.at(hi)
      header-cells.push(table.cell(align: a + horizon, fill: rgb("#eaeff5"))[#text(weight: "bold", size: 11pt, fill: accent)[#h]])
      hi = hi + 1
    }
    let body-cells = ()
    for row in data.rows {
      let ci = 0
      for cell in row {
        if ci < data.headers.len() {
          let a = aligns.at(ci)
          body-cells.push(table.cell(align: a + horizon)[#text(size: 11pt)[#cell]])
        }
        ci = ci + 1
      }
      while ci < data.headers.len() {
        body-cells.push(table.cell()[])
        ci = ci + 1
      }
    }
    v(6pt)
    set text(size: 11pt)
    table(
      columns: columns,
      stroke: 0.4pt + rgb("#94a3b8"),
      inset: 5pt,
      table.header(..header-cells),
      ..body-cells,
    )
    v(8pt)
  }
}

#let render-blocks(
  blocks,
  accent: rgb("#1f2937"),
  light-accent: rgb("#eef2ff"),
  chapter-frame: true,
  frontmatter-frame: false,
) = {
  let frontmatter-blocks = ()
  let main-blocks = ()
  let in-main = false

  for block in blocks {
    if block.kind == "chaptertitle" and block.chapter == "Chapter One" {
      in-main = true
    }
    if in-main {
      main-blocks.push(block)
    } else {
      frontmatter-blocks.push(block)
    }
  }

  let in-references = false
  for block in frontmatter-blocks {
    if block.kind == "references_start" {
      in-references = true
    }
    render-block(block, accent, light-accent, chapter-frame, frontmatter-frame, in-references)
  }

  set page(numbering: "1")
  counter(page).update(1)

  for block in main-blocks {
    if block.kind == "references_start" {
      in-references = true
    }
    render-block(block, accent, light-accent, chapter-frame, frontmatter-frame, in-references)
  }
}
