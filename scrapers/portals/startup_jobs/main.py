import asyncio

from scrapers.portals.startup_jobs.scraper import (
    StartupJobsScraper,
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



from scrapers.core.config.settings import MAX_TOTAL_JOBS_PER_PORTAL, MAX_JOBS_PER_KEYWORD

def limit_reached(all_jobs):
    return len(all_jobs) >= MAX_TOTAL_JOBS_PER_PORTAL


async def main():

    scraper = StartupJobsScraper()

    await scraper.initialize(headless=False)

    csv_storage = CSVStorage()

    all_jobs = []

    existing_urls = URLManager.load_existing_urls("data/startup_jobs.csv")

    seen_urls = set()

    try:
        for keyword in SEARCH_KEYWORDS:
            if limit_reached(all_jobs):
                break

            scraper.logger.info(f"Searching keyword: {keyword}")

            jobs = await scraper.fetch_jobs(
                keyword=keyword,
                max_jobs=MAX_JOBS_PER_KEYWORD,
            )

            scraper.logger.info(f"Fetched {len(jobs)} jobs for keyword: {keyword}")

            for job in jobs:
                link = job.get("link")

                if not link:
                    continue

                if link in seen_urls or link in existing_urls:
                    continue

                seen_urls.add(link)

                all_jobs.append(job)

                scraper.logger.info(f"Added: {job.get('title')}")

                if limit_reached(all_jobs):
                    scraper.logger.info(f"Reached limit of {MAX_TOTAL_JOBS_PER_PORTAL}")

                    break

        scraper.logger.info(f"Saving {len(all_jobs)} jobs")

        csv_storage.save_jobs(
            all_jobs,
            filename="data/startup_jobs.csv",
            dedupe_column="link",
        )

    finally:
        await scraper.cleanup()


asyncio.run(main())
