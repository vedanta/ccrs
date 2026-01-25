"""
CCRS Simple CLI
Essential commands for Claude Code routing
"""
import click
import requests
import json
import time
import os
from typing import Optional


class CCRSClient:
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv('CCRS_URL', 'http://localhost:8001')

    def submit_job(self, tenant_id: str, operation: str, message: str, timeout_seconds: int = 300) -> Optional[dict]:
        """Submit a job to CCRS"""
        try:
            response = requests.post(
                f"{self.base_url}/execute",
                json={
                    "tenant_id": tenant_id,
                    "operation": operation,
                    "message": message,
                    "timeout_seconds": timeout_seconds
                },
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                click.echo(f"❌ Error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            click.echo(f"❌ Request failed: {e}")
            return None

    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get job status"""
        try:
            response = requests.get(f"{self.base_url}/jobs/{job_id}", timeout=10)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                click.echo(f"❌ Job {job_id} not found")
                return None
            else:
                click.echo(f"❌ Error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            click.echo(f"❌ Request failed: {e}")
            return None

    def health_check(self) -> Optional[dict]:
        """Check CCRS health"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                click.echo(f"❌ Health check failed: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            click.echo(f"❌ Health check failed: {e}")
            return None


# Initialize client
client = CCRSClient()


@click.group()
def cli():
    """
    CCRS CLI - Simple Claude Code Routing Service

    Examples:
      ccrs chat "Hello Claude!"
      ccrs chat "Explain Python async" --wait
      ccrs status ccrs-abc12345
      ccrs health
    """
    pass


@cli.command()
@click.argument('message')
@click.option('--tenant', default='demo', help='Tenant ID (default: demo)')
@click.option('--wait', is_flag=True, help='Wait for job completion')
@click.option('--timeout', default=300, help='Timeout in seconds (default: 300)')
def chat(message, tenant, wait, timeout):
    """Send a chat message to Claude"""

    click.echo(f"💬 Sending message to Claude...")

    # Submit job
    job = client.submit_job(
        tenant_id=tenant,
        operation="chat",
        message=message,
        timeout_seconds=timeout
    )

    if not job:
        return

    click.echo(f"📋 Job submitted: {job['job_id']}")

    if wait:
        click.echo("⏳ Waiting for response...")

        # Poll for completion
        max_polls = timeout // 2  # Poll every 2 seconds
        polls = 0

        while polls < max_polls:
            status = client.get_job_status(job['job_id'])

            if not status:
                return

            if status['status'] == 'completed':
                click.echo(f"\n✅ Response from Claude:")
                click.echo(f"{status['result']}")
                return

            elif status['status'] == 'failed':
                click.echo(f"\n❌ Job failed:")
                click.echo(f"{status.get('error', 'Unknown error')}")
                return

            elif status['status'] == 'running':
                click.echo("🏃 Job running...")

            time.sleep(2)
            polls += 1

        click.echo(f"⏰ Timeout after {timeout} seconds. Check status with: ccrs status {job['job_id']}")


@cli.command()
@click.argument('message')
@click.option('--tenant', default='demo', help='Tenant ID (default: demo)')
@click.option('--wait', is_flag=True, help='Wait for job completion')
@click.option('--timeout', default=300, help='Timeout in seconds (default: 300)')
def command(message, tenant, wait, timeout):
    """Execute a Claude CLI command"""

    click.echo(f"⚡ Executing Claude command...")

    # Submit job
    job = client.submit_job(
        tenant_id=tenant,
        operation="command",
        message=message,
        timeout_seconds=timeout
    )

    if not job:
        return

    click.echo(f"📋 Job submitted: {job['job_id']}")

    if wait:
        click.echo("⏳ Waiting for completion...")

        # Poll for completion (same logic as chat)
        max_polls = timeout // 2
        polls = 0

        while polls < max_polls:
            status = client.get_job_status(job['job_id'])

            if not status:
                return

            if status['status'] == 'completed':
                click.echo(f"\n✅ Command result:")
                click.echo(f"{status['result']}")
                return

            elif status['status'] == 'failed':
                click.echo(f"\n❌ Command failed:")
                click.echo(f"{status.get('error', 'Unknown error')}")
                return

            time.sleep(2)
            polls += 1

        click.echo(f"⏰ Timeout after {timeout} seconds. Check status with: ccrs status {job['job_id']}")


@cli.command()
@click.argument('job_id')
def status(job_id):
    """Check job status"""

    click.echo(f"📊 Checking job status: {job_id}")

    status = client.get_job_status(job_id)

    if not status:
        return

    # Display status in a nice format
    click.echo(f"\n📋 Job Details:")
    click.echo(f"  ID: {status['job_id']}")
    click.echo(f"  Tenant: {status['tenant_id']}")
    click.echo(f"  Operation: {status['operation']}")
    click.echo(f"  Status: {status['status']}")
    click.echo(f"  Created: {status['created_at']}")

    if status.get('started_at'):
        click.echo(f"  Started: {status['started_at']}")

    if status.get('completed_at'):
        click.echo(f"  Completed: {status['completed_at']}")

    if status.get('result'):
        click.echo(f"\n✅ Result:")
        click.echo(f"{status['result']}")

    if status.get('error'):
        click.echo(f"\n❌ Error:")
        click.echo(f"{status['error']}")


@cli.command()
def health():
    """Check CCRS service health"""

    click.echo("🏥 Checking CCRS health...")

    health = client.health_check()

    if not health:
        return

    click.echo(f"\n📊 Service Status:")
    click.echo(f"  Status: {health['status']}")
    click.echo(f"  Version: {health['version']}")
    click.echo(f"  Timestamp: {health['timestamp']}")

    if health['status'] == 'healthy':
        click.echo("✅ CCRS is healthy and ready!")
    else:
        click.echo("⚠️  CCRS may have issues")


@cli.command()
def version():
    """Show CLI version"""
    click.echo("CCRS CLI v3.0.0")


if __name__ == '__main__':
    cli()