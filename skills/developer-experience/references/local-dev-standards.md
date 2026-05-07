# Local Development Standards

## Makefile Conventions

Every service must have a `Makefile` at the repository root with these targets:

```makefile
# Standard targets — must work on first run without configuration

.PHONY: dev test lint build clean help

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

dev:  ## Start the service and all dependencies for local development
	docker compose up -d
	air -c .air.toml  # or equivalent hot-reload

test:  ## Run the full test suite locally
	go test ./... -coverprofile=coverage.out
	go tool cover -func=coverage.out | tail -1

test-unit:  ## Run unit tests only (fast, no external deps)
	go test ./internal/... -short

test-integration:  ## Run integration tests (requires Docker)
	go test ./... -run Integration -count=1

lint:  ## Run linter
	golangci-lint run ./...

build:  ## Build the service binary
	go build -o bin/server ./cmd/server

clean:  ## Remove build artifacts
	rm -rf bin/ coverage.out
	docker compose down -v

migrate:  ## Run database migrations
	goose -dir ./migrations postgres "$(DATABASE_URL)" up

seed:  ## Seed the database with development data
	go run ./cmd/seed

generate:  ## Regenerate code (protobuf, OpenAPI clients, mocks)
	go generate ./...
```

---

## Environment Variables

Every service must have a `.env.example` file documenting all environment variables:

```bash
# .env.example — copy to .env for local development
# All variables are required unless marked (optional)

# Service configuration
PORT=8080
LOG_LEVEL=debug        # debug | info | warn | error
ENVIRONMENT=local      # local | staging | production

# Database
DATABASE_URL=postgres://user:pass@localhost:5432/myservice_dev

# Cache
REDIS_URL=redis://localhost:6379

# External services
ANTHROPIC_API_KEY=     # (optional) Only needed for AI features
STRIPE_SECRET_KEY=     # (optional) Only needed for billing features

# Feature flags
FEATURE_NEW_DASHBOARD=false
```

Rules:
- All production-required variables must have an example value (not a real value)
- Sensitive values must have a placeholder: `your_key_here` or empty string
- Optional variables marked with `# (optional)` comment
- `.env.example` is committed; `.env` is gitignored

---

## Docker Compose for Local Development

```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: myservice_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "user"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # Add other dependencies as needed

volumes:
  postgres_data:
```

---

## Dev Container Configuration

Services should provide a `.devcontainer/devcontainer.json` for VS Code and GitHub Codespaces:

```json
{
  "name": "My Service Dev",
  "image": "mcr.microsoft.com/devcontainers/go:1.22",
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/github-cli:1": {}
  },
  "forwardPorts": [8080, 5432, 6379],
  "postCreateCommand": "make dev",
  "customizations": {
    "vscode": {
      "extensions": ["golang.go", "ms-azuretools.vscode-docker"]
    }
  }
}
```

---

## Pre-commit Hooks

Required pre-commit hooks (configured via `.pre-commit-config.yaml` or Husky):

```yaml
repos:
  - repo: local
    hooks:
      - id: lint
        name: Run linter
        entry: make lint
        language: system
        pass_filenames: false
      - id: test-unit
        name: Run unit tests
        entry: make test-unit
        language: system
        pass_filenames: false
      - id: no-secrets
        name: Check for secrets
        entry: gitleaks detect --staged
        language: system
        pass_filenames: false
```

---

## CONTRIBUTING.md Standard Sections

Every repository's `CONTRIBUTING.md` must include:

1. **Prerequisites** — exact versions of tools required (Go 1.22, Node 20, Docker 24, etc.)
2. **Setup** — exact commands from clone to running service (`< 10 commands`)
3. **Running tests** — how to run unit, integration, and specific test cases
4. **Development workflow** — how to create a branch, make changes, and open a PR
5. **Code style** — linter, formatter, and how to fix common linter errors
6. **Troubleshooting** — top 5 most common issues and their solutions

Target: A new engineer should go from `git clone` to `make test` passing in < 15 minutes.