from scrapers.core.base.base_scraper import BaseScraper

from scrapers.core.config.settings import (
    MAX_JOBS_PER_KEYWORD,
)


class BaseGetroScraper(BaseScraper):

    def __init__(
        self,
        portal_name: str,
        jobs_url: str,
        timeout_ms: int = 60000,
    ):

        super().__init__(portal_name=portal_name)

        self.jobs_url = jobs_url

        self.timeout_ms = timeout_ms

    async def fetch_page(
        self,
        keyword,
    ):

        page = await self.context.new_page()

        captured_response = None

        try:

            def handle_response(response):

                nonlocal captured_response

                try:

                    if (
                        "search-jobs" in response.url
                        and response.status == 200
                    ):

                        captured_response = response

                except Exception:
                    pass

            page.on(
                "response",
                handle_response,
            )

            await page.goto(
                self.jobs_url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )

            await page.wait_for_timeout(4000)

            search_box = page.locator(
                "input[data-testid='search-input']"
            ).first

            await search_box.click()

            await search_box.fill(keyword)

            await page.keyboard.press("Enter")

            await page.wait_for_timeout(5000)

            if not captured_response:

                self.logger.error(
                    f"No API response captured for '{keyword}'"
                )

                return {}

            return await captured_response.json()

        except Exception as e:

            self.logger.error(
                f"Getro fetch failed for keyword '{keyword}': {e}"
            )

            return {}

        finally:

            await page.close()

    async def fetch_all_jobs(
        self,
        keyword,
    ):

        data = await self.fetch_page(keyword)

        all_jobs = []

        grouped_jobs = data.get("jobs", [])

        for company_group in grouped_jobs:

            company = company_group.get("company", {})

            for job in company_group.get("jobs", []):

                job["_company"] = company

                if "organization" not in job:

                    job["organization"] = company

                all_jobs.append(job)

                if len(all_jobs) >= MAX_JOBS_PER_KEYWORD:

                    return all_jobs

        return all_jobs