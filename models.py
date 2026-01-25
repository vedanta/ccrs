"""
CCRS-2 Simple Models
Using Pydantic v1 for proven stability
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobRequest(BaseModel):
    """Request to execute a job"""
    tenant_id: str
    operation: str  # 'chat', 'command', 'agent', 'script'
    message: str
    timeout_seconds: Optional[int] = 300


class JobResponse(BaseModel):
    """Response when job is submitted"""
    job_id: str
    tenant_id: str
    status: str  # 'queued', 'running', 'completed', 'failed'
    message: str
    created_at: str  # ISO string to avoid datetime serialization issues


class JobStatus(BaseModel):
    """Complete job status"""
    job_id: str
    tenant_id: str
    operation: str
    status: str
    message: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str = "2.0.0"