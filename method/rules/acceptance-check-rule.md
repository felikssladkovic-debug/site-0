---
id: method.rules.acceptance-check-rule
type: method-rule
status: active
scope: reusable-method
---

# Acceptance Check Rule

Acceptance checks are deterministic validations run after generated artifacts are produced.

## Required behavior

```yaml
required_behavior:
  - validate required generated files exist
  - validate forbidden implementation areas are not generated
  - validate implementation-specific static contracts
  - optionally run executable build/runtime checks when the local environment supports them
```
