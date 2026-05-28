import re

BLOCKED_TERMS = [
    "sales",
    "marketing",
    "designer",
    "recruiter",
    "support",
    "customer support",
    "operations",
    "account executive",
    "business development",
    "finance",
    "legal",
    "compliance",
    "hr",
]

ALLOWED_MAPPINGS = {
    "software engineer": [
        "software engineer",
        "backend engineer",
        "frontend engineer",
        "full stack engineer",
        "fullstack engineer",
        "platform engineer",
    ],
    "data engineer": [
        "data engineer",
        "analytics engineer",
        "data platform",
        "etl engineer",
    ],
    "devops engineer": [
        "devops",
        "sre",
        "infrastructure engineer",
        "platform engineer",
    ],
    "product manager": [
        "product manager",
        "product owner",
    ],
}


def _normalize_text(value):
    if not value:
        return ""
    normalized = str(value).lower().replace("-", " ")
    return " ".join(normalized.split())


def _contains_blocked_term(title):
    for term in BLOCKED_TERMS:
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, title):
            return True
    return False


def is_relevant_job(title: str, keyword: str) -> bool:
    normalized_title = _normalize_text(title)
    normalized_keyword = _normalize_text(keyword)

    if not normalized_title or not normalized_keyword:
        return False

    if _contains_blocked_term(normalized_title):
        return False

    # Try exact keyword mapping first
    allowed = ALLOWED_MAPPINGS.get(normalized_keyword)
    if allowed:
        match = any(alias in normalized_title for alias in allowed)
        return match

    # Fallback: simple substring match
    return normalized_keyword in normalized_title
