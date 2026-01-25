"""
Test CCRS Worker Functionality
"""
import pytest
import json
from unittest.mock import patch, Mock, call

class TestWorkerInitialization:
    """Test worker initialization."""

    @pytest.mark.worker
    def test_worker_init_success(self, worker_instance):
        """Test successful worker initialization."""
        worker, mock_redis = worker_instance

        assert worker.redis_client == mock_redis
        assert worker.queue_name == "ccrs:jobs"
        assert worker.polling_interval == 1
        assert worker.running is False

    @pytest.mark.worker
    @patch('worker.redis.Redis')
    def test_worker_init_redis_failure(self, mock_redis_class):
        """Test worker initialization when Redis fails."""
        mock_redis_class.side_effect = Exception("Redis connection failed")

        from worker import CCRSWorker
        worker = CCRSWorker()

        assert worker.redis_client is None

class TestJobProcessing:
    """Test job processing functionality."""

    @pytest.mark.worker
    def test_process_job_chat_success(self, worker_instance, sample_job_data):
        """Test successful chat job processing."""
        worker, mock_redis = worker_instance

        # Mock successful command execution
        with patch.object(worker, 'execute_claude_command') as mock_execute:
            mock_execute.return_value = "Mock Claude response"

            worker.process_job(sample_job_data)

            # Verify command was called correctly
            mock_execute.assert_called_once_with("chat", "Test message", 300)

            # Verify Redis updates
            assert mock_redis.hset.call_count >= 2  # Started and completed updates

            # Check that job status was updated to completed
            completed_calls = [call for call in mock_redis.hset.call_args_list
                             if len(call[0]) > 2 and call[0][2] == "completed"]
            assert len(completed_calls) > 0

    @pytest.mark.worker
    def test_process_job_command_success(self, worker_instance):
        """Test successful command job processing."""
        worker, mock_redis = worker_instance

        job_data = {
            "job_id": "ccrs-test123",
            "operation": "command",
            "message": "/help",
            "timeout_seconds": "300"
        }

        with patch.object(worker, 'execute_claude_command') as mock_execute:
            mock_execute.return_value = "Mock command response"

            worker.process_job(job_data)

            mock_execute.assert_called_once_with("command", "/help", 300)

    @pytest.mark.worker
    def test_process_job_execution_failure(self, worker_instance, sample_job_data):
        """Test job processing when command execution fails."""
        worker, mock_redis = worker_instance

        with patch.object(worker, 'execute_claude_command') as mock_execute:
            mock_execute.side_effect = Exception("Command execution failed")

            worker.process_job(sample_job_data)

            # Verify Redis was updated with error status
            failed_calls = [call for call in mock_redis.hset.call_args_list
                          if len(call[0]) > 2 and call[0][2] == "failed"]
            assert len(failed_calls) > 0

class TestClaudeCommandExecution:
    """Test Claude command execution."""

    @pytest.mark.worker
    @patch('worker.subprocess.run')
    def test_execute_claude_chat(self, mock_subprocess, worker_instance):
        """Test Claude chat command execution."""
        worker, _ = worker_instance

        # Mock successful subprocess execution
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Claude response"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = worker.execute_claude_command("chat", "Hello", 300)

        assert "Claude response" in result
        mock_subprocess.assert_called_once()

    @pytest.mark.worker
    @patch('worker.subprocess.run')
    def test_execute_claude_command(self, mock_subprocess, worker_instance):
        """Test Claude command execution."""
        worker, _ = worker_instance

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Command output"
        mock_result.stderr = ""
        mock_subprocess.return_value = mock_result

        result = worker.execute_claude_command("command", "/help", 300)

        assert "Command output" in result

    @pytest.mark.worker
    @patch('worker.subprocess.run')
    def test_execute_claude_failure(self, mock_subprocess, worker_instance):
        """Test Claude command execution failure."""
        worker, _ = worker_instance

        # Mock failed subprocess execution
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Command failed"
        mock_subprocess.return_value = mock_result

        with pytest.raises(Exception) as exc_info:
            worker.execute_claude_command("chat", "Hello", 300)

        assert "Command failed" in str(exc_info.value)

    @pytest.mark.worker
    @patch('worker.subprocess.run')
    def test_execute_claude_timeout(self, mock_subprocess, worker_instance):
        """Test Claude command timeout."""
        worker, _ = worker_instance

        # Mock subprocess timeout
        from subprocess import TimeoutExpired
        mock_subprocess.side_effect = TimeoutExpired("claude", 5)

        with pytest.raises(Exception) as exc_info:
            worker.execute_claude_command("chat", "Hello", 5)

        assert "timeout" in str(exc_info.value).lower()

class TestJobQueueOperations:
    """Test job queue operations."""

    @pytest.mark.worker
    def test_get_next_job_available(self, worker_instance, sample_job_data):
        """Test getting next job when job is available."""
        worker, mock_redis = worker_instance

        # Mock Redis returning a job
        mock_redis.brpop.return_value = ("ccrs:jobs", json.dumps(sample_job_data))

        job = worker.get_next_job()

        assert job == sample_job_data
        mock_redis.brpop.assert_called_once_with("ccrs:jobs", timeout=1)

    @pytest.mark.worker
    def test_get_next_job_none_available(self, worker_instance):
        """Test getting next job when no jobs available."""
        worker, mock_redis = worker_instance

        # Mock Redis returning None (timeout)
        mock_redis.brpop.return_value = None

        job = worker.get_next_job()

        assert job is None

    @pytest.mark.worker
    def test_get_next_job_invalid_json(self, worker_instance):
        """Test getting next job with invalid JSON."""
        worker, mock_redis = worker_instance

        # Mock Redis returning invalid JSON
        mock_redis.brpop.return_value = ("ccrs:jobs", "invalid json")

        job = worker.get_next_job()

        assert job is None  # Should handle JSON parsing errors gracefully

    @pytest.mark.worker
    def test_update_job_status(self, worker_instance):
        """Test updating job status in Redis."""
        worker, mock_redis = worker_instance

        worker.update_job_status("ccrs-test123", "running", started_at="2026-01-25T13:30:00Z")

        mock_redis.hset.assert_called_with(
            "job:ccrs-test123",
            "status", "running",
            "started_at", "2026-01-25T13:30:00Z"
        )

    @pytest.mark.worker
    def test_update_job_with_result(self, worker_instance):
        """Test updating job with result."""
        worker, mock_redis = worker_instance

        worker.update_job_status(
            "ccrs-test123",
            "completed",
            completed_at="2026-01-25T13:30:05Z",
            result="Test result"
        )

        mock_redis.hset.assert_called_with(
            "job:ccrs-test123",
            "status", "completed",
            "completed_at", "2026-01-25T13:30:05Z",
            "result", "Test result"
        )

    @pytest.mark.worker
    def test_update_job_with_error(self, worker_instance):
        """Test updating job with error."""
        worker, mock_redis = worker_instance

        worker.update_job_status(
            "ccrs-test123",
            "failed",
            completed_at="2026-01-25T13:30:02Z",
            error="Test error"
        )

        mock_redis.hset.assert_called_with(
            "job:ccrs-test123",
            "status", "failed",
            "completed_at", "2026-01-25T13:30:02Z",
            "error", "Test error"
        )