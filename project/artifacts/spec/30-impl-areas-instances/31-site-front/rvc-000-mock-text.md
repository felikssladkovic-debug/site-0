---
id: project.spec.site-0.site-front.rv-001-mock-text
type: ravioli
status: active
scope: site-0
impl_area: site-front
---

# File purpose

This file defines the contract for the `site-front` implementation area, its first/basic functionality

## Responsibility

`site-front` must render the minimal frontend page for `site-0`.

## Required UI behavior

The generated application must show a simple page with:

```text
Счетчик
1
```

The number `1` is static.

There is no real counter behavior yet.

## Not required

Do not implement:

- mutable counter logic
- increment button
- decrement button
- mutable state
- API calls
- routing
- i18n
- persistence

It is expected project must not include:

- backend
- database
- authentication
- authorization
- admin UI
