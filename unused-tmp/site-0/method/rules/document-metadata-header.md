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

## Rule

Every method-significant or machine-readable file MUST start with a YAML front matter metadata header.

The metadata header gives the file a stable identity inside `project-evo-method` and allows tools to index, validate, select, and connect method/project documents.

## Required when

A metadata header is required for files that belong to one of these categories:

- method ontology
- method rule
- command schema
- command input
- project ontology instance
- project index
- spec source
- impl-area spec
- generated manifest
- generated report
- validation contract
- machine-readable view metadata

## Optional when

A metadata header is optional for files that are purely human-readable and are not used by the method engine.

Examples:

- README files
- temporary notes
- draft explanations
- informal reports
- local scratch files

## Minimum fields

```yaml
---
id: method.rules.example
type: rule
status: active
scope: reusable-method
---