import requests

from scrapers.portals.lsvp_jobs.config import LSVP_CONFIG

from scrapers.core.config.settings import MAX_TOTAL_JOBS_PER_PORTAL, MAX_JOBS_PER_KEYWORD

from scrapers.core.config.search_keywords import (
    SEARCH_KEYWORDS,
)

from scrapers.portals.lsvp_jobs.parser import LSVPParser


class LSVPScraper:
    def __init__(self):

        self.api_url = LSVP_CONFIG["search_api"]

        self.board_id = LSVP_CONFIG["board_id"]

        self.page_size = LSVP_CONFIG["page_size"]

        self.max_jobs = MAX_TOTAL_JOBS_PER_PORTAL

        self.max_jobs_per_keyword = MAX_JOBS_PER_KEYWORD

    def build_payload(
        self,
        keyword,
        size,
        sequence=None,
    ):

        meta = {
            "size": size,
        }

        if sequence:
            meta["sequence"] = sequence

        return {
            "meta": meta,
            "board": {
                "id": self.board_id,
                "isParent": True,
            },
            "query": {
                "titlePrefix": keyword,
                "promoteFeatured": True,
            },
        }

    def fetch_jobs(
        self,
        keyword,
        size,
        sequence=None,
    ):

        payload = self.build_payload(
            keyword,
            size,
            sequence,
        )

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=30,
            )

            response.raise_for_status()

            return response.json()

        except Exception as e:
            print(f"Failed fetching jobs for {keyword}: {e}")

            return {}

    def scrape(self):

        all_jobs = []

        seen_hashes = set()

        for keyword in SEARCH_KEYWORDS:
            print(f"\nFetching keyword: {keyword}")

            size = self.page_size

            sequence = None

            keyword_jobs_count = 0

            while True:
                if keyword_jobs_count >= self.max_jobs_per_keyword:
                    break

                data = self.fetch_jobs(
                    keyword,
                    size,
                    sequence,
                )

                jobs = data.get("jobs", [])

                if not jobs:
                    break

                for job in jobs:
                    parsed_job = LSVPParser.parse_job(
                        job,
                        keyword,
                    )

                    if not parsed_job:
                        continue

                    link_hash = parsed_job.get("link_hash")

                    if not link_hash:
                        continue

                    if link_hash in seen_hashes:
                        continue

                    seen_hashes.add(link_hash)

                    all_jobs.append(parsed_job)

                    keyword_jobs_count += 1

                    if keyword_jobs_count >= self.max_jobs_per_keyword:
                        break

                    if len(all_jobs) >= self.max_jobs:
                        return all_jobs

                meta = data.get("meta", {})

                next_sequence = meta.get("sequence")

                if not next_sequence:
                    break

                sequence = next_sequence

        return all_jobs
