# 🚀 CCRS-2 Deployment Guide

**Integrating Claude Code CLI with Containerized Services**

## The Challenge

CCRS-2 runs API and Redis in Docker containers, but needs to execute Claude Code CLI commands. Since Claude CLI is installed on the host system, we need to bridge the container-host gap.

## 🎯 Deployment Options

### Option 1: Hybrid Deployment (Recommended)

**Architecture:**
```
Host System:
├── claude CLI ✅
├── Worker Process (Python) → Accesses claude directly
└── Docker Containers:
    ├── ccrs2-api (FastAPI)
    └── ccrs2-redis (Queue)
```

**Advantages:**
- ✅ Direct access to Claude CLI
- ✅ No container complexity for worker
- ✅ Easy to debug and develop
- ✅ Uses existing Claude installation

**Setup:**

1. **Start API + Redis containers:**
```bash
# Use hybrid docker-compose
docker-compose -f docker-compose.hybrid.yml up -d

# Check status
docker-compose -f docker-compose.hybrid.yml ps
```

2. **Run worker on host:**
```bash
# Method 1: Use helper script
chmod +x run-worker-host.sh
./run-worker-host.sh

# Method 2: Manual setup
export REDIS_HOST=localhost
export REDIS_PORT=6380
python worker-production.py
```

3. **Test the setup:**
```bash
# API and Redis in containers, worker on host
./ccrs2 health
./ccrs2 chat "Hello Claude!" --wait
```

### Option 2: Full Container with Volume Mount

**Architecture:**
```
Docker Containers:
├── ccrs2-api (FastAPI)
├── ccrs2-redis (Queue)
└── ccrs2-worker (with host volume mounts) → Accesses host claude
```

**Setup:** *(More complex, use Option 1 instead)*

### Option 3: Install Claude in Container

**Install Claude Code CLI inside the Docker image:**

```dockerfile
FROM python:3.11-slim

# Install Claude CLI in container
RUN curl -fsSL https://claude.ai/install.sh | sh
# ... rest of Dockerfile
```

**Note:** This requires Claude CLI to support container installation.

---

## 🔧 Quick Setup (Recommended)

### 1. Start Services

```bash
# Stop current containers if running
docker-compose down

# Start hybrid deployment (API + Redis only)
docker-compose -f docker-compose.hybrid.yml up -d

# Verify containers
docker-compose -f docker-compose.hybrid.yml ps
```

### 2. Switch to Production Worker

```bash
# Replace mock worker with production version
cp worker-production.py worker.py

# Or run production worker directly
python worker-production.py
```

### 3. Test Real Claude Integration

```bash
# Test with actual Claude CLI
./ccrs2 chat "What is the current time?" --wait
./ccrs2 command "/help" --wait
```

---

## 📋 Verification Checklist

### ✅ Prerequisites
- [ ] Claude Code CLI installed and working: `claude --version`
- [ ] Docker and Docker Compose installed
- [ ] Python 3.11+ with pip

### ✅ Service Health
```bash
# Check Docker services
docker-compose -f docker-compose.hybrid.yml ps

# Check Redis connection
redis-cli -p 6380 ping

# Check API health
curl http://localhost:8001/health

# Check Claude CLI
claude --help
```

### ✅ End-to-End Test
```bash
# 1. Start hybrid services
docker-compose -f docker-compose.hybrid.yml up -d

# 2. Run production worker
python worker-production.py &

# 3. Test full pipeline
./ccrs2 chat "Hello from real Claude!" --wait

# Expected: Real response from Claude CLI
```

---

## 🐛 Troubleshooting

### Worker Can't Find Claude CLI
```bash
Error: Claude CLI not found in PATH
```
**Solution:**
```bash
# Check Claude installation
which claude
claude --version

# Add to PATH if needed
export PATH=$PATH:/path/to/claude

# Verify in worker environment
python -c "import shutil; print(shutil.which('claude'))"
```

### Redis Connection Issues
```bash
Error: Worker Redis connection failed
```
**Solution:**
```bash
# Check Redis container
docker-compose -f docker-compose.hybrid.yml ps
docker logs ccrs2-redis

# Test connection
redis-cli -h localhost -p 6380 ping

# Verify environment
echo $REDIS_HOST $REDIS_PORT
```

### Claude CLI Permission Issues
```bash
Error: Permission denied executing Claude
```
**Solution:**
```bash
# Check Claude permissions
ls -la $(which claude)

# Re-authenticate if needed
claude auth login

# Test Claude directly
claude "test message"
```

### Port Conflicts
```bash
Error: Port already in use
```
**Solution:**
```bash
# Check what's using ports
lsof -i :8001  # API port
lsof -i :6380  # Redis port

# Kill conflicting processes or change ports in docker-compose.hybrid.yml
```

---

## 🏗️ Production Deployment

### Systemd Service (Linux)

Create `/etc/systemd/system/ccrs2-worker.service`:
```ini
[Unit]
Description=CCRS-2 Worker
After=docker.service

[Service]
Type=simple
User=ccrs2
WorkingDirectory=/opt/ccrs2
Environment=REDIS_HOST=localhost
Environment=REDIS_PORT=6380
ExecStart=/usr/bin/python3 worker-production.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable ccrs2-worker
sudo systemctl start ccrs2-worker
sudo systemctl status ccrs2-worker
```

### Docker Swarm / Kubernetes

For production scaling, consider:
- Redis Cluster for high availability
- Multiple worker replicas
- Load balancer for API instances
- Monitoring and logging

---

## 📊 Architecture Comparison

| Aspect | Mock Mode | Hybrid Mode | Full Container |
|--------|-----------|-------------|----------------|
| **Claude Access** | Mocked responses | ✅ Real Claude CLI | Complex setup |
| **Development** | ✅ Simple | ✅ Easy debugging | Container complexity |
| **Production** | ❌ Not real | ✅ Recommended | ✅ Fully isolated |
| **Maintenance** | ✅ Low | ✅ Medium | ❌ High |

**Recommendation:** Use **Hybrid Mode** for development and production.

---

## 🎯 Next Steps

1. **Test hybrid deployment:**
```bash
docker-compose -f docker-compose.hybrid.yml up -d
python worker-production.py
./ccrs2 chat "Test real integration" --wait
```

2. **Update bash wrapper** to support hybrid mode
3. **Create monitoring** for worker health
4. **Set up logging** for production debugging

The hybrid approach gives you the best of both worlds: containerized API/Redis for reliability, and direct Claude CLI access for functionality!