---
id: project.spec.20-architecture.implementation-areas
kind: architecture-spec
status: ready
project: site-0
---

# Implementation areas

## Allowed implementation areas

There is exactly one implementation area:

| impl-area | Required | Description |
|---|---:|---|
| `site-front` | yes | Public site frontend implemented with Vue 3, TypeScript, Tailwind CSS, and Vite. |

## Forbidden implementation areas

The generated code must not create these or any similar implementation areas:

- `site-backend`
- `admin-front`
- `admin-backend`
- `etl`
- `db-canonical`
- `db-read`
- `start-orchestrator`

## Connections

There are no inter-area connections because there is only one implementation area.
