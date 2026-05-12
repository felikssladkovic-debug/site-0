---
id: method.reports.implementation-areas
type: report-meta
report_name: implementation-areas.report.md
---

# Implementation Areas Report Meta

## Purpose

Generate a human-readable overview of implementation areas for a project.

## Source files

- `project/method-instance/ontology/<project-id>-ontology-instance.yaml`

## Output file

- `project/artifacts/spec/20-architecture/implementation-areas.report.md`

## Generation rules

The report must include:

1. Project id.
2. List of implementation areas.
3. For each implementation area:
    - id
    - kind
    - owned artifacts
    - dependencies
    - role in the project
4. Connections/dependencies between implementation areas.
5. Warning that this file is generated and must not be edited manually.

## Source-of-truth rule

If this report conflicts with ontology instance YAML, the ontology instance YAML wins.