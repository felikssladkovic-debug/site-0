---
id: project.spec.site-0.index
type: spec-index
status: active
scope: site-0
---

# Site-0 Spec Index

This index lists the minimal project specs for `site-0`.

## Spec files

```yaml
spec_files:
  - id: project.spec.site-0.ontology-instance
    path: project/spec/00-meta/site-0-ontology-instance.md
    role: concrete method graph for this project

  - id: project.spec.site-0.brief
    path: project/spec/10-product/site-0-brief.md
    role: product brief

  - id: project.spec.site-0.implementation-areas
    path: project/spec/20-architecture/implementation-areas.md
    role: implementation area map

  - id: project.spec.site-0.site-front-contract
    path: project/spec/30-site-front/site-front-contract.md
    role: contract for site-front implementation area

  - id: project.spec.site-0.orchestrator-contract
    path: project/spec/40-orchestrator/orchestrator-contract.md
    role: contract for orchestrator implementation area

  - id: project.spec.site-0.acceptance-checks
    path: project/spec/60-quality/acceptance-checks.md
    role: acceptance checks
```

## Method files used by this project

```yaml
method_files:
  - path: method/ontology/project-evo-method-schema.md
  - path: method/rules/impl-area-rule.md
  - path: method/rules/spec-to-code-rule.md
  - path: method/rules/acceptance-check-rule.md
  - path: method/command-schemas/spec-to-code-command-schema.md
```

## Project method instance files

```yaml
project_method_instance_files:
  - path: project/method-instance/rules-profile.md
  - path: project/method-instance/commands/spec-to-code.site-0.md
```
