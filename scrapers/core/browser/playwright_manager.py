# This can be reused across multiple scrapers, so it's placed in the core module.
from playwright.async_api import async_playwright


class PlaywrightManager:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def start(self, headless=True):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
        )

        return self.browser

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
