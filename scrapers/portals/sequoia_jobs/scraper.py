import requests
from typing import List, Dict

from scrapers.portals.sequoia_jobs.config import (
    SEARCH_JOBS_API,
    HEADERS,
)

from scrapers.core.config.settings import (
    MAX_TOTAL_JOBS_PER_PORTAL, MAX_JOBS_PER_KEYWORD,
)

from scrapers.core.config.search_keywords import SEARCH_KEYWORDS


class SequoiaScraper:
    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(HEADERS)

    def build_payload(
        self,
        keyword,
        sequence=None,
    ):

        payload = {
            "meta": {
                "size": 15,
            },
            "board": {
                "id": "sequoia-capital",
                "isParent": True,
            },
            "query": {
                "titlePrefix": keyword,
                "promoteFeatured": True,
            },
            "grouped": True,
        }

        if sequence:
            payload["meta"]["sequence"] = sequence

        return payload

    def fetch_page(
        self,
        keyword,
        sequence=None,
    ):

        payload = self.build_payload(
            keyword=keyword,
            sequence=sequence,
        )

        response = self.session.post(
            SEARCH_JOBS_API,
            json=payload,
            timeout=20,
        )

        response.raise_for_status()

        return response.json()

    def fetch_jobs_for_keyword(
        self,
        keyword,
    ):

        all_jobs = []

        seen_job_ids = set()

        sequence = None

        while True:
            data = self.fetch_page(
                keyword=keyword,
                sequence=sequence,
            )

            grouped_results = data.get(
                "jobs",
                [],
            )

            if not grouped_results:
                break

            page_job_count = 0

            for company_group in grouped_results:
                company_jobs = company_group.get(
                    "jobs",
                    [],
                )

                for job in company_jobs:
                    job_id = job.get("jobId")

                    if not job_id:
                        continue

                    if job_id in seen_job_ids:
                        continue

                    seen_job_ids.add(job_id)

                    job["search_keyword"] = keyword

                    all_jobs.append(job)

                    page_job_count += 1

                    if len(all_jobs) >= MAX_JOBS_PER_KEYWORD:
                        print(
                            f"Reached per-keyword limit of "
                            f"{MAX_JOBS_PER_KEYWORD} for keyword: {keyword}"
                        )

                        return all_jobs

            print(f"Fetched {page_job_count} jobs for keyword: {keyword}")

            print(f"Total jobs collected: {len(all_jobs)}")

            sequence = data.get("meta", {}).get("sequence")

            if not sequence:
                break

        return all_jobs

    def fetch_all_jobs(self) -> List[Dict]:

        all_jobs = []

        global_seen = set()

        for keyword in SEARCH_KEYWORDS:
            print(f"Searching: {keyword}")

            try:
                keyword_jobs = self.fetch_jobs_for_keyword(keyword)

                print(f"Found {len(keyword_jobs)} jobs for keyword: {keyword}")

                for job in keyword_jobs:
                    job_id = job.get("jobId")

                    if not job_id:
                        continue

                    if job_id in global_seen:
                        continue

                    global_seen.add(job_id)

                    all_jobs.append(job)

                    if len(all_jobs) >= MAX_TOTAL_JOBS_PER_PORTAL:
                        print(f"Reached global limit of {MAX_TOTAL_JOBS_PER_PORTAL}")

                        return all_jobs

            except Exception as e:
                print(f"Failed keyword {keyword}: {e}")

        return all_jobs
