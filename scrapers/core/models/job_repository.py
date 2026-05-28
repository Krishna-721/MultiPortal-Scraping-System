class JobRepository:
    async def save_jobs(self, jobs):
        print(f"Saving {len(jobs)} jobs")