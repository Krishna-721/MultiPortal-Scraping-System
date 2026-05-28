from scrapers.portals.sequoia_jobs.scraper import SequoiaScraper

from scrapers.portals.sequoia_jobs.parser import parse_job

from scrapers.core.database.csv_storage import CSVStorage


def main():

    scraper = SequoiaScraper()

    print("Fetching jobs...")

    raw_jobs = scraper.fetch_all_jobs()

    print(f"Fetched {len(raw_jobs)} raw jobs")

    parsed_jobs = [parse_job(job) for job in raw_jobs]

    storage = CSVStorage()

    storage.save_jobs(parsed_jobs, filename="data/sequoia_jobs.csv")

    print(f"Saved {len(parsed_jobs)} jobs")


if __name__ == "__main__":
    main()
