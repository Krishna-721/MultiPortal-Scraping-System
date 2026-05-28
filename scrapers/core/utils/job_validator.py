from scrapers.core.models.job_model import (
    JOB_SCHEMA_COLUMNS,
)

REQUIRED_FIELDS = [
    "title",
    "company",
    "link",
    "source",
]


def validate_job(job: dict):

    if not job:
        return None

    for field in REQUIRED_FIELDS:
        value = job.get(field)

        if not value:
            return None

    normalized = {}

    for column in JOB_SCHEMA_COLUMNS:
        normalized[column] = job.get(column)

    return normalized
