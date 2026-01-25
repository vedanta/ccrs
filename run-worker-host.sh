#!/bin/bash
# CCRS Worker - Host Mode
# Run worker on host system with access to Claude CLI

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Starting CCRS Worker on Host System${NC}"
echo -e "${BLUE}   (with access to Claude CLI)${NC}"
echo ""

# Check if Claude CLI is available
if ! command -v claude &> /dev/null; then
    echo -e "${RED}❌ Error: Claude CLI not found in PATH${NC}"
    echo "   Please install Claude Code CLI first"
    echo "   See: https://claude.ai/claude-code"
    exit 1
fi

echo -e "${GREEN}✅ Claude CLI found: $(which claude)${NC}"

# Check if Redis is accessible
if ! nc -z localhost 6380 2>/dev/null; then
    echo -e "${RED}❌ Error: Redis not accessible on localhost:6380${NC}"
    echo "   Please start Redis first:"
    echo "   docker-compose -f docker-compose.hybrid.yml up -d redis"
    exit 1
fi

echo -e "${GREEN}✅ Redis accessible on localhost:6380${NC}"

# Set environment for host Redis connection
export REDIS_HOST=localhost
export REDIS_PORT=6380

echo -e "${BLUE}📋 Starting worker with environment:${NC}"
echo "   REDIS_HOST=localhost"
echo "   REDIS_PORT=6380"
echo ""

# Install dependencies if needed
if [ ! -f ".venv/pyvenv.cfg" ]; then
    echo -e "${BLUE}📦 Installing Python dependencies...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo -e "${GREEN}🎯 Worker starting... Press Ctrl+C to stop${NC}"
echo ""

# Run worker
python worker.py