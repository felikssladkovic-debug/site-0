---
id: readme.site-0-project-evo-spec-method-instance
type: readme
status: active
scope: site-0
---

# site-0 project-evo spec package

This package is a minimal `project-evo-method` application for the `site-0` case.

It separates:

1. reusable method-level definitions under `method/`
2. project-specific method application under `project/method-instance/`
3. project-specific artifacts under `project/artifacts/`
4. generated code output target under `generated/`

The package intentionally contains only the concepts needed for the minimal `site-0` project.

## Case summary

`site-0` is a minimal frontend-only web application.

It must:

- use TypeScript
- use Vue 3
- use Tailwind
- use Vite
- run through Docker Compose
- display the text `Счетчик`
- display the static number `1`

The project has exactly two implementation areas:

- `site-front` — application implementation area
- `orchestrator` — infrastructure implementation area that owns Docker Compose runtime artifacts

## Main command to execute

Run the project-specific command:

```text
project/method-instance/commands/spec-to-code.site-0.md
```

This command applies the reusable method-level `spec-to-code` command schema to this concrete `site-0` project instance.

## Expected generated output

The code generation agent must create output under:

```text
generated/
```

Expected generated structure:

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

## Runtime command

```bash
docker-compose up --build
```

## Acceptance checks

The generated project is accepted when:

1. Docker Compose build succeeds.
2. Docker Compose starts the frontend service.
3. The page displays `Счетчик` and `1`.
