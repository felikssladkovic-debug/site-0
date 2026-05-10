---
id: project.spec.site-0.orchestrator-contract
type: impl-area-contract
status: active
scope: site-0
impl_area: orchestrator
---

# Orchestrator Contract

This file defines the contract for the `orchestrator` implementation area.

## Responsibility

`orchestrator` must build and run the generated project through Docker Compose.

## Owned artifacts

```yaml
owns:
  - generated/docker-compose.yaml
```

## Required runtime command

The project must be runnable with:

```bash
docker-compose up --build
```

## Required service

Docker Compose must define a service for the frontend application.

Recommended service name:

```yaml
service_name: site-front
```

## Relation to site-front

`orchestrator` runs and builds `site-front`.

```yaml
relations:
  - from: orchestrator
    to: site-front
    relation: runs

  - from: orchestrator
    to: site-front
    relation: builds
```

## Not required

Do not define services for:

- backend
- database
- admin UI
- queue
- cache
- ETL
