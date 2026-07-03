# crelay

> A job runner that **relays** requests to the Claude Code CLI and returns the result.
> Pronounced *cre-lay* — a blend of **Cl**aude + **relay**.

crelay is a small, reliable service for running Claude Code operations
asynchronously. You submit a `chat` prompt or an allowlisted `command`; crelay
queues it, a worker executes the `claude` CLI, and you poll for the result.
It's a clean-room Go rewrite of an earlier Python prototype (CCRS), keeping the
hybrid architecture and replacing the hand-rolled Redis queue with a real,
reliable job queue.

---

## Status

**Design phase.** The architecture and v1 design are complete and under review;
the Go code is not yet scaffolded.

| Area | State |
|---|---|
| Architecture | ✅ [`docs/architecture.md`](docs/architecture.md) |
| v1 design (API, CLI, config, queue) | ✅ [`docs/design.md`](docs/design.md) |
| Go module / binaries | ⏳ not started |
| Tests | ⏳ not started |
| Deploy (Docker) | ⏳ not started |

> This directory currently lives inside the `ccrs` repo and will be **extracted
> into its own repository** (`github.com/vedanta/crelay`). It is designed to be
> self-contained so the move is clean.

---

## What it does

- **Async job execution** — submit an operation, get a `job_id`, poll for the result.
- **Two operations** — `chat` (free-form prompt → Claude) and `command` (an
  allowlisted Claude slash-command like `/help`).
- **Reliable queue** — at-least-once delivery, retries with backoff, dead-letter,
  and automatic reclaim of jobs orphaned by a worker crash.
- **Auth + tenancy** — API keys map to tenants; a key can only see its own jobs.
- **Two binaries** — a distributable client (`crelay`) and a server daemon (`crelayd`).

## Architecture

Hybrid deployment: the **worker runs on the host** for authenticated `claude`
CLI access; the **API + Redis run in containers**. The client runs anywhere.

```
┌─ crelay (client) ─┐   HTTP    ┌──── crelayd (server) ────┐
│ chat/command/     │ ────────► │ serve  → Asynq enqueue   │
│ status/health     │           │            │  Redis      │
└───────────────────┘           │ worker → claude CLI ─────┘
                                            (on host)
```

**Stack:** Go · [Cobra](https://github.com/spf13/cobra) (CLI) ·
[chi](https://github.com/go-chi/chi) (HTTP) ·
[Asynq](https://github.com/hibiken/asynq) over Redis (queue) ·
`log/slog` (structured logs) · `testing` + `miniredis` (tests).

See [`docs/architecture.md`](docs/architecture.md) for full component,
deployment, and lifecycle diagrams.

## Key decisions (v1)

1. **Auth = tenancy.** Client sends `Authorization: Bearer <key>`; the server
   derives the tenant from the key. There is no spoofable `--tenant` flag.
2. **Clean, versioned REST** under `/v1`. No back-compat with the CCRS wire format.
3. **`chat` + `command` only** in v1; the payload leaves room for `agent`/`script`.
4. **`command` is allowlisted, default-deny** — rejected with `403` unless the
   command token is in the server's allowlist. `chat` is open.

Full rationale and contract in [`docs/design.md`](docs/design.md).

---

## Planned layout

```
crelay/
├── go.mod                 # module github.com/vedanta/crelay
├── cmd/
│   ├── crelay/            # client binary  (chat/command/status/health)
│   └── crelayd/           # server binary  (serve / worker)
├── internal/
│   ├── api/               # chi handlers, request/response models, auth
│   ├── worker/            # Asynq handler + claude executor
│   ├── queue/             # Asynq wiring, task payloads, job store
│   ├── job/               # shared wire contract (client ↔ server)
│   ├── claude/            # os/exec wrapper around the claude CLI
│   └── config/            # env + file config loading
├── deploy/
│   ├── docker-compose.yml
│   └── Dockerfile
└── docs/
    ├── architecture.md
    └── design.md
```

`internal/job` is the single source of truth for the wire contract, imported by
both binaries — the client and server can never drift.

## Planned usage

> Reflects the target once implemented (see `docs/design.md`).

**Build**
```bash
go build ./cmd/crelay      # client
go build ./cmd/crelayd     # server
```

**Run the backend** (worker on host, API + Redis in Docker)
```bash
docker compose -f deploy/docker-compose.yml up -d   # redis + crelayd serve
crelayd worker --config crelay.yaml                 # worker on host (claude access)
```

**Use the client**
```bash
export CRELAY_URL="http://localhost:8001"
export CRELAY_API_KEY="sk_live_acme_xxx"

crelay chat "Explain Go channels" --wait
crelay command "/help" --wait
crelay status job_a1b2c3d4e5f6
crelay health
```

Configuration (API-key→tenant map, command allowlist, worker concurrency,
timeouts) lives in `crelay.yaml`; simple scalars can be overridden by
`CRELAY_*` env vars. See [`docs/design.md`](docs/design.md) §5.

---

## Documentation

| Doc | What |
|---|---|
| [`docs/architecture.md`](docs/architecture.md) | System design, stack, Mermaid diagrams, deployment topology |
| [`docs/design.md`](docs/design.md) | v1 contract: API endpoints, CLI, config, queue & execution semantics |

## Conventions

- **Two binaries, one module.** Shared logic lives in `internal/`; nothing is duplicated between client and server.
- **The wire contract is defined once** in `internal/job` and imported by both sides.
- **Fail fast, log structured.** The worker refuses to start without the `claude`
  CLI (opt-in `--mock` for dev); all logs are structured `slog` with `job_id` /
  `tenant` context.
- **Design docs are the source of truth.** Change the design in `docs/` first,
  then the code — the docs in this repo are written to be built against.

## Lineage

crelay is the Go successor to **CCRS** (Claude Code Routing Service), a Python
FastAPI + Redis prototype. crelay keeps the good bones — hybrid deploy, async
submit/poll, tenant-scoped jobs — and fixes the prototype's gaps: reliable
queue, real auth, structured logging, and a single distributable client binary.
