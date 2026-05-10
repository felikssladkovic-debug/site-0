---
id: spec.product.site-0-brief
type: product-brief
status: active
scope: site-0
---

# Site-0 Brief

`site-0` is the smallest useful frontend project generated through project-evo-method.

## Goal

Generate a minimal website page that proves the `spec->code` flow works.

## User-visible behavior

The page must visibly display:

```text
Счетчик
1
```

## Non-goals

This project must not implement:

- real counter state changes
- backend API
- database
- authentication
- admin panel
- routing
- i18n
- persistence

## Success

The generated project is successful when it can be started with Docker Compose and the page displays the required static content.
