---
id: method.rules.minimal-project-evo-rules
type: method-rule
status: active
scope: site-0
---

# Minimal Project Evo Rules

This file defines the minimal method rules for the `site-0` case.

## 1. Source of truth

The source of truth is:

```text
project/spec/**
```

The generated code must be derived from these spec files.

## 2. Generated output

All generated implementation files must be placed under:

```text
generated/
```

Do not write generated application files outside `generated/`.

## 3. Minimal implementation areas

This case has exactly two implementation areas:

```yaml
implementation_areas:
  - id: site-front
    kind: application
  - id: orchestrator
    kind: infrastructure
```

No backend, admin UI, database, ETL, auth, or i18n implementation area is part of this case.

## 4. Command model

This minimal case has exactly one command:

```text
spec->code
```

The command reads the spec and produces generated code.

## 5. No feature lifecycle

This minimal case does not include:

- idea inbox
- feature refinement
- multi-step feature lifecycle
- spec-to-idea validation
- code-to-spec validation

Those concepts are intentionally excluded from this package.

## 6. Acceptance

The generated project is accepted when:

- Docker Compose build succeeds
- Docker Compose starts the frontend service
- the browser-visible page renders `Счетчик`
- the browser-visible page renders `1`
