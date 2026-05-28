import asyncio

from scrapers.core.base.base_scraper import BaseScraper
from scrapers.portals.a16z_jobs.scraper import A16ZScraper

from scrapers.portals.a16z_jobs.parser import (
    parse_a16z_job,
)

from scrapers.adapters.getro.getro_detail_scraper import (
    GetroDetailScraper,
)

from scrapers.core.config.search_keywords import (
    SEARCH_KEYWORDS,
)

from scrapers.core.database.csv_storage import (
    CSVStorage,
)

from scrapers.core.utils.logger import (
    setup_logger as get_logger,
)

from scrapers.core.utils.url_manager import (
    URLManager,
)


from scrapers.core.config.settings import MAX_JOBS_PER_KEYWORD, DETAIL_ENRICHMENT_LIMIT

JOBS_URL = "https://jobs.a16z.com/jobs"


class A16ZJobsScraper(BaseScraper):
    def __init__(self):

        super().__init__("a16z_jobs")

        self.scraper = A16ZScraper()

        self.logger = get_logger("a16z_jobs")

        self.storage = CSVStorage()

        self.detail_scraper = None

        self.existing_urls = URLManager.load_existing_urls("data/a16z_jobs.csv")

        self.seen_urls = set()

    async def scrape(self):

        await self.initialize(headless=False)

        self.detail_scraper = GetroDetailScraper(
            self.context,
            self.logger,
        )

        parsed_jobs = []

        enriched_count = 0

        for keyword in SEARCH_KEYWORDS:
            self.logger.info(f"Searching: {keyword}")

            try:
                raw_jobs = self.scraper.fetch_all_jobs(
                    keyword=keyword,
                    max_jobs=MAX_JOBS_PER_KEYWORD,
                )

            except Exception as e:
                self.logger.error(f"Keyword failed: {keyword} | {e}")

                continue

            for job in raw_jobs:
                try:
                    parsed = parse_a16z_job(job=job)
                    if parsed:
                        parsed["search_keyword"] = keyword
                        
                    if not parsed:
                        continue

                    link = parsed.get("link")

                    if not link:
                        continue

                    if link in self.seen_urls or link in self.existing_urls:
                        continue

                    self.seen_urls.add(link)

                    if enriched_count < DETAIL_ENRICHMENT_LIMIT:
                        try:
                            details = await self.detail_scraper.extract_details(link)

                            if details:
                                parsed.update(details)

                            enriched_count += 1

                        except Exception as e:
                            self.logger.error(f"Enrichment failed: {e}")

                    parsed_jobs.append(parsed)

                    self.logger.info(f"Processed: {parsed.get('title')}")

                except Exception as e:
                    self.logger.error(f"Job parse failed: {e}")

        self.storage.save_jobs(
            parsed_jobs,
            filename="data/a16z_jobs.csv",
        )

        self.logger.info(f"Saved {len(parsed_jobs)} jobs")

        await self.cleanup()


async def main():

    scraper = A16ZJobsScraper()
    await scraper.scrape()


if __name__ == "__main__":
    asyncio.run(main())
