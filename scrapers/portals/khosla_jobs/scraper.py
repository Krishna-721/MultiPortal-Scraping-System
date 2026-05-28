import requests

from scrapers.portals.khosla_jobs.config import (
    SEARCH_API,
    HEADERS,
)

from scrapers.portals.khosla_jobs.parser import (
    parse_job,
)

from scrapers.core.config.search_keywords import (
    SEARCH_KEYWORDS,
)

from scrapers.core.config.settings import (
    MAX_TOTAL_JOBS_PER_PORTAL,
    MAX_JOBS_PER_KEYWORD,
)

from scrapers.core.database.csv_storage import (
    CSVStorage,
)


class KhoslaScraper:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update(HEADERS)

        self.storage = CSVStorage()

    def fetch_page(
        self,
        keyword,
        page,
    ):

        payload = {
            "hitsPerPage": 20,
            "page": page,
            "filters": {
                "q": keyword,
            },
            "query": keyword,
        }

        response = self.session.post(
            SEARCH_API,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def fetch_jobs_for_keyword(
        self,
        keyword,
    ):

        jobs = []

        seen_links = set()

        page = 0

        while True:

            if len(jobs) >= MAX_JOBS_PER_KEYWORD:

                print(
                    f"Reached per-keyword limit "
                    f"of {MAX_JOBS_PER_KEYWORD}"
                )

                break

            data = self.fetch_page(
                keyword=keyword,
                page=page,
            )

            raw_jobs = (
                data.get("results", {})
                .get("jobs", [])
            )

            if not raw_jobs:
                break

            print(
                f"Fetched {len(raw_jobs)} jobs "
                f"from page {page}"
            )

            for raw_job in raw_jobs:

                if len(jobs) >= MAX_JOBS_PER_KEYWORD:

                    print(
                        f"Reached per-keyword limit "
                        f"of {MAX_JOBS_PER_KEYWORD}"
                    )

                    return jobs

                parsed = parse_job(
                    raw_job,
                    search_keyword=keyword,
                )

                if not parsed:
                    continue

                link = parsed.get("link")

                if not link:
                    continue

                if link in seen_links:
                    continue

                seen_links.add(link)

                jobs.append(parsed)

            print(
                f"Total jobs collected "
                f"for {keyword}: {len(jobs)}"
            )

            page += 1

        return jobs

    def scrape(self):

        all_jobs = []

        global_seen = set()

        for keyword in SEARCH_KEYWORDS:

            if len(all_jobs) >= MAX_TOTAL_JOBS_PER_PORTAL:

                print(
                    f"Reached global limit "
                    f"of {MAX_TOTAL_JOBS_PER_PORTAL}"
                )

                break

            print(f"Searching: {keyword}")

            try:

                keyword_jobs = self.fetch_jobs_for_keyword(
                    keyword
                )

                print(
                    f"Found {len(keyword_jobs)} jobs "
                    f"for keyword: {keyword}"
                )

                for job in keyword_jobs:

                    if len(all_jobs) >= MAX_TOTAL_JOBS_PER_PORTAL:

                        print(
                            f"Reached global limit "
                            f"of {MAX_TOTAL_JOBS_PER_PORTAL}"
                        )

                        break

                    link = job.get("link")

                    if not link:
                        continue

                    if link in global_seen:
                        continue

                    global_seen.add(link)

                    all_jobs.append(job)

            except Exception as e:

                print(
                    f"Failed keyword "
                    f"{keyword}: {e}"
                )

        print(f"Fetched {len(all_jobs)} raw jobs")

        self.storage.save_jobs(
            all_jobs,
            "data/khosla_jobs.csv",
        )

        print(f"Saved {len(all_jobs)} jobs")