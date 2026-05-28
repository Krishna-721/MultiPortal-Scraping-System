import requests
from typing import List, Dict


class GetroClient:
    def __init__(
        self,
        board_id: str,
        domain: str,
        query_field: str = "query",
    ):

        self.board_id = board_id

        self.domain = domain

        self.base_url = f"https://jobs.{domain}.com/api-boards/search-jobs"

        self.session = requests.Session()

        self.headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "origin": f"https://jobs.{domain}.com",
            "referer": f"https://jobs.{domain}.com/",
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/136.0.0.0 Safari/537.36"
            ),
        }

        self.query_field = query_field 

    def search_jobs(
        self,
        keyword: str,
        size: int = 15,
    ) -> List[Dict]:

        payload = {
            "meta": {
                "size": size,
            },
            "board": {
                "id": self.board_id,
                "isParent": True,
            },
            "query": {
                self.query_field: keyword,
                "promoteFeatured": True,
            },
            "grouped": True,
        }

        response = self.session.post(
            self.base_url,
            json=payload,
            headers=self.headers,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return self._flatten_jobs(data)

    def _flatten_jobs(self, data: Dict) -> List[Dict]:

        flattened = []

        for company_group in data.get("jobs", []):
            company = company_group.get("company", {})

            for job in company_group.get("jobs", []):
                job["_company"] = company

                flattened.append(job)

        return flattened
