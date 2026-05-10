---
id: method.commands.spec-to-code
type: command
status: active
scope: site-0
inputs:
  - method/ontology/project-evo-method-schema.md
  - method/rules/minimal-project-evo-rules.md
  - project/spec/**
outputs:
  - generated/**
---

# Command: spec->code

You are a code-generation agent working inside a minimal project-evo-method package.

Your task is to generate the implementation from the spec.

## Read first

Read these method-level files first:

```text
method/ontology/project-evo-method-schema.md
method/rules/minimal-project-evo-rules.md
```

Then read all project spec files under:

```text
project/spec/**
```

## Output location

Create all generated files under:

```text
generated/
```

Do not place generated application files outside `generated/`.

## Required implementation areas

Generate code for exactly these implementation areas:

```yaml
implementation_areas:
  - id: site-front
    kind: application
    responsibility: minimal frontend page

  - id: orchestrator
    kind: infrastructure
    responsibility: Docker Compose build and runtime
```

## Required generated structure

Use this structure:

```text
generated/
  site-front/
    package.json
    index.html
    vite.config.ts
    tsconfig.json
    src/
      main.ts
      App.vue
      style.css
    Dockerfile
  docker-compose.yaml
```

Additional frontend config files are allowed only if required for Vue 3, TypeScript, Tailwind, Vite, or Docker Compose to work correctly.

## Technology stack

Use:

- TypeScript
- Vue 3
- Tailwind
- Vite
- Docker
- Docker Compose

## Functional requirement

The generated frontend page must display:

```text
Счетчик
1
```

This is a static page.

Do not implement real counter increment/decrement behavior.

## Runtime requirement

The project must run with:

```bash
cd generated
docker-compose up --build
```

The frontend service must be accessible from the host browser.

Use a simple port mapping such as:

```yaml
ports:
  - "5173:5173"
```

## Constraints

Do not add:

- backend
- database
- admin frontend
- authentication
- authorization
- API calls
- i18n
- routing
- state management libraries
- real counter mutation logic

## Acceptance checks

After generation, the implementation should satisfy:

```text
project/spec/60-quality/acceptance-checks.md
```
