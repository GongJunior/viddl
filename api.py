from fastapi import FastAPI
from pydantic import BaseModel
from dataclasses import dataclass

# dummy class to represent background worker
@dataclass
class BackgroundWorker:
    status: str = "idle"
    current_job: int = 0

app = FastAPI()
dlp = BackgroundWorker()

class DownloadRequest(BaseModel):
    urls: list[str]
    storage_option: str

class DownloadResponse(BaseModel):
    job_id: int
    status: str
    num_links_requested: int

class DownloadsSummary(BaseModel):
    jobs: list[DownloadResponse]
    total_jobs: int
    completed_jobs: int
    pending_jobs: int

@app.get("/api/test")
def read_root() -> dict[str, str]:
    return {"message": "Hello, World!"}

@app.get("/api/downloads")
def get_download_status() -> DownloadsSummary:
    return DownloadsSummary(jobs=[], total_jobs=0, completed_jobs=0, pending_jobs=0)

@app.get("/api/downloads/{job_id}")
def get_download_status_by_id(job_id: int) -> DownloadResponse:
    return DownloadResponse(job_id=job_id, status="queued", num_links_requested=0)

@app.post("/api/downloads")
def add_download_requests(download_request: DownloadRequest) -> DownloadResponse:
    return DownloadResponse(
        job_id=1, 
        status="queued", 
        num_links_requested=len(download_request.urls)
        )