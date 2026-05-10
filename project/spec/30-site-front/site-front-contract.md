---
id: project.spec.site-0.site-front-contract
type: impl-area-contract
status: active
scope: site-0
impl_area: site-front
---

# Site Front Contract

This file defines the contract for the `site-front` implementation area.

## Responsibility

`site-front` must render the minimal frontend page for `site-0`.

## Stack

Use:

```yaml
stack:
  - TypeScript
  - Vue 3
  - Tailwind
  - Vite
```

## Owned artifacts

```yaml
owns:
  - generated/site-front/**
```

Expected files include:

```text
generated/site-front/
  package.json
  index.html
  vite.config.ts
  tsconfig.json
  tailwind.config.*
  postcss.config.*
  src/**
  Dockerfile
```

## Required UI behavior

The rendered page must display:

```text
Счетчик
1
```

## Not required

Do not implement:

- increment button
- decrement button
- mutable state
- API calls
- routing
- i18n
- persistence
