from abc import abstractmethod
from scrapers.core.base.base_scraper import BaseScraper


class BaseJobScraper(BaseScraper):
    def __init__(self, portal_name: str):
        super().__init__(portal_name)

    async def scrape(self):
        self.logger.info(f"Starting job scraping for {self.portal_name}")
        jobs = await self.fetch_jobs()

        self.logger.info(f"Fetched {len(jobs)} jobs")

        normalized_jobs = []
        for job in jobs:
            normalized_job = await self.normalize_job(job)

            if normalized_job:
                normalized_jobs.append(normalized_job)

        self.logger.info(f"Normalized {len(normalized_jobs)} jobs")

        await self.save_jobs(normalized_jobs)

        self.logger.info(f"Saved jobs successfully")

    @abstractmethod
    async def fetch_jobs(self):
        """
        Portal-specific job extraction.
        Must return raw jobs.
        """
        pass

    @abstractmethod
    async def normalize_job(self, job):
        """
        Convert raw job into standardized format.
        """
        pass

    @abstractmethod
    async def save_jobs(self, jobs):
        """
        Save normalized jobs to DB.
        """
        pass
