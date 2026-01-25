"""
Test CCRS Pydantic Models
"""
import pytest
from pydantic import ValidationError
from models import JobRequest, JobResponse, JobStatus, HealthResponse

class TestJobRequest:
    """Test JobRequest model validation."""

    @pytest.mark.unit
    def test_valid_job_request(self):
        """Test valid job request creation."""
        request = JobRequest(
            tenant_id="test",
            operation="chat",
            message="Test message",
            timeout_seconds=300
        )

        assert request.tenant_id == "test"
        assert request.operation == "chat"
        assert request.message == "Test message"
        assert request.timeout_seconds == 300

    @pytest.mark.unit
    def test_job_request_defaults(self):
        """Test job request with default timeout."""
        request = JobRequest(
            tenant_id="test",
            operation="command",
            message="/help"
        )

        assert request.timeout_seconds == 300  # Default value

    @pytest.mark.unit
    def test_job_request_validation_errors(self):
        """Test job request validation failures."""

        # Missing required fields
        with pytest.raises(ValidationError):
            JobRequest()

        # Empty tenant_id is allowed at Pydantic level
        # Validation happens at API level

        # Note: Basic validation - more complex validation
        # happens at the API level

class TestJobResponse:
    """Test JobResponse model."""

    @pytest.mark.unit
    def test_valid_job_response(self):
        """Test valid job response creation."""
        response = JobResponse(
            job_id="ccrs-test123",
            tenant_id="test",
            status="accepted",
            message="Job submitted successfully",
            created_at="2026-01-25T13:30:00Z"
        )

        assert response.job_id == "ccrs-test123"
        assert response.tenant_id == "test"
        assert response.status == "accepted"
        assert response.message == "Job submitted successfully"
        assert response.created_at == "2026-01-25T13:30:00Z"

class TestJobStatus:
    """Test JobStatus model."""

    @pytest.mark.unit
    def test_pending_job_status(self):
        """Test pending job status."""
        status = JobStatus(
            job_id="ccrs-test123",
            tenant_id="test",
            operation="chat",
            status="pending",
            message="Test message",
            created_at="2026-01-25T13:30:00Z"
        )

        assert status.status == "pending"
        assert status.message == "Test message"
        assert status.started_at is None
        assert status.completed_at is None
        assert status.result is None
        assert status.error is None

    @pytest.mark.unit
    def test_completed_job_status(self):
        """Test completed job status."""
        status = JobStatus(
            job_id="ccrs-test123",
            tenant_id="test",
            operation="chat",
            status="completed",
            message="Test message",
            created_at="2026-01-25T13:30:00Z",
            started_at="2026-01-25T13:30:01Z",
            completed_at="2026-01-25T13:30:05Z",
            result="Test response"
        )

        assert status.status == "completed"
        assert status.message == "Test message"
        assert status.started_at == "2026-01-25T13:30:01Z"
        assert status.completed_at == "2026-01-25T13:30:05Z"
        assert status.result == "Test response"
        assert status.error is None

    @pytest.mark.unit
    def test_failed_job_status(self):
        """Test failed job status."""
        status = JobStatus(
            job_id="ccrs-test123",
            tenant_id="test",
            operation="chat",
            status="failed",
            message="Test message",
            created_at="2026-01-25T13:30:00Z",
            started_at="2026-01-25T13:30:01Z",
            completed_at="2026-01-25T13:30:02Z",
            error="Command failed with exit code 1"
        )

        assert status.status == "failed"
        assert status.message == "Test message"
        assert status.error == "Command failed with exit code 1"
        assert status.result is None

class TestHealthResponse:
    """Test HealthResponse model."""

    @pytest.mark.unit
    def test_healthy_response(self):
        """Test healthy service response."""
        response = HealthResponse(
            status="healthy",
            timestamp="2026-01-25T13:30:00Z",
            version="2.0.0"
        )

        assert response.status == "healthy"
        assert response.timestamp == "2026-01-25T13:30:00Z"
        assert response.version == "2.0.0"