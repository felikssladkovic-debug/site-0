---
id: method.rules.minimal-project-evo-rules
kind: rule
status: ready
scope: minimal-site-0
---

# Minimal project-evo rules for site-0

## 1. Source of truth

The source of truth is the spec under `project/spec/**`.

The generated code must not introduce functionality, implementation areas, services, databases, APIs, or UI screens that are not requested by the spec.

## 2. Implementation area boundary

The only implementation area in this package is:

- `site-front`

No backend, admin UI, ETL, database, queue, auth, or orchestrator must be created.

## 3. Output location

All generated implementation files must be placed under:

- `generated/`

The `method/` and `project/spec/` folders must remain documentation/specification inputs and must not be modified unless the user explicitly requests spec changes.

## 4. Runtime contract

The project must be runnable with Docker Compose from `generated/`:

```bash
docker-compose up --build
```

After startup, the frontend must be available from the host machine in a browser.

## 5. Keep the solution minimal

Use the requested stack only:

- TypeScript
- Vue 3
- Tailwind CSS
- Vite
- Docker Compose

Prefer the simplest working structure. Do not add routing, state-management libraries, backend mocks, databases, authentication, component libraries, or deployment-specific infrastructure.
