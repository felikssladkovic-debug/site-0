---
id: project.spec.30-site-front.site-front-contract
kind: implementation-area-spec
status: ready
project: site-0
impl_area: site-front
---

# site-front contract

## Stack

`site-front` must use:

- TypeScript
- Vue 3
- Vite
- Tailwind CSS

## Page contract

The application has a single page.

The page must display:

```text
Счетчик
1
```

The exact layout is not important, but the content must be directly visible after opening the page. The content must not require any user action.

## Suggested UI

A minimal acceptable UI:

- centered card or panel
- heading: `Счетчик`
- large number: `1`

## Forbidden frontend additions

Do not add:

- Vue Router
- Pinia/Vuex
- component libraries
- API clients
- mock servers
- generated sample pages beyond the one required page
