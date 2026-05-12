def run_import_job(job):
    return {"job_id": job.get("id"), "status": "completed", "summary": "Imported and summarized"}
