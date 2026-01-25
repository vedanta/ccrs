# CCRS - Lean Claude Code Routing Service

> Simple, effective, and working Claude Code routing microservice

## 📚 Documentation

- **[📖 User Guide](USER-GUIDE.md)** - Complete getting started guide
- **[⚡ Quick Start](QUICK-START.md)** - Get running in 60 seconds
- **[📋 Command Reference](COMMAND-REFERENCE.md)** - All commands and options
- **[🏗️ Architecture Guide](ARCHITECTURE.md)** - System design and components
- **[👩‍💻 Developer Guide](DEVELOPER.md)** - Development and customization
- **[🔄 Migration Guide](MIGRATION-GUIDE.md)** - Upgrading from CCRS-2
- **[🧪 Testing Guide](README.md#-testing)** - How to run the test suite

## ✨ Features

- **Linux-Style Service Management** - `start`, `stop`, `restart`, `status` commands
- **Hybrid Architecture** - Containers for infrastructure, host for Claude CLI access
- **Background Daemon Mode** - Production-ready worker with PID management
- **Professional CLI** - Clean command interface with comprehensive help
- **Real Claude Integration** - Direct Claude Code CLI integration
- **Multi-Tenant Support** - Workspace isolation and routing
- **Docker Ready** - Single-command containerized deployment
- **Proven Stack** - FastAPI + Redis + Python (battle-tested)

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (for CLI and worker)
- **Docker & Docker Compose** (for infrastructure)
- **Claude Code CLI** (for real Claude integration) - [Install here](https://claude.ai/claude-code)

### 60-Second Setup

```bash
# 1. Clone and setup (10 seconds)
git clone <repo>
cd ccrs
chmod +x ccrs

# 2. Start infrastructure (20 seconds)
./ccrs start

# 3. Start worker daemon (10 seconds)
./ccrs worker start --daemon

# 4. Test integration (20 seconds)
./ccrs health
./ccrs chat "Hello Claude!" --wait
```

🎉 **You're running CCRS with real Claude integration!**

## 🎯 Architecture Overview

### Hybrid Deployment (Recommended)
```
Host System:
├── Claude CLI ✅                 (Direct access)
├── Worker Process (Python) ────┐
└── Docker Containers:           │
    ├── API Server (FastAPI) ────┤
    └── Redis Queue ─────────────┘
```

**Benefits:**
- ✅ **Real Claude Access** - Worker runs on host with direct CLI access
- ✅ **Reliable Infrastructure** - API and Redis containerized for consistency
- ✅ **Easy Development** - Containers for infrastructure, local worker for debugging
- ✅ **Production Ready** - Daemon mode with proper process management

## 📋 CLI Usage

### Service Management (Linux-Style)

```bash
# Start all CCRS services (hybrid mode)
./ccrs start

# Stop all services
./ccrs stop

# Restart everything
./ccrs restart

# Check all service status
./ccrs status-all
```

### Worker Management

```bash
# Start worker (foreground - development)
./ccrs worker start

# Start worker (background daemon - production)
./ccrs worker start --daemon
./ccrs worker start -d

# Stop worker daemon
./ccrs worker stop

# Restart worker
./ccrs worker restart

# Check worker status
./ccrs worker status
```

### Claude Integration

```bash
# Chat with Claude
./ccrs chat "Explain async Python" --wait

# Execute Claude command
./ccrs command "/help" --wait

# Check job status
./ccrs status ccrs-abc12345

# Health check
./ccrs health

# Show version
./ccrs version
```

### Shortcuts

```bash
# Quick commands
./ccrs c "message"              # Chat shortcut
./ccrs s ccrs-abc123            # Status shortcut
./ccrs h                        # Health shortcut

# Monitoring
./ccrs logs                     # Container logs
./ccrs logs worker              # Worker logs
./ccrs ps                       # Container status
```

## 🏗️ Production Deployment

### Recommended Setup

```bash
# 1. Start infrastructure
./ccrs start

# 2. Start worker daemon
./ccrs worker start --daemon

# 3. Verify everything is running
./ccrs status-all

# 4. Test integration
./ccrs chat "Production test" --wait
```

### Daily Operations

```bash
# Health monitoring
./ccrs status-all               # Full system status
./ccrs worker status            # Worker + Claude CLI status
./ccrs health                   # API health check

# Log monitoring
./ccrs logs                     # API and Redis logs
./ccrs logs worker              # Worker process logs
tail -f worker.log              # Live worker logs

# Service management
./ccrs worker restart           # Restart just worker
./ccrs restart                  # Restart everything
```

### Environment Configuration

```bash
# Custom API URL
export CCRS_URL="http://custom-host:8001"

# Custom tenant
export CCRS_TENANT="production"

# Then use normally
./ccrs chat "Hello" --wait
```

## 📊 Job Lifecycle

1. **Submit** - CLI sends job to API
2. **Queue** - API stores job in Redis queue
3. **Process** - Worker picks up job and executes Claude CLI
4. **Complete** - Worker updates job with result
5. **Retrieve** - CLI polls for completion

## 🧪 Testing

CCRS includes a comprehensive pytest test suite covering all components:

### Run Tests

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

## 🛠️ Configuration

### Ports and Services

**Default Configuration:**
- **API Server:** http://localhost:8001
- **Redis Queue:** localhost:6380
- **Worker:** Runs on host system

### Environment Variables

```bash
CCRS_URL=http://localhost:8001    # API endpoint
CCRS_TENANT=demo                  # Default tenant
REDIS_HOST=localhost              # Redis host (for worker)
REDIS_PORT=6380                   # Redis port (for worker)
```

### Custom Ports

Edit `docker-compose.hybrid.yml`:
```yaml
api:
  ports:
    - "9000:8000"  # Use port 9000 instead

redis:
  ports:
    - "7000:6379"  # Use port 7000 instead (container internal port stays 6379)
```

Then update environment:
```bash
export CCRS_URL="http://localhost:9000"
export REDIS_PORT=7000
```

## 🚨 Troubleshooting

### Common Issues

#### Services Won't Start
```bash
# Check ports
./ccrs ps
lsof -i :8001  # API port
lsof -i :6380  # Redis port

# Solution: Stop conflicting services or change ports
```

#### Worker Issues
```bash
# Check worker status
./ccrs worker status

# Common problems:
# - Containers not running: ./ccrs start
# - Claude CLI not found: Install from claude.ai/claude-code
# - Redis not accessible: Check container logs
```

#### API Health Fails
```bash
# Check service logs
./ccrs logs

# Restart services
./ccrs restart

# Check container status
./ccrs ps
```

### Debug Mode

#### View Logs
```bash
# Container logs
./ccrs logs

# Worker logs (daemon mode)
tail -f worker.log

# API logs specifically
docker logs ccrs-api
```

#### Manual Testing
```bash
# Test API directly
curl http://localhost:8001/health

# Test job submission
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "demo", "operation": "chat", "message": "test"}'
```

## 📈 Scaling

### Horizontal Scaling
- **Multiple Workers** - Run multiple worker processes
- **Load Balancer** - Multiple API instances behind load balancer
- **Redis Cluster** - High availability Redis setup
- **Monitoring** - Add Prometheus metrics and Grafana dashboards

### Production Considerations
- **Authentication** - Add API keys or OAuth
- **Rate Limiting** - Prevent abuse
- **SSL/TLS** - Secure communications
- **Monitoring** - Health checks and alerting
- **Persistence** - Redis data persistence

## 📝 Version History

- **v3.0.0** - CCRS production release with Linux-style service management
- **v2.0.0** - CCRS-2 hybrid architecture and real Claude integration
- **v1.0.0** - Initial CCRS microservice implementation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests (`python run_tests.py all`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push branch (`git push origin feature/amazing-feature`)
6. Submit pull request

## 📄 License

MIT License - see LICENSE file for details

---

## 🎯 What Makes CCRS Special

### Simple & Effective
- **One command setup** - `./ccrs start && ./ccrs worker start -d`
- **Linux-style management** - Familiar service patterns
- **Real Claude integration** - No mocks or proxies
- **Production ready** - Proper daemon mode and process management

### Battle-Tested Architecture
- **Proven tech stack** - FastAPI + Redis + Python
- **Hybrid deployment** - Best of containers + host processes
- **Comprehensive testing** - 81 tests covering all components
- **Professional tooling** - Full CLI with help system

### Developer Friendly
- **Clear separation** - Infrastructure vs worker vs client
- **Easy debugging** - Foreground mode for development
- **Comprehensive docs** - Architecture, development, and operation guides
- **Extensible design** - Easy to customize and extend

**CCRS: Simple, effective, and working!** 🚀