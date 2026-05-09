// Shared rendering helpers for Method B Typst designs.
// Design files import this helper and pass their own colors and frontmatter style.

#let manuscript_title = "Psychiatric Medication Use and Public Acceptance in Iraq"
// Kept as a fallback for any legacy design that still imports it by this name.
#let running_header = "Psychiatric Medication Use and Public Acceptance in Iraq"

// Shared running-head state. Designs that set a page header should read this
// state via a context block so continuation pages within a chapter carry the
// current chapter (or section) title rather than a static manuscript title.
#let running-head = state("running-head", "")
#let set-running-head(s) = running-head.update(s)

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
    // Set the running head for all continuation pages of this chapter
    // BEFORE emitting the interstitial so that the first page after the
    // interstitial already sees the correct state. Page headers evaluate
    // the state at the top of the page, so the update must land on the
    // previous page (or earlier) to be visible on the next one.
    set-running-head(block.title)
    // Chapter interstitial page: rendered inside a content block so the
    // `set page(header: none)` rule only applies to this interstitial
    // page. The surrounding page header resumes automatically on the
    // next page. This mirrors typst_content/research.typ's chapter-page.
    [
      #pagebreak(weak: true)
      #set page(header: none)
      #align(center + horizon)[
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
      #pagebreak()
    ]
  } else if block.kind == "references_start" {
    // References start on a new page too; update before any content lands
    // on that page so the header picks up "References" immediately.
    set-running-head("References")
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
    if upper(block.text) == "ABSTRACT" {
      set-running-head("Abstract")
    }
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

