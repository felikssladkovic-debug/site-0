# site-0 project-evo spec package

This package is the minimal `project-evo-method` decomposition for `site-0`.

It replaces a single Codex prompt with a small set of structured spec and method files.

## Scope

`site-0` is intentionally minimal:

- application implementation area: `site-front`
- infrastructure implementation area: `orchestrator`
- frontend stack: TypeScript, Vue 3, Tailwind, Vite
- runtime/build: Docker Compose
- visible UI: render `Счетчик` and `1`
- generation command: `method/commands/spec-to-code.md`

## How to use with Codex

Run Codex from the root of this package and give it the content of:

```text
method/commands/spec-to-code.md
```

The generated implementation must be written to:

```text
generated/
```

The `project/spec/**` files are the source of truth.
