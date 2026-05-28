from scrapers.core.utils.hash_utils import generate_link_hash

def parse_a16z_job(job):

    title = job.get("title")

    url = (
        job.get("url")
        or job.get("applyUrl")
    )

    company = (
        job.get("companyName")
        or ""
    )

    # =========================
    # LOCATION
    # =========================

    locations = job.get("locations") or []

    cleaned_locations = []

    for loc in locations:

        if not loc:
            continue

        loc = str(loc).strip()

        if loc and loc not in cleaned_locations:
            cleaned_locations.append(loc)

    location = ", ".join(cleaned_locations)

    # =========================
    # SALARY
    # =========================

    salary_data = job.get("salary") or {}

    salary_min = salary_data.get("minValue")

    salary_max = salary_data.get("maxValue")

    currency = (
        salary_data.get("currency", {})
        .get("value")
    )

    period = (
        salary_data.get("period", {})
        .get("value")
    )

    salary_range = None

    if salary_min or salary_max:

        salary_range = (
            f"{currency} "
            f"{salary_min or '?'}"
            f"-{salary_max or '?'}"
            f"/{period}"
        )

    # =========================
    # EMPLOYMENT TYPE
    # =========================

    employment_type = None

    if job.get("remote"):
        employment_type = "Remote"

    elif job.get("hybrid"):
        employment_type = "Hybrid"

    else:
        employment_type = "On-site"

    # =========================
    # JOB TYPE
    # =========================

    job_type = None

    job_types = job.get("jobTypes") or []

    if job_types:

        labels = []

        for jt in job_types:

            label = jt.get("label")

            if not label:
                continue

            label = label.strip()

            if label:
                labels.append(label)

        if labels:
            job_type = ", ".join(labels)
 
    return {
        "title": title,
        "company": company,
        "location": location,
        "link": url,
        "link_hash": generate_link_hash(url),
        "source": "a16z_jobs",
        "description": None,
        "salary_range": salary_range,
        "job_type": None,
        "employment_type": employment_type,
        "job_status": "active",
        "search_keyword": None,
    }