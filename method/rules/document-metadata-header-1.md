# YAML Front Matter / Metadata Header Terminology

## Recommended terminology

The correct terminology is:

- YAML front matter — technical format
- document metadata header — semantic role inside project-evo-method
- graph refs / wiki refs — explicit relations between documents

The example below is NOT a wiki-ref:

```yaml
---
id: method.command-schemas.spec-to-code-command-schema
type: command-schema
status: active
scope: reusable-method
---
```

This block is a document metadata header.

---

# Rule Recommendation

Metadata headers SHOULD exist in every machine-readable or method-significant file.

Metadata headers MAY be omitted in purely human-readable files that do not participate in the method engine.

---

# Files that SHOULD contain metadata headers

Examples:

- method rules
- ontology schemas
- ontology instances
- command schemas
- command inputs
- project indexes
- spec files
- impl-area specs
- manifests
- validation contracts
- machine-readable views

Reason:

These files participate in:

- indexing
- validation
- graph construction
- orchestration
- generation
- dependency analysis
- ownership analysis

Without stable metadata, the method engine cannot reliably process the document graph.

---

# Files where metadata headers are OPTIONAL

Examples:

- README files
- temporary notes
- drafts
- scratch files
- informal explanations

These files are considered human-oriented only.

If such files later become part of automation or validation flows, they SHOULD receive metadata headers.

---

# Minimum Required Metadata

Recommended minimum structure:

```yaml
---
id: method.rules.example
type: rule
status: active
scope: reusable-method
---
```

Required fields:

- id
- type
- status
- scope

---

# Meaning of Fields

## id

Stable identifier inside the project-evo graph.

Recommended format:

```text
<scope-area>.<category>.<document-name>
```

Examples:

```text
method.rules.document-metadata-header
method.command-schemas.spec-to-code-command-schema
project.spec.site-front
project.commands.spec-to-code.site-0
```

---

## type

Defines the document kind.

Examples:

```text
rule
command-schema
command-input
ontology-schema
ontology-instance
spec
impl-area-spec
manifest
report
view-meta
```

---

## status

Defines lifecycle state.

Examples:

```text
draft
active
deprecated
archived
```

---

## scope

Defines reuse and ownership scope.

Examples:

```text
reusable-method
project-instance
generated-artifact
```

---

# Optional Graph References

Metadata headers MAY contain graph-reference fields.

Examples:

```yaml
depends_on:
  - method.rules.document-metadata-header

implements:
  - method.command-schemas.spec-to-code-command-schema

derived_from:
  - project.spec.site-0
```

These fields SHOULD exist only when the relation is meaningful for:

- validation
- generation
- dependency analysis
- navigation
- orchestration

The method SHOULD avoid meaningless graph noise.

---

# Core Principle

Metadata headers should be mandatory where automation requires stable structure, and optional where documents exist only for human readability.
