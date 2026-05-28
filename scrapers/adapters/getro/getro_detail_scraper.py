class GetroDetailScraper:
    def __init__(self, context, logger):

        self.context = context

        self.logger = logger

    async def extract_details(self, url):

        page = await self.context.new_page()

        try:
            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=15000,
            )

            await page.wait_for_timeout(2000)

            selectors = [
                # Greenhouse
                "#content",
                ".content",
                ".job-post",
                ".job__description",
                # Lever
                ".posting",
                ".posting-page",
                ".posting-content",
                # Ashby
                ".ashby-job-posting-brief",
                ".job-posting",
                ".jobs-description",
                # Generic
                "main",
                "article",
                "[class*='description']",
                "[class*='content']",
                "[class*='job']",
            ]

            description = None

            for selector in selectors:
                try:
                    locator = page.locator(selector).first

                    if await locator.count() == 0:
                        continue

                    text = await locator.inner_text()

                    cleaned = text.strip()

                    # Ignore garbage text
                    if len(cleaned) < 300:
                        continue

                    # Remove excessive whitespace
                    cleaned = " ".join(cleaned.split())

                    description = cleaned[:8000]

                    break

                except Exception:
                    continue

            return {
                "description": description,
            }
        except Exception as e:
            self.logger.error(f"Detail extraction failed:\n{url}\n{e}")

            return {}

        finally:
            await page.close()
