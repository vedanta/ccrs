# CCRS-2 - Lean Claude Code Routing Service

> Simple, effective, and working Claude Code routing microservice

## 📚 Documentation

- **[📖 User Guide](USER-GUIDE.md)** - Complete getting started guide
- **[⚡ Quick Start](QUICK-START.md)** - Get running in 60 seconds
- **[📋 Command Reference](COMMAND-REFERENCE.md)** - All commands and options
- **[🧪 Testing Guide](README.md#-testing)** - How to run the test suite

## ✨ Features

- **Simple Architecture** - Single FastAPI app, Redis queue, worker process
- **Essential Operations** - Chat, command execution (extensible)
- **Multi-Tenant Support** - Basic tenant isolation
- **Professional CLI** - Easy-to-use command-line interface
- **Docker Ready** - Complete containerized deployment
- **Proven Stack** - FastAPI + Redis + Python (battle-tested)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Redis (or Docker Compose)
- Git

### Option 1: Docker Compose (Recommended)

```bash
# Clone and start
git clone <repo>
cd ccrs2
docker-compose up -d

# Check health
curl http://localhost:8000/health

# Use CLI
ccrs2 chat "Hello Claude!" --wait
```

### Option 2: Bash CLI Wrapper (Easy)

```bash
# Clone and start
git clone <repo>
cd ccrs2
chmod +x ccrs2

# Start services
ccrs2 up

# Check health
ccrs2 health

# Use CLI
ccrs2 chat "Hello Claude!" --wait
```

### Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (separate terminal)
redis-server

# Start API server (separate terminal)
python app.py

# Start worker (separate terminal)
python worker.py

# Use CLI
python cli.py chat "Hello Claude!" --wait
```

## 📋 CLI Usage

### Option 1: Bash Wrapper (Recommended)

```bash
# Chat with Claude
ccrs2 chat "Explain async Python" --wait

# Execute Claude command
ccrs2 command "/help" --wait

# Check job status
ccrs2 status ccrs2-abc12345

# Health check
ccrs2 health

# Show version
ccrs2 version

# Docker shortcuts
ccrs2 up          # Start services
ccrs2 down        # Stop services
ccrs2 ps          # Service status
ccrs2 logs        # View logs
```

### Option 2: Direct Python CLI

```bash
# Chat with Claude
python cli.py chat "Explain async Python" --wait

# Execute Claude command
python cli.py command "/help" --wait

# Check job status
python cli.py status ccrs2-abc12345

# Health check
python cli.py health

# Show version
python cli.py version
```

## 🏗️ Architecture

```
CLI → HTTP Request → FastAPI → Redis Queue → Worker → Claude CLI → Result
```

### Components:

1. **FastAPI App** (`app.py`) - REST API server
2. **Worker** (`worker.py`) - Job processor
3. **CLI** (`cli.py`) - Command-line interface
4. **Redis** - Job queue and result storage

### API Endpoints:

- `GET /` - Service info
- `GET /health` - Health check
- `POST /execute` - Submit job
- `GET /jobs/{job_id}` - Job status

## 🛠️ Configuration

Environment variables:

```bash
REDIS_HOST=localhost     # Redis host
REDIS_PORT=6379         # Redis port
CCRS2_URL=http://localhost:8000  # API URL (CLI)
```

## 📊 Job Lifecycle

1. **Submit** - CLI sends job to API
2. **Queue** - API stores job in Redis queue
3. **Process** - Worker picks up job and executes
4. **Complete** - Worker updates job with result
5. **Retrieve** - CLI polls for completion

## 🧪 Testing

CCRS-2 includes a comprehensive pytest test suite covering all components:

```bash
# Run all tests
python run_tests.py all

# Run specific test categories
python run_tests.py unit          # Model validation tests
python run_tests.py api           # FastAPI endpoint tests
python run_tests.py worker        # Background worker tests
python run_tests.py cli           # CLI command tests
python run_tests.py integration   # End-to-end tests
python run_tests.py fast          # Quick unit + API tests

# Install test dependencies
pip install -r requirements.txt

# Run with pytest directly
pytest tests/ -v
pytest tests/test_models.py -v    # Test specific file
```

### Test Categories

- **Unit Tests** (`test_models.py`) - Pydantic model validation
- **API Tests** (`test_api.py`) - FastAPI endpoint functionality
- **Worker Tests** (`test_worker.py`) - Background job processing
- **CLI Tests** (`test_cli.py`) - Command-line interface
- **Integration Tests** (`test_integration.py`) - End-to-end workflows

The test suite uses:
- **pytest** - Test framework with fixtures and parametrization
- **fakeredis** - In-memory Redis for testing (no external dependencies)
- **httpx** - HTTP client testing for FastAPI
- **unittest.mock** - Mocking external dependencies

## 🚀 CLI Wrapper

CCRS-2 includes a powerful bash wrapper that makes the CLI much easier to use:

### Features
- **Simple commands** - `ccrs2 chat "hello"` instead of `python cli.py chat "hello"`
- **Docker shortcuts** - `ccrs2 up`, `ccrs2 down`, `ccrs2 ps`, `ccrs2 logs`
- **Command shortcuts** - `ccrs2 c "message"` for quick chat
- **Cross-platform** - Bash script for Unix/macOS, batch file for Windows
- **System installation** - Install globally or locally
- **Colorized output** - Beautiful, professional CLI interface

### Installation Options

#### Quick Local Use
```bash
# Make wrapper executable
chmod +x ccrs2

# Use immediately
./ccrs2 chat "Hello Claude!" --wait
```

#### System-Wide Installation
```bash
# Interactive installer
./install.sh

# Or direct options
./install.sh --global    # Install for all users (requires sudo)
./install.sh --local     # Install for current user only
```

#### Windows Support
```cmd
REM Use the included Windows batch file
ccrs2.bat chat "Hello Claude!" --wait
```

### Wrapper Commands

#### Core Commands
```bash
ccrs2 chat "message"              # Send chat message
ccrs2 command "/help"             # Execute Claude command
ccrs2 status ccrs2-abc123         # Check job status
ccrs2 health                      # Check service health
ccrs2 version                     # Show version info
```

#### Docker Management
```bash
ccrs2 up                          # Start all services
ccrs2 down                        # Stop all services
ccrs2 ps                          # Show service status
ccrs2 logs                        # View service logs
ccrs2 check                       # Quick status check
```

#### Shortcuts
```bash
ccrs2 c "message"                 # Chat shortcut
ccrs2 cmd "/help"                 # Command shortcut
ccrs2 s ccrs2-abc123              # Status shortcut
ccrs2 h                           # Health shortcut
```

#### Help & Info
```bash
ccrs2 --help                      # Show comprehensive help
ccrs2 -v                          # Show version
ccrs2 -h                          # Show help
```

### Environment Variables
```bash
export CCRS2_URL="http://custom:8000"     # Override API URL
export CCRS2_TENANT="production"          # Override default tenant
```

## 🔧 Development

### Project Structure:
```
ccrs2/
├── app.py              # FastAPI application
├── worker.py           # Job worker
├── cli.py              # Command-line interface
├── models.py           # Data models
├── requirements.txt    # Dependencies
├── docker-compose.yml  # Container setup
├── Dockerfile          # Container image
└── README.md          # This file
```

### Adding Operations:

1. Update `models.py` for new request types
2. Add handler in `worker.py`
3. Add CLI command in `cli.py`

### Testing:

```bash
# Test API directly
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "demo", "operation": "chat", "message": "hello"}'

# Test CLI
python cli.py chat "test message" --wait
python cli.py health
```

## 📈 Scaling

- **Horizontal Workers** - Run multiple worker processes
- **Load Balancer** - Multiple API instances
- **Redis Cluster** - For high availability
- **Monitoring** - Add Prometheus metrics

## 🔐 Production Considerations

- [ ] Authentication (API keys)
- [ ] Rate limiting
- [ ] Logging and monitoring
- [ ] Error recovery
- [ ] Data persistence
- [ ] SSL/TLS termination

## 📝 Version History

- **v2.0.0** - Initial lean implementation
- Focus on simplicity and reliability
- Proven architecture from CCRS-1 learnings

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Add tests
4. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

---

**CCRS-2: Simple, effective, and working!** 🚀