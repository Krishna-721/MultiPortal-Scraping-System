import subprocess


SCRAPERS = [
    "scrapers.portals.a16z_jobs.main",
    "scrapers.portals.accel_jobs.main",
    "scrapers.portals.bvp_jobs.main",
    "scrapers.portals.lsvp_jobs.main",
    "scrapers.portals.sequoia_jobs.main",
    "scrapers.portals.startup_jobs.main",
    "scrapers.portals.khosla_jobs.main",
    "scrapers.portals.general_catalyst.main",
]


def run_scraper(module):

    print(f"\n ======== Running: {module} ======== \n")

    try:
        result = subprocess.run(
            ["python", "-m", module]
        )
    except Exception as e:
        print(f"{module} failed to start: {e}")
        return False

    if result.returncode != 0:

        print(f"{module} failed with exit code {result.returncode}")
        return False

    return True




def main():

    for scraper in SCRAPERS:
        run_scraper(scraper)


if __name__ == "__main__":
    main()
