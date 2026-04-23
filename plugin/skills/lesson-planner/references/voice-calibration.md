# Voice Calibration

How the skill adapts its output prose to match a teacher's established voice.

### What "voice" means in this context
- Sentence rhythm (length, contractions, imperatives)
- Student-facing vs. teacher-facing tone
- Humor/personality markers
- Recurring phrases (idiolect)
- Formatting habits (headings, bullets, bold)

### Sources of voice signal (in priority order)
1. `voice-profile.md` plus `voice-profile.json` produced by `ingest_past_plans.py`
2. Teacher's answers during onboarding ("describe your teaching style in one sentence")
3. Sample past plans the teacher uploaded but didn't ingest

### Voice rules the skill must enforce
- Never ventriloquize a voice the teacher hasn't confirmed
- If voice profile is thin (<3 plans), use a neutral professional register and say so
- Teacher edits to output override voice profile next run (learning loop)

### Voice-calibrated sections of a lesson plan
- Learning Intentions (student-facing → warmer)
- Agenda (teacher-facing → terse)
- Differentiation notes (teacher-facing → clinical)
- Reflection prompts (student-facing → match teacher's warmth level)

### Application

Prefer the compact JSON sidecar for routine runtime selection and excerpting. Load the markdown profile only when you need the human-edited nuance. Pass excerpts, not the whole profile, into drafting prompts. Run voice application after research verification and before compliance check.
