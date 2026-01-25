# 📖 CCRS User Guide

**Simple, effective Claude Code routing service - Get started in minutes!**

## 🎯 What is CCRS?

CCRS is a lightweight microservice that lets you interact with Claude through a simple REST API and professional CLI. It handles job queuing, processing, and result retrieval - perfect for automating Claude interactions or building applications.

**Key Features:**
- ✅ **Linux-Style Service Management** - Familiar `start`, `stop`, `restart` commands
- ✅ **Hybrid Architecture** - Containers for infrastructure, host for Claude CLI access
- ✅ **Professional CLI** - Easy-to-use command interface
- ✅ **Background Daemon Mode** - Production-ready worker with PID management
- ✅ **Real Claude Integration** - Direct Claude Code CLI integration
- ✅ **Multi-Tenant Support** - Support for different tenants/projects

---

## 🚀 Quick Start (Recommended)

### Prerequisites

- **Docker & Docker Compose** (for infrastructure)
- **Python 3.11+** (for CLI and worker)
- **Claude Code CLI** (for real Claude integration) - Install from [claude.ai/claude-code](https://claude.ai/claude-code)

### 1. Get CCRS

```bash
# Clone the repository
git clone <your-repo-url>
cd ccrs

# Make CLI wrapper executable
chmod +x ccrs
```

### 2. Start CCRS Services

```bash
# Start infrastructure (API + Redis containers)
./ccrs start

# Start worker daemon (Claude integration)
./ccrs worker start --daemon
```

**What this does:**
- 🗄️ **Redis Container** - Job queue and storage (port 6380)
- 🌐 **API Container** - REST API endpoints (port 8001)
- ⚙️ **Worker Process** - Background job processor (runs on host)

### 3. Verify Everything is Running

```bash
# Check all services
./ccrs status-all

# Check specific components
./ccrs worker status
./ccrs health
```

**Expected Output:**
```
🔍 CCRS Service Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Containers: Running
✅ Claude CLI: /Users/username/.local/bin/claude
✅ Worker Process: Running (PID: 12345)
✅ Redis Connection: OK (port 6380)
✅ API: Healthy
```

### 4. Your First Chat

```bash
# Send a message to Claude
./ccrs chat "Hello Claude! How are you today?" --wait
```

**Expected Output:**
```
💬 Sending message to Claude...
📋 Job submitted: ccrs-abc12345
⏳ Waiting for response...

✅ Response from Claude:
Hello! I'm doing well, thank you for asking. I'm here and ready to help you with any questions or tasks you might have. How can I assist you today?
```

🎉 **Congratulations! CCRS is working with real Claude integration!**

---

## 📋 Complete CLI Reference

### Service Management (Linux-Style)

#### Infrastructure Control
```bash
# Start all CCRS services (hybrid mode)
./ccrs start

# Stop all services (containers + worker)
./ccrs stop

# Restart everything
./ccrs restart

# Check all service status
./ccrs status-all
```

#### Worker Management
```bash
# Start worker (foreground - for development)
./ccrs worker start

# Start worker (background daemon - for production)
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

#### Chat with Claude
```bash
# Send a chat message and wait for response
./ccrs chat "Explain Python asyncio" --wait

# Send a message without waiting (async)
./ccrs chat "Analyze this code structure"

# Use shortcuts
./ccrs c "Quick chat message" --wait
```

#### Execute Claude Commands
```bash
# Execute a Claude command
./ccrs command "/help" --wait

# Direct Claude command (e.g., "/status", "/analyze")
./ccrs cmd "/analyze file.py" --wait
```

#### Job Management
```bash
# Check specific job status
./ccrs status ccrs-abc12345

# Use shortcut
./ccrs s ccrs-abc12345
```

#### Health & System Info
```bash
# Check CCRS health
./ccrs health
./ccrs h                  # Shortcut

# Show version
./ccrs version

# Show comprehensive help
./ccrs --help
```

### Advanced Options

#### Multi-Tenant Usage
```bash
# Specify different tenant
./ccrs chat "Hello" --tenant production --wait
./ccrs chat "Hello" --tenant testing --wait

# Default tenants: demo, test, production
```

#### Custom Timeouts
```bash
# Set custom timeout (in seconds)
./ccrs chat "Complex analysis task" --timeout 600 --wait

# Default timeout is 300 seconds (5 minutes)
```

#### Environment Variables
```bash
# Override default API URL
export CCRS_URL="http://custom-server:8001"

# Override default tenant
export CCRS_TENANT="production"

# Then use normally
./ccrs chat "Hello" --wait
```

---

## 🏗️ Production Deployment

### Production Setup

```bash
# 1. Start infrastructure
./ccrs start

# 2. Start worker daemon (background)
./ccrs worker start --daemon

# 3. Verify everything is running
./ccrs status-all

# 4. Test integration
./ccrs chat "Production test" --wait
```

### Daily Operations

#### Health Monitoring
```bash
# Full system status
./ccrs status-all

# Worker-specific status
./ccrs worker status

# API health check
./ccrs health

# Container status
./ccrs ps
```

#### Log Monitoring
```bash
# View all container logs
./ccrs logs

# View worker logs (daemon mode)
./ccrs logs worker

# Live worker logs
tail -f worker.log

# API logs specifically
docker logs ccrs-api
```

#### Service Management
```bash
# Restart just the worker
./ccrs worker restart

# Restart everything
./ccrs restart

# Stop everything cleanly
./ccrs stop
```

### Environment Configuration

```bash
# Production environment setup
export CCRS_URL="http://prod-ccrs:8001"
export CCRS_TENANT="production"
export REDIS_HOST="prod-redis"
export REDIS_PORT="6380"

# Development environment
export CCRS_URL="http://localhost:8001"
export CCRS_TENANT="dev"
```

---

## 🛠️ Configuration

### Port Configuration

**Default Ports:**
- **API:** http://localhost:8001
- **Redis:** localhost:6380 (mapped from container)

**Custom Ports:**
Edit `docker-compose.hybrid.yml`:
```yaml
api:
  ports:
    - "9000:8000"  # Use port 9000 instead

redis:
  ports:
    - "7000:6379"  # Use port 7000 instead (container internal port stays 6379)
```

Then update your environment:
```bash
export CCRS_URL="http://localhost:9000"
export REDIS_PORT=7000
```

### Worker Configuration

The worker automatically detects Claude CLI and connects to Redis:

```bash
# Worker environment variables (auto-configured)
REDIS_HOST=localhost      # Connects to container Redis
REDIS_PORT=6380          # Container Redis port
```

### Multi-Environment Setup

#### Development
```bash
# .env.development
CCRS_URL=http://localhost:8001
CCRS_TENANT=dev
REDIS_HOST=localhost
REDIS_PORT=6380
```

#### Production
```bash
# .env.production
CCRS_URL=http://prod-api:8001
CCRS_TENANT=production
REDIS_HOST=prod-redis
REDIS_PORT=6380
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check if ports are in use
./ccrs ps
lsof -i :8001  # Check API port
lsof -i :6380  # Check Redis port

# Solution: Stop conflicting services or change ports
```

#### 2. Worker Issues
```bash
# Check worker status
./ccrs worker status

# Common problems:
# ❌ Containers not running → ./ccrs start
# ❌ Claude CLI not found → Install from claude.ai/claude-code
# ❌ Redis not accessible → Check container logs
```

#### 3. Claude CLI Not Found
```bash
# Verify Claude CLI installation
which claude
claude --version

# Install if missing
# Visit: https://claude.ai/claude-code

# Add to PATH if needed
export PATH=$PATH:/path/to/claude
```

#### 4. API Health Fails
```bash
# Check service logs
./ccrs logs

# Restart services
./ccrs restart

# Test API manually
curl http://localhost:8001/health
```

#### 5. Worker Won't Start
```bash
# Check dependencies
./ccrs worker status

# Check container prerequisite
./ccrs ps

# Check logs
./ccrs logs worker
tail -f worker.log
```

### Debug Mode

#### View Detailed Logs
```bash
# All container logs
./ccrs logs

# Worker logs (if in daemon mode)
tail -f worker.log

# Real-time API logs
docker logs -f ccrs-api

# Real-time Redis logs
docker logs -f ccrs-redis
```

#### Manual Testing
```bash
# Test API endpoints directly
curl http://localhost:8001/health

# Submit test job
curl -X POST http://localhost:8001/execute \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": "demo", "operation": "chat", "message": "test"}'

# Check Redis directly
redis-cli -p 6380 ping
redis-cli -p 6380 keys "ccrs*"
```

#### Force Clean Restart
```bash
# Nuclear option - clean everything
./ccrs stop
docker system prune -f
./ccrs start
./ccrs worker start --daemon
```

---

## 🔧 Advanced Usage

### Multiple Workers
```bash
# Run multiple workers for high throughput
./ccrs worker start --daemon   # Worker 1
python -u worker.py &            # Worker 2
python -u worker.py &            # Worker 3

# Check all worker processes
ps aux | grep worker.py
```

### Custom API Integration
```python
import requests

# Submit job programmatically
response = requests.post("http://localhost:8001/execute", json={
    "tenant_id": "myapp",
    "operation": "chat",
    "message": "Hello Claude!",
    "timeout_seconds": 300
})

job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8001/jobs/{job_id}")
result = status.json()
```

### Integration with CI/CD
```yaml
# GitHub Actions example
- name: Start CCRS
  run: |
    cd ccrs
    ./ccrs start
    ./ccrs worker start --daemon

- name: Test Claude Integration
  run: |
    cd ccrs
    ./ccrs health
    ./ccrs chat "Run tests for this project" --wait

- name: Cleanup
  run: |
    cd ccrs
    ./ccrs stop
```

### Monitoring Setup
```bash
# Health check endpoint for monitoring
curl http://localhost:8001/health

# Prometheus metrics (if implemented)
curl http://localhost:8001/metrics

# Log aggregation
./ccrs logs | tee /var/log/ccrs/ccrs.log
```

---

## ❓ Need Help?

### Quick Commands
```bash
./ccrs --help              # Comprehensive help
./ccrs worker status        # Check worker + Claude CLI
./ccrs status-all           # Check everything
./ccrs logs                 # View logs
```

### Resources
- **README.md** - Technical overview and architecture
- **ARCHITECTURE.md** - Detailed system design
- **DEVELOPER.md** - Development and customization guide
- **API Documentation** - http://localhost:8001/docs (when running)

### Support Workflow
1. **Check status**: `./ccrs status-all`
2. **Check logs**: `./ccrs logs` and `./ccrs logs worker`
3. **Restart services**: `./ccrs restart`
4. **Test basic functionality**: `./ccrs health`
5. **Test Claude integration**: `./ccrs chat "test" --wait`

---

**🎉 You're now ready to use CCRS! Enjoy your simple, effective Claude Code routing service!**

**Pro tip**: Bookmark the command shortcuts:
- `./ccrs c "message"` - Quick chat
- `./ccrs s <job-id>` - Check status
- `./ccrs worker status` - Check worker health
- `./ccrs status-all` - Check everything