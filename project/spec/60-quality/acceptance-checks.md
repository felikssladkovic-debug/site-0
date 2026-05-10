---
id: project.spec.site-0.acceptance-checks
type: quality-spec
status: active
scope: site-0
---

# Acceptance Checks

The generated `site-0` project is accepted when all checks below pass.

## Check 1: app-builds

```yaml
id: app-builds
description: Docker Compose build succeeds.
validates:
  - generated/**
```

Expected command:

```bash
docker-compose up --build
```

Build must not fail.

## Check 2: app-runs

```yaml
id: app-runs
description: Docker Compose starts the frontend service.
validates:
  - generated/docker-compose.yaml
  - generated/site-front/**
```

The frontend service must start and expose the application in a browser-accessible way.

## Check 3: page-renders-counter

```yaml
id: page-renders-counter
description: The page displays the required static content.
validates:
  - render-counter-static-value
```

The page must display:

```text
Счетчик
1
```
