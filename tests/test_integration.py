"""
Test CCRS Integration
End-to-end functionality testing
"""
import pytest
import time
import json
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""

    @pytest.mark.integration
    def test_health_check_integration(self, api_client):
        """Test complete health check workflow."""
        # Test API health endpoint
        response = api_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
        assert "timestamp" in data

    @pytest.mark.integration
    def test_job_submission_and_retrieval(self, api_client, sample_job_request):
        """Test job submission and status retrieval."""
        # Mock Redis operations for job submission
        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        # Submit job
        response = api_client.post("/execute", json=sample_job_request.dict())
        assert response.status_code == 200

        job_response = response.json()
        job_id = job_response["job_id"]
        assert job_id.startswith("ccrs-")

        # Mock job data for retrieval
        completed_job = {
            "job_id": job_id,
            "tenant_id": "test",
            "operation": "chat",
            "status": "completed",
            "created_at": "2026-01-25T13:30:00Z",
            "started_at": "2026-01-25T13:30:01Z",
            "completed_at": "2026-01-25T13:30:05Z",
            "result": "Integration test response",
            "error": ""
        }

        api_client.mock_redis.exists.return_value = 1
        api_client.mock_redis.hgetall.return_value = completed_job

        # Retrieve job status
        response = api_client.get(f"/jobs/{job_id}")
        assert response.status_code == 200

        status_data = response.json()
        assert status_data["job_id"] == job_id
        assert status_data["status"] == "completed"
        assert status_data["result"] == "Integration test response"

class TestTenantIsolation:
    """Test tenant isolation functionality."""

    @pytest.mark.integration
    def test_multiple_tenant_jobs(self, api_client):
        """Test that jobs from different tenants are properly isolated."""
        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        # Submit jobs for different tenants
        tenants = ["demo", "test", "example"]
        job_ids = []

        for tenant in tenants:
            job_request = {
                "tenant_id": tenant,
                "operation": "chat",
                "message": f"Message from {tenant}"
            }

            response = api_client.post("/execute", json=job_request)
            assert response.status_code == 200

            job_id = response.json()["job_id"]
            job_ids.append(job_id)

        # Verify all jobs were created
        assert len(job_ids) == 3
        assert len(set(job_ids)) == 3  # All unique job IDs

class TestOperationTypes:
    """Test different operation types."""

    @pytest.mark.integration
    @pytest.mark.parametrize("operation,message", [
        ("chat", "Hello Claude"),
        ("command", "/help"),
        ("agent", "Run analysis"),
        ("script", "Execute script.py")
    ])
    def test_operation_types(self, api_client, operation, message):
        """Test different operation types are accepted."""
        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        job_request = {
            "tenant_id": "demo",
            "operation": operation,
            "message": message
        }

        response = api_client.post("/execute", json=job_request)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "accepted"
        assert data["job_id"].startswith("ccrs-")

class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.integration
    def test_redis_unavailable_scenario(self, api_client, sample_job_request):
        """Test graceful handling when Redis is unavailable."""
        # Simulate Redis connection failure
        api_client.mock_redis.lpush.side_effect = Exception("Redis connection failed")

        response = api_client.post("/execute", json=sample_job_request.dict())
        assert response.status_code == 500

        error_data = response.json()
        assert "Failed to submit job" in error_data["detail"]

    @pytest.mark.integration
    def test_malformed_job_request(self, api_client):
        """Test handling of malformed job requests."""
        malformed_requests = [
            {},  # Empty request
            {"tenant_id": "demo"},  # Missing required fields
            {"operation": "chat", "message": "test"},  # Missing tenant_id
            {"tenant_id": "", "operation": "chat", "message": "test"},  # Empty tenant_id
        ]

        for request in malformed_requests:
            response = api_client.post("/execute", json=request)
            assert response.status_code == 422  # Pydantic validation error

class TestConcurrentOperations:
    """Test concurrent operations."""

    @pytest.mark.integration
    def test_concurrent_job_submissions(self, api_client):
        """Test multiple concurrent job submissions."""
        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        # Submit multiple jobs concurrently (simulated)
        job_requests = [
            {"tenant_id": "demo", "operation": "chat", "message": f"Message {i}"}
            for i in range(5)
        ]

        job_ids = []
        for request in job_requests:
            response = api_client.post("/execute", json=request)
            assert response.status_code == 200
            job_ids.append(response.json()["job_id"])

        # Verify all jobs got unique IDs
        assert len(job_ids) == 5
        assert len(set(job_ids)) == 5

class TestJobStatusTransitions:
    """Test job status transitions."""

    @pytest.mark.integration
    def test_job_lifecycle_states(self, api_client, sample_job_request):
        """Test job progresses through expected states."""
        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        # Submit job
        response = api_client.post("/execute", json=sample_job_request.dict())
        job_id = response.json()["job_id"]

        # Test pending state
        pending_job = {
            "job_id": job_id,
            "status": "pending",
            "created_at": "2026-01-25T13:30:00Z"
        }
        api_client.mock_redis.exists.return_value = 1
        api_client.mock_redis.hgetall.return_value = pending_job

        response = api_client.get(f"/jobs/{job_id}")
        assert response.json()["status"] == "pending"

        # Test running state
        running_job = {
            **pending_job,
            "status": "running",
            "started_at": "2026-01-25T13:30:01Z"
        }
        api_client.mock_redis.hgetall.return_value = running_job

        response = api_client.get(f"/jobs/{job_id}")
        assert response.json()["status"] == "running"

        # Test completed state
        completed_job = {
            **running_job,
            "status": "completed",
            "completed_at": "2026-01-25T13:30:05Z",
            "result": "Job completed successfully"
        }
        api_client.mock_redis.hgetall.return_value = completed_job

        response = api_client.get(f"/jobs/{job_id}")
        status_data = response.json()
        assert status_data["status"] == "completed"
        assert status_data["result"] == "Job completed successfully"

class TestServiceIntegration:
    """Test integration between API and worker components."""

    @pytest.mark.integration
    def test_api_worker_communication(self, api_client, worker_instance):
        """Test communication between API and worker."""
        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        worker, worker_redis = worker_instance

        # Submit job via API
        job_request = {
            "tenant_id": "demo",
            "operation": "chat",
            "message": "Integration test"
        }

        response = api_client.post("/execute", json=job_request)
        job_id = response.json()["job_id"]

        # Simulate worker processing
        job_data = {
            "job_id": job_id,
            "operation": "chat",
            "message": "Integration test",
            "timeout_seconds": "300"
        }

        with patch.object(worker, 'execute_claude_command') as mock_execute:
            mock_execute.return_value = "Worker processed successfully"

            worker.process_job(job_data)

            # Verify worker called Claude command
            mock_execute.assert_called_once_with("chat", "Integration test", 300)

            # Verify worker updated job status
            assert worker_redis.hset.call_count >= 2  # Started and completed

class TestValidationIntegration:
    """Test validation across all components."""

    @pytest.mark.integration
    def test_tenant_validation_flow(self, api_client):
        """Test tenant validation from API to worker."""
        # Valid tenant should work
        valid_request = {
            "tenant_id": "demo",
            "operation": "chat",
            "message": "Valid tenant test"
        }

        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        response = api_client.post("/execute", json=valid_request)
        assert response.status_code == 200

        # Invalid tenant should be rejected
        invalid_request = {
            "tenant_id": "invalid_tenant",
            "operation": "chat",
            "message": "Invalid tenant test"
        }

        response = api_client.post("/execute", json=invalid_request)
        assert response.status_code == 400
        assert "Invalid tenant" in response.json()["detail"]

    @pytest.mark.integration
    def test_operation_validation_flow(self, api_client):
        """Test operation validation from API to worker."""
        # Valid operation should work
        valid_request = {
            "tenant_id": "demo",
            "operation": "chat",
            "message": "Valid operation test"
        }

        api_client.mock_redis.lpush.return_value = 1
        api_client.mock_redis.hset.return_value = 1

        response = api_client.post("/execute", json=valid_request)
        assert response.status_code == 200

        # Invalid operation should be rejected
        invalid_request = {
            "tenant_id": "demo",
            "operation": "invalid_operation",
            "message": "Invalid operation test"
        }

        response = api_client.post("/execute", json=invalid_request)
        assert response.status_code == 400
        assert "Invalid operation" in response.json()["detail"]