# 👩‍💻 CCRS Developer Guide

**Development, customization, and contribution guide for CCRS**

## 🎯 Development Setup

### Prerequisites

```bash
# Required tools
- Python 3.11+
- Docker & Docker Compose
- Git
- Claude Code CLI (for testing)

# Recommended tools
- VS Code or PyCharm
- Redis CLI (for debugging)
- curl (for API testing)
```

### Local Development Environment

```bash
# 1. Clone and setup
git clone <repo>
cd ccrs
chmod +x ccrs

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# 5. Verify installation
python -m pytest tests/ -v
```

### IDE Configuration

**VS Code Settings (.vscode/settings.json):**
```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "88"]
}
```

**PyCharm Configuration:**
- Set interpreter to `.venv/bin/python`
- Enable pytest as test runner
- Configure Black as code formatter
- Add run configurations for app.py, worker.py, cli.py

## 🏗️ Project Structure

### File Organization

```
ccrs/
├── Core Components
│   ├── app.py              # FastAPI application
│   ├── worker.py           # Background job processor
│   ├── cli.py              # Command-line interface
│   ├── models.py           # Pydantic data models
│   └── ccrs                # Bash CLI wrapper
│
├── Configuration
│   ├── requirements.txt    # Python dependencies
│   ├── docker-compose.yml  # Full deployment
│   └── docker-compose.hybrid.yml  # Hybrid deployment
│
├── Testing
│   ├── tests/
│   │   ├── conftest.py     # Test fixtures
│   │   ├── test_models.py  # Model validation tests
│   │   ├── test_api.py     # API endpoint tests
│   │   ├── test_worker.py  # Worker process tests
│   │   ├── test_cli.py     # CLI command tests
│   │   └── test_integration.py  # E2E tests
│   └── run_tests.py        # Test runner
│
├── Documentation
│   ├── README.md           # Project overview
│   ├── USER-GUIDE.md       # User documentation
│   ├── QUICK-START.md      # Quick setup guide
│   ├── COMMAND-REFERENCE.md # CLI reference
│   ├── ARCHITECTURE.md     # System design
│   ├── DEVELOPER.md        # This file
│   ├── MIGRATION-GUIDE.md  # Upgrade guide
│   └── DEPLOYMENT-GUIDE.md # Deployment options
│
└── Support Files
    ├── Dockerfile          # Container image
    ├── .gitignore          # Git ignore rules
    ├── run-worker-host.sh  # Worker startup script
    └── install.sh          # CLI installation script
```

### Code Organization Principles

**Separation of Concerns:**
- `models.py`: Data validation and serialization
- `app.py`: HTTP API and routing
- `worker.py`: Background processing
- `cli.py`: User interface

**Configuration Management:**
- Environment variables for runtime config
- Docker Compose for deployment config
- Command-line flags for user preferences

**Error Handling:**
- Comprehensive try/except blocks
- Graceful degradation on failures
- User-friendly error messages

## 🔧 Development Workflows

### Running Components Individually

**API Server (Development):**
```bash
# Terminal 1: Start Redis
docker run -p 6380:6379 redis:7-alpine  # Host port 6380 maps to container port 6379

# Terminal 2: Start API server
source .venv/bin/activate
export REDIS_HOST=localhost
export REDIS_PORT=6380
python app.py

# API available at http://localhost:8001
# API docs at http://localhost:8001/docs
```

**Worker Process (Development):**
```bash
# Terminal 3: Start worker
source .venv/bin/activate
export REDIS_HOST=localhost
export REDIS_PORT=6380
python -u worker.py

# Worker will process jobs from Redis queue
```

**CLI Testing:**
```bash
# Terminal 4: Test CLI
source .venv/bin/activate
export CCRS_URL=http://localhost:8001
python cli.py health
python cli.py chat "Hello Claude!" --wait
```

### Testing Workflows

**Run All Tests:**
```bash
# Comprehensive test suite
python run_tests.py all

# Quick tests (unit + API)
python run_tests.py fast

# Specific test categories
python run_tests.py unit
python run_tests.py api
python run_tests.py worker
python run_tests.py cli
python run_tests.py integration
```

**Run Tests with Coverage:**
```bash
# Generate coverage report
pytest tests/ --cov=. --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

**Manual Testing:**
```bash
# Test API directly
curl http://localhost:8001/health

# Test job submission
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "dev", "operation": "chat", "message": "test"}'

# Test Redis directly
redis-cli -p 6380 ping
redis-cli -p 6380 keys "ccrs*"
```

### Code Quality Workflows

**Code Formatting:**
```bash
# Format code with Black
black app.py worker.py cli.py models.py

# Check formatting
black --check .
```

**Linting:**
```bash
# Check with flake8
flake8 app.py worker.py cli.py models.py

# Type checking with mypy
mypy app.py worker.py cli.py models.py
```

**Pre-commit Hooks:**
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks (.pre-commit-config.yaml)
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

## 🔨 Customization Guide

### Adding New Operations

**Step 1: Update Data Models**
```python
# In models.py
class JobRequest(BaseModel):
    tenant_id: str
    operation: str  # Add your new operation here
    message: str
    timeout_seconds: Optional[int] = 300
    # Add operation-specific fields if needed
    analysis_type: Optional[str] = None  # Example for 'analyze' operation
```

**Step 2: Add Worker Handler**
```python
# In worker.py
def execute_claude_command(self, operation: str, message: str, timeout: int = 300):
    # ... existing operations ...

    elif operation == "analyze":
        # Custom analyze operation
        analysis_type = self.get_analysis_type(message)  # Custom logic
        cmd = ["claude", "--analyze", f"--type={analysis_type}", message]

    elif operation == "custom_op":
        # Your custom operation
        cmd = ["claude", "--custom", message]

    # ... rest of method ...
```

**Step 3: Add CLI Command**
```python
# In cli.py
@cli.command()
@click.argument('file_path')
@click.option('--analysis-type', default='general', help='Type of analysis')
@click.option('--tenant', default='demo', help='Tenant ID')
@click.option('--wait', is_flag=True, help='Wait for completion')
@click.option('--timeout', default=300, help='Timeout in seconds')
def analyze(file_path, analysis_type, tenant, wait, timeout):
    """Analyze a file with Claude"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        job = client.submit_job(
            tenant_id=tenant,
            operation="analyze",
            message=content,
            timeout_seconds=timeout
        )

        if job:
            click.echo(f"📋 Analysis job submitted: {job['job_id']}")
            if wait:
                result = poll_job_completion(job['job_id'], timeout)
                if result:
                    click.echo(f"✅ Analysis complete:\n{result['result']}")

    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}")
```

**Step 4: Add to CLI Wrapper**
```bash
# In ccrs script
analyze|a)
    shift
    run_cli analyze "$@"
    ;;
```

**Step 5: Update Documentation**
```bash
# Add to COMMAND-REFERENCE.md
| `analyze` | `a` | Analyze file with Claude | `./ccrs a file.py --wait` |

# Add to --help text
echo -e "  ${YELLOW}analyze${NC} <file>          Analyze file with Claude"
```

### Custom Backend Integration

**Create Backend Interface:**
```python
# backends.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BackendInterface(ABC):
    @abstractmethod
    def execute(self, operation: str, message: str, timeout: int) -> Dict[str, Any]:
        pass

class ClaudeCLIBackend(BackendInterface):
    def execute(self, operation: str, message: str, timeout: int) -> Dict[str, Any]:
        # Current Claude CLI implementation
        pass

class OpenAIBackend(BackendInterface):
    def execute(self, operation: str, message: str, timeout: int) -> Dict[str, Any]:
        # OpenAI API implementation
        import openai

        if operation == "chat":
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                timeout=timeout
            )
            return {
                "success": True,
                "result": response.choices[0].message.content
            }

class CustomAPIBackend(BackendInterface):
    def execute(self, operation: str, message: str, timeout: int) -> Dict[str, Any]:
        # Your custom API implementation
        pass
```

**Update Worker to Use Backends:**
```python
# In worker.py
from backends import ClaudeCLIBackend, OpenAIBackend

class CCRSWorker:
    def __init__(self):
        # ... existing init ...

        # Configure backend
        backend_type = os.getenv('CCRS_BACKEND', 'claude')
        if backend_type == 'claude':
            self.backend = ClaudeCLIBackend()
        elif backend_type == 'openai':
            self.backend = OpenAIBackend()
        else:
            raise ValueError(f"Unknown backend: {backend_type}")

    def execute_claude_command(self, operation: str, message: str, timeout: int = 300):
        """Execute command using configured backend"""
        return self.backend.execute(operation, message, timeout)
```

### Custom Authentication

**Add Authentication to API:**
```python
# auth.py
from fastapi import HTTPException, Header
import os

def verify_api_key(x_api_key: str = Header(None)):
    valid_api_key = os.getenv('CCRS_API_KEY')
    if not valid_api_key:
        return  # No auth required if not configured

    if not x_api_key or x_api_key != valid_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

# In app.py
from auth import verify_api_key

@app.post("/execute", response_model=JobResponse, dependencies=[Depends(verify_api_key)])
async def execute_job(request: JobRequest):
    # ... existing implementation ...
```

**Update CLI for Authentication:**
```python
# In cli.py
class CCRSClient:
    def __init__(self, base_url: str = None, api_key: str = None):
        self.base_url = base_url or os.getenv('CCRS_URL', 'http://localhost:8001')
        self.api_key = api_key or os.getenv('CCRS_API_KEY')

    def _get_headers(self):
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers

    def submit_job(self, **kwargs):
        response = requests.post(
            f"{self.base_url}/execute",
            json=kwargs,
            headers=self._get_headers(),
            timeout=30
        )
        # ... rest of method ...
```

### Custom Monitoring

**Add Prometheus Metrics:**
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time

# Metrics
job_counter = Counter('ccrs_jobs_total', 'Total jobs processed', ['tenant', 'operation', 'status'])
job_duration = Histogram('ccrs_job_duration_seconds', 'Job processing time', ['tenant', 'operation'])
queue_size = Gauge('ccrs_queue_size', 'Current queue size')
worker_health = Gauge('ccrs_worker_health', 'Worker health status')

def track_job_start(tenant: str, operation: str):
    return time.time()

def track_job_complete(tenant: str, operation: str, status: str, start_time: float):
    duration = time.time() - start_time
    job_counter.labels(tenant=tenant, operation=operation, status=status).inc()
    job_duration.labels(tenant=tenant, operation=operation).observe(duration)

# In app.py
from metrics import generate_latest, queue_size

@app.get("/metrics")
def get_metrics():
    return Response(generate_latest(), media_type="text/plain")

# Update queue size periodically
def update_queue_size():
    size = redis_client.llen("ccrs:job_queue")
    queue_size.set(size)
```

## 🧪 Testing Guide

### Test Architecture

**Test Categories:**
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **API Tests**: HTTP endpoint testing
- **CLI Tests**: Command-line interface testing
- **E2E Tests**: Full workflow testing

**Test Fixtures:**
```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from fakeredis import FakeRedis

@pytest.fixture
def api_client():
    from app import app
    return TestClient(app)

@pytest.fixture
def fake_redis():
    return FakeRedis()

@pytest.fixture
def mock_worker():
    from worker import CCRSWorker
    worker = CCRSWorker()
    worker.redis_client = fake_redis()
    return worker

@pytest.fixture
def sample_job():
    return {
        "job_id": "test-123",
        "tenant_id": "test",
        "operation": "chat",
        "message": "Hello test",
        "status": "pending"
    }
```

### Writing Tests

**API Endpoint Test:**
```python
# test_api.py
def test_health_endpoint(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_execute_job(api_client):
    job_data = {
        "tenant_id": "test",
        "operation": "chat",
        "message": "test message",
        "timeout_seconds": 300
    }
    response = api_client.post("/execute", json=job_data)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["job_id"].startswith("ccrs-")
```

**Worker Process Test:**
```python
# test_worker.py
def test_job_processing(mock_worker, sample_job):
    # Add job to queue
    mock_worker.redis_client.lpush("ccrs:job_queue", sample_job["job_id"])
    mock_worker.redis_client.set(f"job:{sample_job['job_id']}", json.dumps(sample_job))

    # Process job
    mock_worker.process_job(sample_job["job_id"])

    # Verify result
    result = mock_worker.redis_client.get(f"job:{sample_job['job_id']}")
    job_data = json.loads(result)
    assert job_data["status"] == "completed"
```

**CLI Command Test:**
```python
# test_cli.py
from click.testing import CliRunner
from cli import cli

def test_health_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['health'])
    assert result.exit_code == 0
    assert "healthy" in result.output.lower()

def test_chat_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['chat', 'test message', '--tenant', 'test'])
    assert result.exit_code == 0
    assert "job submitted" in result.output.lower()
```

### Debugging Tests

**Run Single Test:**
```bash
# Run specific test
pytest tests/test_api.py::test_health_endpoint -v

# Run test with debugging
pytest tests/test_api.py::test_health_endpoint -v -s --pdb

# Run test with custom markers
pytest -m "unit" -v
pytest -m "integration" -v
```

**Test Debugging Tips:**
```python
# Add debugging to tests
def test_complex_scenario(api_client, caplog):
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Your test code here

    # Check logs
    assert "expected log message" in caplog.text
```

## 🚀 Deployment Customization

### Custom Docker Images

**Multi-stage Dockerfile:**
```dockerfile
# Build stage
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY app.py worker.py models.py ./

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000
CMD ["python", "app.py"]
```

**Custom Compose Configuration:**
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.production
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    environment:
      - REDIS_HOST=redis
      - LOG_LEVEL=INFO
      - WORKERS=4
    networks:
      - ccrs-network

  redis:
    image: redis:7-alpine
    deploy:
      resources:
        limits:
          memory: 256M
    volumes:
      - redis-data:/data
    command: redis-server --save 60 1 --loglevel warning
    networks:
      - ccrs-network

volumes:
  redis-data:

networks:
  ccrs-network:
    driver: bridge
```

### Environment-Specific Configurations

**Development Environment:**
```yaml
# .env.development
CCRS_URL=http://localhost:8001
CCRS_TENANT=dev
LOG_LEVEL=DEBUG
REDIS_HOST=localhost
REDIS_PORT=6380
```

**Staging Environment:**
```yaml
# .env.staging
CCRS_URL=https://staging-ccrs.company.com
CCRS_TENANT=staging
LOG_LEVEL=INFO
REDIS_HOST=staging-redis
REDIS_PORT=6380
API_KEY_REQUIRED=true
```

**Production Environment:**
```yaml
# .env.production
CCRS_URL=https://ccrs.company.com
CCRS_TENANT=production
LOG_LEVEL=WARNING
REDIS_HOST=prod-redis-cluster
REDIS_PORT=6380
API_KEY_REQUIRED=true
METRICS_ENABLED=true
```

## 🐛 Debugging & Troubleshooting

### Common Development Issues

**Port Conflicts:**
```bash
# Check what's using port
lsof -i :8001
lsof -i :6380

# Kill processes
kill -9 $(lsof -t -i:8001)
kill -9 $(lsof -t -i:6380)
```

**Redis Connection Issues:**
```bash
# Test Redis connection
redis-cli -h localhost -p 6380 ping

# Monitor Redis activity
redis-cli -h localhost -p 6380 monitor

# Check Redis logs
docker logs ccrs-redis
```

**Worker Process Issues:**
```bash
# Check worker logs
tail -f worker.log

# Test Claude CLI directly
claude "test message"

# Check worker environment
python -c "
import os
print('REDIS_HOST:', os.getenv('REDIS_HOST'))
print('REDIS_PORT:', os.getenv('REDIS_PORT'))
"
```

**API Issues:**
```bash
# Test API directly
curl -v http://localhost:8001/health

# Check API logs
docker logs ccrs-api

# Test with verbose curl
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"tenant_id":"test","operation":"chat","message":"test"}' \
  -v
```

### Debugging Tools

**Redis Debugging:**
```bash
# Connect to Redis
redis-cli -p 6380

# Useful Redis commands
KEYS *                    # List all keys
LLEN ccrs:job_queue      # Check queue length
LRANGE ccrs:job_queue 0 -1  # List all jobs in queue
GET job:ccrs-abc123      # Get specific job data
FLUSHALL                 # Clear all data (careful!)
```

**Python Debugging:**
```python
# Add debugging to code
import logging
logging.basicConfig(level=logging.DEBUG)

import pdb; pdb.set_trace()  # Breakpoint

# Add extensive logging
logger = logging.getLogger(__name__)
logger.debug(f"Processing job: {job_id}")
logger.info(f"Job completed: {job_id}")
logger.error(f"Job failed: {job_id}, error: {error}")
```

**Performance Profiling:**
```python
# Profile worker performance
import cProfile
import pstats

def profile_worker():
    profiler = cProfile.Profile()
    profiler.enable()

    # Run worker code
    worker.process_job(job_id)

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
```

## 📝 Contributing Guidelines

### Code Style

**Python Code Style:**
- Use Black for formatting (line length: 88)
- Follow PEP 8 naming conventions
- Use type hints where possible
- Write docstrings for public methods

**Example:**
```python
from typing import Optional, Dict, Any

def process_job(self, job_id: str, timeout: Optional[int] = None) -> Dict[str, Any]:
    """
    Process a job from the queue.

    Args:
        job_id: Unique identifier for the job
        timeout: Optional timeout override

    Returns:
        Dict containing job result and status

    Raises:
        JobNotFoundError: If job ID doesn't exist
        ProcessingError: If job processing fails
    """
    # Implementation here
```

### Pull Request Process

**Before Submitting:**
1. Run all tests: `python run_tests.py all`
2. Check code formatting: `black --check .`
3. Run linting: `flake8 .`
4. Update documentation if needed
5. Add/update tests for new features

**PR Description Template:**
```markdown
## Summary
Brief description of changes

## Changes Made
- [ ] Added new operation: `analyze`
- [ ] Updated CLI with new command
- [ ] Added tests for new functionality
- [ ] Updated documentation

## Testing
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Manual testing completed

## Documentation
- [ ] Updated COMMAND-REFERENCE.md
- [ ] Updated README.md if needed
- [ ] Added inline code comments
```

### Release Process

**Version Numbering:**
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update version in multiple files:
  - `ccrs` script: `show_version()`
  - `models.py`: version constant
  - `README.md`: version history

**Release Checklist:**
1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Test deployment scenarios
5. Update documentation
6. Create git tag: `git tag v3.1.0`
7. Push tag: `git push origin v3.1.0`

---

**Happy developing! 🚀**

**Need help?** Check the [Architecture Guide](ARCHITECTURE.md) for system design details, or the [User Guide](USER-GUIDE.md) for usage patterns.