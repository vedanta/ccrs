# crelay — Architecture (Proposed)

> **crelay** (*Claude + relay*) is a clean-room Go rewrite of CCRS, keeping the
> original idea and hybrid architecture. It relays a request to the Claude Code
> CLI and returns the result. The flimsy hand-rolled `LPUSH`/`BRPOP` queue is
> replaced with a real job queue (**Asynq**), and the Python client + Bash
> wrapper + two workers collapse into **two Go binaries**: `crelay` (client) and
> `crelayd` (server).

## Naming

**crelay** — pronounced *cre-lay* (a blend of **Cl**aude + **relay**, spoken as one word).

- **crelay** — the client binary (frontend / interaction). `crelay chat "..."`
- **crelayd** — the server daemon (backend). `crelayd serve`, `crelayd worker`

(Formerly *CCRS — Claude Code Routing Service*. Renamed during the rewrite:
"routing" was inaccurate — the service **queues and relays** work to Claude, it
doesn't route between destinations.)

## Target Stack

| Concern | Python (CCRS, today) | Go (crelay, proposed) |
|---|---|---|
| Client / CLI | Bash wrapper + `ccrs.bat` + `cli.py` (Click) | **`crelay`** binary — [Cobra](https://github.com/spf13/cobra) |
| API server | `app.py` (FastAPI) | **`crelayd serve`** — `net/http` + [chi](https://github.com/go-chi/chi) |
| Worker | `worker.py` + `worker-production.py` | **`crelayd worker`** — [Asynq](https://github.com/hibiken/asynq) handler |
| Queue | Redis `LPUSH`/`BRPOP` (at-most-once) | **Asynq over Redis** (at-least-once, retries, DLQ, reclaim) |
| Job store | JSON blobs in Redis | Asynq task state + result store in Redis |
| Claude exec | `subprocess.run` | `os/exec` `CommandContext` |
| Logging | `print()` | `log/slog` (structured) |
| Config | env vars | env + flags (Cobra/Viper) |
| Observability | none | **asynqmon** dashboard |
| Tests | pytest + fakeredis + httpx | `testing` + `miniredis` + `httptest` |

## Component Architecture

```mermaid
flowchart TB
    subgraph client["🖥️ FRONTEND — crelay (client binary)"]
        direction TB
        CLI["Cobra CLI<br/>chat · command · status · health"]
        HTTPC["HTTP client"]
        CLI --> HTTPC
    end

    subgraph backend["⚙️ BACKEND — crelayd (server binary)"]
        direction TB

        subgraph api["crelayd serve  (API)"]
            ROUTER["chi router<br/>/execute · /jobs/:id · /health"]
            AUTH["API-key auth<br/>middleware"]
            ENQ["Asynq client<br/>(enqueue task)"]
            ROUTER --> AUTH --> ENQ
        end

        subgraph wrk["crelayd worker  (executor)"]
            SRV["Asynq server<br/>worker pool (N goroutines)"]
            HANDLER["job handler<br/>retries · timeout · backoff"]
            EXEC["claude executor<br/>os/exec CommandContext"]
            SRV --> HANDLER --> EXEC
        end
    end

    subgraph infra["📦 INFRASTRUCTURE"]
        REDIS[("Redis 7<br/>Asynq broker + result store")]
        MON["asynqmon<br/>web dashboard"]
    end

    CLAUDE["🤖 Claude Code CLI<br/>(on host, authenticated)"]

    HTTPC -- "HTTP/JSON" --> ROUTER
    ENQ -- "enqueue" --> REDIS
    REDIS -- "dequeue" --> SRV
    HANDLER -- "store result / status" --> REDIS
    ROUTER -- "read job state" --> REDIS
    EXEC -- "exec (stdout/stderr)" --> CLAUDE
    MON -. "observe queues" .-> REDIS

    classDef front fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef back fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef store fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef ext fill:#f3e8ff,stroke:#9333ea,color:#581c87
    class CLI,HTTPC front
    class ROUTER,AUTH,ENQ,SRV,HANDLER,EXEC back
    class REDIS,MON store
    class CLAUDE ext
```

## Deployment Topology (Hybrid — unchanged idea)

The worker stays on the **host** for authenticated `claude` CLI access; API + Redis
stay **containerized**. The client runs anywhere.

```mermaid
flowchart LR
    subgraph laptop["Any machine"]
        C["crelay (client)"]
    end

    subgraph host["Host machine"]
        direction TB
        W["crelayd worker<br/>(host process)"]
        CC["claude CLI<br/>(authenticated)"]
        W -->|os/exec| CC

        subgraph docker["Docker Compose"]
            A["crelayd serve<br/>(container :8001)"]
            R[("Redis :6380")]
            M["asynqmon :8080"]
        end
    end

    C -->|HTTP :8001| A
    A -->|enqueue| R
    R -->|dequeue| W
    W -->|result| R
    A -->|read| R
    M -.->|observe| R
```

## Job Lifecycle (at-least-once with retries)

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant C as crelay (client)
    participant A as crelayd serve
    participant Q as Redis / Asynq
    participant W as crelayd worker
    participant CL as claude CLI

    U->>C: crelay chat "..." --wait
    C->>A: POST /execute  (API key)
    A->>A: auth + validate tenant
    A->>Q: Enqueue(task) → task_id
    A-->>C: 202 { job_id, status: queued }

    loop worker pool
        Q-->>W: dequeue task (lease)
        W->>Q: status = running
        W->>CL: exec claude (with timeout)
        alt success
            CL-->>W: stdout
            W->>Q: status = completed + result
        else non-zero / timeout
            CL-->>W: stderr / timeout
            W->>Q: retry w/ backoff (n attempts)
            Note over W,Q: exhausted → archived (dead-letter)
        else worker crash mid-job
            Note over Q: lease expires → task reclaimed → redelivered
        end
    end

    loop poll (--wait)
        C->>A: GET /jobs/{job_id}
        A->>Q: read task state
        A-->>C: status (+ result when done)
    end
    C-->>U: render result
```

## Proposed Module Layout

```
crelay/
├── go.mod                  # module github.com/vedanta/crelay
├── cmd/
│   ├── crelay/        # client binary (frontend)
│   │   └── main.go    # Cobra root: chat/command/status/health
│   └── crelayd/       # server binary (backend)
│       └── main.go    # Cobra root: serve / worker
├── internal/
│   ├── api/           # chi handlers, request/response models, auth middleware
│   ├── worker/        # Asynq handler + claude executor
│   ├── queue/         # Asynq client/server wiring, task payloads
│   ├── job/           # shared job types (wire contract client↔server)
│   ├── claude/        # os/exec wrapper around the claude CLI
│   └── config/        # env + flag loading
├── deploy/
│   ├── docker-compose.yml
│   └── Dockerfile
└── ARCHITECTURE-GO.md
```

**Key shift from Python:** `internal/job` is the single source of truth for the
wire contract, imported by both `crelay` (client) and `crelayd` (server) — no more
drift between `models.py` and the CLI's hand-built dicts.

## What Carries Over vs. Changes

**Kept (the good bones):**
- Hybrid deploy — worker on host for authenticated Claude access
- Redis as the backing store / broker
- Tenant-scoped jobs, async submit + poll lifecycle
- `chat` / `command` operations

**Changed (the maturity gaps):**
- Reliable queue (Asynq) → retries, dead-letter, crash reclaim, worker pool
- One client binary + one server binary (was: Bash + bat + cli.py + 2 workers)
- API-key auth + tightened CORS
- Structured logging (`slog`) + queue dashboard (asynqmon)
- Single typed wire contract shared by client and server

---

**Status:** proposal for review. Nothing implemented yet — this documents the
target before writing Go.

> **Note:** the git repo itself is still named `ccrs`. Renaming the GitHub repo
> to `crelay` (and the local dir + module path) is a separate step to do when we
> start the actual rewrite.
