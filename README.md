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

## Ontology split

This version separates the reusable method-level ontology from the concrete project instance graph.

```text
method/ontology/project-evo-method-schema.md
project/spec/00-meta/site-0-ontology-instance.md
```

Meaning:

```text
project-evo-method-schema.md
  Defines entity types and relation types:
  Project, Method, Rule, Command, Spec, ImplementationArea, Artifact, AcceptanceCheck, State, Transition...

site-0-ontology-instance.md
  Instantiates that schema for this concrete minimal project:
  site-0, site-front, orchestrator, spec-to-code, generated/site-front/**, generated/docker-compose.yaml...
```

## How to use with Codex

Run Codex from the root of this package and give it the content of:

```text
method/commands/spec-to-code.md
```

The generated implementation must be written to:

```text
generated/
```

The `method/**` and `project/spec/**` files are the source of truth.
