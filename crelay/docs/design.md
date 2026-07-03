# crelay — Design (v1, for review)

> Detailed design for the crelay rewrite. Companion to
> [`architecture.md`](./architecture.md). This nails the API contract, the CLI,
> configuration, and queue behavior before any Go is written.
>
> **Status:** proposal for review. `v1` scope.

---

## 1. Locked decisions

| # | Decision | Choice |
|---|---|---|
| 1 | **Auth & tenancy** | API keys map to tenants. Client sends `Authorization: Bearer <key>`; server derives the tenant from the key. No spoofable `--tenant`. |
| 2 | **API contract** | Clean, versioned REST under `/v1`. No CCRS wire-compat. |
| 3 | **Operations (v1)** | `chat` + `command` only. Payload leaves room for `agent`/`script` later without a breaking change. |
| 4 | **`command` safety** | Allowlisted, default-deny. `command` is rejected unless the command token is in the server's allowlist. `chat` is open. |

---

## 2. Concepts

- **Job** — one submitted operation. Has an `id`, a `status`, and eventually a `result` or `error`.
- **Operation** — `chat` (free-form prompt → Claude) or `command` (a Claude slash-command like `/help`).
- **Tenant** — logical owner of a job, resolved from the API key. Jobs are scoped to their tenant; a tenant can only read its own jobs.
- **Status** — `queued → running → (completed | failed)`.

### Job ID
Format `job_<12 hex>`, e.g. `job_a1b2c3d4e5f6`. Opaque; do not parse.

---

## 3. HTTP API

Base path: **`/v1`**. All requests/responses are JSON (`Content-Type: application/json`).
All endpoints except `/v1/health` require auth.

### Auth
```
Authorization: Bearer <api-key>
```
- Missing/malformed → `401 unauthorized`.
- Unknown key → `401 unauthorized`.
- The key resolves to a tenant server-side; the client never names a tenant.

### Error envelope
Every non-2xx response uses:
```json
{ "error": { "code": "unauthorized", "message": "missing or invalid API key" } }
```

| HTTP | `code` | When |
|---|---|---|
| 400 | `invalid_request` | Malformed body, unknown `operation`, empty `message` |
| 401 | `unauthorized` | Missing/invalid API key |
| 403 | `command_not_allowed` | `operation=command` but command not in allowlist |
| 404 | `not_found` | Job id unknown, or owned by another tenant |
| 503 | `unavailable` | Redis / queue down |

---

### `POST /v1/jobs` — submit a job

Submits an operation and returns immediately (async). Poll `GET /v1/jobs/{id}` for the result.

**Request**
```json
{
  "operation": "chat",
  "message": "Explain Go channels in two sentences.",
  "timeout_seconds": 300
}
```
| Field | Type | Required | Notes |
|---|---|---|---|
| `operation` | string | yes | `chat` \| `command` |
| `message` | string | yes | Prompt (chat) or command string like `/help` (command) |
| `timeout_seconds` | int | no | Default `300`. Max `900`. Bounds the `claude` execution. |

**Response — `202 Accepted`**
```json
{
  "id": "job_a1b2c3d4e5f6",
  "tenant": "acme",
  "operation": "chat",
  "status": "queued",
  "created_at": "2026-07-02T12:00:00Z"
}
```

**`command` example**
```json
{ "operation": "command", "message": "/help" }
```
→ `403` if `/help` is not in the server allowlist:
```json
{ "error": { "code": "command_not_allowed", "message": "command '/help' is not permitted" } }
```

---

### `GET /v1/jobs/{id}` — job status & result

Returns the current state. A job only visible to its owning tenant (else `404`).

**Response — `200 OK`**
```json
{
  "id": "job_a1b2c3d4e5f6",
  "tenant": "acme",
  "operation": "chat",
  "status": "completed",
  "created_at": "2026-07-02T12:00:00Z",
  "started_at":  "2026-07-02T12:00:01Z",
  "completed_at":"2026-07-02T12:00:04Z",
  "result": "Channels are typed conduits ...",
  "error": null,
  "attempts": 1
}
```
| Field | Notes |
|---|---|
| `status` | `queued` \| `running` \| `completed` \| `failed` |
| `result` | Present when `completed` (Claude stdout) |
| `error` | Present when `failed` |
| `attempts` | Number of worker attempts so far (retries) |

Job records expire from the store after `job.ttl` (default 1h).

---

### `GET /v1/health` — health check (no auth)

**Response — `200 OK`** (or `503` when degraded)
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "time": "2026-07-02T12:00:00Z",
  "checks": { "redis": "ok", "queue_depth": 3 }
}
```
`status`: `healthy` (all checks ok) \| `degraded` (Redis unreachable → `503`).

---

## 4. CLI — `crelay` (client)

The frontend binary. Talks to `crelayd serve` over HTTP. Ships as a single static binary.

### Global flags / environment
| Flag | Env | Default | Purpose |
|---|---|---|---|
| `--url` | `CRELAY_URL` | `http://localhost:8001` | crelayd API base URL |
| `--api-key` | `CRELAY_API_KEY` | — | Bearer key (tenant is derived from it) |
| `--json` | — | off | Print raw JSON instead of formatted output |

> There is intentionally **no `--tenant` flag** — the tenant is whatever the API key maps to.

### Commands

```
crelay chat <message>      [--wait] [--timeout <sec>] [--json]
crelay command <cmd>       [--wait] [--timeout <sec>] [--json]
crelay status <job-id>     [--json]
crelay health              [--json]
crelay version
```

| Command | Args | Options | Description |
|---|---|---|---|
| `chat` | `<message>` | `--wait`, `--timeout` (300) | Submit a chat prompt |
| `command` | `<cmd>` | `--wait`, `--timeout` (300) | Submit an allowlisted Claude command |
| `status` | `<job-id>` | — | Fetch a job's status/result |
| `health` | — | — | Check server health |
| `version` | — | — | Print client version |

- `--wait` polls `GET /v1/jobs/{id}` until the job finishes (or `--timeout` elapses), then prints the result. Without `--wait`, the command prints the `job_id` and exits.
- Poll cadence: every 2s, capped by `--timeout`.

### Exit codes
| Code | Meaning |
|---|---|
| 0 | Success (job completed, or submitted without `--wait`) |
| 1 | Job failed |
| 2 | Usage / bad arguments |
| 3 | Network / server error |
| 4 | Timed out waiting (`--wait`) |

### Usage examples

```bash
# Configure once
export CRELAY_URL="http://localhost:8001"
export CRELAY_API_KEY="sk_live_acme_xxx"

# Fire-and-forget: prints a job id
crelay chat "Explain Go channels"
# → job_a1b2c3d4e5f6

# Submit and wait for the answer
crelay chat "Explain Go channels" --wait
# → (streams status, then prints Claude's reply)

# Longer task with a bigger timeout
crelay chat "Refactor this module and summarize" --wait --timeout 600

# Run an allowlisted command
crelay command "/help" --wait

# Check a job later
crelay status job_a1b2c3d4e5f6

# Machine-readable output (scripts / jq)
crelay status job_a1b2c3d4e5f6 --json | jq '.status'
crelay health --json

# Point at a remote server for one call
crelay --url https://crelay.internal chat "ping" --wait
```

---

## 5. Server — `crelayd`

The backend binary. Two subcommands sharing config and internal packages.

```
crelayd serve    [--addr <addr>] [--redis <addr>] [--config <file>]
crelayd worker   [--redis <addr>] [--concurrency <n>] [--config <file>]
crelayd version
```

| Subcommand | Role | Key flags |
|---|---|---|
| `serve` | HTTP API (enqueues jobs, serves status) | `--addr` (`:8000`), `--redis`, `--config` |
| `worker` | Asynq consumer; runs `claude` | `--concurrency` (5), `--redis`, `--config` |

Both handle `SIGINT`/`SIGTERM` with graceful shutdown (drain in-flight, then exit).

### Server configuration

Config file (YAML) is primary — it holds secrets (API keys) and the command
allowlist. Env vars override simple scalars for container use.

```yaml
# crelay.yaml
redis:
  addr: localhost:6380

api:
  addr: ":8000"

# API key → tenant mapping (auth + tenancy in one place)
tenants:
  - name: acme
    key:  sk_live_acme_xxx
  - name: demo
    key:  sk_demo_yyy

# command operation: default-deny allowlist
commands:
  allowlist:
    - /help
    - /status

worker:
  concurrency: 5
  max_retries: 3

job:
  ttl: 1h            # how long job records are retained/readable
  default_timeout: 300s
  max_timeout: 900s
```

| Env var | Overrides | Default |
|---|---|---|
| `CRELAY_REDIS_ADDR` | `redis.addr` | `localhost:6380` |
| `CRELAY_API_ADDR` | `api.addr` | `:8000` |
| `CRELAY_CONCURRENCY` | `worker.concurrency` | `5` |
| `CRELAY_CONFIG` | config file path | `./crelay.yaml` |
| `CRELAY_TENANTS` | inline `name:key,...` (simple deploys) | — |

---

## 6. Queue behavior (Asynq)

- **Task type:** `job:process`, payload `{ "id": "job_xxx" }`. The full job record lives in Redis (`crelay:job:{id}`); the task just carries the id.
- **Delivery:** at-least-once. Worker leases a task; a crash mid-run → lease expires → task is redelivered (fixes the CCRS "stuck in running forever").
- **Retry policy:**
  - `claude` **timeout** or **spawn/transient error** → retry with exponential backoff, up to `max_retries` (default 3). On the final failed attempt, job → `failed`.
  - `claude` **non-zero exit** (deterministic business failure) → **no retry** (`SkipRetry`); job → `failed` immediately with stderr.
- **Timeout:** the job's `timeout_seconds` bounds the `claude` process (via `exec.CommandContext`) and the Asynq task deadline.
- **Retention:** completed/failed Asynq tasks retained ~24h for the dashboard; our own job records honor `job.ttl` (default 1h).
- **Observability:** `asynqmon` dashboard for queue depth, in-flight, retries, archived (dead-letter).

### Job lifecycle → status mapping
| Phase | Job status |
|---|---|
| Enqueued by API | `queued` |
| Worker picks up, before exec | `running` |
| `claude` exits 0 | `completed` (+`result`) |
| Non-zero exit, or retries exhausted | `failed` (+`error`) |

---

## 7. Claude execution

| Operation | Command run |
|---|---|
| `chat` | `claude --print --output-format text <message>` |
| `command` | `claude <command>` (only if `<command>` ∈ allowlist) |

- Run via `exec.CommandContext` with the job timeout; inherits the host env (so the worker's authenticated `claude` session is used).
- `stdout` → `result` on success; `stderr` → `error` on non-zero exit.
- If the `claude` binary is absent, the worker **fails fast at startup** (unlike CCRS's silent mock fallback). A separate `--mock` flag can enable echo-mode for local dev/testing.

---

## 8. Cross-cutting defaults

| Concern | Default |
|---|---|
| Logging | `log/slog`, JSON; fields: `component`, `job_id`, `tenant`, `operation`, `status`, `attempt`, `duration_ms` |
| Shutdown | `signal.NotifyContext(SIGINT, SIGTERM)` → drain in-flight, then exit |
| CORS | Off by default; allowlist origins via config if a browser client is ever needed (no `*` + credentials) |
| Redis keys | Jobs: `crelay:job:{id}`; Asynq owns `asynq:*` |
| Versioning | API under `/v1`; binaries report semver (`0.1.0` at start) |

---

## 9. Explicitly out of scope for v1 (designed-for, not built)

- `agent` / `script` operations (payload already accommodates new `operation` values)
- Rate limiting (`429` code reserved)
- Streaming responses (poll-only for now)
- Multi-queue priorities (single default queue in v1)
- Per-tenant quotas / billing

---

**Review checklist:** endpoints (§3), CLI surface + examples (§4), server config shape (§5), retry/allowlist semantics (§6–7). Flag anything to change and I'll revise before we scaffold Go.
