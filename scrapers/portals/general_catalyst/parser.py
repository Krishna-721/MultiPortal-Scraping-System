from scrapers.core.utils.hash_utils import generate_link_hash

from scrapers.core.utils.type_extractor import (
    extract_employment_type,
    extract_job_type,
)


def parse_job(job, search_keyword=None):

    organization = job.get("organization") or {}

    title = job.get("title")

    url = job.get("url")

    if not title or not url:
        return None

    company = organization.get("name") or ""

    locations = []

    raw_locations = (
        job.get("locations")
        or job.get("searchable_locations")
        or []
    )

    for loc in raw_locations:

        if isinstance(loc, dict):

            name = loc.get("name")

            if name:
                locations.append(name)

        elif isinstance(loc, str):

            locations.append(loc)

    location = ", ".join(
        list(dict.fromkeys(locations))
    )

    salary_min = job.get("compensation_amount_min_cents")

    salary_max = job.get("compensation_amount_max_cents")

    currency = job.get("compensation_currency")

    period = job.get("compensation_period")

    salary_range = None

    if salary_min or salary_max:

        if salary_min:
            salary_min = salary_min / 100

        if salary_max:
            salary_max = salary_max / 100

        salary_range = (
            f"{currency or ''} "
            f"{salary_min or '?'}-"
            f"{salary_max or '?'}"
            f"/{period or ''}"
        ).strip()

    work_mode = job.get("work_mode")

    employment_type = extract_employment_type(
        work_mode,
        f"{title} {location}",
    )

    return {
        "title": title,
        "company": company,
        "location": location,
        "link": url,
        "link_hash": generate_link_hash(url),
        "source": "general_catalyst",
        "description": None,
        "salary_range": salary_range,
        "job_type": extract_job_type(title),
        "employment_type": employment_type,
        "work_auth": None,
        "job_status": "active",
        "search_keyword": search_keyword,
    }