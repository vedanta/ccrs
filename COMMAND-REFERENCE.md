# 📋 CCRS Command Reference

**Complete reference for all CCRS commands and options**

## 🚀 Service Management (Linux-Style)

| Command | Description | Example |
|---------|-------------|---------|
| `./ccrs start` | Start all CCRS services (hybrid mode) | `./ccrs start` |
| `./ccrs stop` | Stop all CCRS services | `./ccrs stop` |
| `./ccrs restart` | Restart all services | `./ccrs restart` |
| `./ccrs status-all` | Show comprehensive service status | `./ccrs status-all` |

## ⚙️ Worker Management

| Command | Shortcut | Description | Example |
|---------|----------|-------------|---------|
| `worker start` | | Start worker (foreground) | `./ccrs worker start` |
| `worker start --daemon` | `worker start -d` | Start worker (background) | `./ccrs worker start -d` |
| `worker stop` | | Stop worker daemon | `./ccrs worker stop` |
| `worker restart` | | Restart worker | `./ccrs worker restart` |
| `worker status` | | Show worker status | `./ccrs worker status` |

## 💬 Claude Integration

| Command | Shortcut | Description | Example |
|---------|----------|-------------|---------|
| `chat` | `c` | Send chat message | `./ccrs c "Hello!" --wait` |
| `command` | `cmd` | Execute Claude command | `./ccrs cmd "/help" --wait` |
| `status` | `s` | Check job status | `./ccrs s ccrs-abc123` |
| `health` | `h` | Check service health | `./ccrs h` |
| `version` | | Show version | `./ccrs version` |

## 🔧 Options & Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--wait` | Wait for job completion | `./ccrs chat "msg" --wait` |
| `--tenant <name>` | Set tenant | `./ccrs chat "msg" --tenant prod` |
| `--timeout <sec>` | Set timeout | `./ccrs chat "msg" --timeout 600` |
| `--daemon` | Run worker in background | `./ccrs worker start --daemon` |
| `--help` | Show help | `./ccrs --help` |
| `-v` | Show version | `./ccrs -v` |
| `-d` | Daemon mode shortcut | `./ccrs worker start -d` |

## 🌍 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CCRS_URL` | Override API URL | `http://localhost:8001` |
| `CCRS_TENANT` | Override default tenant | `demo` |
| `REDIS_HOST` | Redis host (for worker) | `localhost` |
| `REDIS_PORT` | Redis port (for worker) | `6380` |

## 📊 Service Workflow

### Standard Startup
```bash
# 1. Start infrastructure
./ccrs start
# Output: 🚀 Starting CCRS services (hybrid mode)...
#         ✅ Containers started

# 2. Start worker daemon
./ccrs worker start --daemon
# Output: 🚀 Starting CCRS worker (daemon mode)...
#         ✅ Worker started (PID: 12345)

# 3. Verify everything
./ccrs status-all
# Output: ✅ Containers: Running
#         ✅ Worker Process: Running (PID: 12345)
#         ✅ API: Healthy
```

### Usage Examples
```bash
# Quick chat
./ccrs c "What is 2+2?" --wait
# Output: ✅ Response from Claude: 2+2 equals 4.

# Background job
./ccrs chat "Analyze this code"
# Output: 📋 Job submitted: ccrs-abc12345

# Check job status
./ccrs s ccrs-abc12345
# Output: Status: completed, Result: [analysis]
```

## 🔍 Status Codes

| Status | Description |
|--------|-------------|
| `pending` | Job queued, not started |
| `running` | Job being processed by worker |
| `completed` | Job finished successfully |
| `failed` | Job failed with error |

## 📋 Monitoring Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `./ccrs logs` | View container logs | `./ccrs logs` |
| `./ccrs logs worker` | View worker logs | `./ccrs logs worker` |
| `./ccrs ps` | Show container status | `./ccrs ps` |
| `./ccrs worker status` | Worker health check | `./ccrs worker status` |
| `./ccrs status-all` | Complete system status | `./ccrs status-all` |

## 🎯 Common Patterns

### Development Workflow
```bash
./ccrs start                    # Start infrastructure
./ccrs worker start             # Start worker (foreground)
./ccrs health                   # Verify services
./ccrs c "Test message" --wait  # Test integration
./ccrs stop                     # Stop when done
```

### Production Workflow
```bash
./ccrs start                    # Start infrastructure
./ccrs worker start --daemon    # Start worker (background)
./ccrs status-all              # Verify all healthy
./ccrs c "Production test" --wait  # Test end-to-end
```

### Debugging Workflow
```bash
./ccrs status-all              # Check overall health
./ccrs worker status           # Check worker + Claude CLI
./ccrs logs                    # View container logs
./ccrs logs worker             # View worker logs
./ccrs restart                 # Restart if needed
```

### Multi-Tenant Usage
```bash
# Development tenant
./ccrs c "Dev message" --tenant dev --wait

# Production tenant
./ccrs c "Prod message" --tenant production --wait

# Custom tenant with timeout
./ccrs c "Long task" --tenant analytics --timeout 900 --wait
```

## 🚨 Emergency & Recovery

| Situation | Command |
|-----------|---------|
| **Services stuck** | `./ccrs stop && ./ccrs start` |
| **Worker not responding** | `./ccrs worker restart` |
| **Worker stuck** | `./ccrs worker stop && ./ccrs worker start -d` |
| **Port conflicts** | `lsof -i :8001` and `lsof -i :6380` |
| **Clear everything** | `./ccrs stop && docker system prune -f` |
| **Force stop worker** | `kill $(cat .worker.pid)` |

## 🛠️ Advanced Usage

### Multiple Workers
```bash
# Start primary worker daemon
./ccrs worker start --daemon

# Start additional workers manually
python -u worker.py &
python -u worker.py &

# Check all worker processes
ps aux | grep worker.py
```

### Custom Configuration
```bash
# Override API URL
export CCRS_URL="http://custom-host:8001"
./ccrs health

# Override tenant for session
export CCRS_TENANT="production"
./ccrs c "Hello production" --wait

# Worker with custom Redis
export REDIS_HOST="custom-redis"
export REDIS_PORT="6380"
./ccrs worker start
```

### Log Management
```bash
# Container logs
./ccrs logs | tee ccrs-containers.log

# Worker logs (daemon mode)
tail -f worker.log

# Real-time API logs
docker logs -f ccrs-api | tee api.log

# All logs combined
./ccrs logs & tail -f worker.log
```

### Health Monitoring
```bash
# Detailed worker status
./ccrs worker status
# Shows: Claude CLI path, worker PID, Redis connection

# API health endpoint
curl http://localhost:8001/health

# Container health
./ccrs ps

# Complete system check
./ccrs status-all && ./ccrs health
```

## 📞 Help & Support

| Need | Command |
|------|---------|
| **CLI help** | `./ccrs --help` |
| **Command help** | `./ccrs chat --help` |
| **Worker status** | `./ccrs worker status` |
| **Service status** | `./ccrs status-all` |
| **Health check** | `./ccrs health` |
| **View logs** | `./ccrs logs` |
| **API docs** | Open `http://localhost:8001/docs` |

## 🔗 Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error |
| `2` | Command not found |
| `130` | Interrupted (Ctrl+C) |

## 📱 Shortcuts Reference

| Shortcut | Full Command | Purpose |
|----------|--------------|---------|
| `./ccrs c "msg"` | `./ccrs chat "msg"` | Quick chat |
| `./ccrs s job-id` | `./ccrs status job-id` | Check status |
| `./ccrs h` | `./ccrs health` | Health check |
| `./ccrs -v` | `./ccrs version` | Show version |
| `./ccrs -h` | `./ccrs --help` | Show help |

---

## 💡 Pro Tips

1. **Use shortcuts** - `./ccrs c` instead of `./ccrs chat`
2. **Always use --wait** - Get immediate responses with `--wait`
3. **Monitor with status-all** - `./ccrs status-all` shows everything
4. **Use daemon mode in production** - `./ccrs worker start -d`
5. **Check worker status first** - Most issues are worker-related
6. **Bookmark logs command** - `./ccrs logs worker` for debugging

**💡 Tip:** Bookmark this page for quick reference while using CCRS!