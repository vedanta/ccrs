# ⚡ CCRS-2 Quick Start

**Get up and running with CCRS-2 in 60 seconds!**

## 📥 1. Setup (30 seconds)

```bash
# Clone and prepare
git clone <repo-url>
cd ccrs2
chmod +x ccrs2
```

## 🚀 2. Start Services (20 seconds)

```bash
# Start everything
./ccrs2 up

# Check health
./ccrs2 health
```

## 💬 3. First Chat (10 seconds)

```bash
# Chat with Claude
./ccrs2 chat "Hello Claude!" --wait
```

---

## 📋 Essential Commands

| Action | Command |
|--------|---------|
| **Start Services** | `./ccrs2 up` |
| **Stop Services** | `./ccrs2 down` |
| **Check Health** | `./ccrs2 health` |
| **Service Status** | `./ccrs2 ps` |
| **View Logs** | `./ccrs2 logs` |
| **Chat** | `./ccrs2 chat "message" --wait` |
| **Execute Command** | `./ccrs2 command "/help" --wait` |
| **Check Job Status** | `./ccrs2 status ccrs2-abc123` |
| **Help** | `./ccrs2 --help` |

---

## 🎯 Common Scenarios

### Quick Chat
```bash
./ccrs2 c "Explain Python asyncio" --wait
```

### Different Tenant
```bash
./ccrs2 chat "Hello" --tenant production --wait
```

### Custom Timeout
```bash
./ccrs2 chat "Complex task" --timeout 600 --wait
```

### Background Job
```bash
# Submit without waiting
./ccrs2 chat "Analyze this data"

# Check later
./ccrs2 status ccrs2-abc123
```

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Port conflicts** | `lsof -i :8001` then kill conflicting process |
| **Services won't start** | `./ccrs2 down && ./ccrs2 up` |
| **Health check fails** | `./ccrs2 logs` to see errors |
| **Jobs stuck** | `docker-compose restart worker` |

---

## 📖 Need More Help?

- **Full Guide:** See `USER-GUIDE.md`
- **Technical Docs:** See `README.md`
- **CLI Help:** Run `./ccrs2 --help`

**🎉 You're ready to go!**