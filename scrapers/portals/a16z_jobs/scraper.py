import requests


class A16ZScraper:

    SEARCH_API = "https://jobs.a16z.com/api-boards/search-jobs"

    def __init__(self):

        self.session = requests.Session()

        self.board_id = "andreessen-horowitz"

        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "origin": "https://jobs.a16z.com",
            "referer": "https://jobs.a16z.com/",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/136.0.0.0 Safari/537.36"
            ),
        }

    def build_payload(
        self,
        keyword,
        sequence=None,
        size=15,
    ):

        payload = {
            "meta": {
                "size": size,
            },
            "board": {
                "id": self.board_id,
                "isParent": True,
            },
            "query": {
                "titlePrefix": keyword,
                "promoteFeatured": True,
            },
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
            self.SEARCH_API,
            json=payload,
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    def fetch_all_jobs(
        self,
        keyword,
        max_jobs=200,
    ):

        all_jobs = []

        seen_ids = set()

        sequence = None

        while True:

            data = self.fetch_page(
                keyword=keyword,
                sequence=sequence,
            )

            jobs = data.get("jobs", [])

            if not jobs:
                break

            added = 0

            for job in jobs:

                job_id = (
                    job.get("jobId")
                    or job.get("id")
                    or job.get("url")
                )

                if not job_id:
                    continue

                if job_id in seen_ids:
                    continue

                seen_ids.add(job_id)

                all_jobs.append(job)

                added += 1

                if len(all_jobs) >= max_jobs:
                    return all_jobs

            if added == 0:
                break

            sequence = (
                data.get("meta", {})
                .get("sequence")
            )

            if not sequence:
                break

        return all_jobs