---
id: spec.meta.index
type: spec-index
status: active
scope: site-0
---

# Spec Index

This is the source-of-truth spec set for the minimal `site-0` project.

## Files

```text
project/spec/00-meta/spec-index.md
project/spec/00-meta/site-0-ontology.md
project/spec/10-product/site-0-brief.md
project/spec/20-architecture/implementation-areas.md
project/spec/30-site-front/site-front-contract.md
project/spec/40-orchestrator/orchestrator-contract.md
project/spec/60-quality/acceptance-checks.md
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
