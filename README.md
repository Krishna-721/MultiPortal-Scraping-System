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

### Output

Jobs are saved as CSV files in the `data/` directory with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| `title` | string | Job title |
| `company` | string | Company name |
| `location` | string | Job location |
| `link` | string | URL to job posting |
| `link_hash` | string | Hash of link for deduplication |
| `source` | string | Source portal |
| `description` | string | Full job description |
| `salary_range` | string | Salary range (if available) |
| `job_type` | string | Fulltime/Part time/Contract/etc |
| `work_auth` | string | Work authorization requirements |
| `employment_type` | string | Employment type (full-time, remote, hybrid, etc.) |
| `job_status` | string | Active/Inactive/Expired/etc
| `search_keyword` | string | Ex: Software Engineer


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
└── master.py                    # Main scraper coordinator
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
