---
id: method.rules.spec-to-code-rule
type: method-rule
status: active
scope: reusable-method
---

# Spec To Code Rule

A `spec-to-code` runner must generate artifacts only from declared project specs and only inside declared generated artifact ownership boundaries.

## Required behavior

```yaml
required_behavior:
  - load command input
  - validate command input
  - validate spec index paths
  - validate implementation area graph
  - validate artifact ownership
  - create bounded context bundles per implementation area
  - call the configured bounded LLM command per implementation area
  - validate generated boundaries after each call
  - run implementation-area checks
  - repair through bounded LLM calls when checks fail
  - write manifests and final report
```

## Boundary rule

Generated files must be inside `output_root` and must match exactly one declared artifact ownership pattern unless an explicit shared ownership rule exists.
