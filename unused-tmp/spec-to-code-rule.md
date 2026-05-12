---
id: method.rules.spec-to-code-rule
type: method-rule
status: active
scope: reusable-method
---

# Spec To Code Rule

This reusable rule defines the contract for transforming project specs into generated code.

It does not contain project-specific instructions.

## Rule

The code generation agent must treat `Spec` as the source of truth.

The agent must:

```yaml
must:
  - read the project method instance
  - read enabled reusable method rules
  - read the project spec files
  - generate only artifacts allowed by the project method instance
  - preserve implementation area boundaries
  - satisfy declared acceptance checks
```

The agent must not:

```yaml
must_not:
  - invent undeclared implementation areas
  - generate undeclared services
  - add undeclared runtime dependencies
  - add features not present in the project spec
  - modify method-level reusable schema files as part of code generation
```

## Input contract

A concrete `spec-to-code` command instance should provide:

```yaml
inputs:
  - method ontology schema
  - enabled method rules
  - command schema
  - project method instance profile
  - project ontology instance
  - project spec files
```

## Output contract

A concrete `spec-to-code` command instance should declare the output root.

The output root should contain all generated code and runtime artifacts.
