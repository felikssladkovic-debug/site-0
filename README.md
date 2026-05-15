# project-evo-method foundation-00-minimal / site-0

This repository is a minimal executable slice of `project-evo-method`.

Foundation version: `foundation-00-minimal`.

The goal of this version is to validate the vertical chain:

```text
/meta checks /method
/method executes a method action
/project--site-0 provides project input/state
/project--site-0/generated receives generated runnable code
```

`project-evo-method` is treated here as an executable method environment.

A human uses it through predefined commands and project files. The method reads project state, performs deterministic or LLM-assisted actions, writes artifacts, and validates the result.

In this v0 skeleton, the only supported application project is:

```text
project--site-0
```

The single entry point for user-facing commands is:

```bash
./evo-root.sh
```

## Commands

Show help:

```bash
./evo-root.sh help
```

Check metadata headers in `/method`:

```bash
./evo-root.sh check-document-metadata-header
```

Run tests for the metadata-header checker:

```bash
./evo-root.sh test check-document-metadata-header
```

Generate runnable code for `project--site-0` from its single spec document:

```bash
./evo-root.sh spec-to-code
```

Run tests for `spec-to-code`:

```bash
./evo-root.sh test spec-to-code
```

Run all tests:

```bash
./evo-root.sh test
```

Run the full minimal smoke check:

```bash
bash ./evo-root.sh smoke
```

How the smoke command works:
- the smoke command performs the checks in a managed run workspace, not in the original project tree:

```text
- create .project-evo/runs/<run-id>/
- copy the repository into .project-evo/runs/<run-id>/workspace/
- check-document-metadata-header inside the workspace
- test inside the workspace
- spec-to-code through method/tools/fake-llm.py inside the workspace
- verify that project--site-0/generated/index.html exists inside the workspace
- delete the workspace on success
- keep the workspace on failure for inspection
- keep run.yaml and logs/smoke.log as the run journal
```

For debugging, keep the workspace even after a successful smoke run:

```bash
bash ./evo-root.sh smoke --keep-workspace
```

## Directory roles

```text
/.project-evo
```

Runtime bookkeeping for method command runs. At v0, `smoke` writes run journals under `.project-evo/runs/<run-id>/`. Successful runs keep only `run.yaml` and `logs/smoke.log`; failed runs also keep the copied `workspace/` for debugging.

```text
/meta
```

Layer-0 tools and rules.

`/meta` checks the structure of `/method`. At v0, it only checks document metadata headers in method documents.

Files in `/meta` are not required to follow the method document metadata-header rule.

```text
/method
```

Layer-1 implementation of `project-evo-method`.

It contains executable tools and method documents. At v0, there is one method action:

```text
method/tools/spec-to-code.py
```

```text
/project--site-0
```

Concrete application project workspace managed by the method.

At v0, it contains:

```text
project--site-0/spec/index.md
project--site-0/generated/
```

The generated runnable application code is the main practical output for the human, but inside `project-evo-method` it is treated as a generated artifact of a method action.

## Known limitations

This foundation is intentionally minimal. Known limitations:

- document metadata headers are required only for method documents in `/method`
- project documents are not required to have metadata headers
- `spec-to-code` reads exactly one project spec document
- `project--site-0` is the default project
- no impl-area graph is used
- no project ontology is used
- no ownership graph is used
- no repair loop is used
- generated code is intentionally minimal
- smoke still writes a run journal under `.project-evo/runs/`; generated project changes happen only inside the managed workspace

## Expected result

After running:

```bash
./evo-root.sh spec-to-code
```

the generated folder should contain a minimal static site:

```text
project--site-0/generated/index.html
```

You can open that file in a browser. It should display:

```text
Счетчик
1
```
