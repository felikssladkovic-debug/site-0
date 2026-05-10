---
id: project.method-instance.site-0.rules-profile
type: method-instance-profile
status: active
scope: site-0
---

# Site-0 Rules Profile

This file declares how the reusable `project-evo-method` rules are applied to the concrete `site-0` project.

## Project

```yaml
project:
  id: site-0
```

## Enabled method rules

```yaml
enabled_rules:
  - method.rules.impl-area-rule
  - method.rules.spec-to-code-rule
  - method.rules.acceptance-check-rule
```

## Enabled command schemas

```yaml
enabled_command_schemas:
  - method.command-schemas.spec-to-code-command-schema
```

## Allowed implementation areas

```yaml
allowed_impl_areas:
  - id: site-front
    kind: application

  - id: orchestrator
    kind: infrastructure
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

## Output root

```yaml
output_root: generated/
```

## Required generated artifact ownership

```yaml
artifact_ownership:
  - owner: site-front
    artifacts:
      - generated/site-front/**

  - owner: orchestrator
    artifacts:
      - generated/docker-compose.yaml
```

## Required acceptance checks

```yaml
required_acceptance_checks:
  - app-builds
  - app-runs
  - page-renders-counter
```

## Explicitly excluded functionality

```yaml
excluded_functionality:
  - backend API
  - database
  - admin UI
  - authentication
  - authorization
  - routing
  - i18n
  - real mutable counter
  - persistence
```
