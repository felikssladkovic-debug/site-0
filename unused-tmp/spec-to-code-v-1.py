#!/usr/bin/env python3
"""
project-evo spec-to-code runner.

Pipeline implemented for the current site-0 method instance:

1. load input yaml
2. preflight
3. load ontology yaml
4. validate command input
5. validate spec-index paths
6. validate impl-area graph
7. validate artifact ownership
8. create generated/.project-evo/
9. create context bundle for site-front
10. call PROJECT_EVO_LLM_COMMAND for site-front
11. validate generated boundaries
12. run site-front checks
13. repair site-front if needed
14. write site-front manifest
15. create context bundle for orchestrator
16. call PROJECT_EVO_LLM_COMMAND for orchestrator
17. validate generated boundaries
18. run orchestrator checks
19. repair orchestrator if needed
20. write orchestrator manifest
21. run final acceptance checks
22. write final report

The runner is intentionally deterministic around validation, file ownership, context
construction, and check execution. The only bounded non-deterministic part is the
external command referenced by the input YAML field `llm.command_env`, normally:

    PROJECT_EVO_LLM_COMMAND="<your llm/codegen command>"

The command is executed with the project root as cwd and receives the generated
prompt on stdin. It may modify files directly under the declared output root.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover - depends on runtime image
    raise SystemExit(
        "PyYAML is required. Install it with: python3 -m pip install pyyaml"
    ) from exc


DEFAULT_INPUT = "project/method-instance/commands/spec-to-code.site-0.input.yaml"
META_DIR_NAME = ".project-evo"


class RunnerError(RuntimeError):
    """Expected runner failure with an actionable message."""


@dataclass
class CommandResult:
    name: str
    command: list[str] | str
    cwd: str
    returncode: int
    stdout: str = ""
    stderr: str = ""
    started_at: str = ""
    finished_at: str = ""

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "command": self.command,
            "cwd": self.cwd,
            "returncode": self.returncode,
            "ok": self.ok,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "stdout": self.stdout[-12000:],
            "stderr": self.stderr[-12000:],
        }


@dataclass
class AreaRun:
    area: str
    attempts: int = 0
    llm_calls: list[CommandResult] = field(default_factory=list)
    checks: list[CommandResult] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
    repaired: bool = False
    manifest_path: str | None = None

    @property
    def ok(self) -> bool:
        return not self.validation_errors and all(c.ok for c in self.checks)

    def to_dict(self) -> dict[str, Any]:
        return {
            "area": self.area,
            "attempts": self.attempts,
            "repaired": self.repaired,
            "ok": self.ok,
            "validation_errors": self.validation_errors,
            "llm_calls": [c.to_dict() for c in self.llm_calls],
            "checks": [c.to_dict() for c in self.checks],
            "manifest_path": self.manifest_path,
        }


@dataclass
class RunnerState:
    root: Path
    input_path: Path
    command_input: dict[str, Any]
    ontology: dict[str, Any]
    output_root: Path
    meta_root: Path
    dry_run: bool = False
    fail_fast: bool = False
    started_at: str = field(default_factory=lambda: utc_now())
    area_runs: list[AreaRun] = field(default_factory=list)
    final_checks: list[CommandResult] = field(default_factory=list)
    final_errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RunnerError(f"YAML file not found: {path}")
    data = yaml.safe_load(read_text(path))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise RunnerError(f"YAML root must be a mapping: {path}")
    return data


def normalize_repo_path(root: Path, raw: str) -> Path:
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise RunnerError(f"Path escapes repository root: {raw}") from exc
    return candidate


def list_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted([p for p in root.rglob("*") if p.is_file()])


def snapshot_files(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in list_files(root)} if root.exists() else set()


def run_command(
    name: str,
    command: list[str] | str,
    cwd: Path,
    *,
    stdin: str | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 300,
    shell: bool = False,
) -> CommandResult:
    started = utc_now()
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd),
            input=stdin,
            text=True,
            capture_output=True,
            timeout=timeout,
            env=env,
            shell=shell,
            check=False,
        )
        return CommandResult(
            name=name,
            command=command,
            cwd=str(cwd),
            returncode=completed.returncode,
            stdout=completed.stdout or "",
            stderr=completed.stderr or "",
            started_at=started,
            finished_at=utc_now(),
        )
    except FileNotFoundError as exc:
        return CommandResult(
            name=name,
            command=command,
            cwd=str(cwd),
            returncode=127,
            stderr=str(exc),
            started_at=started,
            finished_at=utc_now(),
        )
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            name=name,
            command=command,
            cwd=str(cwd),
            returncode=124,
            stdout=exc.stdout or "",
            stderr=(exc.stderr or "") + f"\nTimed out after {timeout}s.",
            started_at=started,
            finished_at=utc_now(),
        )


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


# ---------------------------------------------------------------------------
# YAML/spec extraction and validation
# ---------------------------------------------------------------------------


def extract_yaml_blocks(markdown: str) -> list[Any]:
    blocks: list[Any] = []
    for match in re.finditer(r"```ya?ml\s*(.*?)```", markdown, flags=re.DOTALL | re.I):
        raw = match.group(1).strip()
        if not raw:
            continue
        parsed = yaml.safe_load(raw)
        if parsed is not None:
            blocks.append(parsed)
    return blocks


def extract_spec_index_paths(spec_index_md: str) -> list[str]:
    paths: list[str] = []
    for block in extract_yaml_blocks(spec_index_md):
        if not isinstance(block, dict):
            continue
        for key in ("spec_files", "method_files", "project_method_instance_files"):
            items = block.get(key)
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict) and isinstance(item.get("path"), str):
                    paths.append(item["path"])
    return paths


def validate_command_input(root: Path, data: dict[str, Any]) -> None:
    required_top = [
        "command",
        "project",
        "output_root",
        "method_files",
        "project_files",
        "allowed_impl_areas",
        "artifact_ownership",
        "generation_order",
        "validation_order",
        "repair",
        "llm",
    ]
    missing = [key for key in required_top if key not in data]
    if missing:
        raise RunnerError(f"Command input is missing required fields: {missing}")

    if data["command"] != "spec-to-code":
        raise RunnerError(f"Unsupported command: {data['command']!r}")

    allowed = data.get("allowed_impl_areas")
    order = data.get("generation_order")
    ownership = data.get("artifact_ownership")
    if not isinstance(allowed, list) or not all(isinstance(x, str) for x in allowed):
        raise RunnerError("allowed_impl_areas must be a list of strings")
    if not isinstance(order, list) or not all(isinstance(x, str) for x in order):
        raise RunnerError("generation_order must be a list of strings")
    if set(order) != set(allowed):
        raise RunnerError(
            f"generation_order must contain exactly allowed_impl_areas. "
            f"allowed={allowed}, generation_order={order}"
        )
    if not isinstance(ownership, dict):
        raise RunnerError("artifact_ownership must be a mapping")
    for area in allowed:
        patterns = ownership.get(area)
        if not isinstance(patterns, list) or not patterns or not all(isinstance(x, str) for x in patterns):
            raise RunnerError(f"artifact_ownership.{area} must be a non-empty list of strings")

    project_files = data.get("project_files")
    if not isinstance(project_files, dict):
        raise RunnerError("project_files must be a mapping")
    for key in ["rules_profile", "spec_index", "ontology_instance_md", "ontology_instance_yaml"]:
        raw = project_files.get(key)
        if not isinstance(raw, str):
            raise RunnerError(f"project_files.{key} must be declared")
        path = normalize_repo_path(root, raw)
        if not path.exists():
            raise RunnerError(f"Declared project file does not exist: {raw}")

    for raw in data.get("method_files", []):
        path = normalize_repo_path(root, raw)
        if not path.exists():
            raise RunnerError(f"Declared method file does not exist: {raw}")

    output_root = normalize_repo_path(root, data["output_root"])
    if output_root == root:
        raise RunnerError("output_root must not be repository root")


def validate_spec_index_paths(root: Path, command_input: dict[str, Any]) -> list[str]:
    spec_index_path = normalize_repo_path(root, command_input["project_files"]["spec_index"])
    indexed_paths = extract_spec_index_paths(read_text(spec_index_path))
    if not indexed_paths:
        raise RunnerError(f"No paths found in spec index YAML blocks: {rel(spec_index_path, root)}")

    missing = [p for p in indexed_paths if not normalize_repo_path(root, p).exists()]
    if missing:
        raise RunnerError("Spec index references missing files:\n" + "\n".join(f"- {p}" for p in missing))
    return indexed_paths


def validate_impl_area_graph(command_input: dict[str, Any], ontology: dict[str, Any]) -> None:
    allowed = set(command_input["allowed_impl_areas"])
    impl_areas = ontology.get("impl_areas")
    if not isinstance(impl_areas, list):
        raise RunnerError("ontology.impl_areas must be a list")

    ontology_ids: set[str] = set()
    for item in impl_areas:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise RunnerError("Each ontology.impl_areas item must contain string id")
        ontology_ids.add(item["id"])

    if ontology_ids != allowed:
        raise RunnerError(f"Impl-area mismatch. command={sorted(allowed)}, ontology={sorted(ontology_ids)}")

    relations = ontology.get("relations", [])
    if not isinstance(relations, list):
        raise RunnerError("ontology.relations must be a list when declared")
    for relation in relations:
        if not isinstance(relation, dict):
            raise RunnerError("Each ontology relation must be a mapping")
        src = relation.get("from")
        dst = relation.get("to")
        kind = relation.get("relation")
        if src not in allowed or dst not in allowed or not isinstance(kind, str):
            raise RunnerError(f"Invalid ontology relation: {relation}")


def validate_artifact_ownership(command_input: dict[str, Any], ontology: dict[str, Any]) -> None:
    input_ownership: dict[str, list[str]] = command_input["artifact_ownership"]
    ontology_ownership: dict[str, list[str]] = {}

    for area in ontology.get("impl_areas", []):
        if isinstance(area, dict):
            owns = area.get("owns", [])
            if not isinstance(owns, list) or not all(isinstance(x, str) for x in owns):
                raise RunnerError(f"ontology.impl_areas[{area.get('id')}].owns must be a list of strings")
            ontology_ownership[area["id"]] = owns

    for area, patterns in input_ownership.items():
        if ontology_ownership.get(area) != patterns:
            raise RunnerError(
                f"Artifact ownership mismatch for {area}. "
                f"command={patterns}, ontology={ontology_ownership.get(area)}"
            )

    all_patterns: list[tuple[str, str]] = []
    for area, patterns in input_ownership.items():
        for pattern in patterns:
            if not pattern.startswith(command_input["output_root"].rstrip("/") + "/"):
                raise RunnerError(f"Ownership pattern must stay under output_root: {area}: {pattern}")
            all_patterns.append((area, pattern))

    for i, (area_a, pattern_a) in enumerate(all_patterns):
        for area_b, pattern_b in all_patterns[i + 1 :]:
            if area_a == area_b:
                continue
            if ownership_patterns_overlap(pattern_a, pattern_b):
                raise RunnerError(
                    f"Potentially overlapping ownership patterns: {area_a}:{pattern_a} and {area_b}:{pattern_b}"
                )


def ownership_patterns_overlap(a: str, b: str) -> bool:
    """Conservative overlap detector for this method's glob style."""
    prefix_a = a.split("**", 1)[0].rstrip("*")
    prefix_b = b.split("**", 1)[0].rstrip("*")
    return prefix_a.startswith(prefix_b) or prefix_b.startswith(prefix_a) or a == b


def validate_generated_boundaries(root: Path, command_input: dict[str, Any], area: str) -> list[str]:
    output_root = normalize_repo_path(root, command_input["output_root"])
    ownership = command_input["artifact_ownership"]
    allowed_patterns = ownership[area]
    all_owned_patterns = [p for ps in ownership.values() for p in ps]

    errors: list[str] = []
    if not output_root.exists():
        errors.append(f"Output root does not exist: {rel(output_root, root)}")
        return errors

    for file_path in list_files(output_root):
        rel_to_root = rel(file_path, root)
        if rel_to_root.startswith(f"{command_input['output_root'].rstrip('/')}/{META_DIR_NAME}/"):
            continue
        if not matches_any(rel_to_root, all_owned_patterns):
            errors.append(f"Generated file is not owned by any impl-area: {rel_to_root}")

    for file_path in list_files(output_root):
        rel_to_root = rel(file_path, root)
        if rel_to_root.startswith(f"{command_input['output_root'].rstrip('/')}/{META_DIR_NAME}/"):
            continue
        matching_owners = [a for a, ps in ownership.items() if matches_any(rel_to_root, ps)]
        if len(matching_owners) > 1:
            errors.append(f"Generated file has multiple owners {matching_owners}: {rel_to_root}")

    area_owned_files = [
        rel(p, root)
        for p in list_files(output_root)
        if matches_any(rel(p, root), allowed_patterns)
    ]
    if area == "site-front" and not any(x.startswith("generated/site-front/") for x in area_owned_files):
        errors.append("site-front did not create files under generated/site-front/")
    if area == "orchestrator" and "generated/docker-compose.yaml" not in area_owned_files:
        errors.append("orchestrator did not create generated/docker-compose.yaml")

    return errors


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    normalized = path.replace(os.sep, "/")
    return any(fnmatch.fnmatch(normalized, pattern) for pattern in patterns)


# ---------------------------------------------------------------------------
# Context bundles and LLM command
# ---------------------------------------------------------------------------


def create_context_bundle(state: RunnerState, area: str, attempt: int, repair_errors: list[str] | None = None) -> Path:
    bundle_dir = state.meta_root / "context-bundles" / f"{area}-attempt-{attempt}"
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    input_data = state.command_input
    indexed_paths = validate_spec_index_paths(state.root, input_data)
    paths_to_copy: list[str] = []
    paths_to_copy.extend(input_data.get("method_files", []))
    paths_to_copy.extend(input_data.get("project_files", {}).values())
    paths_to_copy.extend(indexed_paths)

    seen: set[str] = set()
    copied: list[str] = []
    for raw in paths_to_copy:
        if raw in seen:
            continue
        seen.add(raw)
        src = normalize_repo_path(state.root, raw)
        dst = bundle_dir / "files" / raw
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(raw)

    prompt = build_llm_prompt(state, area, attempt, copied, repair_errors or [])
    write_text(bundle_dir / "prompt.md", prompt)
    write_json(
        bundle_dir / "bundle-manifest.json",
        {
            "area": area,
            "attempt": attempt,
            "created_at": utc_now(),
            "project": input_data.get("project"),
            "output_root": input_data.get("output_root"),
            "copied_files": copied,
            "repair_errors": repair_errors or [],
        },
    )
    return bundle_dir


def build_llm_prompt(
    state: RunnerState,
    area: str,
    attempt: int,
    copied_files: list[str],
    repair_errors: list[str],
) -> str:
    input_data = state.command_input
    ownership = input_data["artifact_ownership"][area]
    allowed = input_data["allowed_impl_areas"]
    project = input_data["project"]

    repair_block = ""
    if repair_errors:
        repair_block = """
## Repair target

The previous attempt failed these deterministic checks:

{errors}

Modify only the artifacts owned by this implementation area unless the error explicitly identifies an unowned generated file that must be removed.
""".format(errors="\n".join(f"- {e}" for e in repair_errors))

    return textwrap.dedent(
        f"""
        You are the bounded LLM/codegen step inside project-evo `spec-to-code`.

        Project: `{project}`
        Current implementation area: `{area}`
        Attempt: `{attempt}`

        {repair_block}

        ## Hard boundaries

        Allowed implementation areas for the whole project:

        ```yaml
        {yaml.safe_dump(allowed, allow_unicode=True, sort_keys=False).strip()}
        ```

        You are currently allowed to create or modify only these artifacts:

        ```yaml
        {yaml.safe_dump(ownership, allow_unicode=True, sort_keys=False).strip()}
        ```

        Do not modify files under `method/` or `project/`.
        Do not create backend, database, admin UI, auth, routing, i18n, API, persistence, queue, cache, or ETL artifacts.
        Do not create implementation areas outside the declared set.

        ## Required behavior

        Generate or repair the `{area}` artifacts from the provided method and project specs.

        Site requirement: the resulting app must display exactly the required static content:

        ```text
        Счетчик
        1
        ```

        ## Available context files

        These files are copied into the context bundle and are also present at the same paths in the repository root:

        {chr(10).join(f"- `{p}`" for p in copied_files)}

        ## Output rules

        Write files directly into the repository working tree under `generated/`.
        Keep the generated project minimal.
        Prefer deterministic, conventional files.
        Do not ask questions.
        Finish by exiting with code 0 if files were written successfully.
        """
    ).strip() + "\n"


def call_llm_for_area(state: RunnerState, area: str, bundle_dir: Path) -> CommandResult:
    env_name = state.command_input.get("llm", {}).get("command_env")
    if not isinstance(env_name, str) or not env_name:
        raise RunnerError("llm.command_env must name the environment variable containing the LLM command")

    llm_command = os.environ.get(env_name)
    prompt = read_text(bundle_dir / "prompt.md")

    if state.dry_run:
        return CommandResult(
            name=f"llm:{area}:dry-run",
            command=f"${env_name}",
            cwd=str(state.root),
            returncode=0,
            stdout=f"Dry run: would call {env_name}. Bundle: {rel(bundle_dir, state.root)}\n",
            started_at=utc_now(),
            finished_at=utc_now(),
        )

    if not llm_command:
        raise RunnerError(
            f"Environment variable {env_name} is not set. "
            f"Example: {env_name}='codex exec --skip-git-repo-check'"
        )

    env = os.environ.copy()
    env.update(
        {
            "PROJECT_EVO_AREA": area,
            "PROJECT_EVO_CONTEXT_BUNDLE": str(bundle_dir),
            "PROJECT_EVO_PROMPT_FILE": str(bundle_dir / "prompt.md"),
            "PROJECT_EVO_OUTPUT_ROOT": str(state.output_root),
            "PROJECT_EVO_PROJECT": str(state.command_input.get("project", "")),
        }
    )
    return run_command(
        name=f"llm:{area}",
        command=llm_command,
        cwd=state.root,
        stdin=prompt,
        env=env,
        timeout=1800,
        shell=True,
    )


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


def run_site_front_checks(root: Path) -> list[CommandResult]:
    checks: list[CommandResult] = []
    site = root / "generated" / "site-front"

    checks.append(file_check("site-front:file-structure", root, site_front_file_errors(root)))
    checks.append(file_check("site-front:content", root, site_front_content_errors(root)))

    package_json = site / "package.json"
    if package_json.exists() and command_exists("npm"):
        if not (site / "node_modules").exists():
            checks.append(run_command("site-front:npm-install", ["npm", "install"], site, timeout=600))
        checks.append(run_command("site-front:npm-build", ["npm", "run", "build"], site, timeout=600))
    else:
        reason = "npm not found" if not command_exists("npm") else "package.json not found"
        checks.append(CommandResult("site-front:npm-build:skipped", ["npm", "run", "build"], str(site), 0, stdout=reason, started_at=utc_now(), finished_at=utc_now()))

    return checks


def site_front_file_errors(root: Path) -> list[str]:
    site = root / "generated" / "site-front"
    required = [
        site / "package.json",
        site / "index.html",
        site / "vite.config.ts",
        site / "tsconfig.json",
        site / "src",
        site / "Dockerfile",
    ]
    errors = [f"Missing required site-front artifact: {rel(p, root)}" for p in required if not p.exists()]
    if site.exists() and not any(site.glob("tailwind.config.*")):
        errors.append("Missing required site-front artifact: generated/site-front/tailwind.config.*")
    if site.exists() and not any(site.glob("postcss.config.*")):
        errors.append("Missing required site-front artifact: generated/site-front/postcss.config.*")
    return errors


def site_front_content_errors(root: Path) -> list[str]:
    site = root / "generated" / "site-front"
    source_files = [
        p
        for p in list_files(site)
        if p.suffix in {".vue", ".ts", ".js", ".html", ".css"}
        and "node_modules" not in p.parts
        and "dist" not in p.parts
        and META_DIR_NAME not in p.parts
    ]
    text = "\n".join(read_text(p) for p in source_files) if site.exists() else ""
    errors: list[str] = []
    if "Счетчик" not in text:
        errors.append("Required UI text not found in site-front source: Счетчик")
    if not re.search(r"(?<!\d)1(?!\d)", text):
        errors.append("Required static number not found in site-front source: 1")
    forbidden_markers = [
        ("router", "routing must not be implemented"),
        ("vue-router", "routing must not be implemented"),
        ("i18n", "i18n must not be implemented"),
        ("axios", "API calls must not be implemented"),
        ("fetch(", "API calls must not be implemented"),
        ("increment", "mutable counter behavior must not be implemented"),
        ("decrement", "mutable counter behavior must not be implemented"),
    ]
    lower = text.lower()
    for marker, message in forbidden_markers:
        if marker in lower:
            errors.append(f"Forbidden site-front marker `{marker}` found: {message}")
    return errors


def run_orchestrator_checks(root: Path) -> list[CommandResult]:
    checks: list[CommandResult] = []
    compose = root / "generated" / "docker-compose.yaml"
    checks.append(file_check("orchestrator:file-structure", root, orchestrator_file_errors(root)))
    checks.append(file_check("orchestrator:content", root, orchestrator_content_errors(root)))

    if compose.exists():
        compose_cmd = docker_compose_command()
        if compose_cmd:
            checks.append(run_command("orchestrator:compose-config", compose_cmd + ["-f", "docker-compose.yaml", "config"], root / "generated", timeout=300))
        else:
            checks.append(CommandResult("orchestrator:compose-config:skipped", "docker compose config", str(root / "generated"), 0, stdout="docker compose/docker-compose not found", started_at=utc_now(), finished_at=utc_now()))
    return checks


def orchestrator_file_errors(root: Path) -> list[str]:
    compose = root / "generated" / "docker-compose.yaml"
    return [] if compose.exists() else ["Missing required orchestrator artifact: generated/docker-compose.yaml"]


def orchestrator_content_errors(root: Path) -> list[str]:
    compose = root / "generated" / "docker-compose.yaml"
    if not compose.exists():
        return []
    text = read_text(compose)
    errors: list[str] = []
    parsed = yaml.safe_load(text) or {}
    services = parsed.get("services") if isinstance(parsed, dict) else None
    if not isinstance(services, dict) or not services:
        errors.append("docker-compose.yaml must define at least one service")
    else:
        service_names = set(services.keys())
        if "site-front" not in service_names:
            errors.append("docker-compose.yaml should define service `site-front`")
        forbidden = {"backend", "api", "database", "db", "mongo", "postgres", "admin", "redis", "queue", "etl"}
        unexpected = sorted(service_names & forbidden)
        if unexpected:
            errors.append(f"docker-compose.yaml defines forbidden services: {unexpected}")
    if "site-front" not in text:
        errors.append("docker-compose.yaml must reference site-front")
    return errors


def run_final_acceptance_checks(root: Path) -> list[CommandResult]:
    checks: list[CommandResult] = []
    checks.extend(run_site_front_checks(root))
    checks.extend(run_orchestrator_checks(root))

    compose_cmd = docker_compose_command()
    compose = root / "generated" / "docker-compose.yaml"
    if compose.exists() and compose_cmd:
        checks.append(run_command("final:compose-build", compose_cmd + ["-f", "docker-compose.yaml", "build"], root / "generated", timeout=900))
    elif compose.exists():
        checks.append(CommandResult("final:compose-build:skipped", "docker compose build", str(root / "generated"), 0, stdout="docker compose/docker-compose not found", started_at=utc_now(), finished_at=utc_now()))

    return checks


def docker_compose_command() -> list[str] | None:
    if command_exists("docker"):
        return ["docker", "compose"]
    if command_exists("docker-compose"):
        return ["docker-compose"]
    return None


def file_check(name: str, root: Path, errors: list[str]) -> CommandResult:
    return CommandResult(
        name=name,
        command="internal",
        cwd=str(root),
        returncode=1 if errors else 0,
        stdout="OK\n" if not errors else "",
        stderr="\n".join(errors),
        started_at=utc_now(),
        finished_at=utc_now(),
    )


# ---------------------------------------------------------------------------
# Manifest/report
# ---------------------------------------------------------------------------


def write_area_manifest(state: RunnerState, area_run: AreaRun) -> Path:
    area = area_run.area
    owned_patterns = state.command_input["artifact_ownership"][area]
    files = [
        rel(p, state.root)
        for p in list_files(state.output_root)
        if matches_any(rel(p, state.root), owned_patterns)
    ]
    manifest = {
        "project": state.command_input.get("project"),
        "area": area,
        "generated_at": utc_now(),
        "owned_patterns": owned_patterns,
        "files": files,
        "run": area_run.to_dict(),
    }
    path = state.meta_root / "manifests" / f"{area}.manifest.json"
    write_json(path, manifest)
    area_run.manifest_path = rel(path, state.root)
    return path


def write_final_report(state: RunnerState) -> Path:
    ok = not state.final_errors and all(area.ok for area in state.area_runs) and all(c.ok for c in state.final_checks)
    report = {
        "project": state.command_input.get("project"),
        "command": state.command_input.get("command"),
        "started_at": state.started_at,
        "finished_at": utc_now(),
        "ok": ok,
        "dry_run": state.dry_run,
        "input": rel(state.input_path, state.root),
        "output_root": rel(state.output_root, state.root),
        "areas": [a.to_dict() for a in state.area_runs],
        "final_checks": [c.to_dict() for c in state.final_checks],
        "final_errors": state.final_errors,
    }
    path = state.meta_root / "reports" / "spec-to-code.final-report.json"
    write_json(path, report)

    md = render_report_markdown(report)
    write_text(state.meta_root / "reports" / "spec-to-code.final-report.md", md)
    return path


def render_report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# spec-to-code final report",
        "",
        f"Project: `{report['project']}`",
        f"Status: `{'OK' if report['ok'] else 'FAILED'}`",
        f"Dry run: `{report['dry_run']}`",
        f"Finished at: `{report['finished_at']}`",
        "",
        "## Implementation areas",
        "",
    ]
    for area in report["areas"]:
        lines.append(f"### {area['area']}")
        lines.append("")
        lines.append(f"- Status: `{'OK' if area['ok'] else 'FAILED'}`")
        lines.append(f"- Attempts: `{area['attempts']}`")
        lines.append(f"- Repaired: `{area['repaired']}`")
        if area.get("manifest_path"):
            lines.append(f"- Manifest: `{area['manifest_path']}`")
        if area.get("validation_errors"):
            lines.append("- Validation errors:")
            for err in area["validation_errors"]:
                lines.append(f"  - {err}")
        failed_checks = [c for c in area.get("checks", []) if not c.get("ok")]
        if failed_checks:
            lines.append("- Failed checks:")
            for check in failed_checks:
                lines.append(f"  - `{check['name']}`: {check.get('stderr', '').strip()[:500]}")
        lines.append("")
    lines.append("## Final checks")
    lines.append("")
    for check in report["final_checks"]:
        status = "OK" if check["ok"] else "FAILED"
        lines.append(f"- `{check['name']}`: `{status}`")
    if report.get("final_errors"):
        lines.append("")
        lines.append("## Final errors")
        lines.append("")
        for err in report["final_errors"]:
            lines.append(f"- {err}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Runner orchestration
# ---------------------------------------------------------------------------


def preflight(root: Path, input_path: Path) -> None:
    if not root.exists() or not root.is_dir():
        raise RunnerError(f"Project root is not a directory: {root}")
    if not input_path.exists():
        raise RunnerError(f"Input YAML not found: {rel(input_path, root)}")
    if not os.access(root, os.W_OK):
        raise RunnerError(f"Project root is not writable: {root}")


def run_area(state: RunnerState, area: str) -> AreaRun:
    area_run = AreaRun(area=area)
    max_attempts = int(state.command_input.get("repair", {}).get("max_attempts", 1))
    max_attempts = max(1, max_attempts)
    previous_errors: list[str] = []

    for attempt in range(1, max_attempts + 1):
        area_run.attempts = attempt
        bundle = create_context_bundle(state, area, attempt, previous_errors)
        llm_result = call_llm_for_area(state, area, bundle)
        area_run.llm_calls.append(llm_result)
        write_json(bundle / "llm-result.json", llm_result.to_dict())

        errors: list[str] = []
        if not llm_result.ok:
            errors.append(f"LLM command failed for {area}, attempt {attempt}: exit {llm_result.returncode}")
            if llm_result.stderr.strip():
                errors.append(llm_result.stderr.strip()[-2000:])

        if state.dry_run:
            area_run.checks = [
                CommandResult(
                    name=f"{area}:checks:dry-run",
                    command="internal",
                    cwd=str(state.root),
                    returncode=0,
                    stdout="Dry run: generated-boundary and implementation checks skipped.\n",
                    started_at=utc_now(),
                    finished_at=utc_now(),
                )
            ]
            area_run.validation_errors = errors
            write_area_manifest(state, area_run)
            return area_run

        boundary_errors = validate_generated_boundaries(state.root, state.command_input, area)
        errors.extend(boundary_errors)

        checks = run_site_front_checks(state.root) if area == "site-front" else run_orchestrator_checks(state.root)
        area_run.checks = checks
        errors.extend(check.stderr for check in checks if not check.ok and check.stderr)
        area_run.validation_errors = errors

        if not errors:
            write_area_manifest(state, area_run)
            return area_run

        previous_errors = errors
        if attempt < max_attempts:
            area_run.repaired = True
        elif state.fail_fast:
            break

    write_area_manifest(state, area_run)
    return area_run


def run_pipeline(root: Path, input_path: Path, *, dry_run: bool = False, fail_fast: bool = False) -> RunnerState:
    root = root.resolve()
    input_path = input_path.resolve()

    # 1. load input yaml
    command_input = load_yaml(input_path)

    # 2. preflight
    preflight(root, input_path)

    # 3. load ontology yaml
    ontology_path_raw = command_input.get("project_files", {}).get("ontology_instance_yaml")
    if not isinstance(ontology_path_raw, str):
        raise RunnerError("project_files.ontology_instance_yaml must be declared before ontology load")
    ontology = load_yaml(normalize_repo_path(root, ontology_path_raw))

    # 4. validate command input
    validate_command_input(root, command_input)

    # 5. validate spec-index paths
    validate_spec_index_paths(root, command_input)

    # 6. validate impl-area graph
    validate_impl_area_graph(command_input, ontology)

    # 7. validate artifact ownership
    validate_artifact_ownership(command_input, ontology)

    # 8. create generated/.project-evo/
    output_root = normalize_repo_path(root, command_input["output_root"])
    meta_root = output_root / META_DIR_NAME
    meta_root.mkdir(parents=True, exist_ok=True)

    state = RunnerState(
        root=root,
        input_path=input_path,
        command_input=command_input,
        ontology=ontology,
        output_root=output_root,
        meta_root=meta_root,
        dry_run=dry_run,
        fail_fast=fail_fast,
    )

    write_json(
        meta_root / "run-input.snapshot.json",
        {
            "input_path": rel(input_path, root),
            "command_input": command_input,
            "ontology": ontology,
            "started_at": state.started_at,
        },
    )

    # 9-20. area generation/check/repair/manifest in declared order
    for area in command_input["generation_order"]:
        area_run = run_area(state, area)
        state.area_runs.append(area_run)
        if fail_fast and not area_run.ok:
            break

    # 21. run final acceptance checks
    if all(area.ok for area in state.area_runs) and not dry_run:
        state.final_checks = run_final_acceptance_checks(root)
    elif dry_run:
        state.final_checks = [
            CommandResult(
                name="final-acceptance:dry-run",
                command="internal",
                cwd=str(root),
                returncode=0,
                stdout="Dry run: final acceptance checks skipped.\n",
                started_at=utc_now(),
                finished_at=utc_now(),
            )
        ]
    else:
        state.final_errors.append("Final acceptance skipped because one or more implementation areas failed.")

    # 22. write final report
    write_final_report(state)
    return state


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run project-evo spec-to-code pipeline")
    parser.add_argument(
        "--root",
        default=".",
        help="Repository/project root. Default: current directory.",
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help=f"Command input YAML path. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Create bundles and reports without calling the LLM command or final runtime checks.",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop after the first implementation area that fails.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = Path(args.root).resolve()
    input_path = normalize_repo_path(root, args.input)

    try:
        state = run_pipeline(root, input_path, dry_run=args.dry_run, fail_fast=args.fail_fast)
        report_path = state.meta_root / "reports" / "spec-to-code.final-report.json"
        ok = not state.final_errors and all(a.ok for a in state.area_runs) and all(c.ok for c in state.final_checks)
        print(f"spec-to-code {'OK' if ok else 'FAILED'}")
        print(f"report: {rel(report_path, state.root)}")
        return 0 if ok else 1
    except RunnerError as exc:
        print(f"spec-to-code FAILED: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("spec-to-code interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
