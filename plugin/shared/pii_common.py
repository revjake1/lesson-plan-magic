"""Shared PII scanning primitives for lesson-planner and classroom-artifacts."""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable


NAME_WORD_PATTERN = r"[^\W\d_]+(?:['\-][^\W\d_]+)*"

_PII_PATTERNS = (
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "SSN"),
    (re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"), "phone"),
    (
        re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
        "email address",
    ),
    (
        re.compile(
            r"\b(?:student(?:\s+id)?|id)\s*#?\s*(?:[:\-]\s*)?\d{5,12}\b",
            re.IGNORECASE,
        ),
        "student ID",
    ),
    (
        re.compile(
            r"\b(?:dob|date of birth|birth ?date|birthday)\s*[:\-]?\s*"
            r"(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|[A-Z][a-z]+ \d{1,2}, \d{4})\b",
            re.IGNORECASE,
        ),
        "DOB / birthday field",
    ),
    (
        re.compile(
            r"\b(?:address|home address)\s*[:\-]?\s*\d{1,6}\s+[A-Za-z0-9][A-Za-z0-9 .'\-]{1,80}"
            r"\b(?:street|st|avenue|ave|road|rd|boulevard|blvd|lane|ln|drive|dr|court|ct|"
            r"way|trail|trl|circle|cir|place|pl)\b(?:[^\n]{0,40})",
            re.IGNORECASE,
        ),
        "home address field",
    ),
    (
        re.compile(
            r"\b(?:parent|guardian|mother|father|caregiver)(?:\s+(?:contact|phone|email|name))?"
            r"\s*[:\-]?\s*(?:"
            r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"
            r"|(?:\+?1[-.\s]?)?\d{3}[-.]?\d{3}[-.]?\d{4}"
            rf"|{NAME_WORD_PATTERN}\s+{NAME_WORD_PATTERN}"
            r")\b",
            re.IGNORECASE,
        ),
        "parent/guardian contact field",
    ),
    (
        re.compile(
            r"\b(?:free[- ]and[- ]reduced(?:[- ]lunch)?|free[- ]lunch status|"
            r"reduced[- ]lunch status|frl status)\b",
            re.IGNORECASE,
        ),
        "lunch-status field",
    ),
    (
        re.compile(
            r"\b(?:medical|health|nurse|medication|medicine|allergy|allergies|inhaler|"
            r"epipen|epi-pen|asthma|diabetes|seizure)(?:\s+(?:note|notes|info|information|"
            r"form|plan|needs?|status))?\s*[:\-]\s*[^\n]{1,120}",
            re.IGNORECASE,
        ),
        "medical-note field",
    ),
    (
        re.compile(
            r"\b(?:discipline record|incident report|office referral|behavior referral|"
            r"suspension|detention|expulsion|behavior note)\b(?:\s*[:\-]\s*[^\n]{0,120})?",
            re.IGNORECASE,
        ),
        "discipline-note field",
    ),
    (
        re.compile(
            r"\b(?:student|pupil|kid|child|learner)s?[:;][ \t]*"
            rf"({NAME_WORD_PATTERN})\s+({NAME_WORD_PATTERN})\b",
            re.IGNORECASE,
        ),
        "roster-like name",
    ),
    (
        re.compile(rf"\b(?:IEP|504|ELL|SPED)[:\s]+{NAME_WORD_PATTERN}\b"),
        "named accommodation",
    ),
)

OVERLAPPING_NAME_PAIR_PATTERN = re.compile(
    rf"(?=\b({NAME_WORD_PATTERN})[ \t]+({NAME_WORD_PATTERN})\b)"
)
INITIAL_NAME_PATTERN = re.compile(
    rf"\b({NAME_WORD_PATTERN})[ \t]+([^\W\d_])\.(?=[\s,;:!?]|$)"
)

SENTENCE_STARTERS: set[str] = {
    "Review", "Introduce", "Discuss", "Explore", "Explain", "Present",
    "Summarize", "Analyze", "Compare", "Contrast", "Evaluate", "Apply",
    "Create", "Describe", "Identify", "Show", "Today", "Tomorrow",
    "Yesterday", "Consider", "Remember", "Note", "Notice", "Think",
    "Write", "Read", "Watch", "Listen", "Study", "Complete", "Begin",
    "Start", "Finish", "Close", "Open", "Ask", "Answer", "Choose",
    "See", "Visit", "Go", "Work", "Continue", "Finally", "First",
    "Second", "Third", "Next", "Then", "After", "Before", "During",
    "While", "When", "Where", "Why", "How", "What", "Who", "Which",
    "Let", "Have", "Give", "Take", "Make", "Use", "Pick", "Pair",
    "Group", "Team", "Class", "Students", "Student", "Teacher",
    "Include", "Exclude", "Provide", "Allow", "Encourage", "Model",
    "Demonstrate", "Practice", "Extend", "Reduce", "Spiral", "Reteach",
    "Test", "Hand", "Collect",
}

STRUCTURAL_WORDS: set[str] = {
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
    "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
    "Subject", "Teacher", "Date", "Week", "Day", "Period", "Periods",
    "Standards", "Learning", "Intention", "Success", "Criteria",
    "Agenda", "Materials", "Differentiation", "Evidence", "Assessment",
    "Unit", "Lesson", "Bell", "Ringer", "Warm", "Warmup", "Warm-up",
    "Exit", "Ticket", "Homework", "Objective", "Objectives", "Goal",
    "Goals", "Frameworks", "Framework", "Schedule", "Room",
    "Chapter", "Section", "Module", "Topic", "Activity", "Activities",
    "Do", "Now", "Opener", "Closer", "Main", "Intro", "Outro",
    "Reflection", "Reflections", "Notes", "Note", "Of",
    "Weekly", "Plan", "Plans", "Daily",
    "Question", "Questions", "Additional", "Extension",
    "Check", "Understanding", "Response", "Responses", "Instructions",
    "Prompt", "Backup", "Emergency", "Attendance",
    "Classroom", "Setup", "Location", "Nearby", "Office",
    "Clinic", "Center", "School", "District",
    "Department", "Library", "Building",
    "If", "Unless", "Since", "Because", "While",
    "Finish", "Early", "Finished", "Finisher", "Finishers",
    "Grade", "Level", "Course", "Semester", "Quarter", "Trimester",
    "Quiz", "Exam", "Project", "Group", "Groups", "Pair", "Pairs",
    "Worksheet", "Practice", "Set", "Sheet", "Handout", "Drawer",
    "Calculator", "Calculators", "Cart", "Door", "Desk", "Stack",
    "Left", "Right", "Top", "Bottom", "Front", "Back", "Inside", "Outside",
    "ELL", "SPED", "IEP", "BIP", "MTSS", "RTI", "ESE", "GT",
    "Math", "Science", "English", "History", "Social", "Studies",
    "Chemistry", "Biology", "Physics", "Algebra", "Geometry", "Calculus",
    "Literature", "Writing", "Reading", "Art", "Music", "PE",
    "Health", "Economics", "Government", "World", "American", "US",
    "Chorus", "Band", "Orchestra", "Journalism", "Media", "Video",
    "Production", "Broadcast", "Yearbook", "Newspaper",
    "Energy", "Force", "Forces", "Motion", "Velocity", "Acceleration",
    "Diagram", "Diagrams", "Equation", "Equations", "Reaction", "Reactions",
    "Classification", "Temperature", "Curve", "Transfer", "Transfers",
    "Substitute",
}

DEFAULT_ALLOWED_NAMES: set[str] = {
    "Rosa Parks", "Abraham Lincoln", "Martin Luther",
    "Martin Luther King", "William Shakespeare",
    "Mark Twain", "Langston Hughes", "Maya Angelou",
    "Frederick Douglass", "Harriet Tubman", "Isaac Newton",
    "Albert Einstein", "Marie Curie", "Jane Austen",
    "Charles Dickens", "Emily Dickinson", "Mary Oliver",
    "United States", "New York", "Los Angeles", "San Francisco",
    "Great Britain", "Great Depression", "Civil War",
    "World War", "Cold War", "Newton's Second", "Newton Second",
}

_STUDENT_CONTEXT_WORDS = {
    "student",
    "students",
    "pupil",
    "pupils",
    "kid",
    "kids",
    "child",
    "children",
    "learner",
    "learners",
}


def _split_name_segments(word: str) -> list[str]:
    word = re.sub(r"['’]s$", "", word)
    return [segment for segment in re.split(r"['\-]", word) if segment]


def _display_name_word(word: str) -> str:
    return re.sub(r"['’]s$", "", word)


def _is_titlecase_name_word(word: str) -> bool:
    segments = _split_name_segments(word)
    if not segments:
        return False
    return all(
        segment[0].isupper() and (len(segment) == 1 or segment[1:].islower())
        for segment in segments
    )


def _is_upper_name_word(word: str) -> bool:
    segments = _split_name_segments(word)
    if not segments:
        return False
    return all(segment.isupper() for segment in segments)


def normalize_scan_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Cf")


def scan_text_for_pii_matches(
    text: str,
    allowed_names: Iterable[str] = (),
    *,
    strip_markdown_headings: bool = False,
) -> list[tuple[str, str]]:
    """Return ``[(matched_text, label), ...]`` for suspicious PII."""

    text = normalize_scan_text(text)
    if strip_markdown_headings:
        text = "\n".join(
            line
            for line in text.splitlines()
            if not line.lstrip().startswith("#")
        )

    normalized_allowed = {
        normalize_scan_text(name)
        for name in allowed_names
        if isinstance(name, str) and name.strip()
    }

    matches: list[tuple[str, str]] = []
    for pattern, label in _PII_PATTERNS:
        for match in pattern.finditer(text):
            matches.append((match.group(0), label))

    all_allowed = normalized_allowed | {
        normalize_scan_text(name) for name in DEFAULT_ALLOWED_NAMES
    }
    allowlist_words: set[str] = set()
    for phrase in all_allowed:
        for word in phrase.split():
            if word and word[0].isupper():
                allowlist_words.add(word)

    structural_lower = {word.lower() for word in STRUCTURAL_WORDS}
    starters_lower = {word.lower() for word in SENTENCE_STARTERS}
    allowlist_words_lower = {word.lower() for word in allowlist_words}
    allowed_lower = {phrase.lower() for phrase in all_allowed}

    seen_pairs: set[str] = set()
    for match in OVERLAPPING_NAME_PAIR_PATTERN.finditer(text):
        first = match.group(1)
        second = match.group(2)
        if not (_is_titlecase_name_word(first) and _is_titlecase_name_word(second)):
            continue
        pair = f"{_display_name_word(first)} {_display_name_word(second)}"
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        if pair in all_allowed:
            continue
        if first in STRUCTURAL_WORDS or second in STRUCTURAL_WORDS:
            continue
        if first in SENTENCE_STARTERS:
            if second in allowlist_words or second in STRUCTURAL_WORDS:
                continue
            # Tradeoff: a sentence-starter that is not itself a
            # student-context keyword ("Today", "Review", "Activity") is
            # treated as prose rather than a name pair. This suppresses
            # false positives like "Review Standards" but lets "Today
            # Maria" slip by. Keyword-anchored patterns (Student:, Parent:,
            # roster fields) remain the primary defense for real PII.
            if first.lower() not in _STUDENT_CONTEXT_WORDS:
                continue
        if first in allowlist_words and second in allowlist_words:
            continue
        if any(pair in matched_text for matched_text, _label in matches):
            continue
        matches.append((pair, "bare name (unallowlisted)"))

    seen_upper_pairs: set[str] = set()
    for match in OVERLAPPING_NAME_PAIR_PATTERN.finditer(text):
        first = match.group(1)
        second = match.group(2)
        if not (_is_upper_name_word(first) and _is_upper_name_word(second)):
            continue
        pair = f"{_display_name_word(first)} {_display_name_word(second)}"
        first_l = first.lower()
        second_l = second.lower()
        if pair in seen_upper_pairs:
            continue
        seen_upper_pairs.add(pair)
        if pair.lower() in allowed_lower:
            continue
        if first_l in structural_lower or second_l in structural_lower:
            continue
        if first_l in starters_lower:
            if second_l in allowlist_words_lower or second_l in structural_lower:
                continue
            if first_l not in _STUDENT_CONTEXT_WORDS:
                continue
        if first_l in allowlist_words_lower and second_l in allowlist_words_lower:
            continue
        if any(
            pair in matched_text or pair.lower() in matched_text.lower()
            for matched_text, _label in matches
        ):
            continue
        matches.append((pair, "bare name (all-caps, unallowlisted)"))

    for match in INITIAL_NAME_PATTERN.finditer(text):
        first = match.group(1)
        initial = match.group(2)
        if not _is_titlecase_name_word(first) or not initial.isupper():
            continue
        label = f"{_display_name_word(first)} {initial}."
        if any(phrase.startswith(f"{first} {initial}") for phrase in all_allowed):
            continue
        if first in SENTENCE_STARTERS or first in STRUCTURAL_WORDS:
            continue
        matches.append((label, "initial-form name"))

    return matches
