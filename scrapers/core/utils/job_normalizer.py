import re


JOB_TYPE_PATTERNS = {
    "Full-time": [
        r"full[\s-]?time",
    ],
    "Part-time": [
        r"part[\s-]?time",
    ],
    "Internship": [
        r"internship",
        r"\bintern\b",
    ],
    "Contract": [
        r"contract",
        r"contractor",
        r"1099",
        r"c2c",
        r"w2",
    ],
}


EMPLOYMENT_TYPE_PATTERNS = {
    "remote": [
        r"remote",
        r"work from home",
    ],
    "hybrid": [
        r"hybrid",
    ],
    "onsite": [
        r"on[\s-]?site",
        r"in office",
    ],
}


WORK_AUTH_PATTERNS = {
    "us_citizen": [
        r"us citizen",
        r"citizenship required",
    ],
    "security_clearance": [
        r"security clearance",
        r"clearance required",
    ],
    "no_sponsorship": [
        r"no sponsorship",
    ],
    "visa_sponsorship": [
        r"visa sponsorship",
        r"sponsorship available",
    ],
}


def extract_category(text, patterns):

    if not text:
        return None

    text = text.lower()

    for category, regexes in patterns.items():
        for regex in regexes:
            if re.search(regex, text):
                return category

    return None


def safe_str(value):

    if value is None:
        return ""

    try:
        if value != value:
            return ""

    except:
        pass

    return str(value)


def normalize_job_metadata(
    title="",
    description="",
    location="",
):

    combined = " ".join(
        [
            safe_str(title),
            safe_str(description),
            safe_str(location),
        ]
    )

    return {
        "job_type": extract_category(
            combined,
            JOB_TYPE_PATTERNS,
        ),
        "employment_type": extract_category(
            combined,
            EMPLOYMENT_TYPE_PATTERNS,
        ),
        "work_auth": extract_category(
            combined,
            WORK_AUTH_PATTERNS,
        ),
    }
