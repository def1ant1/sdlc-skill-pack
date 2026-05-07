# Service Patterns

## Service Architecture

### Service Types

| Type | Purpose | Characteristics |
|---|---|---|
| API Service | Serves synchronous HTTP requests | Stateless; horizontally scalable |
| Worker | Processes async jobs from queue | Stateful job context; ack/nack |
| Scheduler | Triggers time-based jobs | Single leader (distributed lock) |
| Stream Processor | Consumes event streams | At-least-once; idempotent handlers |
| Gateway | Routes, authenticates, rate-limits | No business logic |

---

## Service Template Structure

```
services/<service-name>/
  cmd/
    server/main.go    # entry point
  internal/
    handler/          # HTTP handlers (thin — delegate to domain)
    domain/           # business logic
    repository/       # data access (interface + implementation)
    service/          # orchestration of domain operations
  pkg/
    client/           # generated client for other services to import
  api/
    openapi.yaml      # the source-of-truth spec
  migrations/         # DB migration files (numbered, immutable)
  Dockerfile
  README.md           # service overview, local run instructions
```

---

## Dependency Injection

Use constructor injection exclusively. No service locators, no global state.

```go
type AccountService struct {
    repo   AccountRepository
    events EventPublisher
    logger *slog.Logger
}

func NewAccountService(repo AccountRepository, events EventPublisher, logger *slog.Logger) *AccountService {
    return &AccountService{repo: repo, events: events, logger: logger}
}
```

---

## Database Patterns

### Repository Interface

```go
type AccountRepository interface {
    GetByID(ctx context.Context, id string) (*Account, error)
    Create(ctx context.Context, account *Account) error
    Update(ctx context.Context, account *Account) error
    Delete(ctx context.Context, id string) error
    List(ctx context.Context, filter ListFilter) ([]*Account, error)
}
```

### Migrations

- One migration file per schema change
- Files named `NNN_description.sql` (e.g., `001_create_accounts.sql`)
- Migrations are immutable once applied; never edit; always add new
- Test migrations in CI against empty database

### Transactions

- Wrap multi-step operations in a single transaction
- Pass `context.Context` to all DB calls for timeout propagation
- Roll back on any error; log rollback event

---

## Async Messaging Pattern

### Producer

```go
event := Event{
    ID:        uuid.New().String(),
    Type:      "account.created",
    Timestamp: time.Now().UTC(),
    Payload:   account,
}
err = eventBus.Publish(ctx, "accounts", event)
```

**Rules**:
- Events are immutable facts; past tense names (`account.created`, not `create.account`)
- Include `correlation_id` from request context in every event
- Events must be idempotent to process (consumers handle duplicate delivery)

### Consumer

```go
func (h *Handler) HandleAccountCreated(ctx context.Context, event Event) error {
    // Check idempotency key — skip if already processed
    if h.processed(event.ID) { return nil }
    // Process
    err := h.doWork(ctx, event.Payload)
    if err != nil { return err }  // nack → retry
    // Mark processed
    return h.markProcessed(event.ID)
}
```

---

## Circuit Breaker

All outbound service calls must use a circuit breaker:

| State | Condition | Behavior |
|---|---|---|
| Closed (normal) | Error rate < threshold | Pass through |
| Open (tripped) | Error rate ≥ threshold | Fail fast; return error immediately |
| Half-open (probe) | Timeout after open | Allow one request to probe health |

Default thresholds: open when 50% errors in a 10-request window; retry after 30s.

---

## Health Check Endpoints

Every service must expose:

```
GET /health/live    → 200 if process is alive
GET /health/ready   → 200 if service can serve requests (DB connected, etc.)
```

Liveness: used by orchestrator to restart crashed pods.
Readiness: used by load balancer to route traffic.

---

## Structured Logging

```go
logger.Info("account created",
    slog.String("account_id", account.ID),
    slog.String("correlation_id", correlationID(ctx)),
    slog.String("service", "account-service"),
    slog.Duration("latency_ms", latency),
)
```

Rules:
- JSON format in all environments
- Required fields: `service`, `correlation_id`, `level`, `timestamp`
- No PII in logs — mask or omit
- Errors include `error` field with message; never include stack traces in production logs