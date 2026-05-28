def extract_employment_type(work_mode=None, text_to_search=""):
    """
    Returns Hybrid, Remote, or On-site.
    """
    emp_type = None

    if work_mode:
        wm_lower = work_mode.lower()
        if "remote" in wm_lower:
            emp_type = "Remote"
        elif "on_site" in wm_lower or "onsite" in wm_lower:
            emp_type = "On-site"
        elif "hybrid" in wm_lower:
            emp_type = "Hybrid"

    if not emp_type and text_to_search:
        text_lower = text_to_search.lower()
        if "remote" in text_lower:
            emp_type = "Remote"
        elif "hybrid" in text_lower:
            emp_type = "Hybrid"
        elif "on-site" in text_lower or "onsite" in text_lower:
            emp_type = "On-site"

    return emp_type

def extract_job_type(text_to_search=""):
    """
    Returns Full-time, Part-time, Contract, or Internship.
    """
    job_type = None
    if not text_to_search:
        return None
        
    text_lower = text_to_search.lower()
    
    job_type_patterns = {
        "Full-time": ["full-time", "full time"],
        "Part-time": ["part-time", "part time"],
        "Contract": ["contract role", "contract position", "contract basis", "contractor", "contract"],
        "Internship": ["internship", "intern", "co-op"],
    }
    
    for jt, patterns in job_type_patterns.items():
        if any(p in text_lower for p in patterns):
            job_type = jt
            break

    return job_type
