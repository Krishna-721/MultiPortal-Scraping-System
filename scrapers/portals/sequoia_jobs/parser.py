from scrapers.core.utils.hash_utils import generate_link_hash
from scrapers.core.utils.type_extractor import extract_employment_type, extract_job_type

def parse_job(job):

    salary = job.get("salary") or {}

    currency = salary.get("currency") or {}

    salary_min = salary.get("minValue")

    salary_max = salary.get("maxValue")

    salary_range = None

    if salary_min or salary_max:
        salary_range = (
            f"{currency.get('value', '')} {salary_min or '?'}-{salary_max or '?'}"
        )

    locations = []

    for loc in job.get("locations", []):
        if isinstance(loc, dict):
            name = loc.get("name")

            if name:
                locations.append(name)

        elif isinstance(loc, str):
            locations.append(loc)

    location = ", ".join(locations)

    title = job.get("title")

    company = job.get("companyName")

    link = job.get("url") or job.get("applyUrl")

    return {
        "title": title,
        "company": company,
        "location": location,
        "link": link,
        "link_hash": generate_link_hash(link),
        "source": "sequoia_jobs",
        "description": None,
        "salary_range": salary_range,
        "job_type": extract_job_type(title),
        "employment_type": extract_employment_type(
            "Remote" if job.get("remote") else "Hybrid" if job.get("hybrid") else None,
            title
        ),
        "work_auth": None,
        "job_status": "active",
        "search_keyword": job.get("search_keyword"),
    }
