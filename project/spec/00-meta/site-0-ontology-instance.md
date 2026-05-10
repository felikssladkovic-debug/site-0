---
id: spec.meta.site-0-ontology-instance
type: ontology-instance
status: active
scope: site-0
conforms_to: method.ontology.project-evo-method-schema
---

# Site-0 Ontology Instance

This document describes the concrete `site-0` instance graph that conforms to the method-level schema:

```text
method/ontology/project-evo-method-schema.md
```

It does not define the general project-evo-method ontology. It instantiates it for this minimal case.

---

# 1. Instance Scope

`site-0` is a minimal generated software project with:

```yaml
scope:
  project: site-0
  implementation_areas:
    - site-front
    - orchestrator
  command:
    - spec-to-code
  output_root: generated/
  primary_visible_behavior: render-counter-static-value
```

---

# 2. Entity Instances

```yaml
instances:
  - id: site-0
    type: Project
    name: site-0
    purpose: minimal Vue site generated from spec

  - id: project-evo-method-minimal
    type: Method
    scope: site-0 minimal project-evo workflow

  - id: project-evo-method-schema
    type: method-ontology-schema
    path: method/ontology/project-evo-method-schema.md

  - id: minimal-project-evo-rules
    type: Rule
    path: method/rules/minimal-project-evo-rules.md

  - id: spec-to-code
    type: Command
    path: method/commands/spec-to-code.md
    input: project/spec/**
    output: generated/**

  - id: site-0-spec
    type: Spec
    root: project/spec/

  - id: spec-index
    type: SpecFile
    path: project/spec/00-meta/spec-index.md
    role: spec index

  - id: site-0-ontology-instance
    type: SpecFile
    path: project/spec/00-meta/site-0-ontology-instance.md
    role: concrete ontology instance graph

  - id: site-0-brief
    type: SpecFile
    path: project/spec/10-product/site-0-brief.md
    role: product brief

  - id: implementation-areas
    type: SpecFile
    path: project/spec/20-architecture/implementation-areas.md
    role: implementation area map

  - id: site-front-contract
    type: SpecFile
    path: project/spec/30-site-front/site-front-contract.md
    role: site-front contract

  - id: orchestrator-contract
    type: SpecFile
    path: project/spec/40-orchestrator/orchestrator-contract.md
    role: orchestrator contract

  - id: acceptance-checks
    type: SpecFile
    path: project/spec/60-quality/acceptance-checks.md
    role: acceptance checks

  - id: site-front
    type: ImplementationArea
    kind: application
    responsibility: render the minimal visible frontend page

  - id: orchestrator
    type: ImplementationArea
    kind: infrastructure
    responsibility: build and run the generated application through Docker Compose

  - id: generated-code
    type: GeneratedCode
    root: generated/
    produced_by: spec-to-code

  - id: generated-site-front
    type: Artifact
    path: generated/site-front/**
    generated: true

  - id: generated-docker-compose
    type: Artifact
    path: generated/docker-compose.yaml
    generated: true

  - id: render-counter-static-value
    type: Behavior
    description: page renders the text "Счетчик" and the number "1"

  - id: app-builds
    type: AcceptanceCheck
    description: docker-compose build succeeds

  - id: app-runs
    type: AcceptanceCheck
    description: docker-compose up starts the frontend service

  - id: page-renders-counter
    type: AcceptanceCheck
    description: the page displays "Счетчик" and "1"
```

---

# 3. Concrete Relations

```yaml
relations:
  - subject: site-0
    predicate: uses_method
    object: project-evo-method-minimal

  - subject: project-evo-method-minimal
    predicate: defines_schema
    object: project-evo-method-schema

  - subject: project-evo-method-minimal
    predicate: defines_rule
    object: minimal-project-evo-rules

  - subject: project-evo-method-minimal
    predicate: defines_command
    object: spec-to-code

  - subject: site-0
    predicate: has_spec
    object: site-0-spec

  - subject: site-0-spec
    predicate: contains_spec_file
    object: spec-index

  - subject: site-0-spec
    predicate: contains_spec_file
    object: site-0-ontology-instance

  - subject: site-0-spec
    predicate: contains_spec_file
    object: site-0-brief

  - subject: site-0-spec
    predicate: contains_spec_file
    object: implementation-areas

  - subject: site-0-spec
    predicate: contains_spec_file
    object: site-front-contract

  - subject: site-0-spec
    predicate: contains_spec_file
    object: orchestrator-contract

  - subject: site-0-spec
    predicate: contains_spec_file
    object: acceptance-checks

  - subject: site-0
    predicate: has_impl_area
    object: site-front

  - subject: site-0
    predicate: has_impl_area
    object: orchestrator

  - subject: site-front
    predicate: owns
    object: generated-site-front

  - subject: orchestrator
    predicate: owns
    object: generated-docker-compose

  - subject: orchestrator
    predicate: runs
    object: site-front

  - subject: orchestrator
    predicate: builds
    object: site-front

  - subject: orchestrator
    predicate: depends_on
    object: site-front

  - subject: spec-to-code
    predicate: reads
    object: site-0-spec

  - subject: spec-to-code
    predicate: follows_rule
    object: minimal-project-evo-rules

  - subject: spec-to-code
    predicate: generates
    object: generated-code

  - subject: generated-code
    predicate: includes_artifact
    object: generated-site-front

  - subject: generated-code
    predicate: includes_artifact
    object: generated-docker-compose

  - subject: site-front
    predicate: provides_behavior
    object: render-counter-static-value

  - subject: app-builds
    predicate: validates
    object: generated-docker-compose

  - subject: app-runs
    predicate: validates
    object: generated-code

  - subject: page-renders-counter
    predicate: validates
    object: render-counter-static-value
```

---

# 4. Workflow Instance

```yaml
workflow:
  - id: site-0-spec-to-code-flow
    from: site-0-spec
    command: spec-to-code
    to: generated-code
```

---

# 5. State Instance

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

```yaml
transitions:
  - id: generate-code-from-spec
    from: spec-defined
    to: code-generated
    triggered_by: spec-to-code

  - id: run-generated-code
    from: code-generated
    to: runnable
    triggered_by: docker-compose up --build succeeds

  - id: accept-generated-code
    from: runnable
    to: accepted
    triggered_by: acceptance checks pass
```

---

# 6. Instance Boundary

Explicitly absent from this site-0 instance:

```yaml
not_used:
  implementation_areas:
    - site-backend
    - admin-front
    - admin-backend
    - db-canonical
    - db-read
    - etl

  product_capabilities:
    - real counter mutation
    - backend API
    - persistence
    - authentication
    - authorization
    - admin UI
    - i18n
    - routing
```
