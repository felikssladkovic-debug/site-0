---
id: method.ontology.project-evo-method-schema
type: method-schema
status: active
scope: reusable-method
---

# Project Evo Method Schema

This document defines the reusable ontology schema for the minimal slice of `project-evo-method` used by `site-0`.

It defines entity types, relation types, and structural constraints.

It must not contain project-specific values such as `site-0`, `site-front`, `orchestrator`, Vue, Vite, Tailwind, Docker Compose, or concrete UI text.

## 1. Entity Types

```yaml
entity_types:
  - Project
  - Method
  - Rule
  - CommandSchema
  - CommandInstance
  - Spec
  - SpecFile
  - ImplementationArea
  - Artifact
  - GeneratedCode
  - AcceptanceCheck
  - Behavior
  - State
  - Transition
```

## 2. Entity Type Definitions

### Project

A `Project` is the root unit of work managed by the method.

### Method

A `Method` is a reusable system of ontology, rules, and command schemas.

### Rule

A `Rule` is a reusable constraint that governs artifacts, commands, implementation areas, generated code, or validation.

### CommandSchema

A `CommandSchema` is a reusable command contract. It defines expected inputs, outputs, and behavior, but does not contain project-specific instructions.

### CommandInstance

A `CommandInstance` is a concrete command applied to a specific project. It references a `CommandSchema` and supplies project-specific context and constraints.

### Spec

A `Spec` is a source-of-truth artifact set that describes the desired project behavior, structure, implementation areas, runtime, and acceptance checks.

### SpecFile

A `SpecFile` is one file inside a `Spec`.

### ImplementationArea

An `ImplementationArea` is a bounded part of the generated system that owns a coherent set of artifacts.

Implementation areas may be application-level or infrastructure-level.

### Artifact

An `Artifact` is a file or directory that is produced, owned, validated, or consumed.

### GeneratedCode

`GeneratedCode` is the output artifact set produced from specs by a command instance.

### AcceptanceCheck

An `AcceptanceCheck` is a validation condition for generated artifacts and behavior.

### Behavior

A `Behavior` is an observable property of the generated system.

### State

A `State` is a named point in the workflow lifecycle.

### Transition

A `Transition` is a permitted movement from one state to another.

## 3. Relation Types

```yaml
relation_types:
  - subject_type: Project
    predicate: uses_method
    object_type: Method

  - subject_type: Method
    predicate: defines_rule
    object_type: Rule

  - subject_type: Method
    predicate: defines_command_schema
    object_type: CommandSchema

  - subject_type: Project
    predicate: has_spec
    object_type: Spec

  - subject_type: Spec
    predicate: contains
    object_type: SpecFile

  - subject_type: Project
    predicate: has_impl_area
    object_type: ImplementationArea

  - subject_type: ImplementationArea
    predicate: owns
    object_type: Artifact

  - subject_type: ImplementationArea
    predicate: depends_on
    object_type: ImplementationArea
    question: приведи пример, когда этот connection?

  - subject_type: CommandInstance
    predicate: instantiates
    object_type: CommandSchema
    question: нужно точнее описать механизм для команд - что именно в method/command-schema, а что в project/method-instance/commands - класс+экземпляр(как Java), или prototype+addon(как JavaScript) 

  - subject_type: CommandInstance
    predicate: reads
    object_type: Spec

  - subject_type: CommandInstance
    predicate: follows_rule
    object_type: Rule

  - subject_type: CommandInstance
    predicate: generates
    object_type: GeneratedCode

  - subject_type: GeneratedCode
    predicate: contains
    object_type: Artifact

  - subject_type: AcceptanceCheck
    predicate: validates
    object_type: Artifact
    question: нужно уточнить, что такое AcceptanceCheck - это набор правил валидации(данные для валидатора), или это экземпляр кода, который выполняет валидацию 
      
  - subject_type: AcceptanceCheck
    predicate: validates
    object_type: Behavior
    question: как будто это разные AcceptanceCheck - для Artifact и для Behavior. Хотя, смысл/назначения - про одно, это проверка валидности. Как обычно в таких случаях делают - разделяют или нет?  
    
  - subject_type: Transition
    predicate: from_state
    object_type: State

  - subject_type: Transition
    predicate: to_state
    object_type: State

  - subject_type: Transition
    predicate: triggered_by
    object_type: CommandInstance
```

## 4. Structural Constraints

```yaml
constraints:
  - id: project-has-method
    rule: Every Project must use exactly one Method in a minimal method application.

  - id: project-has-spec
    rule: Every Project must have a Spec.

  - id: project-has-impl-area
    rule: Every Project must have one or more ImplementationArea instances.

  - id: impl-area-owns-artifacts
    rule: Every ImplementationArea must own at least one Artifact pattern.

  - id: artifact-owned-once
    rule: Each generated artifact should be owned by exactly one ImplementationArea unless explicitly declared shared.

  - id: command-instance-instantiates-schema
    rule: Every CommandInstance must instantiate exactly one CommandSchema.

  - id: command-instance-has-output
    rule: Every CommandInstance must generate a GeneratedCode artifact set or another explicitly declared output artifact set.

  - id: generated-code-validated
    rule: GeneratedCode must be covered by AcceptanceCheck instances appropriate to the project scope.
```
