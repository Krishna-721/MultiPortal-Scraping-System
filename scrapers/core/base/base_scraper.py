from abc import ABC, abstractmethod
from scrapers.core.utils.logger import setup_logger
from scrapers.core.browser.playwright_manager import PlaywrightManager
from playwright_stealth import Stealth


class BaseScraper(ABC):
    def __init__(self, portal_name: str):
        self.portal_name = portal_name
        self.logger = setup_logger(portal_name)

        self.playwright_manager = PlaywrightManager()

        self.browser = None
        self.page = None

        self.logger.info(f"{self.portal_name} scraper started")

    # Initialization and cleanup can be overridden by child classes if needed, but they provide a default implementation that logs the actions.
    async def initialize(self, headless=False):
        self.logger.info(f"Initializing {self.portal_name} scraper")
        self.browser = await self.playwright_manager.start(headless=headless)
        self.context = await self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/136.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )

        self.page = await self.context.new_page()

        await Stealth().apply_stealth_async(self.page)
        self.logger.info(f"Browser initialized for {self.portal_name}")

    async def cleanup(self):
        self.logger.info(f"Cleaning up {self.portal_name} scraper")
        if self.context:
            await self.context.close()

        await self.playwright_manager.stop()

    @abstractmethod
    async def scrape(self):
        pass
