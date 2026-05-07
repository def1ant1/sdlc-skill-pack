# Architecture Inference Rules

Used by `skills/repo-intelligence/SKILL.md` to identify the architectural pattern of a
repository and map its module structure from file system and import signals alone.

---

## Pattern Recognition

| Pattern | Strong Signals | Module Boundary Signal |
|---|---|---|
| **Layered (N-tier)** | Folders named `controllers/`, `services/`, `repositories/`, `models/` | Imports flow top-down: controller → service → repository |
| **Hexagonal / Ports & Adapters** | Folders named `domain/`, `ports/`, `adapters/`, `application/` | Domain has no imports from adapters; adapters import from ports |
| **Modular Monolith** | Top-level folders = feature names (e.g., `billing/`, `auth/`, `reporting/`) | Cross-module imports only via index/public API files |
| **Microservices** | Multiple `Dockerfile` / `docker-compose.yml` at project root; separate `package.json` per service | Each service is an independent import graph |
| **Event-driven** | Presence of `events/`, `handlers/`, `subscribers/`, message broker config | Modules communicate via event types, not direct calls |
| **Monolith (unstructured)** | Flat file structure; imports reference individual files directly | No clear boundaries; high coupling across files |
| **Plugin / Extension** | `plugins/`, `extensions/`, `hooks/` with registration pattern | Core defines interfaces; plugins implement them |

---

## Entry Point Detection

| Language | Entry Point Signals |
|---|---|
| Python | `main.py`, `app.py`, `__main__.py`, `wsgi.py`, `asgi.py`, `cli.py` |
| JavaScript/TypeScript | `index.js`, `index.ts`, `server.js`, `app.js`, `main.ts` |
| Go | `main.go` in `cmd/` or root |
| Java | Class with `public static void main`, `Application.java` with `@SpringBootApplication` |
| Rust | `src/main.rs`, `src/lib.rs` |

---

## Layer Identification Heuristics

Assign each file to a layer based on its location and import pattern:

| Layer | File Location Signals | Import Behavior |
|---|---|---|
| Presentation | `routes/`, `controllers/`, `views/`, `handlers/`, `api/` | Imports from application layer; no DB imports |
| Application | `services/`, `use_cases/`, `application/`, `commands/` | Imports from domain and infrastructure |
| Domain | `domain/`, `models/`, `entities/`, `core/` | No imports from infrastructure or presentation |
| Infrastructure | `repositories/`, `adapters/`, `database/`, `storage/`, `external/` | Imports from domain; implements domain interfaces |
| Cross-cutting | `shared/`, `common/`, `utils/`, `lib/` | Imported by all layers |

---

## Boundary Interface Detection

A boundary interface is a file that:
- Is imported by multiple modules (fan-in > 3)
- Exports only type definitions, interfaces, or abstract classes
- Has no implementation logic (functions return `NotImplemented` or are abstract)
- Is located in a `ports/`, `interfaces/`, or `contracts/` directory

---

## Output: Architecture Map

```
Architecture Map
─────────────────
Pattern:        [identified pattern]
Confidence:     high | medium | low
Signals:        [key signals that led to this classification]

Entry Points:
  [file] — [role]

Layers:
  Presentation: [N files] — [key files]
  Application:  [N files] — [key files]
  Domain:       [N files] — [key files]
  Infrastructure:[N files] — [key files]
  Cross-cutting: [N files] — [key files]

Boundary Interfaces:
  [file] — [fan-in: N] — [exported types]

Anomalies:
  [file]: [why it doesn't fit the pattern]
```