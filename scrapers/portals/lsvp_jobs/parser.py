from scrapers.core.utils.hash_utils import generate_link_hash
from scrapers.core.utils.type_extractor import extract_employment_type, extract_job_type

class LSVPParser:
    @staticmethod
    def parse_job(job, search_keyword):

        salary = job.get("salary")

        salary_range = None

        if salary:
            currency = salary.get("currency", {}).get("value")

            min_salary = salary.get("minValue")

            max_salary = salary.get("maxValue")

            salary_range = f"{currency} {min_salary}-{max_salary}"

        locations = job.get("locations") or []

        location = ", ".join(locations) if locations else None

        job_types = job.get("jobTypes") or []

        parsed_job_types = ", ".join(
            [jt.get("label") for jt in job_types if jt.get("label")]
        )

        apply_url = job.get("applyUrl")

        if not apply_url:
            return None

        return {
            "title": job.get("title"),
            "company": job.get("companyName"),
            "location": location,
            "link": apply_url,
            "link_hash": generate_link_hash(apply_url),
            "source": "lsvp_jobs",
            "description": None,
            "salary_range": salary_range,
            "job_type": extract_job_type(f"{job.get('title', '')} {parsed_job_types}"),
            "work_auth": None,
            "employment_type": extract_employment_type(None, f"{job.get('title', '')} {parsed_job_types}"),
            "job_status": "active",
            "search_keyword": search_keyword,
        }
