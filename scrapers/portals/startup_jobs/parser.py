import re
from scrapers.core.utils.hash_utils import generate_job_hash 


class StartupJobsDetailScraper:
    def __init__(self, page, logger):

        self.page = page
        self.logger = logger

    async def extract_job_details(self, job):

        detail_page = await self.page.context.new_page()

        link = job.get("link")

        try:
            await detail_page.goto(
                link,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            await detail_page.wait_for_selector(
                ".post__content",
                timeout=15000,
            )

            self.logger.info(f"Opened: {link}")

            job_data = job.copy()

            # =========================
            # TITLE
            # =========================

            title_locator = detail_page.locator("h1")

            if await title_locator.count() > 0:
                title = await title_locator.first.inner_text()

                job_data["title"] = title.strip()

            # =========================
            # COMPANY
            # =========================

            company = None

            company_selectors = [
                'a[href*="/company/"]',
                'a[href*="/companies/"]',
                "main a",
            ]

            for selector in company_selectors:
                locator = detail_page.locator(selector)

                count = await locator.count()

                if count > 0:
                    for i in range(min(count, 5)):
                        try:
                            text = await locator.nth(i).text_content()

                            if not text:
                                continue

                            cleaned = text.strip()

                            if (
                                len(cleaned) > 1
                                and len(cleaned) < 40
                                and "apply" not in cleaned.lower()
                                and "startup jobs" not in cleaned.lower()
                            ):
                                company = cleaned

                                break

                        except:
                            pass

                if company:
                    break

            job_data["company"] = company

            # =========================
            # TOP METADATA SECTION
            # =========================

            main_locator = detail_page.locator("main")

            main_text = (
                await main_locator.inner_text()
                if await main_locator.count() > 0
                else ""
            )

            top_text = "\n".join(main_text.split("\n")[:40])

            top_lower = top_text.lower()

            # =========================
            # LOCATION
            # =========================

            location = None

            metadata_lines = [
                line.strip() for line in top_text.split("\n") if line.strip()
            ]

            bad_location_keywords = [
                "engineering",
                "product",
                "marketing",
                "customer",
                "sales",
                "founders",
                "cto",
                "manager",
                "enterprise",
                "partnership",
                "startup jobs",
                "browse jobs",
            ]

            for line in metadata_lines:
                lower = line.lower()

                # skip obvious garbage

                if any(bad in lower for bad in bad_location_keywords):
                    continue

                # valid location indicators

                if "," in line and len(line) < 40:
                    parts = [p.strip() for p in line.split(",")]

                    # must look like actual geo names

                    if len(parts) == 2 and all(len(p.split()) <= 3 for p in parts):
                        location = line

                        break

            job_data["location"] = location

            # =========================
            # EMPLOYMENT TYPE
            # =========================

            employment_type = None

            if "remote" in top_lower:
                employment_type = "Remote"

            elif "hybrid" in top_lower:
                employment_type = "Hybrid"

            elif "on-site" in top_lower or "onsite" in top_lower:
                employment_type = "On-site"

            job_data["employment_type"] = employment_type

            # =========================
            # JOB TYPE
            # =========================

            job_type = None

            job_type_patterns = {
                "Full-time": [
                    "full-time",
                    "full time",
                ],
                "Part-time": [
                    "part-time",
                    "part time",
                ],
                "Contract": [
                    "contract role",
                    "contract position",
                    "contract basis",
                ],
                "Internship": [
                    "internship",
                ],
            }

            for jt, patterns in job_type_patterns.items():
                if any(p in top_lower for p in patterns):
                    job_type = jt

                    break

            job_data["job_type"] = job_type

            # =========================
            # WORK AUTH
            # =========================

            work_auth = None

            work_auth_patterns = [
                "visa sponsorship",
                "work authorization",
                "authorized to work",
                "sponsorship available",
                "no sponsorship",
            ]

            for pattern in work_auth_patterns:
                if pattern in top_lower:
                    work_auth = pattern

                    break

            job_data["work_auth"] = work_auth

            # =========================
            # DESCRIPTION
            # =========================

            description_locator = detail_page.locator(".post__content")

            if await description_locator.count() > 0:
                description = await description_locator.first.inner_text()

                job_data["description"] = description.strip()[:5000]

            else:
                job_data["description"] = None

            # =========================
            # SALARY
            # =========================

            salary_match = re.search(
                r"(\$[\d,]+(?:\s*[-–]\s*\$?[\d,]+)?(?:\/hr|\/year|k)?)",
                main_text,
                re.IGNORECASE,
            )

            job_data["salary_range"] = salary_match.group(1) if salary_match else None
            # =========================
            # FINAL METADATA
            # =========================

            job_data["source"] = "startup_jobs"

            job_data["job_status"] = "active"

            job_data["link_hash"] = generate_job_hash(
                job_data.get("title"),
                job_data.get("company"),
                job_data.get("location"),
)
            return job_data

        except Exception as e:
            self.logger.error(f"Failed extracting:\n{link}\n{e}")

            return None

        finally:
            await detail_page.close()
