from scrapers.portals.lsvp_jobs.scraper import LSVPScraper

from scrapers.core.database.csv_storage import CSVStorage


def main():

    scraper = LSVPScraper()

    jobs = scraper.scrape()

    print(f"\nScraped {len(jobs)} jobs")

    if not jobs:
        print("No jobs found")

        return

    storage = CSVStorage()

    storage.save_jobs(jobs, "data/lsvp_jobs.csv")

    print("\nSaved jobs to data/lsvp_jobs.csv")


if __name__ == "__main__":
    main()
