from typing import Optional

from scrapers.core.models.job_model import JOB_SCHEMA_COLUMNS


def _normalize_whitespace(value):
    if value is None:
        return None
    if isinstance(value, str):
        return " ".join(value.split())
    return value


def validate_job(job: dict) -> Optional[dict]:
    if not job or not isinstance(job, dict):
        return None

    normalized = {
        key: _normalize_whitespace(value)
        for key, value in job.items()
    }

    for field in ("title", "company", "link"):
        value = normalized.get(field)
        if value is None:
            return None
        if isinstance(value, str) and not value:
            return None

    for column in JOB_SCHEMA_COLUMNS:
        normalized.setdefault(column, None)

    return normalized
