import asyncio
import sys

from scrapers.core.base.base_scraper import BaseScraper

from scrapers.adapters.getro.base_getro_parser import (
    parse_getro_job,
)

from scrapers.adapters.getro.getro_detail_scraper import (
    GetroDetailScraper,
)

from scrapers.portals.accel_jobs.config import (
    SEARCH_JOBS_API,
    HEADERS,
)

from scrapers.core.config.search_keywords import (
    SEARCH_KEYWORDS,
)

from scrapers.core.database.csv_storage import (
    CSVStorage,
)

from scrapers.core.utils.url_manager import (
    URLManager,
)

from scrapers.core.utils.relevance_filter import (
    is_relevant_job,
)
from scrapers.core.config.settings import  MAX_JOBS_PER_KEYWORD, DETAIL_ENRICHMENT_LIMIT
sys.stdout.reconfigure(encoding="utf-8")

DETAIL_CONCURRENCY = 3
REQUEST_TIMEOUT_MS = 15000


class AccelJobsScraper(BaseScraper):
    def __init__(self):

        super().__init__("accel_jobs")

        self.csv_storage = CSVStorage()

        self.detail_scraper = None

        self.existing_urls = URLManager.load_existing_urls("data/accel_jobs.csv")

        self.seen_urls = set()

    async def _fetch_page(self, page, keyword):

        payload = {
            "hitsPerPage": 20,
            "page": page,
            "query": keyword,
        }

        response = await self.context.request.post(
            SEARCH_JOBS_API,
            data=payload,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT_MS,
        )

        if response.status != 200:
            raise RuntimeError(f"Accel API failed: {response.status}")

        return await response.json()

    async def _fetch_all_jobs(self, keyword, max_jobs):

        all_jobs = []

        seen_ids = set()

        page = 0

        while True:
            data = await self._fetch_page(page, keyword)

            jobs = data.get("results", {}).get("jobs", [])

            if not jobs:
                break

            for job in jobs:
                job_id = job.get("id")

                if not job_id:
                    continue

                if job_id in seen_ids:
                    continue

                seen_ids.add(job_id)

                all_jobs.append(job)

                if len(all_jobs) >= max_jobs:
                    return all_jobs

            page += 1

        return all_jobs

    async def _enrich_jobs(self, jobs):

        if not jobs:
            return

        semaphore = asyncio.Semaphore(DETAIL_CONCURRENCY)

        async def enrich(job):

            async with semaphore:
                try:
                    details = await self.detail_scraper.extract_details(job["link"])

                    if not details:
                        return

                    if details.get("description"):
                        job["description"] = details["description"]

                    if details.get("job_type") and not job.get("job_type"):
                        job["job_type"] = details["job_type"]
                        
                    if details.get("employment_type") and not job.get("employment_type"):
                        job["employment_type"] = details["employment_type"]

                except Exception as e:
                    self.logger.error(f"Enrichment failed: {e}")

        self.logger.info(f"Starting enrichment for {len(jobs)} jobs")

        await asyncio.gather(*(enrich(job) for job in jobs))

        self.logger.info("Enrichment complete")

    async def scrape(self):

        await self.initialize(headless=False)

        self.detail_scraper = GetroDetailScraper(
            self.context,
            self.logger,
        )

        parsed_jobs = []

        enrich_targets = []

        enriched_count = 0

        for keyword in SEARCH_KEYWORDS:
            self.logger.info(f"Searching: {keyword}")

            try:
                raw_jobs = await self._fetch_all_jobs(
                    keyword,
                    MAX_JOBS_PER_KEYWORD,
                )

            except Exception as e:
                self.logger.error(f"Failed keyword {keyword}: {e}")

                continue

            for job in raw_jobs:
                try:
                    parsed = parse_getro_job(
                        job=job,
                        source="accel_jobs",
                    )

                    if not parsed:
                        continue

                    if not is_relevant_job(
                        parsed.get("title"),
                        keyword,
                    ):
                        continue

                    link = parsed.get("link")

                    if not link:
                        continue

                    title = parsed.get("title") or ""

                    if not title.strip():
                        continue

                    if link in self.seen_urls or link in self.existing_urls:
                        continue

                    self.seen_urls.add(link)

                    parsed["id"] = job.get("id")

                    parsed_jobs.append(parsed)

                    needs_enrichment = (
                        not parsed.get("description")
                        or not parsed.get("job_type")
                        or not parsed.get("employment_type")
                    )

                    if (needs_enrichment and enriched_count < DETAIL_ENRICHMENT_LIMIT):                        
                        enrich_targets.append(parsed)

                        enriched_count += 1

                    self.logger.info(f"Processed: {title}")

                except Exception as e:
                    self.logger.error(f"Job parse failed: {e}")

        await self._enrich_jobs(enrich_targets)

        self.csv_storage.save_jobs(
            parsed_jobs,
            filename="data/accel_jobs.csv",
        )

        self.logger.info(f"Saved {len(parsed_jobs)} jobs")

        await self.cleanup()


async def main():

    scraper = AccelJobsScraper()

    await scraper.scrape()


if __name__ == "__main__":
    asyncio.run(main())
