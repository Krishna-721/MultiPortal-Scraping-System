ROLE_ALIASES = {
    "software engineer": [
        "software engineer",
        "backend engineer",
        "frontend engineer",
        "full stack engineer",
        "fullstack engineer",
        "developer",
        "swe",
    ],

    "data engineer": [
        "data engineer",
        "etl engineer",
        "analytics engineer",
        "data platform",
    ],

    "devops engineer": [
        "devops",
        "site reliability",
        "sre",
        "platform engineer",
        "infrastructure engineer",
    ],

    "product manager": [
        "product manager",
        "technical product manager",
        "product owner",
    ],
}


def is_relevant_job(
    title: str,
    keyword: str,
):

    if not title or not keyword:
        return False

    title = title.lower()

    keyword = keyword.lower()

    aliases = ROLE_ALIASES.get(
        keyword,
        [keyword],
    )

    return any(
        alias in title
        for alias in aliases
    )