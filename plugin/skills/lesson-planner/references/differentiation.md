# Differentiation

How the skill produces useful, concrete, **FERPA-safe** differentiation content.

### Core rule (FERPA-safe differentiation)

Differentiation addresses **populations and accommodations**, never named
students. The only exception is the teacher's own name (from config). A
lesson plan should say:

> Students with extended-time accommodations: provide the bond-energy table
> in large-print format; permit calculator use on the closing problem set.

...and NEVER:

> Sarah H. (504): give her extra time.

### Dimensions of differentiation

1. **Readiness** — varying the complexity of content for where the student is
2. **Interest** — offering entry points via student interest
3. **Learning profile** — varying the mode (visual, verbal, kinesthetic, etc.)
4. **Product** — varying how students show what they learned

### Accommodation categories to plan for (abstract only)

- IEP / 504 (language: "students with IEP-specified accommodations")
- Multilingual / EL (tiered language support)
- Gifted / advanced
- Below-grade-level readiness
- Attentional / executive-function support needs

### Tiered support language templates

- **Scaffold:** "students needing additional scaffolding may..."
- **Extend:** "for students ready to extend, provide..."
- **Modify:** "on an as-needed basis, modify the task to..."

### What the skill MUST refuse

- Naming students
- Diagnosing students the teacher hasn't labeled in config/tags
- Writing "for students like [name]"
- Inventing specific student performance history

### How past-plan ingestion interacts

If past plans contain named students, `ingest_past_plans.py` redacts them
before voice analysis. The voice profile can preserve *how* the teacher
writes differentiation (warm vs. clinical) without preserving *who* they
wrote it about.
