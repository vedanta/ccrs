"""
CCRS - Simple & Effective Claude Code Routing Service
Single FastAPI file for lean implementation
"""
import json
import uuid
import redis
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

from models import JobRequest, JobResponse, JobStatus, HealthResponse

# Initialize FastAPI app
app = FastAPI(
    title="CCRS",
    description="Lean Claude Code Routing Service",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis connection
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True
    )
    # Test connection
    redis_client.ping()
    print("✅ Redis connection established")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    redis_client = None

# Simple tenant validation (extensible)
VALID_TENANTS = {"demo", "test", "example"}

def validate_tenant(tenant_id: str) -> bool:
    """Simple tenant validation"""
    return tenant_id in VALID_TENANTS

def generate_job_id() -> str:
    """Generate unique job ID"""
    return f"ccrs-{uuid.uuid4().hex[:8]}"

def get_current_time() -> str:
    """Get current time as ISO string"""
    return datetime.utcnow().isoformat() + "Z"


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Simple health check"""
    redis_status = "connected" if redis_client else "disconnected"

    return HealthResponse(
        status="healthy" if redis_client else "degraded",
        timestamp=get_current_time()
    )


@app.post("/execute", response_model=JobResponse)
async def execute_job(request: JobRequest):
    """Execute a Claude operation - main endpoint"""

    # Validate tenant
    if not validate_tenant(request.tenant_id):
        raise HTTPException(status_code=403, detail=f"Invalid tenant: {request.tenant_id}")

    # Check Redis connection
    if not redis_client:
        raise HTTPException(status_code=503, detail="Job queue unavailable")

    # Generate job
    job_id = generate_job_id()
    current_time = get_current_time()

    # Create job data
    job_data = {
        "job_id": job_id,
        "tenant_id": request.tenant_id,
        "operation": request.operation,
        "message": request.message,
        "status": "queued",
        "created_at": current_time,
        "timeout_seconds": request.timeout_seconds
    }

    try:
        # Store job in Redis (expires in 1 hour)
        redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))

        # Add to job queue
        redis_client.lpush("ccrs:job_queue", job_id)

        print(f"📋 Job {job_id} queued for {request.tenant_id}: {request.operation}")

        return JobResponse(
            job_id=job_id,
            tenant_id=request.tenant_id,
            status="queued",
            message=f"Job {job_id} queued for {request.operation} operation",
            created_at=current_time
        )

    except Exception as e:
        print(f"❌ Failed to queue job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to queue job")


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status and results"""

    if not redis_client:
        raise HTTPException(status_code=503, detail="Job store unavailable")

    try:
        # Get job from Redis
        job_data_raw = redis_client.get(f"job:{job_id}")

        if not job_data_raw:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        job_data = json.loads(job_data_raw)

        return JobStatus(**job_data)

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid job data")
    except Exception as e:
        print(f"❌ Failed to get job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "CCRS",
        "version": "3.0.0",
        "description": "Lean Claude Code Routing Service",
        "endpoints": {
            "health": "/health",
            "execute": "/execute",
            "job_status": "/jobs/{job_id}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)