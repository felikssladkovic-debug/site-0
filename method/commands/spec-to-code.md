---
id: method.commands.spec-to-code
kind: command
status: ready
command_name: spec-to-code
input: project/spec/**
output: generated/**
---

# Command: spec-to-code

You are Codex working inside the root of this unpacked project-evo package.

Your task is to generate code from the spec files in `project/spec/**`.

## Required reading order

Read these files before writing code:

1. `method/rules/minimal-project-evo-rules.md`
2. `project/spec/00-meta/spec-index.md`
3. `project/spec/10-product/site-0-brief.md`
4. `project/spec/20-architecture/implementation-areas.md`
5. `project/spec/30-site-front/site-front-contract.md`
6. `project/spec/50-infra/docker-compose-contract.md`
7. `project/spec/60-quality/acceptance-checks.md`

## Generation task

Create a complete runnable implementation under `generated/`.

The implementation must satisfy all spec files exactly and minimally.

## Required output structure

Create this structure, unless you have a strong technical reason to keep it even simpler while still satisfying the spec:

```text
generated/
  docker-compose.yml
  site-front/
    Dockerfile
    package.json
    package-lock.json OR pnpm-lock.yaml OR yarn.lock if produced by the chosen package manager
    index.html
    vite.config.ts
    tsconfig.json
    tsconfig.node.json if needed by Vite
    postcss.config.js
    tailwind.config.js
    src/
      main.ts
      App.vue
      style.css
```

## Implementation requirements

- Use TypeScript.
- Use Vue 3.
- Use Vite.
- Use Tailwind CSS.
- Run through Docker Compose.
- The only service in Docker Compose must be the frontend service for `site-front`.
- The rendered page must show `Счетчик` and `1`.
- The page may be visually simple but must be clean and centered.
- No backend, database, API, admin app, auth, router, or extra implementation area.

## Validation commands to run before finishing

From `generated/` run:

```bash
docker-compose config
docker-compose build
docker-compose up -d
```

Then verify that the app is reachable from the host on the configured port and that the page displays `Счетчик` and `1`.

If you cannot run Docker in the current environment, still create all files and explain exactly which validation commands the user should run.

## Final response format

After generating the files, respond with:

1. Short summary of generated files.
2. Exact commands to run.
3. Expected URL.
4. Any validation that could not be performed.
