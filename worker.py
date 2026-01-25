"""
CCRS Production Worker
Processes jobs from Redis queue with real Claude CLI integration
"""
import json
import subprocess
import redis
import time
import os
import shutil
from datetime import datetime
from typing import Dict, Any


class CCRSWorker:
    def __init__(self):
        """Initialize worker with Redis connection and Claude CLI verification"""
        # Check Claude CLI availability
        claude_path = shutil.which("claude")
        if not claude_path:
            print("⚠️  Warning: Claude CLI not found in PATH")
            print("   Install from: https://claude.ai/claude-code")
            print("   Falling back to mock mode...")
            self.mock_mode = True
        else:
            print(f"✅ Claude CLI found: {claude_path}")
            self.mock_mode = False

        try:
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6380)),
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()
            print("✅ Worker Redis connection established")
        except Exception as e:
            print(f"❌ Worker Redis connection failed: {e}")
            raise

    def get_current_time(self) -> str:
        """Get current time as ISO string"""
        return datetime.utcnow().isoformat() + "Z"

    def update_job_status(self, job_id: str, updates: Dict[str, Any]):
        """Update job status in Redis"""
        try:
            # Get current job data
            job_data_raw = self.redis_client.get(f"job:{job_id}")
            if not job_data_raw:
                print(f"❌ Job {job_id} not found for update")
                return

            job_data = json.loads(job_data_raw)
            job_data.update(updates)

            # Save updated job data
            self.redis_client.setex(f"job:{job_id}", 3600, json.dumps(job_data))
            print(f"📝 Job {job_id} updated: {updates.get('status', 'unknown')}")

        except Exception as e:
            print(f"❌ Failed to update job {job_id}: {e}")

    def execute_claude_command(self, operation: str, message: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute Claude CLI command and return result"""
        try:
            if self.mock_mode:
                # Fallback to mock mode if Claude CLI not available
                if operation == "chat":
                    cmd = ["echo", f"Mock Claude response to: {message}"]
                elif operation == "command":
                    cmd = ["echo", f"Mock command execution: {message}"]
                else:
                    return {
                        "success": False,
                        "error": f"Unsupported operation: {operation}"
                    }
                print(f"🎭 Mock mode: {' '.join(cmd)}")

            else:
                # Real Claude CLI integration
                if operation == "chat":
                    # Claude chat command
                    cmd = ["claude", "--print", "--output-format", "text", message]

                elif operation == "command":
                    # Direct Claude command (e.g., "/help", "/status")
                    cmd = ["claude", message]

                else:
                    return {
                        "success": False,
                        "error": f"Unsupported operation: {operation}"
                    }

                print(f"🚀 Executing Claude: {operation} -> {message[:50]}...")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ.copy()  # Pass current environment to subprocess
            )

            if result.returncode == 0:
                return {
                    "success": True,
                    "result": result.stdout.strip()
                }
            else:
                error_msg = result.stderr.strip() or "Command failed with no error output"
                return {
                    "success": False,
                    "error": error_msg
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Claude command timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }

    def process_job(self, job_id: str):
        """Process a single job"""
        try:
            # Get job data
            job_data_raw = self.redis_client.get(f"job:{job_id}")
            if not job_data_raw:
                print(f"❌ Job {job_id} not found")
                return

            job_data = json.loads(job_data_raw)
            print(f"🏃 Processing job {job_id}: {job_data['operation']}")

            # Update status to running
            self.update_job_status(job_id, {
                "status": "running",
                "started_at": self.get_current_time()
            })

            # Execute the operation
            result = self.execute_claude_command(
                operation=job_data["operation"],
                message=job_data["message"],
                timeout=job_data.get("timeout_seconds", 300)
            )

            # Update with final result
            if result["success"]:
                self.update_job_status(job_id, {
                    "status": "completed",
                    "completed_at": self.get_current_time(),
                    "result": result["result"]
                })
                print(f"✅ Job {job_id} completed successfully")
            else:
                self.update_job_status(job_id, {
                    "status": "failed",
                    "completed_at": self.get_current_time(),
                    "error": result["error"]
                })
                print(f"❌ Job {job_id} failed: {result['error']}")

        except Exception as e:
            print(f"💥 Critical error processing job {job_id}: {e}")
            self.update_job_status(job_id, {
                "status": "failed",
                "completed_at": self.get_current_time(),
                "error": f"Worker error: {str(e)}"
            })

    def run(self):
        """Main worker loop"""
        print("🚀 CCRS Worker starting...")
        if self.mock_mode:
            print("🎭 Running in MOCK mode (Claude CLI not found)")
        else:
            print("🎯 Running in PRODUCTION mode (Real Claude integration)")
        print("📋 Waiting for jobs...")

        while True:
            try:
                # Blocking pop from job queue (timeout 1 second)
                result = self.redis_client.brpop("ccrs:job_queue", timeout=1)

                if result:
                    queue_name, job_id = result
                    print(f"📨 Received job: {job_id}")
                    self.process_job(job_id)

            except KeyboardInterrupt:
                print("\n🛑 Worker stopping...")
                break
            except Exception as e:
                print(f"💥 Worker error: {e}")
                time.sleep(5)  # Wait before retrying


if __name__ == "__main__":
    worker = CCRSWorker()
    worker.run()