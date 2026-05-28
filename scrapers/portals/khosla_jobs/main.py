from scrapers.portals.khosla_jobs.scraper import (
    KhoslaScraper,
)


def main():

    scraper = KhoslaScraper()

    scraper.scrape()


if __name__ == "__main__":
    main()