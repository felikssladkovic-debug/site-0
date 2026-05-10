---
id: method.ontology.project-evo-method-schema
type: method-ontology-schema
status: active
scope: project-evo-method-minimal
version: 0.1.0
---

# Project Evo Method Schema

This document defines the minimal method-level ontology schema used by the `site-0` case.

It describes entity types, relation types, and validation expectations that can be reused by concrete project instances.

This schema intentionally contains no `site-0`-specific technology choices, UI text, service names, or generated file paths except when used as examples.

---

# 1. Purpose

The schema separates the reusable project-evo-method model from a concrete project instance.

The method schema answers:

```text
What kinds of things may exist in a project-evo project?
How may they be connected?
What minimal structural constraints should an instance satisfy?
```

A project instance answers:

```text
Which concrete project, impl-areas, commands, specs, artifacts, and checks exist now?
```

---

# 2. Entity Types

## 2.1 Project

A `Project` is the root unit of work managed by project-evo-method.

Required properties:

```yaml
Project:
  id: string
  name: string
  purpose: string
```

---

## 2.2 Method

A `Method` is a set of rules, commands, ontology schema, and workflow constraints used to evolve a project.

Required properties:

```yaml
Method:
  id: string
  scope: string
```

---

## 2.3 Rule

A `Rule` is a constraint that governs interpretation, transformation, or validation of project artifacts.

Required properties:

```yaml
Rule:
  id: string
  path: string
```

---

## 2.4 Command

A `Command` is an executable instruction for an LLM/code agent.

Required properties:

```yaml
Command:
  id: string
  path: string
  input: string
  output: string
```

---

## 2.5 Spec

A `Spec` is a source-of-truth artifact set describing what should be produced.

Required properties:

```yaml
Spec:
  id: string
  root: string
```

---

## 2.6 SpecFile

A `SpecFile` is one file inside the spec set.

Required properties:

```yaml
SpecFile:
  id: string
  path: string
  role: string
```

---

## 2.7 ImplementationArea

An `ImplementationArea` is a bounded part of the system that owns a coherent set of implementation artifacts.

An implementation area may be application-level or infrastructure-level.

Required properties:

```yaml
ImplementationArea:
  id: string
  kind: application | infrastructure
  responsibility: string
```

---

## 2.8 Artifact

An `Artifact` is a concrete file, directory, or generated output owned by an implementation area.

Required properties:

```yaml
Artifact:
  id: string
  path: string
  generated: boolean
```

---

## 2.9 GeneratedCode

`GeneratedCode` is the output artifact set produced by a command.

Required properties:

```yaml
GeneratedCode:
  id: string
  root: string
  produced_by: Command
```

---

## 2.10 Behavior

A `Behavior` is an observable behavior that generated code must provide.

Required properties:

```yaml
Behavior:
  id: string
  description: string
```

---

## 2.11 AcceptanceCheck

An `AcceptanceCheck` is a validation condition used to decide whether generated artifacts satisfy the spec.

Required properties:

```yaml
AcceptanceCheck:
  id: string
  description: string
  validates: Artifact | Behavior | ImplementationArea | GeneratedCode
```

---

## 2.12 State

A `State` is a named point in a project workflow.

Required properties:

```yaml
State:
  id: string
  meaning: string
```

---

## 2.13 Transition

A `Transition` is an allowed movement between workflow states.

Required properties:

```yaml
Transition:
  id: string
  from: State
  to: State
  triggered_by: Command | condition
```

---

# 3. Relation Types

The following relation types are allowed in the minimal schema.

```yaml
relation_types:
  - predicate: uses_method
    subject_type: Project
    object_type: Method

  - predicate: defines_rule
    subject_type: Method
    object_type: Rule

  - predicate: defines_command
    subject_type: Method
    object_type: Command

  - predicate: defines_schema
    subject_type: Method
    object_type: method-ontology-schema

  - predicate: has_spec
    subject_type: Project
    object_type: Spec

  - predicate: contains_spec_file
    subject_type: Spec
    object_type: SpecFile

  - predicate: has_impl_area
    subject_type: Project
    object_type: ImplementationArea

  - predicate: owns
    subject_type: ImplementationArea
    object_type: Artifact

  - predicate: reads
    subject_type: Command
    object_type: Spec

  - predicate: follows_rule
    subject_type: Command
    object_type: Rule

  - predicate: generates
    subject_type: Command
    object_type: GeneratedCode

  - predicate: includes_artifact
    subject_type: GeneratedCode
    object_type: Artifact

  - predicate: provides_behavior
    subject_type: ImplementationArea
    object_type: Behavior

  - predicate: validates
    subject_type: AcceptanceCheck
    object_type: Artifact | Behavior | ImplementationArea | GeneratedCode

  - predicate: depends_on
    subject_type: ImplementationArea
    object_type: ImplementationArea

  - predicate: runs
    subject_type: ImplementationArea
    object_type: ImplementationArea

  - predicate: builds
    subject_type: ImplementationArea
    object_type: ImplementationArea
```

---

# 4. Minimal Structural Constraints

A valid minimal project instance must satisfy these constraints.

```yaml
constraints:
  - id: project-has-method
    rule: Every Project must use exactly one Method.

  - id: project-has-spec
    rule: Every Project must have one Spec root.

  - id: project-has-command
    rule: The Method must define at least one Command.

  - id: command-has-input-output
    rule: Every Command must define input and output.

  - id: impl-area-owns-artifacts
    rule: Every ImplementationArea must own at least one Artifact or explicitly declare that it owns no generated artifacts yet.

  - id: generated-code-produced-by-command
    rule: Every GeneratedCode root must be produced by one Command.

  - id: generated-artifacts-owned
    rule: Every generated Artifact must be owned by one ImplementationArea.

  - id: acceptance-checks-exist
    rule: A minimal project must define acceptance checks for build/run and primary visible behavior when applicable.
```

---

# 5. Minimal Workflow Pattern

The minimal workflow pattern is:

```text
spec -> code
```

Formal schema:

```yaml
workflow_pattern:
  id: spec-to-code-flow
  input_type: Spec
  command_type: Command
  output_type: GeneratedCode
```

---

# 6. Boundary

This schema is intentionally minimal. It does not yet model:

```yaml
excluded_from_minimal_schema:
  - idea lifecycle
  - feature lifecycle
  - code-to-spec validation
  - spec-to-idea validation
  - multiple environments
  - deployment targets
  - test coverage model
  - database model
  - API model
  - agent roles
  - human approval gates
```
