"""
Test CCRS-2 CLI Functionality
"""
import pytest
import json
from unittest.mock import patch, Mock
from click.testing import CliRunner
from cli import cli, CCRS2Client, client

class TestCCRS2Client:
    """Test CCRS2Client class."""

    @pytest.mark.cli
    def test_client_initialization_default(self):
        """Test client initialization with defaults."""
        client = CCRS2Client()
        assert client.base_url == "http://localhost:8001"

    @pytest.mark.cli
    def test_client_initialization_custom(self):
        """Test client initialization with custom URL."""
        client = CCRS2Client("http://custom:9000")
        assert client.base_url == "http://custom:9000"

    @pytest.mark.cli
    @patch.dict('os.environ', {'CCRS2_URL': 'http://env-url:8080'})
    def test_client_initialization_env_var(self):
        """Test client initialization with environment variable."""
        client = CCRS2Client()
        assert client.base_url == "http://env-url:8080"

class TestJobSubmission:
    """Test job submission functionality."""

    @pytest.mark.cli
    @patch('cli.requests.post')
    def test_submit_job_success(self, mock_post, cli_client):
        """Test successful job submission."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "job_id": "ccrs2-test123",
            "status": "accepted",
            "message": "Job submitted successfully"
        }
        mock_post.return_value = mock_response

        result = cli_client.submit_job("demo", "chat", "Test message", 300)

        assert result is not None
        assert result["job_id"] == "ccrs2-test123"
        assert result["status"] == "accepted"

        # Verify request
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]['json']['tenant_id'] == "demo"
        assert call_args[1]['json']['operation'] == "chat"
        assert call_args[1]['json']['message'] == "Test message"

    @pytest.mark.cli
    @patch('cli.requests.post')
    def test_submit_job_http_error(self, mock_post, cli_client):
        """Test job submission with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        result = cli_client.submit_job("demo", "chat", "Test message")

        assert result is None

    @pytest.mark.cli
    @patch('cli.requests.post')
    def test_submit_job_connection_error(self, mock_post, cli_client):
        """Test job submission with connection error."""
        from requests.exceptions import RequestException
        mock_post.side_effect = RequestException("Connection failed")

        result = cli_client.submit_job("demo", "chat", "Test message")

        assert result is None

class TestJobStatus:
    """Test job status functionality."""

    @pytest.mark.cli
    @patch('cli.requests.get')
    def test_get_job_status_success(self, mock_get, cli_client, sample_completed_job):
        """Test successful job status retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_completed_job
        mock_get.return_value = mock_response

        result = cli_client.get_job_status("ccrs2-test123")

        assert result is not None
        assert result["job_id"] == "ccrs2-test123"
        assert result["status"] == "completed"

    @pytest.mark.cli
    @patch('cli.requests.get')
    def test_get_job_status_not_found(self, mock_get, cli_client):
        """Test job status retrieval for non-existent job."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = cli_client.get_job_status("ccrs2-nonexistent")

        assert result is None

class TestHealthCheck:
    """Test health check functionality."""

    @pytest.mark.cli
    @patch('cli.requests.get')
    def test_health_check_success(self, mock_get, cli_client):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": "2026-01-25T13:30:00Z"
        }
        mock_get.return_value = mock_response

        result = cli_client.health_check()

        assert result is not None
        assert result["status"] == "healthy"
        assert result["version"] == "2.0.0"

    @pytest.mark.cli
    @patch('cli.requests.get')
    def test_health_check_failure(self, mock_get, cli_client):
        """Test health check failure."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        result = cli_client.health_check()

        assert result is None

class TestChatCommand:
    """Test chat CLI command."""

    @pytest.mark.cli
    @patch.object(client, 'submit_job')
    def test_chat_command_without_wait(self, mock_submit):
        """Test chat command without waiting."""
        mock_submit.return_value = {"job_id": "ccrs2-test123", "status": "accepted"}

        runner = CliRunner()
        result = runner.invoke(cli, ['chat', 'Hello Claude'])

        assert result.exit_code == 0
        assert "Job submitted: ccrs2-test123" in result.output
        mock_submit.assert_called_once_with(
            tenant_id="demo",
            operation="chat",
            message="Hello Claude",
            timeout_seconds=300
        )

    @pytest.mark.cli
    @patch.object(client, 'get_job_status')
    @patch.object(client, 'submit_job')
    def test_chat_command_with_wait_success(self, mock_submit, mock_status):
        """Test chat command with waiting for completion."""
        mock_submit.return_value = {"job_id": "ccrs2-test123", "status": "accepted"}
        mock_status.return_value = {
            "job_id": "ccrs2-test123",
            "status": "completed",
            "result": "Mock Claude response"
        }

        runner = CliRunner()
        result = runner.invoke(cli, ['chat', 'Hello Claude', '--wait'])

        assert result.exit_code == 0
        assert "Response from Claude:" in result.output
        assert "Mock Claude response" in result.output

    @pytest.mark.cli
    @patch.object(client, 'get_job_status')
    @patch.object(client, 'submit_job')
    def test_chat_command_with_wait_failed(self, mock_submit, mock_status):
        """Test chat command with job failure."""
        mock_submit.return_value = {"job_id": "ccrs2-test123", "status": "accepted"}
        mock_status.return_value = {
            "job_id": "ccrs2-test123",
            "status": "failed",
            "error": "Command execution failed"
        }

        runner = CliRunner()
        result = runner.invoke(cli, ['chat', 'Hello Claude', '--wait'])

        assert result.exit_code == 0
        assert "Job failed:" in result.output
        assert "Command execution failed" in result.output

    @pytest.mark.cli
    @patch.object(client, 'submit_job')
    def test_chat_command_submission_failure(self, mock_submit):
        """Test chat command when job submission fails."""
        mock_submit.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, ['chat', 'Hello Claude'])

        assert result.exit_code == 0
        # Should handle gracefully and not crash

class TestCommandCommand:
    """Test command CLI command."""

    @pytest.mark.cli
    @patch.object(client, 'submit_job')
    def test_command_execution(self, mock_submit):
        """Test command execution."""
        mock_submit.return_value = {"job_id": "ccrs2-test123", "status": "accepted"}

        runner = CliRunner()
        result = runner.invoke(cli, ['command', '/help'])

        assert result.exit_code == 0
        assert "Job submitted: ccrs2-test123" in result.output
        mock_submit.assert_called_once_with(
            tenant_id="demo",
            operation="command",
            message="/help",
            timeout_seconds=300
        )

class TestStatusCommand:
    """Test status CLI command."""

    @pytest.mark.cli
    @patch.object(client, 'get_job_status')
    def test_status_command_completed_job(self, mock_status, sample_completed_job):
        """Test status command for completed job."""
        mock_status.return_value = sample_completed_job

        runner = CliRunner()
        result = runner.invoke(cli, ['status', 'ccrs2-test123'])

        assert result.exit_code == 0
        assert "Job Details:" in result.output
        assert "ID: ccrs2-test123" in result.output
        assert "Status: completed" in result.output
        assert "Result:" in result.output

    @pytest.mark.cli
    @patch.object(client, 'get_job_status')
    def test_status_command_job_not_found(self, mock_status):
        """Test status command for non-existent job."""
        mock_status.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, ['status', 'ccrs2-nonexistent'])

        assert result.exit_code == 0
        # Should handle gracefully

class TestHealthCommand:
    """Test health CLI command."""

    @pytest.mark.cli
    @patch.object(client, 'health_check')
    def test_health_command_healthy(self, mock_health):
        """Test health command when service is healthy."""
        mock_health.return_value = {
            "status": "healthy",
            "version": "2.0.0",
            "timestamp": "2026-01-25T13:30:00Z"
        }

        runner = CliRunner()
        result = runner.invoke(cli, ['health'])

        assert result.exit_code == 0
        assert "CCRS-2 is healthy and ready!" in result.output

    @pytest.mark.cli
    @patch.object(client, 'health_check')
    def test_health_command_unhealthy(self, mock_health):
        """Test health command when service is unhealthy."""
        mock_health.return_value = None

        runner = CliRunner()
        result = runner.invoke(cli, ['health'])

        assert result.exit_code == 0
        # Should handle gracefully

class TestVersionCommand:
    """Test version CLI command."""

    @pytest.mark.cli
    def test_version_command(self):
        """Test version command."""
        runner = CliRunner()
        result = runner.invoke(cli, ['version'])

        assert result.exit_code == 0
        assert "CCRS-2 CLI v2.0.0" in result.output