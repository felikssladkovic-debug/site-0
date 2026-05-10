---
id: readme
kind: workspace-readme
status: ready
project: site-0
---

# site-0 project-evo spec package

This package contains the minimal project-evo-method files needed to generate `site-0` from spec.

## Purpose

Generate a minimal frontend-only web application with exactly one implementation area:

- `site-front`

The application must compile and run through `docker-compose` and display:

- text: `Счетчик`
- number: `1`

## How to use with Codex

1. Unzip this package.
2. Open the unpacked folder as the working directory for Codex.
3. Run the command prompt from:
   - `method/commands/spec-to-code.md`
4. Codex must create implementation files under:
   - `generated/`

