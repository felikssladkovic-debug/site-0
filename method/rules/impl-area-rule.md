---
id: method.rules.impl-area-rule
type: method-rule
status: active
scope: reusable-method
---

# Implementation Area Rule

This reusable rule defines how implementation areas must be represented.

It does not name any concrete project implementation area.

## Rule

Each `ImplementationArea` must define:

```yaml
required_fields:
  - id
  - kind
  - responsibility
  - spec-folder
  - owns
```

## Allowed kinds

```yaml
allowed_kinds:
  - application
  - infrastructure
```

A minimal project may use only a subset of these kinds.

## Ownership rule

Each implementation area must own one or more generated artifact patterns.

Example shape:

```yaml
implementation_area:
  id: some-area
  kind: application
  responsibility: describe the bounded responsibility
  owns:
    - generated/some-area/**
```

## Infrastructure areas

Infrastructure implementation areas are valid implementation areas.

They may own artifacts such as:

```yaml
examples:
  - docker-compose.yaml
  - Dockerfile
  - deployment manifests
  - startup scripts
```

## Dependency rule

An implementation area may depend on another implementation area.

The dependency should describe the operational meaning, for example:

```yaml
relations:
  - from: infrastructure-area-1
    to: application-area-1
    relation: runs
```
