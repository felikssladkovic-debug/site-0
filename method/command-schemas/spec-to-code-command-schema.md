---
id: method.command-schemas.spec-to-code-command-schema
type: command-schema
status: active
scope: reusable-method
---

# Spec To Code Command Schema

This is the reusable command schema for generating code from project specs.

It defines the generic command contract.

It must not include concrete project values.

## Command schema

```yaml
command_schema:
  id: spec-to-code
  purpose: Generate implementation artifacts from project specs.
```

## Required inputs

A concrete command instance must read:

```yaml
required_inputs:
  - method ontology schema
  - reusable method rules enabled by the project instance
  - this command schema
  - project method instance profile
  - project ontology instance
  - project spec files
```

## Required outputs

A concrete command instance must write generated artifacts into the output root declared by the project instance.

```yaml
required_outputs:
  - generated code artifact set
```

## Generic execution behavior

The executing agent must:

```yaml
steps:
  - identify project-specific implementation areas
  - identify generated artifact ownership for each implementation area
  - read all project spec files
  - generate code and runtime artifacts under the declared output root
  - keep generated artifacts aligned with implementation area contracts
  - avoid any undeclared functionality
  - provide a concise completion summary
```

## Generic refusal conditions

The agent should stop and report an issue if:

```yaml
stop_conditions:
  - required project method instance files are missing
  - implementation area ownership is contradictory
  - output root is not declared
  - acceptance checks contradict project specs
```
