# 🏗️ CCRS Architecture Guide

**Detailed system design and technical architecture**

## 🎯 Architecture Overview

CCRS follows a **hybrid microservice architecture** that combines the reliability of containerized infrastructure with the flexibility of host-based processing for Claude CLI integration.

### High-Level System Architecture

```mermaid
graph TB
    subgraph "Host System"
        CLI[CCRS CLI<br/>Python Client]
        Worker[Worker Process<br/>Python Background Service]
        Claude[Claude CLI<br/>Real AI Integration]

        Worker --> Claude
    end

    subgraph "Docker Containers"
        API[FastAPI Server<br/>Port 8001]
        Redis[Redis Queue<br/>Port 6380]

        API --> Redis
    end

    User[👤 User] --> CLI
    CLI --> API
    API --> Redis
    Worker --> Redis
    Worker --> API

    style User fill:#e1f5fe
    style Claude fill:#fff3e0
    style API fill:#f3e5f5
    style Redis fill:#ffebee
    style Worker fill:#e8f5e8
    style CLI fill:#fff9c4
```

### Job Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI as CCRS CLI
    participant API as FastAPI Server
    participant Redis as Redis Queue
    participant Worker as Worker Process
    participant Claude as Claude CLI

    User->>CLI: ./ccrs chat "message" --wait
    CLI->>API: POST /execute
    API->>Redis: Store job data
    API->>Redis: Push job ID to queue
    API->>CLI: Return job ID

    Worker->>Redis: BRPOP job from queue
    Redis->>Worker: Return job ID
    Worker->>Redis: Update status: running
    Worker->>Claude: Execute command
    Claude->>Worker: Return response
    Worker->>Redis: Store result & status: completed

    loop Poll for completion
        CLI->>API: GET /jobs/{job_id}
        API->>Redis: Get job status
        Redis->>API: Return job data
        API->>CLI: Return status
    end

    CLI->>User: Display Claude response
```

## 🧩 Core Components

### 1. CCRS CLI (Client)
**File:** `cli.py`
**Purpose:** User interface and API client

**Responsibilities:**
- Command-line interface for user interactions
- HTTP client for API communication
- Job submission and status polling
- Result formatting and display

**Key Features:**
- Click-based command structure
- Automatic job polling with `--wait`
- Multi-tenant support
- Environment variable configuration

### 2. FastAPI Server (API)
**File:** `app.py`
**Container:** `ccrs-api`

**Responsibilities:**
- REST API endpoints
- Job validation and queuing
- Health checks and monitoring
- Multi-tenant job isolation

**Key Endpoints:**
```python
GET  /              # Service info
GET  /health        # Health check
POST /execute       # Submit job
GET  /jobs/{job_id} # Job status
```

**Architecture Pattern:**
- Stateless request handling
- Redis-backed job storage
- Pydantic model validation
- FastAPI automatic documentation

### 3. Redis Queue (Storage)
**Container:** `ccrs-redis`
**Port:** `6380` (host) → `6379` (container)

**Responsibilities:**
- Job queue management
- Result storage and caching
- Multi-tenant data isolation
- Persistent job history

**Data Structures:**
```redis
# Job Queue
ccrs:job_queue → List of job IDs

# Job Storage
job:{job_id} → JSON job data with status/result

# Example:
job:ccrs-abc123 → {
  "job_id": "ccrs-abc123",
  "tenant_id": "demo",
  "operation": "chat",
  "message": "Hello Claude!",
  "status": "completed",
  "result": "Hello! How can I help?",
  "created_at": "2024-01-25T10:00:00Z",
  "completed_at": "2024-01-25T10:00:05Z"
}
```

### 4. Worker Process (Processor)
**File:** `worker.py`
**Location:** Host system

**Responsibilities:**
- Job queue consumption
- Claude CLI execution
- Result processing and storage
- Error handling and recovery

**Architecture Pattern:**
- Blocking queue consumer (`brpop`)
- Direct Claude CLI subprocess execution
- Graceful error handling
- Automatic reconnection on failures

## 🔄 Data Flow & Job Lifecycle

### Component Interaction Diagram

```mermaid
graph TB
    subgraph "User Interface Layer"
        User[👤 User]
        CLI[CCRS CLI]
    end

    subgraph "API Layer"
        API[FastAPI Server]
        Health[Health Endpoint]
        Execute[Execute Endpoint]
        Status[Status Endpoint]
    end

    subgraph "Storage Layer"
        Redis[(Redis Queue)]
        JobQueue[ccrs:job_queue]
        JobData[job:job-id]
    end

    subgraph "Processing Layer"
        Worker[Worker Process]
        Claude[Claude CLI]
    end

    User --> CLI
    CLI --> Execute
    CLI --> Status
    CLI --> Health

    Execute --> API
    Status --> API
    Health --> API

    API --> Redis
    Redis --> JobQueue
    Redis --> JobData

    Worker --> JobQueue
    Worker --> JobData
    Worker --> Claude

    style User fill:#e1f5fe
    style Claude fill:#fff3e0
    style API fill:#f3e5f5
    style Redis fill:#ffebee
    style Worker fill:#e8f5e8
    style CLI fill:#fff9c4
```

### Job State Machine

```mermaid
stateDiagram-v2
    [*] --> queued : Job submitted
    queued --> running : Worker picks up job
    running --> completed : Claude execution successful
    running --> failed : Claude execution fails
    running --> timeout : Execution exceeds timeout
    completed --> [*]
    failed --> [*]
    timeout --> [*]

    state running {
        [*] --> executing
        executing --> processing_result
        processing_result --> storing_result
        storing_result --> [*]
    }
```

### Detailed Job Processing Flow

```mermaid
flowchart TD
    A[User Command] --> B{Validate Input}
    B -->|Valid| C[Generate HTTP Request]
    B -->|Invalid| D[Show Error]
    C --> E[POST /execute]
    E --> F[Generate Job ID]
    F --> G[Store Job Data in Redis]
    G --> H[Add Job ID to Queue]
    H --> I[Return Job ID to CLI]
    I --> J{--wait flag?}
    J -->|Yes| K[Start Polling]
    J -->|No| L[Show Job ID & Exit]

    K --> M[GET /jobs/job-id]
    M --> N{Job Status?}
    N -->|queued/running| O[Wait & Retry]
    N -->|completed| P[Display Result]
    N -->|failed| Q[Display Error]
    N -->|timeout| R[Show Timeout Message]

    O --> M
    P --> S[End]
    Q --> S
    R --> S
    L --> S
    D --> S

    style A fill:#e1f5fe
    style S fill:#e8f5e8
    style D fill:#ffcdd2
    style Q fill:#ffcdd2
    style R fill:#fff3e0
```

## 🌐 Network Architecture

### Hybrid Deployment Network Diagram

```mermaid
graph TB
    subgraph "Host System (localhost)"
        User[👤 User]
        CLI[CCRS CLI<br/>Python Client]
        Worker[Worker Process<br/>Port: 6380 client]
        Claude[Claude CLI<br/>Local Binary]

        User --> CLI
        Worker --> Claude
    end

    subgraph "Docker Network (ccrs_default)"
        API[FastAPI Server<br/>Container Port: 8000]
        Redis[Redis Server<br/>Container Port: 6379]

        API --> Redis
    end

    subgraph "Port Mappings"
        Port8001[Host Port 8001]
        Port6380[Host Port 6380]

        Port8001 --> API
        Port6380 --> Redis
    end

    CLI -.->|HTTP| Port8001
    Worker -.->|TCP| Port6380

    style User fill:#e1f5fe
    style Claude fill:#fff3e0
    style API fill:#f3e5f5
    style Redis fill:#ffebee
    style Worker fill:#e8f5e8
    style CLI fill:#fff9c4
```

### Network Configuration Details

```mermaid
graph LR
    subgraph "External Access"
        ExtUser[External User]
        ExtApp[External App]
    end

    subgraph "Host Network Interface"
        HostAPI["localhost:8001<br/>FastAPI Endpoint"]
        HostRedis["localhost:6380<br/>Redis Access"]
    end

    subgraph "Docker Internal Network"
        IntAPI["ccrs-api:8000<br/>Internal API"]
        IntRedis["ccrs-redis:6379<br/>Internal Redis"]
    end

    subgraph "Host Processes"
        CLIProc[CCRS CLI Process]
        WorkerProc[Worker Process]
        ClaudeProc[Claude CLI Process]
    end

    ExtUser --> HostAPI
    ExtApp --> HostAPI
    CLIProc --> HostAPI
    WorkerProc --> HostRedis

    HostAPI --> IntAPI
    HostRedis --> IntRedis

    WorkerProc --> ClaudeProc

    style HostAPI fill:#f3e5f5
    style HostRedis fill:#ffebee
    style IntAPI fill:#f3e5f5
    style IntRedis fill:#ffebee
```

### Container Networking Configuration

```yaml
# docker-compose.hybrid.yml
networks:
  default:
    driver: bridge

services:
  api:
    container_name: ccrs-api
    ports: ["8001:8000"]
    environment:
      REDIS_HOST: redis          # Container-to-container
      REDIS_PORT: 6379          # Internal port
    networks:
      - default

  redis:
    container_name: ccrs-redis
    ports: ["6380:6379"]
    networks:
      - default

# Worker (host) configuration:
# REDIS_HOST=localhost     # Host to container
# REDIS_PORT=6380         # Mapped port
```

### Security Considerations
- **Container Isolation**: API and Redis run in isolated containers
- **Host Access**: Worker has controlled access to host Claude CLI
- **Port Binding**: Only necessary ports exposed to host
- **Network Segmentation**: Containers communicate via internal network

## 🏗️ Technology Stack

### Backend Stack
```yaml
API Server:
  Framework: FastAPI 0.104+
  Language: Python 3.11+
  Validation: Pydantic v1 (for stability)
  Server: Uvicorn ASGI

Queue System:
  Database: Redis 7-alpine
  Client: redis-py
  Pattern: Blocking queue consumer (brpop)

Worker System:
  Runtime: Python 3.11+
  Subprocess: Claude CLI direct execution
  Process Management: PID file tracking
  Logging: File-based in daemon mode
```

### Infrastructure Stack
```yaml
Containerization:
  Engine: Docker 20.10+
  Orchestration: Docker Compose v2
  Base Images: python:3.11-slim, redis:7-alpine

Host Integration:
  CLI Framework: Click 8.0+
  HTTP Client: requests
  Process Management: subprocess, signal handling
```

### Development Stack
```yaml
Testing:
  Framework: pytest
  Mocking: unittest.mock
  Redis: fakeredis (in-memory)
  HTTP Testing: httpx

Code Quality:
  Type Hints: Python typing
  Validation: Pydantic models
  Error Handling: Comprehensive try/except
```

## 🔧 Configuration Architecture

### Environment-Based Configuration

**API Container:**
```bash
REDIS_HOST=redis          # Internal container name
REDIS_PORT=6379          # Internal container port
```

**Worker Process:**
```bash
REDIS_HOST=localhost     # Host Redis access
REDIS_PORT=6380         # Host-mapped Redis port
```

**CLI Client:**
```bash
CCRS_URL=http://localhost:8001  # API endpoint
CCRS_TENANT=demo                # Default tenant
```

### Configuration Hierarchy
1. **Environment Variables** (highest priority)
2. **Command-line flags** (medium priority)
3. **Default values** (lowest priority)

### Multi-Environment Support
```bash
# Development
export CCRS_URL="http://localhost:8001"
export CCRS_TENANT="dev"

# Staging
export CCRS_URL="http://staging-ccrs:8001"
export CCRS_TENANT="staging"

# Production
export CCRS_URL="http://prod-ccrs:8001"
export CCRS_TENANT="production"
```

## 🚀 Deployment Architecture

### Hybrid Deployment Model

**Containers (Infrastructure):**
- **Pros**: Consistent environment, easy scaling, isolated dependencies
- **Cons**: No direct host access, complex volume mounting
- **Used for**: API server, Redis queue

**Host Processes (Integration):**
- **Pros**: Direct CLI access, simple debugging, native performance
- **Cons**: Host dependencies, environment variations
- **Used for**: Worker process, CLI client

### Production Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer Layer"
        LB[Load Balancer<br/>nginx/HAProxy<br/>:80, :443]
    end

    subgraph "API Layer (Containers)"
        API1[API Instance 1<br/>ccrs-api-1<br/>:8000]
        API2[API Instance 2<br/>ccrs-api-2<br/>:8000]
        API3[API Instance 3<br/>ccrs-api-3<br/>:8000]
    end

    subgraph "Storage Layer"
        RedisCluster[Redis Cluster<br/>High Availability<br/>:6379]
        RedisMaster[Redis Master]
        RedisSlave1[Redis Slave 1]
        RedisSlave2[Redis Slave 2]
    end

    subgraph "Processing Layer"
        Host1[Worker Host 1<br/>2x Worker Processes]
        Host2[Worker Host 2<br/>2x Worker Processes]
        Host3[Worker Host 3<br/>2x Worker Processes]

        Host1Worker1[Worker 1A<br/>PID: 1001]
        Host1Worker2[Worker 1B<br/>PID: 1002]
        Host2Worker1[Worker 2A<br/>PID: 2001]
        Host2Worker2[Worker 2B<br/>PID: 2002]
        Host3Worker1[Worker 3A<br/>PID: 3001]
        Host3Worker2[Worker 3B<br/>PID: 3002]

        Host1 --> Host1Worker1
        Host1 --> Host1Worker2
        Host2 --> Host2Worker1
        Host2 --> Host2Worker2
        Host3 --> Host3Worker1
        Host3 --> Host3Worker2
    end

    subgraph "External Integrations"
        Claude1[Claude CLI<br/>Host 1]
        Claude2[Claude CLI<br/>Host 2]
        Claude3[Claude CLI<br/>Host 3]
    end

    Internet[🌐 Internet] --> LB
    LB --> API1
    LB --> API2
    LB --> API3

    API1 --> RedisCluster
    API2 --> RedisCluster
    API3 --> RedisCluster

    RedisCluster --> RedisMaster
    RedisCluster --> RedisSlave1
    RedisCluster --> RedisSlave2

    Host1Worker1 --> RedisCluster
    Host1Worker2 --> RedisCluster
    Host2Worker1 --> RedisCluster
    Host2Worker2 --> RedisCluster
    Host3Worker1 --> RedisCluster
    Host3Worker2 --> RedisCluster

    Host1Worker1 --> Claude1
    Host1Worker2 --> Claude1
    Host2Worker1 --> Claude2
    Host2Worker2 --> Claude2
    Host3Worker1 --> Claude3
    Host3Worker2 --> Claude3

    style LB fill:#e3f2fd
    style API1 fill:#f3e5f5
    style API2 fill:#f3e5f5
    style API3 fill:#f3e5f5
    style RedisCluster fill:#ffebee
    style Claude1 fill:#fff3e0
    style Claude2 fill:#fff3e0
    style Claude3 fill:#fff3e0
```

### Scaling Strategy Diagram

```mermaid
graph LR
    subgraph "Horizontal Scaling"
        subgraph "API Layer"
            direction TB
            API_Current[Current: 2 instances]
            API_Scaled[Scaled: 4+ instances]
            API_Current --> API_Scaled
        end

        subgraph "Worker Layer"
            direction TB
            Worker_Current[Current: 2 hosts, 4 workers]
            Worker_Scaled[Scaled: 4+ hosts, 8+ workers]
            Worker_Current --> Worker_Scaled
        end

        subgraph "Storage Layer"
            direction TB
            Redis_Current[Current: Single Redis]
            Redis_Scaled[Scaled: Redis Cluster]
            Redis_Current --> Redis_Scaled
        end
    end

    subgraph "Vertical Scaling"
        subgraph "Resource Scaling"
            CPU[CPU: 2→4+ cores]
            Memory[Memory: 4→8+ GB]
            Storage[Storage: SSD optimization]
        end
    end

    subgraph "Performance Metrics"
        Throughput[Jobs/sec: 10→50+]
        Latency[Response time: <2s]
        Availability[Uptime: 99.9%+]
    end

    style API_Scaled fill:#e8f5e8
    style Worker_Scaled fill:#e8f5e8
    style Redis_Scaled fill:#e8f5e8
    style Throughput fill:#fff3e0
    style Latency fill:#fff3e0
    style Availability fill:#fff3e0
```

## 📊 Monitoring & Observability

### Monitoring Architecture Overview

```mermaid
graph TB
    subgraph "CCRS System"
        API[FastAPI Server]
        Worker[Worker Process]
        Redis[(Redis Queue)]
        Claude[Claude CLI]

        Worker --> Claude
        API --> Redis
        Worker --> Redis
    end

    subgraph "Health Checks"
        APIHealth[GET /health<br/>Every 30s]
        WorkerHealth[Worker Status<br/>Every 60s]
        RedisHealth[Redis Ping<br/>Every 30s]
        ClaudeHealth[Claude CLI Check<br/>On startup]

        API --> APIHealth
        Worker --> WorkerHealth
        Redis --> RedisHealth
        Claude --> ClaudeHealth
    end

    subgraph "Logging Layer"
        APILogs[API Logs<br/>Docker stdout]
        WorkerLogs[Worker Logs<br/>worker.log]
        SystemLogs[System Logs<br/>/var/log]

        API --> APILogs
        Worker --> WorkerLogs
    end

    subgraph "Metrics Collection"
        JobMetrics[Job Metrics<br/>• Queue length<br/>• Processing time<br/>• Success/failure rate]
        SystemMetrics[System Metrics<br/>• CPU/Memory usage<br/>• Network I/O<br/>• Disk usage]
        ClaudeMetrics[Claude Metrics<br/>• Response time<br/>• Token usage<br/>• Error rates]

        Redis --> JobMetrics
        Worker --> ClaudeMetrics
    end

    subgraph "Alerting"
        HealthAlerts[Health Alerts<br/>• API down<br/>• Worker crashed<br/>• Redis disconnected]
        PerformanceAlerts[Performance Alerts<br/>• High queue depth<br/>• Slow responses<br/>• High error rate]

        JobMetrics --> PerformanceAlerts
        APIHealth --> HealthAlerts
        WorkerHealth --> HealthAlerts
        RedisHealth --> HealthAlerts
    end

    style API fill:#f3e5f5
    style Redis fill:#ffebee
    style Worker fill:#e8f5e8
    style Claude fill:#fff3e0
```

### Health Check Flow Diagram

```mermaid
sequenceDiagram
    participant Monitor as Monitoring System
    participant API as FastAPI Health
    participant Redis as Redis Queue
    participant Worker as Worker Process
    participant Claude as Claude CLI

    loop Every 30 seconds
        Monitor->>API: GET /health
        API->>Redis: PING
        Redis-->>API: PONG
        API->>Redis: LLEN ccrs:job_queue
        Redis-->>API: Queue length
        API-->>Monitor: Health response
    end

    loop Every 60 seconds
        Monitor->>Worker: Check PID status
        Worker-->>Monitor: Running/Stopped
        Monitor->>Worker: Check Claude CLI
        Worker->>Claude: which claude
        Claude-->>Worker: /path/to/claude
        Worker-->>Monitor: Claude available
    end

    Note over Monitor: Aggregate status:<br/>✅ All healthy<br/>⚠️ Degraded<br/>❌ Critical
```

### Logging and Observability Stack

```mermaid
graph LR
    subgraph "Log Sources"
        APIContainer[API Container<br/>Docker logs]
        WorkerProcess[Worker Process<br/>worker.log]
        RedisContainer[Redis Container<br/>Docker logs]
        SystemHost[Host System<br/>System logs]
    end

    subgraph "Log Aggregation"
        DockerLogs[docker logs]
        FileTail[tail -f]
        Syslog[systemd journal]
    end

    subgraph "Log Storage"
        LogFiles[Log Files<br/>/var/log/ccrs/]
        RotatedLogs[Rotated Logs<br/>logrotate]
    end

    subgraph "Monitoring Tools"
        CCRSLogs[./ccrs logs]
        StatusCheck[./ccrs status-all]
        WorkerStatus[./ccrs worker status]
    end

    APIContainer --> DockerLogs
    WorkerProcess --> FileTail
    RedisContainer --> DockerLogs
    SystemHost --> Syslog

    DockerLogs --> LogFiles
    FileTail --> LogFiles
    Syslog --> LogFiles

    LogFiles --> RotatedLogs

    LogFiles --> CCRSLogs
    LogFiles --> StatusCheck
    WorkerProcess --> WorkerStatus

    style LogFiles fill:#f3e5f5
    style CCRSLogs fill:#e8f5e8
    style StatusCheck fill:#e8f5e8
    style WorkerStatus fill:#e8f5e8
```

### Health Check Endpoints and Responses

**API Health Endpoint:**
```python
GET /health
Response: {
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2026-01-25T20:00:00Z",
  "dependencies": {
    "redis": "connected",
    "queue_size": 5
  }
}
```

**Worker Health Check:**
```bash
./ccrs worker status
# Output:
# ✅ Claude CLI: /Users/user/.local/bin/claude
# ✅ Worker Process: Running (PID: 12345)
# ✅ Redis Connection: OK (port 6380)
```

## 🔒 Security Architecture

### Threat Model & Mitigations

**API Security:**
- **Input Validation**: Pydantic models prevent malicious input
- **Rate Limiting**: Consider implementing in production
- **Authentication**: Add API keys for production use

**Worker Security:**
- **Subprocess Isolation**: Claude CLI runs in controlled subprocess
- **Resource Limits**: Set timeout and memory limits
- **Error Sanitization**: Prevent information leakage in errors

**Network Security:**
- **Container Isolation**: API and Redis isolated from host
- **Port Exposure**: Only necessary ports exposed
- **Internal Communication**: Containers use internal network

### Production Security Checklist

```yaml
API Security:
  □ Add API authentication (API keys/JWT)
  □ Implement rate limiting
  □ Add request size limits
  □ Configure CORS properly
  □ Use HTTPS in production

Worker Security:
  □ Run worker with limited user privileges
  □ Set subprocess timeouts
  □ Sanitize Claude CLI output
  □ Monitor for resource abuse

Infrastructure Security:
  □ Use official base images
  □ Keep containers updated
  □ Use secrets management
  □ Enable Docker content trust
  □ Configure firewall rules
```

## 🔧 Extension Points

### Custom Operations

**Adding New Operations:**
1. Update `models.py` for new request types
2. Add handler in `worker.py`
3. Add CLI command in `cli.py`

Example:
```python
# In worker.py
elif operation == "analyze":
    cmd = ["claude", "--analyze", "--format", "json", message]

# In cli.py
@cli.command()
def analyze(file_path, wait=False):
    # Implementation
```

### Custom Backends

**Claude CLI Alternatives:**
```python
# Worker backend interface
class BackendInterface:
    def execute(self, operation: str, message: str) -> dict:
        pass

class ClaudeCLIBackend(BackendInterface):
    def execute(self, operation, message):
        # Current implementation

class CustomBackend(BackendInterface):
    def execute(self, operation, message):
        # Custom implementation
```

### Monitoring Integration

**Prometheus Metrics:**
```python
# Add to app.py
from prometheus_client import Counter, Histogram

job_counter = Counter('ccrs_jobs_total', 'Total jobs processed')
job_duration = Histogram('ccrs_job_duration_seconds', 'Job processing time')

@app.get("/metrics")
def metrics():
    return Response(generate_latest())
```

---

**This architecture provides a solid foundation for reliable, scalable Claude Code routing with clear separation of concerns and well-defined extension points.**