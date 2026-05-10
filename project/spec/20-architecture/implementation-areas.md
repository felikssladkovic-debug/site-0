---
id: spec.architecture.implementation-areas
type: architecture-spec
status: active
scope: site-0
---

# Implementation Areas

This minimal case has exactly two implementation areas.

## 1. site-front

```yaml
id: site-front
kind: application
type: frontend
responsibility: render the minimal user-visible page
owns:
  - generated/site-front/**
```

Technology stack:

```yaml
stack:
  - TypeScript
  - Vue 3
  - Tailwind
  - Vite
```

Required behavior:

```yaml
behavior:
  - render "Счетчик"
  - render "1"
```

## 2. orchestrator

```yaml
id: orchestrator
kind: infrastructure
type: docker-compose-runtime
responsibility: build and run site-front through Docker Compose
owns:
  - generated/docker-compose.yaml
```

Technology stack:

```yaml
stack:
  - Docker
  - Docker Compose
```

Required behavior:

```yaml
behavior:
  - build site-front container
  - run site-front container
  - expose frontend to host browser
```

## Relations

```yaml
relations:
  - from: orchestrator
    to: site-front
    relation: builds

  - from: orchestrator
    to: site-front
    relation: runs
```

## Explicitly absent implementation areas

```yaml
not_used:
  - site-backend
  - admin-front
  - admin-backend
  - db-canonical
  - db-read
  - etl
```
