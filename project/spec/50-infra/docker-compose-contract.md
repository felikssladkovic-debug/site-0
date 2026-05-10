---
id: project.spec.50-infra.docker-compose-contract
kind: infra-spec
status: ready
project: site-0
runtime: docker-compose
---

# Docker Compose contract

## Runtime command

The generated project must be started from `generated/` with:

```bash
docker-compose up --build
```

## Services

Docker Compose must define exactly one application service:

- `site-front`

## Port

Expose the frontend to the host on port:

- `5173`

The expected browser URL is:

```text
http://localhost:5173
```

## Environment variables

No external environment variables are required.

If any environment values are needed by the scaffold, they may be embedded directly in the generated files for this minimal case.

## Container behavior

The container must run the Vite development server and make it reachable outside the container by binding to `0.0.0.0`.
