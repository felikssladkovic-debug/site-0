---
id: project.spec.10-product.site-0-brief
kind: product-brief
status: ready
project: site-0
feature: initial-minimal-site
---

# site-0 brief

## Goal

Create the smallest possible runnable web application that proves the `site-front` implementation area can be generated, built, and started through Docker Compose.

## User-visible behavior

The application renders one page.

The page must visibly contain:

- the Russian text `Счетчик`
- the number `1`

## Non-goals

Do not implement:

- counter increment/decrement behavior
- persistence
- backend API
- admin UI
- routing
- authentication
- localization system
- database
- tests unless they are required by the generator's default scaffolding
