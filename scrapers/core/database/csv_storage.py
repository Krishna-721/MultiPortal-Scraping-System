import os
import pandas as pd

from scrapers.core.models.job_model import JOB_SCHEMA_COLUMNS
from scrapers.core.utils.job_normalizer import (
    normalize_job_metadata,
)


class CSVStorage:
    def save_jobs(self, jobs, filename, dedupe_column="link_hash"):

        if not jobs:
            print("No jobs to save")

            return

        new_df = pd.DataFrame(jobs)
        normalized_rows = []

        for _, row in new_df.iterrows():

            row = row.to_dict()

            metadata = normalize_job_metadata(
                title=row.get("title"),
                description=row.get("description"),
                location=row.get("location"),
            )

            # if not row.get("job_type"):
            #     pass
            
            if not row.get("employment_type"):
                row["employment_type"] = metadata["employment_type"]

            if not row.get("work_auth"):
                row["work_auth"] = metadata["work_auth"]

            normalized_rows.append(row)

        new_df = pd.DataFrame(normalized_rows)

        new_df = new_df[
            new_df["link"].notna()
        ]

        new_df = new_df[
            new_df["link_hash"].notna()
        ]

        new_df = new_df[
            new_df["title"].notna()
        ]

        # =========================
        # ENSURE SCHEMA COLUMNS
        # =========================

        new_df = new_df.reindex(columns=JOB_SCHEMA_COLUMNS)

        # =========================
        # LOAD EXISTING
        # =========================

        if os.path.exists(filename):
            existing_df = pd.read_csv(filename)

            existing_df = existing_df.reindex(
                columns=JOB_SCHEMA_COLUMNS
            )

            combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        else:
            combined_df = new_df

        # =========================
        # CLEAN
        # =========================

        combined_df = (
            combined_df.drop_duplicates(subset=[dedupe_column], keep="last")
            .fillna("")
            .reset_index(drop=True)
        )

        # =========================
        # SAVE
        # =========================

        combined_df.to_csv(filename, index=False)

        final_count = len(combined_df)

        print(f"Saved {final_count} total jobs")

        return final_count
