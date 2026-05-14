# project-evo-method v0 / site-0

This repository is a minimal executable slice of `project-evo-method`.

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

## v0 constraints

At this stage:

- document metadata headers are required only for method documents in `/method`
- project documents are not required to have metadata headers
- `spec-to-code` reads exactly one project spec document
- `project--site-0` is the default project
- no impl-area graph is used
- no project ontology is used
- no ownership graph is used
- no repair loop is used
- generated code is intentionally minimal

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
