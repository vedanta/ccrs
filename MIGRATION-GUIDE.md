# 🚀 CCRS Migration Guide

**CCRS-2 is now CCRS** - Clean transition to production-ready Claude Code routing service

## 🎯 What Changed

### Naming Convention
- **Old**: `ccrs2` → **New**: `ccrs`
- **Directory**: `output/ccrs2/` → `output/ccrs/`
- **Environment**: `CCRS2_URL` → `CCRS_URL`
- **Containers**: `ccrs2-api` → `ccrs-api`

### Architecture Simplification
- **Hybrid Mode**: Now the **only recommended mode**
- **No more mode confusion**: Containers for infrastructure, host for worker
- **Real Claude CLI**: Production integration by default

### Linux-Style Service Management
- **Service control**: `start`, `stop`, `restart`, `status-all`
- **Worker daemon**: Background mode with PID tracking
- **Process management**: Proper signal handling and cleanup

## 🛠️ New Command Structure

### Unified Service Management
```bash
# Start all CCRS services (hybrid mode)
ccrs start

# Stop all services (containers + worker)
ccrs stop

# Restart everything
ccrs restart

# Check all service status
ccrs status-all
```

### Linux-Style Worker Management
```bash
# Start worker (foreground - for development)
ccrs worker start

# Start worker (background daemon - for production)
ccrs worker start --daemon
ccrs worker start -d

# Stop worker daemon
ccrs worker stop

# Restart worker
ccrs worker restart

# Check worker status
ccrs worker status
```

### Claude Integration (Unchanged)
```bash
# Chat with Claude
ccrs chat "Hello Claude!" --wait

# Execute Claude commands
ccrs command "/help" --wait

# Check job status
ccrs status ccrs-abc12345

# Health check
ccrs health
```

## 🔄 Migration Steps

### From CCRS-2 Setup

If you were using the old `./ccrs2` commands:

```bash
# Old workflow
./ccrs2 up-hybrid          # Start containers
./ccrs2 worker-host         # Start worker

# New workflow
./ccrs start               # Start containers
./ccrs worker start -d     # Start worker daemon
```

### Environment Variables

Update your environment variables:

```bash
# Old
export CCRS2_URL="http://localhost:8001"
export CCRS2_TENANT="demo"

# New
export CCRS_URL="http://localhost:8001"
export CCRS_TENANT="demo"
```

### Docker Container Names

If you have scripts that reference container names:

```bash
# Old
docker logs ccrs2-api
docker restart ccrs2-worker

# New
docker logs ccrs-api
docker restart ccrs-worker  # (not recommended - use ccrs worker restart)
```

## 🎯 Recommended Workflow

### Development Setup
```bash
# 1. Start CCRS infrastructure
ccrs start

# 2. Start worker (foreground for debugging)
ccrs worker start

# 3. In another terminal, test
ccrs chat "What is 2+2?" --wait
```

### Production Setup
```bash
# 1. Start CCRS infrastructure
ccrs start

# 2. Start worker daemon
ccrs worker start --daemon

# 3. Verify everything is running
ccrs status-all

# 4. Test integration
ccrs health
ccrs chat "Production test" --wait
```

### Daily Operations
```bash
# Check overall health
ccrs status-all

# View logs
ccrs logs                  # Container logs
ccrs logs worker           # Worker logs

# Restart components
ccrs worker restart        # Just worker
ccrs restart              # Everything
```

## 🆕 New Features

### Background Worker Management
- **PID tracking**: `.worker.pid` file for process management
- **Graceful shutdown**: SIGTERM followed by SIGKILL if needed
- **Status monitoring**: Real-time process and connection checks
- **Log rotation**: Worker logs to `worker.log` in daemon mode

### Enhanced Status Reporting
```bash
ccrs worker status
# Shows:
# ✅ Claude CLI: /Users/username/.local/bin/claude
# ✅ Worker Process: Running (PID: 12345)
# ✅ Redis Connection: OK (port 6380)

ccrs status-all
# Shows containers, worker, and API health in one view
```

### Simplified Container Management
- **Single command startup**: `ccrs start` handles everything
- **Intelligent fallbacks**: Uses hybrid config if available
- **Clean shutdown**: Stops worker before containers
- **Dependency checking**: Worker won't start without containers

## 🐛 Troubleshooting

### Worker Won't Start
```bash
# Check dependencies
ccrs worker status

# Common issues:
# - Containers not running: ccrs start
# - Claude CLI not found: Install from claude.ai/claude-code
# - Redis not accessible: Check container status
```

### Daemon Mode Issues
```bash
# Check worker logs
tail -f worker.log

# Force stop stuck worker
kill $(cat .worker.pid)
rm .worker.pid
ccrs worker start -d
```

### Environment Variables
```bash
# Verify current settings
echo $CCRS_URL
echo $CCRS_TENANT

# Test with custom settings
CCRS_URL=http://custom:8001 ccrs health
```

## ✅ Benefits of New Architecture

### Operational Benefits
- **Clear service separation**: Infrastructure vs. worker vs. client
- **Standard Linux patterns**: Service management feels familiar
- **Better monitoring**: Granular status checking
- **Production ready**: Daemon mode with proper process management

### Developer Experience
- **Simplified commands**: No more mode confusion
- **Better debugging**: Foreground mode for development
- **Consistent naming**: Everything is just `ccrs`
- **Comprehensive help**: `ccrs --help` shows all options

### Maintenance Benefits
- **Single deployment mode**: Only hybrid mode to support
- **PID-based management**: Reliable process tracking
- **Graceful shutdowns**: Clean process termination
- **Log management**: Separate logs for containers vs. worker

**CCRS is now production-ready with enterprise-grade process management!** 🚀
