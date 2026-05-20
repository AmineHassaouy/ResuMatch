import re

COMPATIBILITY_THRESHOLD = 60.0


def _build_pattern(skill):
    escaped = re.escape(skill.strip())
    # Lookahead/lookbehind instead of \b to handle skills like C++, C#, .NET
    return re.compile(
        r'(?<![a-zA-Z0-9_])' + escaped + r'(?![a-zA-Z0-9_])',
        re.IGNORECASE,
    )


def match_skills(preprocessed_text, required_skills_str):
    """Returns (score_float, matched_list, unmatched_list)."""
    if not required_skills_str.strip():
        return 0.0, [], []

    required = [s.strip() for s in required_skills_str.split(',') if s.strip()]
    if not required:
        return 0.0, [], []

    matched, unmatched = [], []
    for skill in required:
        pattern = _build_pattern(skill)
        (matched if pattern.search(preprocessed_text) else unmatched).append(skill)

    score = (len(matched) / len(required)) * 100.0
    return score, matched, unmatched


def is_compatible(score):
    return score >= COMPATIBILITY_THRESHOLD
