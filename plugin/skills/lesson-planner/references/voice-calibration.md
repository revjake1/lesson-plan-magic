# Voice Calibration

How the skill adapts its output prose to match a teacher's established voice.

### What "voice" means in this context
- Sentence rhythm (length, contractions, imperatives)
- Student-facing vs. teacher-facing tone
- Humor/personality markers
- Recurring phrases (idiolect)
- Formatting habits (headings, bullets, bold)

### Sources of voice signal (in priority order)
1. `voice-profile.md` produced by `ingest_past_plans.py`
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

v0.1 injects `voice-profile.md` as a system-prompt appendix before generating any prose section of the plan. Run after research verification, before compliance check.
