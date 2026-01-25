# ⚡ CCRS Quick Start

**Get up and running with CCRS in 60 seconds!**

## 📥 1. Setup (20 seconds)

```bash
# Clone and prepare
git clone <repo-url>
cd ccrs
chmod +x ccrs
```

## 🚀 2. Start Services (20 seconds)

```bash
# Start infrastructure (API + Redis containers)
./ccrs start

# Start worker daemon (Claude integration)
./ccrs worker start --daemon

# Check everything is running
./ccrs status-all
```

## 💬 3. First Chat (20 seconds)

```bash
# Chat with Claude
./ccrs chat "Hello Claude!" --wait
```

---

## 📋 Essential Commands

| Action | Command |
|--------|---------|
| **Start Services** | `./ccrs start` |
| **Stop Services** | `./ccrs stop` |
| **Start Worker** | `./ccrs worker start --daemon` |
| **Stop Worker** | `./ccrs worker stop` |
| **Check All Status** | `./ccrs status-all` |
| **Check Worker** | `./ccrs worker status` |
| **Chat** | `./ccrs chat "message" --wait` |
| **Execute Command** | `./ccrs command "/help" --wait` |
| **Check Job Status** | `./ccrs status ccrs-abc123` |
| **Health Check** | `./ccrs health` |
| **View Logs** | `./ccrs logs` |
| **Help** | `./ccrs --help` |

---

## 🎯 Common Usage Patterns

### Quick Chat
```bash
./ccrs c "Explain Python asyncio" --wait
```

### Background Job
```bash
# Submit without waiting
./ccrs chat "Analyze this data"

# Check later
./ccrs status ccrs-abc123
```

### Different Tenant
```bash
./ccrs chat "Hello" --tenant production --wait
```

### Custom Timeout
```bash
./ccrs chat "Complex task" --timeout 600 --wait
```

### Service Management
```bash
# Development workflow
./ccrs start                    # Start infrastructure
./ccrs worker start             # Start worker (foreground)

# Production workflow
./ccrs start                    # Start infrastructure
./ccrs worker start --daemon    # Start worker (background)
./ccrs status-all              # Verify everything running
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Port conflicts** | `lsof -i :8001` then kill process or change ports |
| **Services won't start** | `./ccrs stop && ./ccrs start` |
| **Worker issues** | `./ccrs worker status` to diagnose |
| **Health check fails** | `./ccrs logs` to see errors |
| **Claude CLI not found** | Install from [claude.ai/claude-code](https://claude.ai/claude-code) |

---

## ⚙️ Prerequisites

- **Docker & Docker Compose** (for infrastructure)
- **Python 3.11+** (for CLI and worker)
- **Claude Code CLI** (for real Claude integration)

**Install Claude CLI:**
```bash
# Visit: https://claude.ai/claude-code
# Follow installation instructions

# Verify installation
which claude
claude --version
```

---

## 🌍 Environment Variables

```bash
# Override defaults (optional)
export CCRS_URL="http://localhost:8001"     # API endpoint
export CCRS_TENANT="demo"                   # Default tenant
export REDIS_HOST="localhost"               # Redis host (worker)
export REDIS_PORT="6380"                    # Redis port (worker)
```

---

## 🎯 What's Happening?

### Architecture
```
Host System:
├── Claude CLI ✅                 (Direct access)
├── Worker Process (Python) ────┐
└── Docker Containers:           │
    ├── API Server (FastAPI) ────┤
    └── Redis Queue ─────────────┘
```

### Job Flow
1. **Submit** - `./ccrs chat "message"` → API
2. **Queue** - API stores job in Redis
3. **Process** - Worker executes Claude CLI
4. **Complete** - Worker stores result
5. **Retrieve** - CLI gets response

### Ports & Services
- **API:** http://localhost:8001
- **Redis:** localhost:6380 (container)
- **Worker:** Runs on host system

---

## 📖 Need More Help?

- **Complete Guide:** See [USER-GUIDE.md](USER-GUIDE.md)
- **Command Reference:** See [COMMAND-REFERENCE.md](COMMAND-REFERENCE.md)
- **Architecture Details:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **CLI Help:** Run `./ccrs --help`

---

**🎉 You're ready to go! CCRS is simple, effective, and working!** 🚀

**Pro Tips:**
- Use `./ccrs c "message"` for quick chats
- Run `./ccrs status-all` to check everything
- Use `--daemon` for production worker mode
- Check `./ccrs worker status` if Claude CLI issues