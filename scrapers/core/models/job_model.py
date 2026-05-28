from dataclasses import dataclass
from typing import Optional

JOB_SCHEMA_COLUMNS = [
    "title",
    "company",
    "location",
    "link",
    "link_hash",
    "source",
    "description",
    "salary_range",
    "job_type",
    "work_auth",
    "employment_type",
    "job_status",
    "search_keyword",
]


@dataclass
class JobModel:
    title: str = ""

    company: str = ""

    location: str = ""

    link: str = ""

    link_hash: str = ""

    description: str = ""

    salary_range: str = ""

    job_type: str = ""

    work_auth: Optional[str] = None

    employment_type: str = ""

    job_status: str = "active"

    posted_at: Optional[str] = None

    source: str = ""

    search_keyword: Optional[str] = None


__all__ = [
    "JOB_SCHEMA_COLUMNS",
    "JobModel",
]
