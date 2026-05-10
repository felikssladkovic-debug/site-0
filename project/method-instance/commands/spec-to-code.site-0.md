---
id: project.method-instance.commands.spec-to-code.site-0
type: command-instance
status: active
scope: site-0
instantiates: method.command-schemas.spec-to-code-command-schema
---

# Command: spec-to-code for site-0

Use this command in Codex or another code generation agent to generate the `site-0` implementation from the project specs.

This is a concrete command instance. It applies the reusable `spec-to-code` command schema to the `site-0` project.

## Read these method-level files

```text
method/ontology/project-evo-method-schema.md
method/rules/impl-area-rule.md
method/rules/spec-to-code-rule.md
method/rules/acceptance-check-rule.md
method/command-schemas/spec-to-code-command-schema.md
```

## Read these project-level method instance files

```text
project/method-instance/rules-profile.md
project/spec/00-meta/site-0-ontology-instance.md
```

## Read these project spec files

```text
project/spec/00-meta/spec-index.md
project/spec/10-product/site-0-brief.md
project/spec/20-architecture/implementation-areas.md
project/spec/30-site-front/site-front-contract.md
project/spec/40-orchestrator/orchestrator-contract.md
project/spec/60-quality/acceptance-checks.md
```

## Generate output

Generate all code and runtime artifacts under:

```text
generated/
```

## Allowed implementation areas

Generate artifacts only for these implementation areas:

```yaml
allowed_impl_areas:
  - site-front
  - orchestrator
```

## Required generated structure

```text
generated/
  site-front/
    package.json
    index.html
    vite.config.ts
    tsconfig.json
    tailwind.config.*
    postcss.config.*
    src/**
    Dockerfile
  docker-compose.yaml
```

Equivalent minor variations are acceptable only if `docker-compose up --build` works from the `generated/` directory or from the repository root with clear instructions.

## Do not generate

Do not generate:

```yaml
forbidden:
  - backend service
  - API server
  - database
  - admin frontend
  - admin backend
  - auth system
  - real counter mutation
  - persistence
  - routing
  - i18n framework
  - extra implementation areas
```

## Functional requirement

The generated frontend must render a simple page that displays:

```text
Счетчик
1
```

The number is static. No increment/decrement behavior is required.

## Stack requirement

Use:

```yaml
site-front_stack:
  - TypeScript
  - Vue 3
  - Tailwind
  - Vite
```

Use Docker Compose for build and launch.

## Runtime requirement

The generated project must be runnable with:

```bash
docker-compose up --build
```

## Acceptance criteria

The implementation is accepted when:

1. Docker Compose build succeeds.
2. Docker Compose starts the frontend service.
3. The opened page displays `Счетчик` and `1`.
