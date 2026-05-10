---
id: spec.site-front.contract
type: impl-area-contract
status: active
scope: site-0
impl_area: site-front
---

# Site Front Contract

## Responsibility

`site-front` is the application implementation area for the minimal frontend.

It owns:

```text
generated/site-front/**
```

## Stack

Use:

- TypeScript
- Vue 3
- Tailwind
- Vite

## Required files

The generated implementation should include at least:

```text
generated/site-front/package.json
generated/site-front/index.html
generated/site-front/vite.config.ts
generated/site-front/tsconfig.json
generated/site-front/src/main.ts
generated/site-front/src/App.vue
generated/site-front/src/style.css
generated/site-front/Dockerfile
```

Additional config files are allowed only when needed for the required stack.

## UI contract

The page must display:

```text
Счетчик
1
```

## Behavior constraints

The counter value is static.

Do not implement:

- increment button
- decrement button
- mutable counter state
- API calls
- persistence
- routing
- global state management
