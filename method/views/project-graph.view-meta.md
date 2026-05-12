# Project Graph View Meta

## Purpose

Generate a human-readable overview of the full project-evo graph for a project instance.

## Source files

- `project/method-instance/ontology/<project-id>-ontology-instance.yaml`
- optional: `project/artifacts/spec/spec-index.md`

## Output file

- `project/artifacts/views/project-graph.view.md`

## Generation rules

The generated view should include:

1. Project id.
2. Project state.
3. Implementation areas.
4. Dependencies between implementation areas.
5. Artifact ownership.
6. Source spec artifacts.
7. Generated artifacts.
8. Command instances.
9. Validation/report artifacts.
10. State transitions if present.

## Rendering style

The view should prioritize readability for a human reviewer.

Use:
- sections
- tables
- dependency lists
- ASCII graph snippets when useful

## Source-of-truth rule

If the generated view conflicts with ontology-instance YAML,
the ontology-instance YAML wins.