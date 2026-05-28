# Job Scraper System

A production-hardened web scraping system for aggregating job listings from 8 major venture capital and startup job portals.

## Overview

This scraper collects job postings from multiple sources, enriches them with additional details, applies relevance filtering, and outputs normalized data to CSV format.

**Supported Portals:**
- Startup.jobs (DOM scraping + enrichment)
- A16Z (API + Playwright enrichment)
- Accel (API + Playwright enrichment)
- BVP (API)
- LSVP (API)
- Sequoia (API)
- Khosla (API)
- General Catalyst (API)

## Features

- **Multi-source aggregation** — Collects from 8 major VC/startup job platforms
- **Smart relevance filtering** — Filters out sales, marketing, and irrelevant roles
- **Data enrichment** — Fetches additional job details via Playwright for select portals
- **Schema validation** — Ensures consistent data structure across all sources
- **Duplicate prevention** — Deduplicates jobs across portals
- **Error resilience** — Handles timeouts, network errors, and parser failures gracefully
- **CSV normalization** — Outputs consistent, deduplicated job data
- **Production-safe** — Lightweight, no heavy dependencies; ready for integration

## Installation

### Requirements
- Python 3.7+
- pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Scraping_System
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers (required for DOM and detail scraping):
```bash
playwright install chromium
```

## Usage

### Run All Scrapers

Execute the master orchestrator:
```bash
python master.py
```

This sequentially runs all 8 scraper portals and outputs aggregated results to CSV files in the `data/` directory.

### Output

Jobs are saved as CSV files in the `data/` directory with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| `job_id` | string | Unique job identifier |
| `title` | string | Job title |
| `company` | string | Company name |
| `link` | string | URL to job posting |
| `location` | string | Job location |
| `description` | string | Full job description |
| `salary` | string | Salary range (if available) |
| `equity` | string | Equity information (if available) |
| `job_type` | string | Employment type (full-time, contract, etc.) |
| `experience` | string | Experience level required |
| `skills` | string | Required skills |
| `work_auth` | string | Work authorization requirements |
| `portal` | string | Source portal |
| `posted_date` | string | Job posting date |
| `scraped_at` | datetime | When the job was scraped |

### Relevance Filtering

The system automatically filters out non-technical roles:

**Blocked roles:**
- Sales, Marketing, Designer, Recruiter
- Support, Customer Support, Operations
- Account Executive, Business Development
- Finance, Legal, Compliance, HR

**Allowed mappings:**
- Software Engineer → backend, frontend, full stack, platform engineer
- Data Engineer → analytics engineer, data platform, ETL engineer
- DevOps Engineer → SRE, infrastructure engineer, platform engineer
- Product Manager → product owner

## Architecture

```
scrapers/
├── core/
│   ├── models/
│   │   └── job_models.py          # Job schema definitions
│   ├── utils/
│   │   ├── relevance_filter.py    # Role filtering logic
│   │   ├── schema_validator.py    # Job validation
│   │   ├── job_normalizer.py      # Data normalization
│   │   └── enricher.py            # Detail enrichment
│   ├── database/
│   │   └── csv_storage.py         # CSV I/O and deduplication
│   └── browser/
│       └── playwright_setup.py    # Browser initialization
├── portals/                        # Portal-specific scrapers
│   ├── startup_jobs/
│   ├── a16z_jobs/
│   ├── accel_jobs/
│   ├── bvp_jobs/
│   ├── lsvp_jobs/
│   ├── sequoia_jobs/
│   ├── khosla_jobs/
│   └── general_catalyst/
└── scrapers.py                    # Main scraper coordinator
```

## Portal Details

### Startup.jobs
- **Method:** DOM scraping with Playwright
- **Details:** Enriches with company data and job descriptions
- **Field:** Extracts work authorization, equity, and salary

### A16Z, Accel
- **Method:** API call + Playwright enrichment
- **Details:** Fetches additional information via browser
- **Enrichment:** Company details, full descriptions

### BVP, LSVP, Sequoia, Khosla, General Catalyst
- **Method:** REST API
- **Details:** Direct API calls, no browser enrichment
- **Parsing:** Standardized JSON parsing

## Production Considerations

### Scalability
- **Current:** Sequential portal execution (~5-10 min for full run)
- **Optimization:** Consider async/parallel execution for large-scale deployments
- **Resource Usage:** Minimal (~500MB RAM); Playwright uses ~200MB for browser instances

### Reliability
- **Timeouts:** All HTTP requests (30s), Playwright (60s)
- **Retry:** Failed jobs logged but not retried (idempotent across runs)
- **Failure Isolation:** Single portal failure doesn't crash entire pipeline

### Data Quality
- **Deduplication:** Prevents duplicate CSV rows across runs
- **Validation:** Rejects jobs missing required fields (title, company, link)
- **Normalization:** Standardizes whitespace, formats, and field names

### Monitoring
- **Logging:** INFO/WARNING logs for each scraper and enrichment step
- **CSV Output:** Check `data/` directory for scraped results
- **Error Logs:** Console output shows failures with reason and portal

### Integration
- **CSV-based:** Easy to import into databases or data pipelines
- **Idempotent:** Safe to re-run; duplicates are detected and skipped
- **Stateless:** No persistent state required between runs
- **Dependencies:** Only standard libraries + requests + pandas + playwright

## Performance Metrics

- **A16Z:** ~30-50 jobs/run (browser enrichment)
- **Accel:** ~40-60 jobs/run (browser enrichment)
- **Startup.jobs:** ~100-150 jobs/run (full DOM scraping)
- **API Portals:** ~200-400 jobs/run (combined)

**Total:** ~500-800 jobs per full run (depending on keyword relevance)

## Troubleshooting

### Playwright Issues
```bash
# Reinstall browsers if missing
playwright install chromium
```

### CSV Not Updating
- Check `data/` directory permissions
- Verify sufficient disk space
- Review console logs for validation errors

### Slow Scraping
- Monitor network latency to job portals
- Reduce browser enrichment scope if needed
- Check for rate limiting (503/429 responses in logs)

### Missing Jobs
- Verify keyword relevance (non-technical jobs are filtered)
- Check if portal API is down (console logs will indicate)
- Review validation logs for schema mismatches

## Contributing

When modifying scrapers:
- Preserve CSV schema consistency
- Add validation for new fields
- Use relevance filters for job titles
- Add timeout/error handling for network calls
- Test with sample data before production use

## License

[Specify your license]

## Contact

For issues or questions about the scraper system, please open an issue in the repository.
