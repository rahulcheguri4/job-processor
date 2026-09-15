from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime
import time
import uuid


app = FastAPI(
    title="Background Job Processor",
    description="Simple background job processing system",
    version="1.0"
)


# Store jobs
jobs = {}


# Request model
class JobRequest(BaseModel):
    task_name: str


# Background job function
def process_job(job_id: str, task_name: str):

    jobs[job_id]["status"] = "RUNNING"

    jobs[job_id]["logs"].append(
        f"{datetime.now()} - Job started"
    )

    try:
        # Simulate time-consuming work
        time.sleep(10)

        jobs[job_id]["status"] = "COMPLETED"

        jobs[job_id]["logs"].append(
            f"{datetime.now()} - Job completed successfully"
        )

    except Exception as e:

        jobs[job_id]["status"] = "FAILED"

        jobs[job_id]["logs"].append(
            f"{datetime.now()} - Job failed: {str(e)}"
        )


# Home API
@app.get("/")
def home():

    return {
        "message": "Background Job Processor is running"
    }


# Submit a new job
@app.post("/jobs")
def create_job(
    request: JobRequest,
    background_tasks: BackgroundTasks
):

    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "task_name": request.task_name,
        "status": "PENDING",
        "created_at": str(datetime.now()),
        "logs": []
    }

    background_tasks.add_task(
        process_job,
        job_id,
        request.task_name
    )

    return {
        "message": "Job submitted successfully",
        "job_id": job_id,
        "status": "PENDING"
    }


# Check job status
@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):

    if job_id not in jobs:

        return {
            "error": "Job not found"
        }

    return jobs[job_id]


# Get job logs
@app.get("/jobs/{job_id}/logs")
def get_job_logs(job_id: str):

    if job_id not in jobs:

        return {
            "error": "Job not found"
        }

    return {
        "job_id": job_id,
        "logs": jobs[job_id]["logs"]
    }