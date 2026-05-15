# project-evo-method foundation-00-minimal / site-0

This repository is a minimal executable slice of `project-evo-method`.

Foundation version: `foundation-00-minimal`.

The goal of this version is to validate the vertical chain:

```text
/meta checks /method
/method executes method-level actions
/project--site-0 provides project input/state
/project--site-0/generated receives generated runnable code
```

`project-evo-method` is treated here as an executable method environment.

A human uses it through predefined commands and project files. The method reads project state, performs deterministic or LLM-assisted actions, writes artifacts, and validates the result.

In this v0 skeleton, the included application project is:

```text
project--site-0
```

## Entry points

The command surface is intentionally split by context.

```text
/method/evo-method.sh
```

Method-level CLI. Use this to work with the method itself, run method checks, run method smoke, or initialize application projects.

```text
/meta/evo-meta.sh
```

Meta-level CLI. Use this for checks that validate the method implementation.

```text
/project--site-0/evo.sh
```

Application-project CLI. Use this inside a concrete project managed by the method.

## Runtime directories

```text
/project--site-0/.evo
```

Runtime bookkeeping for an application project.

```text
/method/.evo-method
```

Runtime bookkeeping for method-level command runs. At v0, `smoke` writes run journals under `method/.evo-method/runs/<run-id>/`.

```text
/meta/.evo-meta
```

Runtime bookkeeping for meta-level command runs. At v0, it only reserves the namespace.

## Method commands

Show method help:

```bash
bash ./method/evo-method.sh help
```

Check metadata headers in `/method` through the method CLI:

```bash
bash ./method/evo-method.sh check-document-metadata-header
```

Run all tests:

```bash
bash ./method/evo-method.sh test
```

Run tests for one command:

```bash
bash ./method/evo-method.sh test check-document-metadata-header
bash ./method/evo-method.sh test spec-to-code
```

Generate runnable code for `project--site-0` from its single spec document:

```bash
bash ./method/evo-method.sh spec-to-code --project-dir ./project--site-0
```

Run the full minimal smoke check:

```bash
bash ./method/evo-method.sh smoke
```

The smoke command performs the checks in a managed run workspace, not in the original project tree:

```text
- create method/.evo-method/runs/<run-id>/
- copy the repository into method/.evo-method/runs/<run-id>/workspace/
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
bash ./method/evo-method.sh smoke --keep-workspace
```

## Application project commands

From the included project:

```bash
cd project--site-0
bash ./evo.sh help
bash ./evo.sh spec-to-code
```

`project--site-0/evo.sh` dispatches to command scripts under:

```text
project--site-0/evo/
```

## Meta commands

Show meta help:

```bash
bash ./meta/evo-meta.sh help
```

Run the metadata-header check directly from meta level:

```bash
bash ./meta/evo-meta.sh check-document-metadata-header
```

Run meta tests:

```bash
bash ./meta/evo-meta.sh test
```

## Init a new application project

Create a new empty directory, enter it, and run:

```bash
bash /path/to/method/evo-method.sh init
```

You can also provide the project name explicitly:

```bash
bash /path/to/method/evo-method.sh init --name my-project
```

If the current directory name matches `project--<project-name>`, the default project name is `<project-name>`.

`init` refuses to run when the current directory is already inside:

```text
- an application project marked by .evo
- a method service area marked by .evo-method
- a meta service area marked by .evo-meta
- a directory containing meta/ or method/
```

Exception: service-area checks are relaxed inside `.evo-method/runs/...` and `.evo-meta/runs/...` because smoke/test workspaces are allowed there.

## Command layout rule

If a shell entry point is named:

```text
<some-name>.sh
```

then command parts that belong to it live in a sibling directory:

```text
<some-name>/
```

Examples:

```text
method/evo-method.sh
method/evo-method/smoke.sh
method/evo-method/test.sh
method/evo-method/spec-to-code/

meta/evo-meta.sh
meta/evo-meta/check-document-metadata-header.sh
meta/evo-meta/check-document-metadata-header/

project--site-0/evo.sh
project--site-0/evo/spec-to-code.sh
```

## Directory roles

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

It contains executable tools and method documents. At v0, there is one project-affecting method action:

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
project--site-0/.evo/
```

The generated runnable application code is the main practical output for the human, but inside `project-evo-method` it is treated as a generated artifact of a method action.

## Known limitations

This foundation is intentionally minimal. Known limitations:

- document metadata headers are required only for method documents in `/method`
- project documents are not required to have metadata headers
- `spec-to-code` reads exactly one project spec document
- `project--site-0` is the included default project
- no impl-area graph is used
- no project ontology is used
- no ownership graph is used
- no repair loop is used
- generated code is intentionally minimal
- `.evo`, `.evo-method`, and `.evo-meta` are introduced as namespaces, but only method smoke currently writes a detailed run journal
- `init` creates a minimal project skeleton only; it does not copy a full foundation snapshot yet

## Expected result

After running:

```bash
cd project--site-0
bash ./evo.sh spec-to-code
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
