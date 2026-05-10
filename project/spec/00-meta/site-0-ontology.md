---
id: spec.meta.site-0-ontology
type: ontology
status: active
scope: site-0
project_evo_method_level: minimal
---

# Site-0 Ontology

This document defines the minimal ontology used by the `site-0` project-evo case.

It intentionally includes only concepts that are already present in this minimal case.

It does not describe the full project-evo-method.

---

# 1. Scope

`site-0` is a minimal generated software project with:

- two implementation areas:
  - `site-front`
  - `orchestrator`
- one command:
  - `spec->code`
- one visible UI behavior:
  - render the text `Счетчик`
  - render the number `1`
- one target output area:
  - `generated/`

---

# 2. Core Entity Types

## 2.1 Project

A `Project` is the root unit of work managed by project-evo-method.

In this case:

```yaml
project:
  id: site-0
  name: site-0
  purpose: minimal Vue site generated from spec
```

---

## 2.2 Method

A `Method` is the set of rules and commands that define how project artifacts evolve.

In this case:

```yaml
method:
  id: project-evo-method-minimal
  scope: site-0
```

The method contains:

- rules
- commands

---

## 2.3 Rule

A `Rule` is a constraint that governs how artifacts should be interpreted or transformed.

In this case:

```yaml
rules:
  - id: minimal-project-evo-rules
    path: method/rules/minimal-project-evo-rules.md
```

---

## 2.4 Command

A `Command` is an executable instruction for an LLM/code agent.

In this case:

```yaml
commands:
  - id: spec-to-code
    path: method/commands/spec-to-code.md
    input: project/spec/**
    output: generated/**
```

The command transforms spec into generated code.

---

## 2.5 Spec

A `Spec` is a source-of-truth artifact that describes what should be generated.

In this case, the spec consists of:

```yaml
spec_files:
  - path: project/spec/00-meta/spec-index.md
    role: spec index

  - path: project/spec/00-meta/site-0-ontology.md
    role: minimal ontology

  - path: project/spec/10-product/site-0-brief.md
    role: product brief

  - path: project/spec/20-architecture/implementation-areas.md
    role: implementation area map

  - path: project/spec/30-site-front/site-front-contract.md
    role: site-front contract

  - path: project/spec/40-orchestrator/orchestrator-contract.md
    role: orchestrator contract

  - path: project/spec/60-quality/acceptance-checks.md
    role: acceptance checks
```

---

## 2.6 Implementation Area

An `ImplementationArea` is a bounded part of the generated system that owns a coherent set of generated artifacts.

In this case there are exactly two implementation areas:

```yaml
implementation_areas:
  - id: site-front
    kind: application
    type: frontend
    responsibility: render the minimal visible page
    stack:
      - TypeScript
      - Vue 3
      - Tailwind
      - Vite
    owns:
      - generated/site-front/**

  - id: orchestrator
    kind: infrastructure
    type: docker-compose-runtime
    responsibility: build and run the generated application
    stack:
      - Docker
      - Docker Compose
    owns:
      - generated/docker-compose.yaml
```

Explicitly absent:

```yaml
not_used:
  - site-backend
  - admin-front
  - admin-backend
  - db-canonical
  - db-read
  - etl
```

---

## 2.7 Generated Code

`GeneratedCode` is the output created by the `spec-to-code` command.

In this case:

```yaml
generated_code:
  path: generated/
  produced_by: spec-to-code
  implements:
    - site-front
    - orchestrator
```

---

## 2.8 UI Behavior

A `UIBehavior` is an observable behavior of the generated frontend.

In this case:

```yaml
ui_behaviors:
  - id: render-counter-static-value
    area: site-front
    expected_text:
      - "Счетчик"
      - "1"
```

This is static behavior. There is no real counter logic yet.

---

## 2.9 Acceptance Check

An `AcceptanceCheck` is a validation condition used to decide whether generated code satisfies the spec.

In this case:

```yaml
acceptance_checks:
  - id: app-builds
    description: docker-compose build succeeds

  - id: app-runs
    description: docker-compose up starts the frontend service

  - id: page-renders-counter
    description: the page displays "Счетчик" and "1"
```

---

# 3. Relations

## 3.1 Project Structure Relations

```yaml
relations:
  - subject: site-0
    predicate: uses_method
    object: project-evo-method-minimal

  - subject: site-0
    predicate: has_spec
    object: project/spec

  - subject: site-0
    predicate: has_implementation_area
    object: site-front

  - subject: site-0
    predicate: has_implementation_area
    object: orchestrator

  - subject: site-0
    predicate: has_generated_output
    object: generated/
```

---

## 3.2 Command Relations

```yaml
relations:
  - subject: spec-to-code
    predicate: reads
    object: project/spec/**

  - subject: spec-to-code
    predicate: follows_rules
    object: minimal-project-evo-rules

  - subject: spec-to-code
    predicate: generates
    object: generated/

  - subject: spec-to-code
    predicate: must_implement
    object: site-front

  - subject: spec-to-code
    predicate: must_implement
    object: orchestrator
```

---

## 3.3 Implementation Relations

```yaml
relations:
  - subject: site-front
    predicate: uses_stack
    object: TypeScript

  - subject: site-front
    predicate: uses_stack
    object: Vue 3

  - subject: site-front
    predicate: uses_stack
    object: Tailwind

  - subject: site-front
    predicate: uses_stack
    object: Vite

  - subject: site-front
    predicate: provides_behavior
    object: render-counter-static-value

  - subject: orchestrator
    predicate: uses_stack
    object: Docker

  - subject: orchestrator
    predicate: uses_stack
    object: Docker Compose

  - subject: orchestrator
    predicate: builds
    object: site-front

  - subject: orchestrator
    predicate: runs
    object: site-front
```

---

## 3.4 Validation Relations

```yaml
relations:
  - subject: acceptance-checks
    predicate: validate
    object: generated/

  - subject: page-renders-counter
    predicate: validates_behavior
    object: render-counter-static-value

  - subject: app-builds
    predicate: validates_impl_area
    object: orchestrator

  - subject: app-runs
    predicate: validates_impl_area
    object: orchestrator
```

---

# 4. Minimal Workflow Model

The minimal workflow contains exactly one transformation:

```text
spec -> code
```

Formalized as:

```yaml
workflow:
  - id: spec-to-code-flow
    from: project/spec/**
    command: method/commands/spec-to-code.md
    to: generated/**
```

There are no separate idea, brief-refinement, code-to-spec, spec-validation, or feature-evolution commands in this minimal case.

---

# 5. State Model

Only the following states are relevant in this case:

```yaml
states:
  - id: spec-defined
    meaning: minimal spec files exist and define site-0

  - id: code-generated
    meaning: generated/ contains implementation produced from spec

  - id: runnable
    meaning: docker-compose up --build starts the application

  - id: accepted
    meaning: acceptance checks pass
```

Allowed transitions:

```yaml
transitions:
  - from: spec-defined
    to: code-generated
    command: spec-to-code

  - from: code-generated
    to: runnable
    condition: docker-compose up --build succeeds

  - from: runnable
    to: accepted
    condition: acceptance checks pass
```

---

# 6. Boundary

This ontology intentionally excludes concepts that are not used in `site-0`.

Excluded from this case:

```yaml
excluded:
  product:
    - user roles
    - authentication
    - authorization
    - real counter mutation
    - persistence
    - backend API
    - admin UI
    - database
    - i18n
    - routing
    - business workflows

  method:
    - idea inbox
    - accepted ideas
    - feature lifecycle
    - code-to-spec validation
    - spec-to-idea validation
    - multi-agent workflow
    - more than two implementation areas
    - complex dependency graph between implementation areas
```

---

# 7. Ontology Summary

```yaml
ontology_summary:
  project: site-0

  method:
    rules:
      - minimal-project-evo-rules
    commands:
      - spec-to-code

  spec:
    root: project/spec
    files:
      - 00-meta/spec-index.md
      - 00-meta/site-0-ontology.md
      - 10-product/site-0-brief.md
      - 20-architecture/implementation-areas.md
      - 30-site-front/site-front-contract.md
      - 40-orchestrator/orchestrator-contract.md
      - 60-quality/acceptance-checks.md

  implementation_areas:
    - site-front
    - orchestrator

  generated_output:
    - generated/

  observable_behavior:
    - render "Счетчик"
    - render "1"

  main_transformation:
    from: spec
    to: code
    command: spec-to-code
```
