import re

filepath = 'production/src/build_production.py'

with open(filepath, 'r') as f:
    text = f.read()

text = text.replace(
'''CONTENT_FILES = [
    "00_cover.md",
    "00_abstract.md",
    "01_introduction.md",
    "02_literature_review.md",
    "03_methodology.md",
    "04_results.md",
    "05_discussion.md",
    "06_recommendations_conclusion.md",
]''',
'''CONTENT_FILES = [
    "00_cover.md",
    "00_abstract.md",
    "01_chapter_one.md",
    "02_chapter_two.md",
    "03_chapter_three.md",
    "04_chapter_four.md",
    "05_chapter_five.md",
]'''
)

with open(filepath, 'w') as f:
    f.write(text)
