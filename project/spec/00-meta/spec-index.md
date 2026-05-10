---
id: spec.meta.index
type: spec-index
status: active
scope: site-0
---

# Spec Index

This is the source-of-truth spec set for the minimal `site-0` project.

## Method-level files

```text
method/ontology/project-evo-method-schema.md
method/rules/minimal-project-evo-rules.md
method/commands/spec-to-code.md
```

## Project spec files

```text
project/spec/00-meta/spec-index.md
project/spec/00-meta/site-0-ontology-instance.md
project/spec/10-product/site-0-brief.md
project/spec/20-architecture/implementation-areas.md
project/spec/30-site-front/site-front-contract.md
project/spec/40-orchestrator/orchestrator-contract.md
project/spec/60-quality/acceptance-checks.md
```

## Ontology relation

```text
method/ontology/project-evo-method-schema.md
  -> defines reusable project-evo-method entity and relation types

project/spec/00-meta/site-0-ontology-instance.md
  -> instantiates the method schema for site-0
```

## Method command

The only command needed for this case is:

```text
method/commands/spec-to-code.md
```

## Main transformation

```text
spec -> code
```

Input:

```text
project/spec/**
```

Output:

```text
generated/**
```
