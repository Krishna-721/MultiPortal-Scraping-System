from scrapers.portals.general_catalyst.scraper import (
    GeneralCatalystScraper,
)


def main():

    scraper = GeneralCatalystScraper()

    scraper.scrape()


if __name__ == "__main__":
    main()