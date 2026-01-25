# 📋 CCRS-2 Command Reference

**Quick reference for all CCRS-2 commands**

## 🚀 Service Management

| Command | Description | Example |
|---------|-------------|---------|
| `./ccrs2 up` | Start all services | `./ccrs2 up` |
| `./ccrs2 down` | Stop all services | `./ccrs2 down` |
| `./ccrs2 ps` | Show service status | `./ccrs2 ps` |
| `./ccrs2 logs` | View all logs | `./ccrs2 logs` |
| `./ccrs2 check` | Quick health check | `./ccrs2 check` |

## 💬 Core Commands

| Command | Shortcut | Description | Example |
|---------|----------|-------------|---------|
| `chat` | `c` | Send chat message | `./ccrs2 c "Hello!" --wait` |
| `command` | `cmd` | Execute Claude command | `./ccrs2 cmd "/help" --wait` |
| `status` | `s` | Check job status | `./ccrs2 s ccrs2-abc123` |
| `health` | `h` | Check service health | `./ccrs2 h` |
| `version` |  | Show version | `./ccrs2 version` |

## 🔧 Options & Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--wait` | Wait for job completion | `./ccrs2 chat "msg" --wait` |
| `--tenant <name>` | Set tenant | `./ccrs2 chat "msg" --tenant prod` |
| `--timeout <sec>` | Set timeout | `./ccrs2 chat "msg" --timeout 600` |
| `--help` | Show help | `./ccrs2 --help` |
| `-v` | Show version | `./ccrs2 -v` |

## 🌍 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CCRS2_URL` | Override API URL | `http://localhost:8001` |
| `CCRS2_TENANT` | Override default tenant | `demo` |

## 📊 Job Workflow

```bash
# 1. Submit job
./ccrs2 chat "Analyze this code" --tenant dev
# Output: Job submitted: ccrs2-abc123

# 2. Check status
./ccrs2 status ccrs2-abc123
# Output: Status: completed, Result: ...

# OR: Submit and wait
./ccrs2 chat "Quick question" --wait
# Output: Direct response
```

## 🔍 Status Codes

| Status | Description |
|--------|-------------|
| `pending` | Job queued, not started |
| `running` | Job being processed |
| `completed` | Job finished successfully |
| `failed` | Job failed with error |

## 🎯 Common Patterns

### Development Workflow
```bash
./ccrs2 up                           # Start services
./ccrs2 health                       # Verify running
./ccrs2 c "Test message" --wait      # Quick test
./ccrs2 logs                         # Monitor if needed
./ccrs2 down                         # Stop when done
```

### Production Workflow
```bash
./ccrs2 c "Task" --tenant prod --timeout 900 --wait
./ccrs2 ps                           # Check services
./ccrs2 health                       # Verify health
```

### Debugging Workflow
```bash
./ccrs2 ps                           # Check service status
./ccrs2 logs                         # View logs
./ccrs2 check                        # Quick diagnostics
docker-compose restart worker        # Restart if needed
```

### Batch Processing
```bash
# Submit multiple jobs
./ccrs2 c "Task 1" --tenant batch
./ccrs2 c "Task 2" --tenant batch
./ccrs2 c "Task 3" --tenant batch

# Check results later
./ccrs2 s ccrs2-job1
./ccrs2 s ccrs2-job2
./ccrs2 s ccrs2-job3
```

## 🚨 Emergency Commands

| Situation | Command |
|-----------|---------|
| **Services stuck** | `./ccrs2 down && ./ccrs2 up` |
| **Worker not responding** | `docker-compose restart worker` |
| **Clear job queue** | `docker-compose exec redis redis-cli FLUSHALL` |
| **Reset everything** | `./ccrs2 down && docker system prune -f && ./ccrs2 up` |

## 📞 Help & Support

| Need | Command |
|------|---------|
| **CLI help** | `./ccrs2 --help` |
| **Command help** | `./ccrs2 chat --help` |
| **Service status** | `./ccrs2 ps` |
| **Health check** | `./ccrs2 health` |
| **View logs** | `./ccrs2 logs` |
| **API docs** | Open `http://localhost:8001/docs` |

---

**💡 Tip:** Bookmark this page for quick reference while using CCRS-2!