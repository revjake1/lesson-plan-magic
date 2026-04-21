# Agenda Slide Patterns

How the skill generates a daily agenda slide (.pptx or Google Slide) from
the day's lesson plan.

### What an agenda slide is

A single slide, projected at the start of class, showing:
- Date
- Learning Intention
- Success Criteria
- Agenda (with time allocations)
- Do-Now prompt (if applicable)
- Materials to grab

### Template requirements

- Readable from the back of the room (min 24pt body, 36pt heading)
- Teacher's subject/course name in footer or header
- Neutral color scheme — teacher can restyle in their own deck

### Source-of-truth fields from the lesson plan

Maps 1:1 from the lesson plan's daily markdown sections:
- `# <Date>` → slide title
- `## Learning Intention` → Learning Intention block
- `## Success Criteria` → bulleted list
- `## Agenda` → numbered list with time allocations
- `## Do-Now` (if present) → lower-third block

### Output formats

- `.pptx` via python-pptx (ships with Cowork)
- Future: Google Slides via API (v0.2+)
