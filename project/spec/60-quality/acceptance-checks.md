---
id: project.spec.60-quality.acceptance-checks
kind: quality-spec
status: ready
project: site-0
---

# Acceptance checks

The generated code is accepted when all checks pass.

## File checks

- `generated/docker-compose.yml` exists.
- `generated/site-front/package.json` exists.
- `generated/site-front/src/App.vue` exists.
- No backend, database, admin, ETL, or orchestrator folders are created.

## Runtime checks

From `generated/`:

```bash
docker-compose config
docker-compose build
docker-compose up -d
```

Then open:

```text
http://localhost:5173
```

The page must visibly display:

- `Счетчик`
- `1`

## Minimality checks

The generated solution must not include features outside the spec.
