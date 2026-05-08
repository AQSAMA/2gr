// Default Method B Typst entry point.
// The production build uses generated/design_*.typ to compile all designs.
// Compile this file after running build_all.py if you only need the classic design.
#import "templates/design_01_classic.typ": project, render-manuscript
#import "generated/body.typ": manuscript_blocks

#show: project
#render-manuscript(manuscript_blocks)
