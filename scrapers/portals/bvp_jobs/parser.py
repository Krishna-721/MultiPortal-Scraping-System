from typing import Dict, Optional

from scrapers.core.utils.hash_utils import (
    generate_link_hash,
)

from scrapers.core.utils.type_extractor import (
    extract_employment_type,
)

def parse_job(job: Dict) -> Optional[Dict]:

    company_data = job.get("_company", {})

    # =========================
    # LOCATIONS
    # =========================

    locations = []

    for loc in job.get("locations", []):

        if isinstance(loc, dict):

            name = loc.get("name")

            if name:
                locations.append(name)

        elif isinstance(loc, str):

            locations.append(loc)

    # =========================
    # SALARY
    # =========================

    salary = job.get("salary") or {}

    salary_range = None

    min_salary = salary.get("minValue")

    max_salary = salary.get("maxValue")

    currency = (
        salary.get("currency", {})
        .get("value")
    )

    if min_salary or max_salary:

        salary_range = (
            f"{currency} "
            f"{min_salary or '?'}-"
            f"{max_salary or '?'}"
        )

    # =========================
    # URL
    # =========================

    url = (
        job.get("url")
        or job.get("applyUrl")
    )

    if not url:
        return None

    # =========================
    # EMPLOYMENT TYPE
    # =========================

    employment_type = extract_employment_type(
        "Remote" if job.get("remote")
        else "Hybrid" if job.get("hybrid")
        else None,
        job.get("title", ""),
    )

    return { 

        "title": job.get("title"),

        "company": (
            job.get("companyName")
            or company_data.get("name")
        ),

        "link": url,

        "link_hash": generate_link_hash(url),

        "location": ", ".join(locations),

        "description": None,

        "salary_range": salary_range,

        "job_type": None,

        "employment_type": employment_type,

        "job_status": "active",

        "source": "bvp_jobs",

        "search_keyword": job.get("search_keyword"),
    }