import asyncio

from scrapers.core.base.base_scraper import BaseScraper

from scrapers.portals.startup_jobs.selectors import (
    JOB_CARD,
    JOB_TITLE,
    JOB_TITLE_LINK,
    NEXT_PAGE,
)

from scrapers.portals.startup_jobs.parser import (
    StartupJobsDetailScraper,
)

from scrapers.core.config.settings import DETAIL_ENRICHMENT_LIMIT
from scrapers.core.utils.relevance_filter import (
    is_relevant_job,
)

PAGE_GOTO_TIMEOUT_MS = 20000

class StartupJobsScraper(BaseScraper):
    def __init__(self):

        super().__init__("startup_jobs")

        self.detail_scraper = None

    async def fetch_jobs(
        self,
        keyword="",
        max_jobs=100,
        existing_urls=None,
        seen_urls=None,
    ):

        if existing_urls is None:
            existing_urls = set()

        if seen_urls is None:
            seen_urls = set()

        search_url = f"https://startup.jobs/?q={keyword}"

        try:
            await self.page.goto(
                search_url,
                wait_until="domcontentloaded",
                timeout=PAGE_GOTO_TIMEOUT_MS,
            )
        except Exception as e:
            self.logger.error(f"Search page failed: {search_url} | {e}")
            return []

        self.logger.info(f"Searching: {keyword}")

        self.detail_scraper = StartupJobsDetailScraper(
            self.page,
            self.logger,
        )

        jobs = []

        seen_links = set()

        # =========================
        # PAGINATION LOOP
        # =========================

        while True:
            await self.page.wait_for_timeout(2000)

            job_cards = await self.page.locator(JOB_CARD).all()

            self.logger.info(f"Found {len(job_cards)} cards on current page")

            for card in job_cards:
                if len(jobs) >= max_jobs:
                    break

                try:
                    title = await card.locator(JOB_TITLE).inner_text()

                    title = title.strip()

                    link = await card.locator(JOB_TITLE_LINK).get_attribute("href")

                    if not link:
                        continue

                    full_link = f"https://startup.jobs{link}"

                    if (
                        full_link in seen_links
                        or full_link in existing_urls
                        or full_link in seen_urls
                    ):
                        continue

                    if not is_relevant_job(title, keyword):
                        continue

                    seen_links.add(full_link)

                    jobs.append(
                        {
                            "title": title,
                            "link": full_link,
                            "search_keyword": keyword,
                        }
                    )

                except Exception as e:
                    self.logger.error(f"Card parse failed: {e}")

            self.logger.info(f"Collected so far: {len(jobs)} jobs")

            if len(jobs) >= max_jobs:
                break

            # =========================
            # NEXT PAGE
            # =========================

            next_button = self.page.locator(NEXT_PAGE)

            if await next_button.count() == 0:
                self.logger.info("No more pages found")

                break

            try:
                next_href = await next_button.first.get_attribute("href")

                if not next_href:
                    break

                next_url = (
                    next_href
                    if next_href.startswith("http")
                    else f"https://startup.jobs{next_href}"
                )

                self.logger.info(f"Moving to next page: {next_url}")

                await self.page.goto(
                    next_url,
                    wait_until="domcontentloaded",
                    timeout=PAGE_GOTO_TIMEOUT_MS,
                )

            except Exception as e:
                self.logger.error(f"Pagination failed: {e}")

                break

        self.logger.info(f"Final raw jobs count: {len(jobs)}")

        # =========================
        # DETAIL EXTRACTION
        # =========================

        semaphore = asyncio.Semaphore(3)

        async def limited_extract(job):

            async with semaphore:
                return await self.detail_scraper.extract_job_details(job)

        jobs_to_enrich = jobs[:DETAIL_ENRICHMENT_LIMIT]

        self.logger.info(
            f"Enriching {len(jobs_to_enrich)} jobs "
            f"out of {len(jobs)} raw jobs"
        )

        tasks = [limited_extract(job) for job in jobs_to_enrich]

        detailed_jobs = await asyncio.gather(*tasks)

        detailed_jobs = [job for job in detailed_jobs if job is not None]

        self.logger.info(f"Detailed jobs extracted: {len(detailed_jobs)}")

        return detailed_jobs

    async def scrape(self):

        pass
