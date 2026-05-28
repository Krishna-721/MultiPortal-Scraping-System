import hashlib
import re


def normalize_text(value):

    if not value:
        return ""

    value = str(value).lower().strip()

    value = re.sub(r"\s+", " ", value)

    return value


def generate_job_hash(
    title,
    company,
    location,
):

    title = normalize_text(title)

    company = normalize_text(company)

    location = normalize_text(location)

    unique_string = f"{title}|{company}|{location}"

    return hashlib.sha256(
        unique_string.encode()
    ).hexdigest()


def generate_link_hash(url):

    url = normalize_text(url)

    return hashlib.sha256(
        url.encode()
    ).hexdigest()