# site-0 Spec

## Purpose

Generate the smallest possible runnable website from a single project spec.

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

## Runtime

The result should be a static HTML page that can be opened directly in a browser.
