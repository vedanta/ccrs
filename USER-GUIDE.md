# 📖 CCRS-2 User Guide

**Simple, effective Claude Code routing service - Get started in minutes!**

## 🎯 What is CCRS-2?

CCRS-2 is a lightweight microservice that lets you interact with Claude through a simple REST API and professional CLI. It handles job queuing, processing, and result retrieval - perfect for automating Claude interactions or building applications.

**Key Features:**
- ✅ **Simple Architecture** - FastAPI + Redis + Worker
- ✅ **Professional CLI** - Easy-to-use command interface
- ✅ **Multi-Tenant** - Support for different tenants/projects
- ✅ **Docker Ready** - One-command deployment
- ✅ **Job Queue** - Reliable background processing

---

## 🎯 Claude Integration (Production Mode)

**CCRS-2 supports two modes:**

### 🧪 Mock Mode (Default)
- Perfect for testing the architecture
- Returns simulated Claude responses
- No Claude CLI required
- Ideal for development and CI/CD

### 🚀 Production Mode (Real Claude)
- Connects to actual Claude Code CLI
- Returns real Claude responses
- Requires Claude CLI installation
- **Recommended setup: Hybrid deployment**

**Quick Production Setup:**
```bash
# 1. Install Claude CLI (if not already installed)
# Visit: https://claude.ai/claude-code

# 2. Start hybrid services (API + Redis in containers)
./ccrs2 up-hybrid

# 3. Run worker on host (accesses Claude CLI directly)
./ccrs2 worker-host

# 4. Test real integration
./ccrs2 chat "What is 2+2?" --wait
```

See **[DEPLOYMENT-GUIDE.md](DEPLOYMENT-GUIDE.md)** for detailed Claude integration instructions.

---

## 🚀 Quick Start (Recommended)

### Prerequisites

- **Docker & Docker Compose** (for easy setup)
- **Python 3.11+** (for CLI usage)
- **Git** (to clone the repository)
- **Claude Code CLI** (for real Claude integration) - Install from [claude.ai/claude-code](https://claude.ai/claude-code)

### 1. Get CCRS-2

```bash
# Clone the repository
git clone <your-repo-url>
cd ccrs2

# Make CLI wrapper executable
chmod +x ccrs2
```

### 2. Start CCRS-2 Services

```bash
# Start all services with Docker Compose
./ccrs2 up

# Or use docker-compose directly
docker-compose up -d
```

**What this does:**
- 🗄️ **Redis** - Job queue and storage (port 6380)
- 🌐 **API Server** - REST API endpoints (port 8001)
- ⚙️ **Worker** - Background job processor

### 3. Verify Everything is Running

```bash
# Check service status
./ccrs2 ps

# Check CCRS-2 health
./ccrs2 health
```

**Expected Output:**
```
🏥 Checking CCRS-2 health...

📊 Service Status:
  Status: healthy
  Version: 2.0.0
  Timestamp: 2026-01-25T14:00:00Z
✅ CCRS-2 is healthy and ready!
```

### 4. Your First Chat

```bash
# Send a message to Claude
./ccrs2 chat "Hello Claude! How are you today?" --wait
```

**Expected Output:**
```
💬 Sending message to Claude...
📋 Job submitted: ccrs2-abc12345
⏳ Waiting for response...

✅ Response from Claude:
Mock Claude response to: Hello Claude! How are you today?
```

🎉 **Congratulations! CCRS-2 is working!**

---

## 📋 Complete CLI Reference

### Basic Commands

#### Chat with Claude
```bash
# Send a chat message and wait for response
./ccrs2 chat "Explain Python asyncio" --wait

# Send a message without waiting
./ccrs2 chat "Analyze this code structure"

# Use shortcuts
./ccrs2 c "Quick chat message" --wait
```

#### Execute Claude Commands
```bash
# Execute a Claude command
./ccrs2 command "/help" --wait

# Use shortcut
./ccrs2 cmd "/analyze file.py" --wait
```

#### Check Job Status
```bash
# Check specific job status
./ccrs2 status ccrs2-abc12345

# Use shortcut
./ccrs2 s ccrs2-abc12345
```

#### Health & System Info
```bash
# Check CCRS-2 health
./ccrs2 health

# Show version
./ccrs2 version

# Show help
./ccrs2 --help
```

### Advanced Options

#### Multi-Tenant Usage
```bash
# Specify different tenant
./ccrs2 chat "Hello" --tenant production --wait
./ccrs2 chat "Hello" --tenant testing --wait

# Default tenants: demo, test, example
```

#### Custom Timeouts
```bash
# Set custom timeout (in seconds)
./ccrs2 chat "Complex analysis task" --timeout 600 --wait

# Default timeout is 300 seconds (5 minutes)
```

#### Environment Variables
```bash
# Override default API URL
export CCRS2_URL="http://custom-server:8001"

# Override default tenant
export CCRS2_TENANT="production"

# Then use normally
./ccrs2 chat "Hello" --wait
```

---

## 🐳 Docker Management

### Service Control
```bash
# Start services
./ccrs2 up

# Stop services
./ccrs2 down

# Restart services
./ccrs2 down && ./ccrs2 up
```

### Monitoring
```bash
# Check service status
./ccrs2 ps

# View logs (all services)
./ccrs2 logs

# View logs for specific service
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f redis
```

### Troubleshooting
```bash
# Quick status check
./ccrs2 check

# Restart a specific service
docker-compose restart api
docker-compose restart worker

# Rebuild and restart
docker-compose down
docker-compose up --build -d
```

---

## ⚙️ Manual Setup (Without Docker)

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install and start Redis
# On macOS with Homebrew:
brew install redis
brew services start redis

# On Ubuntu:
sudo apt install redis-server
sudo systemctl start redis-server
```

### Start Services Manually

#### Terminal 1: API Server
```bash
python app.py
```

#### Terminal 2: Worker
```bash
python worker.py
```

#### Terminal 3: Use CLI
```bash
# Direct Python CLI
python cli.py health
python cli.py chat "Hello Claude!" --wait

# Or use the wrapper
./ccrs2 health
./ccrs2 chat "Hello Claude!" --wait
```

---

## 🔧 Configuration

### Port Configuration

**Default Ports:**
- **API:** 8001 (mapped from internal 8000)
- **Redis:** 6380 (mapped from internal 6379)

**Custom Ports:**
Edit `docker-compose.yml`:
```yaml
api:
  ports:
    - "9000:8000"  # Use port 9000 instead

redis:
  ports:
    - "7000:6379"  # Use port 7000 instead
```

Then update your environment:
```bash
export CCRS2_URL="http://localhost:9000"
```

### Environment Variables

Create `.env` file in CCRS-2 directory:
```bash
# API Configuration
CCRS2_URL=http://localhost:8001

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6380

# Default Tenant
CCRS2_TENANT=demo
```

---

## 🛠️ Installation Options

### Option 1: Local Installation
```bash
# Install for current user only
./install.sh --local

# Then use globally
ccrs2 chat "Now available everywhere!" --wait
```

### Option 2: System-Wide Installation
```bash
# Install for all users (requires sudo)
./install.sh --global

# Then any user can run
ccrs2 chat "Available system-wide!" --wait
```

### Option 3: Windows Installation
```cmd
# Use the Windows batch file
ccrs2.bat chat "Hello from Windows!" --wait

# Copy to a directory in your PATH for global access
```

---

## 📊 Usage Examples

### Basic Workflow
```bash
# 1. Start services
./ccrs2 up

# 2. Check health
./ccrs2 health

# 3. Chat with Claude
./ccrs2 chat "Explain the difference between async and sync programming" --wait

# 4. Execute a command
./ccrs2 command "/help" --wait

# 5. Check job status (if not using --wait)
./ccrs2 status ccrs2-abc12345

# 6. Stop services when done
./ccrs2 down
```

### Development Workflow
```bash
# Start services
./ccrs2 up

# Run multiple jobs
./ccrs2 chat "First question" --tenant dev
./ccrs2 chat "Second question" --tenant dev
./ccrs2 chat "Third question" --tenant dev

# Check all job statuses
./ccrs2 status ccrs2-job1
./ccrs2 status ccrs2-job2
./ccrs2 status ccrs2-job3

# Monitor logs
./ccrs2 logs
```

### Production-Like Usage
```bash
# Use production tenant with longer timeout
./ccrs2 chat "Complex analysis task" \
  --tenant production \
  --timeout 900 \
  --wait

# Check system health regularly
./ccrs2 health

# Monitor service status
./ccrs2 ps
```

---

## 🚨 Troubleshooting

### Common Issues

#### 1. Services Won't Start
```bash
# Check if ports are in use
./ccrs2 ps
lsof -i :8001  # Check API port
lsof -i :6380  # Check Redis port

# Solution: Stop conflicting services or change ports
```

#### 2. Health Check Fails
```bash
# Check service logs
./ccrs2 logs

# Restart services
./ccrs2 down
./ccrs2 up

# Check individual service status
docker-compose ps
```

#### 3. Jobs Get Stuck
```bash
# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker

# Clear Redis queue (if needed)
docker-compose exec redis redis-cli FLUSHALL
```

#### 4. CLI Command Not Found
```bash
# Make sure wrapper is executable
chmod +x ccrs2

# Use full path
./ccrs2 health

# Or install globally
./install.sh --local
```

### Debug Mode

#### Enable Verbose Logging
Add to `docker-compose.yml`:
```yaml
api:
  environment:
    - LOG_LEVEL=DEBUG

worker:
  environment:
    - LOG_LEVEL=DEBUG
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

---

## 🔒 Security Notes

### Default Configuration
- **Demo Mode:** Uses mock Claude responses for testing
- **No Authentication:** Default setup has no auth (add for production)
- **Local Access:** Services bound to localhost by default

### Production Considerations
- Add API authentication/authorization
- Use proper secrets management
- Configure SSL/TLS
- Set up monitoring and alerting
- Use production Redis with persistence

---

## 📚 Next Steps

### Integration with Real Claude
Replace mock responses in `worker.py`:
```python
# Replace this mock execution
cmd = ["echo", f"Mock Claude response to: {message}"]

# With real Claude CLI
cmd = ["claude", "--print", "--output-format", "text", message]
```

### Build Applications
Use CCRS-2 as a backend service:
```python
import requests

# Submit job
response = requests.post("http://localhost:8001/execute", json={
    "tenant_id": "myapp",
    "operation": "chat",
    "message": "Hello Claude!"
})

job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8001/jobs/{job_id}")
result = status.json()
```

### Scale Up
- Add multiple worker instances
- Use Redis cluster for high availability
- Add load balancing
- Implement monitoring and metrics

---

## ❓ Need Help?

### Quick Commands
```bash
./ccrs2 --help          # Comprehensive help
./ccrs2 health           # Check if running
./ccrs2 ps               # Service status
./ccrs2 logs             # View logs
./ccrs2 check            # Quick status check
```

### Resources
- **README.md** - Technical documentation
- **API Documentation** - http://localhost:8001/docs (when running)
- **Docker Logs** - `./ccrs2 logs` for detailed service logs

---

**🎉 You're now ready to use CCRS-2! Enjoy your simple, effective Claude Code routing service!**