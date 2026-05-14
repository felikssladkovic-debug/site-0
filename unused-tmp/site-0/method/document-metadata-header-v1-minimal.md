---
id: method.rules.document-metadata-header
type: rule
status: active
scope: reusable-method
---

# Document Metadata Header

## Purpose

This document defines the rules for metadata headers used in method documents inside `project-evo-method`.

This rule applies only to documents that belong to the reusable method itself.

It does NOT define rules for:

- project instance documents
- generated code
- generated artifacts
- application runtime files

Rules for project-level documents MAY be introduced later as separate method rules.

---

# Core Rule

Every method document that participates in the method engine MUST start with a YAML front matter metadata header.

Method documents that do not participate in the method engine MAY omit the metadata header.

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

The metadata header gives the document:

- stable identity
- document type
- lifecycle status
- scope/ownership

---

# Naming

## Correct terminology

The technical format is called:

- YAML front matter

Inside `project-evo-method`, its semantic role is called:

- document metadata header

---

# When metadata headers are REQUIRED

A metadata header is REQUIRED for reusable method documents used by:

- validation
- generation
- graph construction
- context selection
- orchestration
- method automation

This includes files such as:

- method rules
- ontology schemas
- command schemas
- machine-readable method views
- method validation contracts

---

# When metadata headers are OPTIONAL

A metadata header is OPTIONAL for reusable method files that are only informational or human-oriented.

Examples:

- README files
- temporary notes
- scratch files
- informal drafts
- purely explanatory documents

If such files later become part of automation or validation flows, they MUST receive metadata headers.

---

# Minimum required fields

Every metadata header MUST contain exactly these fields:

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

Additional metadata fields are not part of the current rule version.

---

# Field Definitions

## id

Stable document identifier inside the reusable method graph.

The identifier SHOULD remain stable across refactors whenever possible.

Recommended format:

```text
<domain>.<category>.<document-name>
```

Examples:

```text
method.rules.document-metadata-header
method.command-schemas.spec-to-code-command-schema
method.rules.validation-contract
```

The `id` is the canonical identity of the document.

File paths MAY change.
The `id` SHOULD change only when the document meaning changes.

---

## type

Defines the document kind.

Examples:

```text
rule
command-schema
ontology-schema
view-meta
validation-contract
```

The `type` field is used by tooling to determine processing behavior.

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
generated-artifact
```

Recommended meaning:

- `reusable-method` — reusable across projects
- `generated-artifact` — produced automatically by method tooling

---

# Validation Rules

Tools MAY validate:

- metadata header existence
- required fields existence
- unique `id`
- known `type`
- known `status`
- known `scope`

---

# Design Principle

The metadata header exists because `project-evo-method` treats reusable method documents as a structured automation graph.

A document without identity cannot reliably participate in:

- orchestration
- validation
- context construction
- bounded generation
- reproducible automation

At the same time, the method should avoid unnecessary complexity during early stages of method development.

The first version of the metadata header is intentionally minimal.

The goal is:

- strict structure where automation requires it
- minimal cognitive load
- minimal ontology surface
- gradual evolution of the method
