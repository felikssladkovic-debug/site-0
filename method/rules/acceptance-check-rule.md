---
id: method.rules.acceptance-check-rule
type: method-rule
status: active
scope: reusable-method
---

# Acceptance Check Rule

This reusable rule defines how acceptance checks must be represented and used.

It does not contain project-specific acceptance checks.

## Rule

Each acceptance check must define:

```yaml
required_fields:
  - id
  - description
  - validates
```

## Validation targets

An acceptance check may validate:

```yaml
validation_targets:
  - generated artifact
  - runtime behavior
  - observable UI behavior
  - build process
  - service startup
```

## Coverage rule

A minimal generated project should have acceptance checks for:

```yaml
minimal_coverage:
  - build succeeds
  - runtime starts
  - core observable behavior is present
```

## Boundary rule

Acceptance checks should validate only declared project scope.

They must not require undeclared features, services, APIs, databases, authentication, authorization, routing, localization, or admin UI.
