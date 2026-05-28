from scrapers.adapters.getro.client import GetroClient
from scrapers.portals.bvp_jobs.parser import parse_job


from scrapers.core.config.search_keywords import (
    SEARCH_KEYWORDS
)


from scrapers.core.config.settings import MAX_TOTAL_JOBS_PER_PORTAL, MAX_JOBS_PER_KEYWORD

def limit_reached(all_jobs):
    return len(all_jobs) >= MAX_TOTAL_JOBS_PER_PORTAL

def main():

    client = GetroClient(
        board_id="bessemer-ventures",
        domain="bvp",
        query_field="titlePrefix"
    )

    all_jobs = []

    for keyword in SEARCH_KEYWORDS:
        if limit_reached(all_jobs):
            break

        print(f"Fetching: {keyword}")

        try:

            jobs = client.search_jobs(keyword)

            print(f"Found {len(jobs)} jobs")

            for job in jobs[:MAX_JOBS_PER_KEYWORD]:

                parsed = parse_job(job)

                parsed["search_keyword"] = keyword

                all_jobs.append(parsed)
                
                if limit_reached(all_jobs):
                    print(f"Reached limit of {MAX_TOTAL_JOBS_PER_PORTAL}")
                    break

        except Exception as e:

            print(f"Failed keyword {keyword}: {e}")

    if not all_jobs:

        print("No jobs found")
        return

    from scrapers.core.database.csv_storage import CSVStorage
    storage = CSVStorage()
    output_file = "data/bvp_jobs.csv"
    storage.save_jobs(all_jobs, output_file)

if __name__ == "__main__":
    main()