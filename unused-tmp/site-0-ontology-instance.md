---
id: project.spec.site-0.ontology-instance
type: ontology-instance
status: active
scope: site-0
conforms_to: method.ontology.project-evo-method-schema
---

# Site-0 Ontology Instance

This file is the concrete method graph for `site-0`.

It instantiates the reusable entity types and relation types from:

```text
method/ontology/project-evo-method-schema.md
```

## 1. Instances

```yaml
instances:
  - id: site-0
    type: Project

  - id: project-evo-method-minimal
    type: Method

  - id: method.rules.impl-area-rule
    type: Rule

  - id: method.rules.spec-to-code-rule
    type: Rule

  - id: method.rules.acceptance-check-rule
    type: Rule

  - id: method.command-schemas.spec-to-code-command-schema
    type: CommandSchema

  - id: project.method-instance.commands.spec-to-code.site-0
    type: CommandInstance

  - id: project-spec
    type: Spec
    path: project/artifacts/spec/**

  - id: spec-index
    type: SpecFile
    path: project/artifacts/00-meta/spec-index.md

  - id: site-0-brief
    type: SpecFile
    path: project/artifacts/10-product/brief-000-structure.md

  - id: implementation-areas-spec
    type: SpecFile
    path: project/views/implementation-areas.view.md

  - id: site-front-contract
    type: SpecFile
    path: project/artifacts/spec/30-impl-areas-instances/31-site-front/site-front-contract.md

  - id: orchestrator-contract
    type: SpecFile
    path: project/artifacts/spec/30-impl-areas-instances/32-orchestrator/orchestrator-contract.md

  - id: acceptance-checks-spec
    type: SpecFile
    path: project/artifacts/spec/60-quality/acceptance-checks.md

  - id: site-front
    type: ImplementationArea
    kind: application

  - id: orchestrator
    type: ImplementationArea
    kind: infrastructure

  - id: generated-code
    type: GeneratedCode
    path: generated/**

  - id: generated-site-front
    type: Artifact
    path: generated/site-front/**

  - id: generated-docker-compose
    type: Artifact
    path: generated/docker-compose.yaml

  - id: render-counter-static-value
    type: Behavior

  - id: app-builds
    type: AcceptanceCheck

  - id: app-runs
    type: AcceptanceCheck

  - id: page-renders-counter
    type: AcceptanceCheck

  - id: spec-defined
    type: State

  - id: code-generated
    type: State

  - id: runnable
    type: State

  - id: accepted
    type: State
```

## 2. Relations

```yaml
relations:
  - subject: site-0
    predicate: uses_method
    object: project-evo-method-minimal

  - subject: project-evo-method-minimal
    predicate: defines_rule
    object: method.rules.impl-area-rule

  - subject: project-evo-method-minimal
    predicate: defines_rule
    object: method.rules.spec-to-code-rule

  - subject: project-evo-method-minimal
    predicate: defines_rule
    object: method.rules.acceptance-check-rule

  - subject: project-evo-method-minimal
    predicate: defines_command_schema
    object: method.command-schemas.spec-to-code-command-schema

  - subject: site-0
    predicate: has_spec
    object: project-spec

  - subject: project-spec
    predicate: contains
    object: spec-index

  - subject: project-spec
    predicate: contains
    object: site-0-brief

  - subject: project-spec
    predicate: contains
    object: implementation-areas-spec

  - subject: project-spec
    predicate: contains
    object: site-front-contract

  - subject: project-spec
    predicate: contains
    object: orchestrator-contract

  - subject: project-spec
    predicate: contains
    object: acceptance-checks-spec

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
    predicate: depends_on
    object: site-front

  - subject: project.method-instance.commands.spec-to-code.site-0
    predicate: instantiates
    object: method.command-schemas.spec-to-code-command-schema

  - subject: project.method-instance.commands.spec-to-code.site-0
    predicate: reads
    object: project-spec

  - subject: project.method-instance.commands.spec-to-code.site-0
    predicate: follows_rule
    object: method.rules.impl-area-rule

  - subject: project.method-instance.commands.spec-to-code.site-0
    predicate: follows_rule
    object: method.rules.spec-to-code-rule

  - subject: project.method-instance.commands.spec-to-code.site-0
    predicate: follows_rule
    object: method.rules.acceptance-check-rule

  - subject: project.method-instance.commands.spec-to-code.site-0
    predicate: generates
    object: generated-code

  - subject: generated-code
    predicate: contains
    object: generated-site-front

  - subject: generated-code
    predicate: contains
    object: generated-docker-compose

  - subject: site-front
    predicate: provides
    object: render-counter-static-value

  - subject: app-builds
    predicate: validates
    object: generated-code

  - subject: app-runs
    predicate: validates
    object: generated-docker-compose

  - subject: page-renders-counter
    predicate: validates
    object: render-counter-static-value
```

## 3. Workflow states

```yaml
states:
  - id: spec-defined
    meaning: project specs and method instance exist

  - id: code-generated
    meaning: generated/ contains code produced from specs

  - id: runnable
    meaning: generated project starts with Docker Compose

  - id: accepted
    meaning: acceptance checks pass
```

## 4. Transitions

```yaml
transitions:
  - id: generate-code
    from: spec-defined
    to: code-generated
    triggered_by: project.method-instance.commands.spec-to-code.site-0

  - id: run-project
    from: code-generated
    to: runnable
    condition: docker-compose up --build succeeds

  - id: accept-project
    from: runnable
    to: accepted
    condition: acceptance checks pass
```
