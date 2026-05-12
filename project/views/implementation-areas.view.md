---
id: project.spec.site-0.implementation-areas
type: architecture-spec
status: active
scope: site-0
---

# Implementation Areas

`site-0` has exactly two implementation areas.

## 1. site-front

```yaml
id: site-front
kind: application
responsibility: Render the minimal visible frontend page.
owns:
  - generated/site-front/**
stack:
  - TypeScript
  - Vue 3
  - Tailwind
  - Vite
```

## 2. orchestrator

```yaml
id: orchestrator
kind: infrastructure
responsibility: Build and run the generated project through Docker Compose.
owns:
  - generated/docker-compose.yaml
stack:
  - Docker
  - Docker Compose
```

## Relations

```yaml
relations:
  - from: orchestrator
    to: site-front
    relation: runs
    via: docker-compose service

  - from: orchestrator
    to: site-front
    relation: builds
    via: Dockerfile or Docker Compose build context
```

## Forbidden implementation areas

```yaml
forbidden_impl_areas:
  - site-backend
  - admin-front
  - admin-backend
  - db-canonical
  - db-read
  - etl
```
