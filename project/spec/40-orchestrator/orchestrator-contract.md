---
id: spec.orchestrator.contract
type: impl-area-contract
status: active
scope: site-0
impl_area: orchestrator
---

# Orchestrator Contract

## Responsibility

`orchestrator` is the infrastructure implementation area for this minimal project.

It owns:

```text
generated/docker-compose.yaml
```

It may also rely on a frontend Dockerfile owned by `site-front`:

```text
generated/site-front/Dockerfile
```

## Runtime contract

The whole generated project must run with:

```bash
cd generated
docker-compose up --build
```

## Docker Compose contract

`generated/docker-compose.yaml` must define one service for `site-front`.

Recommended service name:

```yaml
services:
  site-front:
```

The service must:

- build the frontend container
- run the Vite dev server or an equivalent frontend server
- expose the frontend to the host browser

Recommended port mapping:

```yaml
ports:
  - "5173:5173"
```

## Dependency on site-front

The `orchestrator` implementation area depends on the `site-front` implementation area.

```yaml
relations:
  - from: orchestrator
    to: site-front
    relation: builds

  - from: orchestrator
    to: site-front
    relation: runs
```

## Constraints

Do not add services for:

- backend
- database
- admin UI
- ETL
- auth
- message broker
- cache
