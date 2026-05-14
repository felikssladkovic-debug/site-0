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

## Implementation kind

It is implemented via python3 code: tools/spec-to-code.py
