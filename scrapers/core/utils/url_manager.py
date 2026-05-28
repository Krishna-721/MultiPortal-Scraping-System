import csv
import os


class URLManager:
    @staticmethod
    def load_existing_urls(filename):

        existing_urls = set()

        if not os.path.exists(filename):
            return existing_urls

        with open(filename, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                job_url = row.get("link")

                if job_url:
                    existing_urls.add(job_url)

        return existing_urls
