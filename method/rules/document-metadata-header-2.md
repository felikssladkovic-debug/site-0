---
id: method.rules.document-metadata-header
type: rule
status: active
scope: reusable-method
---

# Document Metadata Header

## Purpose

This document defines the rules for metadata headers used in `project-evo-method`.

The metadata header is part of the method contract.

It serves both purposes simultaneously:

1. machine-readable contract for tools and automation
2. human-readable explanation of document identity and graph structure

This file itself is the source of truth.
No parallel README or duplicate explanation should exist for the same rule.

---

# Core Rule

Every file that participates in the method engine MUST start with a YAML front matter metadata header.

Files that do not participate in the method engine MAY omit the metadata header.

---

# What is a metadata header

The metadata header is a YAML front matter block placed at the beginning of the file.

Example:

```yaml
---
id: method.rules.document-metadata-header
type: rule
status: active
scope: reusable-method
---
```

The metadata header gives the file:

- stable identity
- document type
- lifecycle status
- scope/ownership
- optional graph relations

---

# Naming

## Correct terminology

The technical format is called:

- YAML front matter

Inside `project-evo-method`, its semantic role is called:

- document metadata header

The term:

- wiki refs

should NOT be used for the metadata header itself.

Instead, `wiki refs` should refer only to explicit graph relations between documents.

Examples:

```yaml
depends_on:
  - method.rules.document-metadata-header

implements:
  - method.command-schemas.spec-to-code-command-schema
```

---

# When metadata headers are REQUIRED

A metadata header is REQUIRED for all files that are used by:

- validation
- generation
- graph construction
- context selection
- orchestration
- ownership analysis
- dependency analysis
- method automation

This includes files such as:

- method rules
- ontology schemas
- ontology instances
- command schemas
- command inputs
- project indexes
- spec files
- impl-area specs
- manifests
- generated reports
- machine-readable view metadata

---

# When metadata headers are OPTIONAL

A metadata header is OPTIONAL for files that are only informational and are not used by the method engine.

Examples:

- README files
- temporary notes
- scratch files
- informal drafts
- purely explanatory documents

If such files later become part of automation or validation flows, they MUST receive metadata headers.

---

# Minimum required fields

Every metadata header MUST contain at least:

```yaml
---
id: method.rules.example
type: rule
status: active
scope: reusable-method
---
```

Required fields:

- `id`
- `type`
- `status`
- `scope`

---

# Field Definitions

## id

Stable document identifier inside the project-evo graph.

The identifier MUST remain stable across refactors whenever possible.

Recommended format:

```text
<domain>.<category>.<document-name>
```

Examples:

```text
method.rules.document-metadata-header
method.command-schemas.spec-to-code-command-schema
project.spec.site-front
project.commands.spec-to-code.site-0
```

The `id` is the canonical identity of the document.
File paths MAY change.
The `id` should change only when the document meaning changes.

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

The `type` field is used by tooling to determine processing rules.

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

Recommended meaning:

- `draft` — unstable work in progress
- `active` — current valid document
- `deprecated` — still recognized but should not be used for new work
- `archived` — historical reference only

---

## scope

Defines reuse and ownership boundaries.

Examples:

```text
reusable-method
project-instance
generated-artifact
```

Recommended meaning:

- `reusable-method` — reusable across many projects
- `project-instance` — specific to one project instance
- `generated-artifact` — produced by automation or generation

---

# Optional Graph Relation Fields

Metadata headers MAY contain explicit graph relations.

Examples:

```yaml
depends_on:
  - method.rules.document-metadata-header

implements:
  - method.command-schemas.spec-to-code-command-schema

derived_from:
  - project.spec.site-0
```

These fields are OPTIONAL.

They should exist only when the relationship is meaningful for:

- validation
- navigation
- generation
- dependency analysis
- orchestration
- ownership analysis

The method SHOULD avoid meaningless graph noise.

---

# Validation Rules

Tools MAY validate:

- metadata header existence
- required fields existence
- unique `id`
- known `type`
- known `status`
- known `scope`
- existence of referenced graph targets
- broken references
- duplicate ownership definitions
- invalid dependency chains

---

# Design Principle

The metadata header exists because `project-evo-method` treats documents as a graph of contracts.

A document without identity cannot reliably participate in:

- orchestration
- validation
- dependency analysis
- context construction
- bounded generation
- reproducible automation

At the same time, the method should avoid unnecessary metadata in files that are purely human-oriented and not part of the executable graph.

The goal is:

- strict structure where automation requires it
- low complexity where automation does not require it
