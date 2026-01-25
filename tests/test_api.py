"""
Test CCRS-2 FastAPI Endpoints
"""
import pytest
import json
from unittest.mock import patch, Mock

class TestHealthEndpoint:
    """Test health check endpoint."""

    @pytest.mark.api
    def test_health_check(self, api_client):
        """Test GET /health endpoint."""
        response = api_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
        assert "timestamp" in data

class TestRootEndpoint:
    """Test root endpoint."""

    @pytest.mark.api
    def test_root_endpoint(self, api_client):
        """Test GET / endpoint."""
        response = api_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "CCRS-2"
        assert data["version"] == "2.0.0"

class TestExecuteEndpoint:
    """Test job execution endpoint."""

    @pytest.mark.api
    def test_execute_valid_job(self, api_client, sample_job_request):
        """Test POST /execute with valid job."""
        # Mock Redis operations
        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        response = api_client.post(
            "/execute",
            json=sample_job_request.dict()
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
        assert data["job_id"].startswith("ccrs2-")
        assert "Job submitted successfully" in data["message"]

        # Verify Redis calls
        api_client.mock_redis.lpush.assert_called_once()
        api_client.mock_redis.hset.assert_called_once()

    @pytest.mark.api
    def test_execute_invalid_tenant(self, api_client):
        """Test POST /execute with invalid tenant."""
        invalid_request = {
            "tenant_id": "invalid",
            "operation": "chat",
            "message": "test"
        }

        response = api_client.post("/execute", json=invalid_request)

        assert response.status_code == 400
        data = response.json()
        assert "Invalid tenant" in data["detail"]

    @pytest.mark.api
    def test_execute_invalid_operation(self, api_client):
        """Test POST /execute with invalid operation."""
        invalid_request = {
            "tenant_id": "demo",
            "operation": "invalid_op",
            "message": "test"
        }

        response = api_client.post("/execute", json=invalid_request)

        assert response.status_code == 400
        data = response.json()
        assert "Invalid operation" in data["detail"]

    @pytest.mark.api
    def test_execute_redis_error(self, api_client, sample_job_request):
        """Test POST /execute when Redis is unavailable."""
        # Mock Redis error
        api_client.mock_redis.lpush.side_effect = Exception("Redis connection failed")

        response = api_client.post(
            "/execute",
            json=sample_job_request.dict()
        )

        assert response.status_code == 500
        data = response.json()
        assert "Failed to submit job" in data["detail"]

class TestJobStatusEndpoint:
    """Test job status endpoint."""

    @pytest.mark.api
    def test_get_job_status_found(self, api_client, sample_completed_job):
        """Test GET /jobs/{job_id} when job exists."""
        job_id = sample_completed_job["job_id"]

        # Mock Redis to return job data
        api_client.mock_redis.exists.return_value = 1
        api_client.mock_redis.hgetall.return_value = sample_completed_job

        response = api_client.get(f"/jobs/{job_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["status"] == "completed"
        assert data["result"] == "Test response"

        # Verify Redis calls
        api_client.mock_redis.exists.assert_called_once_with(f"job:{job_id}")
        api_client.mock_redis.hgetall.assert_called_once_with(f"job:{job_id}")

    @pytest.mark.api
    def test_get_job_status_not_found(self, api_client):
        """Test GET /jobs/{job_id} when job doesn't exist."""
        job_id = "ccrs2-nonexistent"

        # Mock Redis to return no job
        api_client.mock_redis.exists.return_value = 0

        response = api_client.get(f"/jobs/{job_id}")

        assert response.status_code == 404
        data = response.json()
        assert "Job not found" in data["detail"]

    @pytest.mark.api
    def test_get_job_status_redis_error(self, api_client):
        """Test GET /jobs/{job_id} when Redis fails."""
        job_id = "ccrs2-test123"

        # Mock Redis error
        api_client.mock_redis.exists.side_effect = Exception("Redis connection failed")

        response = api_client.get(f"/jobs/{job_id}")

        assert response.status_code == 500
        data = response.json()
        assert "Failed to retrieve job" in data["detail"]

class TestTenantValidation:
    """Test tenant validation functionality."""

    @pytest.mark.api
    @pytest.mark.parametrize("tenant_id", ["demo", "test", "example"])
    def test_valid_tenants(self, api_client, tenant_id):
        """Test that valid tenants are accepted."""
        job_request = {
            "tenant_id": tenant_id,
            "operation": "chat",
            "message": "test"
        }

        # Mock Redis operations
        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        response = api_client.post("/execute", json=job_request)
        assert response.status_code == 200

    @pytest.mark.api
    @pytest.mark.parametrize("tenant_id", ["invalid", "", "unknown", "admin"])
    def test_invalid_tenants(self, api_client, tenant_id):
        """Test that invalid tenants are rejected."""
        job_request = {
            "tenant_id": tenant_id,
            "operation": "chat",
            "message": "test"
        }

        response = api_client.post("/execute", json=job_request)
        assert response.status_code == 400

class TestOperationValidation:
    """Test operation validation functionality."""

    @pytest.mark.api
    @pytest.mark.parametrize("operation", ["chat", "command", "agent", "script"])
    def test_valid_operations(self, api_client, operation):
        """Test that valid operations are accepted."""
        job_request = {
            "tenant_id": "demo",
            "operation": operation,
            "message": "test"
        }

        # Mock Redis operations
        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        response = api_client.post("/execute", json=job_request)
        assert response.status_code == 200

    @pytest.mark.api
    @pytest.mark.parametrize("operation", ["invalid", "", "unknown", "delete"])
    def test_invalid_operations(self, api_client, operation):
        """Test that invalid operations are rejected."""
        job_request = {
            "tenant_id": "demo",
            "operation": operation,
            "message": "test"
        }

        response = api_client.post("/execute", json=job_request)
        assert response.status_code == 400