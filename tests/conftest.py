"""
CCRS-2 Test Configuration
Shared fixtures and test utilities
"""
import pytest
import fakeredis
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json
import time

# Import our application modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import JobRequest, JobResponse, JobStatus, HealthResponse

@pytest.fixture
def fake_redis():
    """Provide a fake Redis instance for testing."""
    return fakeredis.FakeRedis(decode_responses=True)

@pytest.fixture
def mock_redis_client():
    """Mock Redis client for testing."""
    mock_redis = Mock()
    mock_redis.ping.return_value = True
    mock_redis.lpush.return_value = 1
    mock_redis.brpop.return_value = None
    mock_redis.hset.return_value = 1
    mock_redis.hget.return_value = None
    mock_redis.hgetall.return_value = {}
    mock_redis.exists.return_value = 0
    return mock_redis

@pytest.fixture
def sample_job_request():
    """Sample job request for testing."""
    return JobRequest(
        tenant_id="test",
        operation="chat",
        message="Test message",
        timeout_seconds=300
    )

@pytest.fixture
def sample_job_data():
    """Sample job data for Redis storage."""
    return {
        "job_id": "ccrs2-test123",
        "tenant_id": "test",
        "operation": "chat",
        "message": "Test message",
        "timeout_seconds": "300",
        "status": "pending",
        "created_at": "2026-01-25T13:30:00Z",
        "started_at": "",
        "completed_at": "",
        "result": "",
        "error": ""
    }

@pytest.fixture
def sample_completed_job():
    """Sample completed job data."""
    return {
        "job_id": "ccrs2-test123",
        "tenant_id": "test",
        "operation": "chat",
        "message": "Test message",
        "timeout_seconds": "300",
        "status": "completed",
        "created_at": "2026-01-25T13:30:00Z",
        "started_at": "2026-01-25T13:30:01Z",
        "completed_at": "2026-01-25T13:30:05Z",
        "result": "Test response",
        "error": ""
    }

@pytest.fixture
def api_client():
    """FastAPI test client with mocked Redis."""
    with patch('app.redis_client') as mock_redis:
        mock_redis.ping.return_value = True

        from app import app
        client = TestClient(app)

        # Store mock_redis on client for access in tests
        client.mock_redis = mock_redis
        yield client

@pytest.fixture
def worker_instance():
    """Worker instance for testing."""
    with patch('worker.redis') as mock_redis_module:
        mock_redis = Mock()
        mock_redis_module.Redis.return_value = mock_redis

        from worker import CCRS2Worker
        worker = CCRS2Worker()
        worker.redis_client = mock_redis
        yield worker, mock_redis

@pytest.fixture
def cli_client():
    """CLI client for testing."""
    from cli import CCRS2Client
    return CCRS2Client(base_url="http://test-server:8000")

# Test utilities
def generate_test_job_id():
    """Generate a test job ID."""
    return f"ccrs2-test{int(time.time())}"

def create_mock_response(status_code=200, json_data=None):
    """Create a mock HTTP response."""
    mock_resp = Mock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data or {}
    mock_resp.text = json.dumps(json_data or {})
    return mock_resp