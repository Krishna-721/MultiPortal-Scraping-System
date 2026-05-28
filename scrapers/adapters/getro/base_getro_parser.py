from scrapers.core.utils.hash_utils import generate_link_hash
from scrapers.core.utils.schema_validator import validate_job


def parse_getro_job(job, source="getro"):

    organization = job.get("organization") or {}

    title = job.get("title")

    url = (
        job.get("url")
        or job.get("applyUrl")
    )

    if not title or not url:
        return None

    company = (
        organization.get("name")
        or job.get("companyName")
        or ""
    )

    # =========================
    # LOCATIONS
    # =========================

    raw_locations = (
        job.get("searchable_locations")
        or job.get("locations")
        or []
    )

    cleaned_locations = []

    for loc in raw_locations:

        if isinstance(loc, dict):

            name = loc.get("name")

            if name:
                cleaned_locations.append(name)

        elif isinstance(loc, str):

            cleaned_locations.append(loc)

    location = ", ".join(cleaned_locations)

    # =========================
    # SALARY
    # =========================

    salary_range = None

    salary_data = job.get("salary") or {}

    salary_min = (
        job.get("compensation_amount_min_cents")
        or salary_data.get("minValue")
    )

    salary_max = (
        job.get("compensation_amount_max_cents")
        or salary_data.get("maxValue")
    )

    currency = (
        job.get("compensation_currency")
        or salary_data.get("currency", {}).get("value")
    )

    period = (
        job.get("compensation_period")
        or salary_data.get("period", {}).get("value")
    )

    if salary_min or salary_max:

        if salary_min and salary_min > 100000:
            salary_min = salary_min / 100

        if salary_max and salary_max > 100000:
            salary_max = salary_max / 100

        min_val = f"{salary_min:.0f}" if salary_min else "?"

        max_val = f"{salary_max:.0f}" if salary_max else "?"

        salary_range = (
            f"{currency} "
            f"{min_val}-{max_val}/{period}"
        )


    return validate_job({
        "title": title,
        "company": company,
        "link": url,
        "link_hash": generate_link_hash(url),
        "location": location,
        "description": None,
        "salary_range": salary_range,
        "job_type": None,
        "employment_type": None,
        "job_status": "active",
        "source": source,
        "search_keyword": job.get("search_keyword"),
    })
