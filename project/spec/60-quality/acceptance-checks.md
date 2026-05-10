---
id: spec.quality.acceptance-checks
type: quality-spec
status: active
scope: site-0
---

# Acceptance Checks

The generated implementation is accepted when all checks below pass.

## Check 1: Generated files exist

Expected files:

```text
generated/site-front/package.json
generated/site-front/index.html
generated/site-front/vite.config.ts
generated/site-front/src/main.ts
generated/site-front/src/App.vue
generated/site-front/Dockerfile
generated/docker-compose.yaml
```

## Check 2: Docker Compose build succeeds

Command:

```bash
cd generated
docker-compose build
```

Expected result:

```text
build succeeds
```

## Check 3: Docker Compose starts the app

Command:

```bash
cd generated
docker-compose up --build
```

Expected result:

```text
site-front service starts
frontend is reachable from host browser
```

## Check 4: Page renders required static content

The page must visibly contain:

```text
Счетчик
1
```

## Check 5: No extra implementation areas

The generated project must not include:

```text
backend
admin frontend
database
ETL
auth service
```
