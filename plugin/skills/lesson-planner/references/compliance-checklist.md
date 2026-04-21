# Compliance Checklist

Pre-delivery gates every generated plan must pass before the skill writes
final output.

### Hard gates (must-pass, else refuse to write)

1. **FERPA** — zero named students, zero student PII, zero roster data
2. **Research verification** — every URL passed `verify_research.py`
3. **Template hash match** — template file hasn't changed since mapping was confirmed
4. **Standards coverage** — every claimed standard code exists in the parsed standards doc
5. **Schedule sanity** — no lessons on non-instructional days per `parse_calendar.py`

### Soft gates (warn, teacher can override)

1. **SWIRL coverage** (if SWIRL framework active) — week hits ≥ 3 of 5 modalities
2. **Differentiation present** — every lesson has at least one tiered support note
3. **Assessment evidence present** — every lesson has a formative check
4. **Materials list complete** — every activity's materials appear in Materials section
5. **Voice drift** — output register matches voice-profile.md (fuzzy similarity ≥ 0.6)

### Output

The skill prints the checklist results to the teacher BEFORE writing output:

```
Compliance check — 2026-04-20 chem weekly:
  [PASS] FERPA
  [PASS] Research verification (3 URLs)
  [PASS] Template hash match
  [PASS] Standards coverage (5 codes)
  [PASS] Schedule sanity
  [PASS] SWIRL coverage (4 of 5 modes)
  [WARN] Differentiation — Tuesday missing tiered support (soft)
  [PASS] Assessment evidence
  [PASS] Materials list complete
  [PASS] Voice drift (0.78 similarity)

Proceed? (y/edit/n)
```
