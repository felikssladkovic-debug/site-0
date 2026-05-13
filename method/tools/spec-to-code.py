#!/usr/bin/env python3
"""
project-evo spec-to-code runner.

"""

from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - intentionally explicit runtime error
    raise SystemExit("PyYAML is required: install with `python3 -m pip install pyyaml`.") from exc


DEFAULT_INPUT = "project/method-instance/commands/spec-to-code.site-0.input.yaml"
META_DIR_NAME = ".project-evo"
FENCE_RE = re.compile(r"```(?:yaml|yml)\s*(.*?)```", re.DOTALL | re.IGNORECASE)
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


class RunnerError(RuntimeError):
    """Raised when the runner cannot continue safely."""


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: list[str] = field(default_factory=list)


@dataclass
class LlmCallResult:
    area: str
    attempt: int
    returncode: int
    stdout_path: str
    stderr_path: str
    prompt_path: str


@dataclass
class AreaRunResult:
    area: str
    attempts: int = 0
    llm_calls: list[LlmCallResult] = field(default_factory=list)
    checks: list[CheckResult] = field(default_factory=list)
    generated_files: list[str] = field(default_factory=list)
    manifest_path: str | None = None


class SpecToCodeRunner:
    def __init__(self, root: Path, input_path: Path, dry_run: bool, execute_acceptance: bool, env_file: Path | None):
        self.root = root.resolve()
        self.input_path = self.resolve_repo_path(input_path)
        self.dry_run = dry_run
        self.execute_acceptance = execute_acceptance
        self.env_file = self.resolve_repo_path(env_file) if env_file else None
        self.command: dict[str, Any] = {}
        self.ontology: dict[str, Any] = {}
        self.output_root: Path = self.root / "generated"
        self.meta_dir: Path = self.output_root / META_DIR_NAME
        self.report: dict[str, Any] = {
            "runner": "method/tools/spec-to-code.py",
            "started_at": utc_now(),
            "dry_run": dry_run,
            "execute_acceptance": execute_acceptance,
            "steps": [],
            "warnings": [],
            "area_results": [],
            "final_checks": [],
        }

    def resolve_repo_path(self, path: str | Path | None) -> Path | None:
        if path is None:
            return None
        p = Path(path)
        if p.is_absolute():
            return p
        return self.root / p

    def rel(self, path: str | Path) -> str:
        p = Path(path)
        try:
            return p.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return p.as_posix()

    def step(self, name: str, status: str = "ok", **data: Any) -> None:
        item = {"name": name, "status": status, "at": utc_now()}
        item.update(data)
        self.report["steps"].append(item)
        print(f"[{status}] {name}")

    def run(self) -> int:
        try:
            self.load_input_yaml()
            self.preflight()
            self.load_ontology_yaml()
            self.validate_command_input()
            self.validate_spec_index_paths()
            self.validate_impl_area_graph()
            self.validate_artifact_ownership()
            self.create_meta_dir()

            if self.dry_run:
                for area in self.command["generation_order"]:
                    self.create_context_bundle(area)
                    self.validate_generated_boundaries(area)
                self.write_final_report("dry-run-success")
                self.step("write final report", report="generated/.project-evo/final-report.md")
                return 0

            for area in self.command["generation_order"]:
                result = self.run_area(area)
                self.report["area_results"].append(dataclass_to_json(result))

            final_checks = self.run_final_acceptance_checks()
            self.report["final_checks"] = [dataclass_to_json(c) for c in final_checks]
            if not all(c.ok for c in final_checks):
                raise RunnerError("Final acceptance checks failed.")

            self.write_final_report("success")
            self.step("write final report", report="generated/.project-evo/final-report.md")
            return 0
        except Exception as exc:
            self.report["error"] = str(exc)
            try:
                self.write_final_report("failed")
            except Exception:
                pass
            print(f"[failed] {exc}", file=sys.stderr)
            return 1

    # 1
    def load_input_yaml(self) -> None:
        if not self.input_path.exists():
            raise RunnerError(f"Input YAML not found: {self.rel(self.input_path)}")
        self.command = load_yaml_file(self.input_path)
        if not isinstance(self.command, dict):
            raise RunnerError("Input YAML must contain a mapping at top level.")
        self.output_root = self.resolve_output_root(str(self.command.get("output_root", "generated/")))
        self.meta_dir = self.output_root / META_DIR_NAME
        self.step("load input yaml", input=self.rel(self.input_path))

    # 2
    def preflight(self) -> None:
        require_dirs = ["method", "project"]
        missing_dirs = [d for d in require_dirs if not (self.root / d).is_dir()]
        if missing_dirs:
            raise RunnerError(f"Missing required root directories: {missing_dirs}")
        if self.env_file:
            load_env_file(self.env_file)
        if not self.dry_run:
            env_name = self.command.get("llm", {}).get("command_env", "PROJECT_EVO_LLM_COMMAND")
            if not os.environ.get(env_name):
                raise RunnerError(
                    f"Environment variable {env_name} is not set. "
                    f"Set it or run with --dry-run for validation-only mode."
                )
        self.step("preflight", root=self.rel(self.root), python=sys.version.split()[0])

    # 3
    def load_ontology_yaml(self) -> None:
        ontology_path = self.resolve_repo_path(self.command.get("project_files", {}).get("ontology_instance_yaml"))
        if not ontology_path or not ontology_path.exists():
            raise RunnerError("Ontology instance YAML is missing or path is invalid.")
        self.ontology = load_yaml_file(ontology_path)
        if not isinstance(self.ontology, dict):
            raise RunnerError("Ontology instance YAML must contain a mapping at top level.")
        self.step("load ontology yaml", ontology=self.rel(ontology_path))

    # 4
    def validate_command_input(self) -> None:
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
        missing = [k for k in required_top if k not in self.command]
        if missing:
            raise RunnerError(f"Command input is missing required fields: {missing}")
        if self.command["command"] != "spec-to-code":
            raise RunnerError("Only command=spec-to-code is supported by this runner.")
        if self.command["project"] != self.ontology.get("project"):
            raise RunnerError("Command project must match ontology project.")
        allowed = as_str_list(self.command["allowed_impl_areas"])
        order = as_str_list(self.command["generation_order"])
        if set(order) != set(allowed):
            raise RunnerError("generation_order must contain exactly allowed_impl_areas.")
        if self.command.get("repair", {}).get("max_attempts", 0) < 0:
            raise RunnerError("repair.max_attempts must be >= 0.")

        file_paths = list(self.command.get("method_files", [])) + list(self.command.get("project_files", {}).values())
        missing_files = [p for p in file_paths if p and not self.resolve_repo_path(p).exists()]
        if missing_files:
            raise RunnerError(f"Command input references missing files: {missing_files}")
        self.step("validate command input", allowed_impl_areas=allowed)

    # 5
    def validate_spec_index_paths(self) -> None:
        spec_index_path = self.resolve_repo_path(self.command["project_files"]["spec_index"])
        spec_index = read_markdown_yaml_payload(spec_index_path)
        spec_files = spec_index.get("spec_files") or spec_index.get("files") or []
        if not spec_files:
            raise RunnerError("spec-index must contain `spec_files` or `files` YAML list.")
        missing = [p for p in spec_files if not self.resolve_repo_path(p).exists()]
        if missing:
            raise RunnerError(f"spec-index contains missing paths: {missing}")
        self.command["_resolved_spec_files"] = spec_files
        self.step("validate spec-index paths", count=len(spec_files))

    # 6
    def validate_impl_area_graph(self) -> None:
        areas = self.ontology.get("impl_areas") or []
        if not isinstance(areas, list) or not areas:
            raise RunnerError("ontology.impl_areas must be a non-empty list.")
        allowed = set(as_str_list(self.command["allowed_impl_areas"]))
        required_fields = {"id", "kind", "responsibility", "spec-folder", "owns"}
        area_ids: set[str] = set()
        for area in areas:
            missing = required_fields - set(area.keys())
            if missing:
                raise RunnerError(f"Implementation area {area.get('id')} is missing fields: {sorted(missing)}")
            if area["id"] not in allowed:
                raise RunnerError(f"Ontology contains non-allowed impl area: {area['id']}")
            area_ids.add(area["id"])
            spec_folder = self.resolve_project_relative_path(area["spec-folder"])
            if not spec_folder.exists():
                raise RunnerError(f"Spec folder for {area['id']} not found: {self.rel(spec_folder)}")
            if area["kind"] not in {"application", "infrastructure"}:
                raise RunnerError(f"Unsupported impl area kind for {area['id']}: {area['kind']}")
        if area_ids != allowed:
            raise RunnerError(f"Ontology impl areas {sorted(area_ids)} do not match allowed {sorted(allowed)}")
        for relation in self.ontology.get("relations") or []:
            if relation.get("from") not in area_ids or relation.get("to") not in area_ids:
                raise RunnerError(f"Relation references unknown impl area: {relation}")
            if not relation.get("relation"):
                raise RunnerError(f"Relation is missing relation type: {relation}")
        self.step("validate impl-area graph", impl_areas=sorted(area_ids))

    # 7
    def validate_artifact_ownership(self) -> None:
        command_ownership = normalize_ownership(self.command.get("artifact_ownership") or {})
        ontology_ownership = {a["id"]: as_str_list(a.get("owns", [])) for a in self.ontology.get("impl_areas", [])}
        if command_ownership != ontology_ownership:
            raise RunnerError(
                "artifact_ownership in command input must match ontology impl_area owns declarations. "
                f"command={command_ownership}, ontology={ontology_ownership}"
            )
        patterns = [(owner, p) for owner, values in command_ownership.items() for p in values]
        for owner, pattern in patterns:
            if not pattern.startswith(self.output_root.name + "/"):
                raise RunnerError(f"Ownership pattern for {owner} must start with {self.output_root.name}/: {pattern}")
        exact = [(o, p) for o, p in patterns if not any(ch in p for ch in "*?[")]
        seen: dict[str, str] = {}
        for owner, pattern in exact:
            if pattern in seen and seen[pattern] != owner:
                raise RunnerError(f"Artifact {pattern} is owned by both {seen[pattern]} and {owner}")
            seen[pattern] = owner
        self.step("validate artifact ownership", owners=command_ownership)

    # 8
    def create_meta_dir(self) -> None:
        self.meta_dir.mkdir(parents=True, exist_ok=True)
        for sub in ["context-bundles", "logs", "manifests", "reports"]:
            (self.meta_dir / sub).mkdir(parents=True, exist_ok=True)
        self.step("create generated/.project-evo", path=self.rel(self.meta_dir))

    def run_area(self, area: str) -> AreaRunResult:
        result = AreaRunResult(area=area)
        context = self.create_context_bundle(area)
        max_attempts = int(self.command.get("repair", {}).get("max_attempts", 0))
        attempt = 0

        if not self.dry_run:
            call = self.call_llm(area, context, attempt=0, repair=False, prior_checks=[])
            result.llm_calls.append(call)
            result.attempts += 1
            if call.returncode != 0:
                raise RunnerError(f"LLM command failed for {area}, attempt 0.")
        else:
            self.step(f"call LLM for {area}", status="skipped", reason="dry-run")

        self.validate_generated_boundaries(area)
        checks = self.run_area_checks(area)
        result.checks = checks

        while not all(c.ok for c in checks) and attempt < max_attempts and not self.dry_run:
            attempt += 1
            call = self.call_llm(area, context, attempt=attempt, repair=True, prior_checks=checks)
            result.llm_calls.append(call)
            result.attempts += 1
            if call.returncode != 0:
                raise RunnerError(f"LLM repair command failed for {area}, attempt {attempt}.")
            self.validate_generated_boundaries(area)
            checks = self.run_area_checks(area)
            result.checks = checks

        if not all(c.ok for c in checks):
            failed = [c.name for c in checks if not c.ok]
            raise RunnerError(f"Checks failed for {area}: {failed}")

        result.generated_files = self.generated_files_for_area(area)
        result.manifest_path = self.write_area_manifest(area, result)
        self.step(f"write {area} manifest", manifest=result.manifest_path)
        return result

    # 9, 15
    def create_context_bundle(self, area: str) -> str:
        bundle_dir = self.meta_dir / "context-bundles" / area
        bundle_dir.mkdir(parents=True, exist_ok=True)
        files = self.context_files_for_area(area)
        context_md = build_context_markdown(self.root, area, files)
        prompt = self.build_generation_prompt(area, context_md)
        (bundle_dir / "context.md").write_text(context_md, encoding="utf-8")
        (bundle_dir / "prompt.md").write_text(prompt, encoding="utf-8")
        (bundle_dir / "manifest.json").write_text(json.dumps({
            "area": area,
            "created_at": utc_now(),
            "files": files,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        self.step(f"create context bundle for {area}", files=len(files), path=self.rel(bundle_dir))
        return prompt

    def context_files_for_area(self, area: str) -> list[str]:
        base = []
        base.extend(self.command.get("method_files", []))
        base.extend(str(v) for v in self.command.get("project_files", {}).values())
        base.extend(self.command.get("_resolved_spec_files", []))
        # Keep the bundle bounded: include all source-of-truth specs, but no generated code
        # except previous area manifests for downstream areas.
        if area == "orchestrator":
            manifest = self.meta_dir / "manifests" / "site-front.manifest.json"
            if manifest.exists():
                base.append(self.rel(manifest))
        return unique_existing_paths(self.root, base)

    def build_generation_prompt(self, area: str, context_md: str) -> str:
        allowed_patterns = normalize_ownership(self.command["artifact_ownership"])[area]
        forbidden_areas = [
            "site-backend",
            "admin-front",
            "admin-backend",
            "db-canonical",
            "db-read",
            "etl",
        ]
        return textwrap.dedent(f"""
        You are a bounded code-generation agent inside project-evo spec-to-code.

        Generate or repair ONLY this implementation area: {area}

        Hard boundaries:
        - Repository root is the current working directory.
        - You may write only files matching these ownership patterns:
        {indent_yaml(allowed_patterns, 10)}
        - Do not write generated files outside `generated/`.
        - Do not create forbidden implementation areas: {', '.join(forbidden_areas)}.
        - Preserve files under `method/` and `project/`.
        - Preserve `generated/.project-evo/` runner metadata.

        Required result for site-0:
        - Minimal frontend-only application.
        - TypeScript + Vue 3 + Tailwind + Vite for site-front.
        - Docker Compose orchestration for orchestrator.
        - The visible page must render exactly the text `Счетчик` and the static number `1`.
        - No backend, database, admin UI, auth, routing, i18n, persistence, or mutable counter behavior.

        Use the context below as the source of truth.

        {context_md}
        """).strip() + "\n"

    # 10, 16 and repair
    def call_llm(self, area: str, prompt: str, attempt: int, repair: bool, prior_checks: list[CheckResult]) -> LlmCallResult:
        env_name = self.command.get("llm", {}).get("command_env", "PROJECT_EVO_LLM_COMMAND")
        cmd = os.environ.get(env_name)
        if not cmd:
            raise RunnerError(f"{env_name} is not set.")
        logs_dir = self.meta_dir / "logs" / area
        logs_dir.mkdir(parents=True, exist_ok=True)
        prompt_text = prompt
        if repair:
            prompt_text += "\n\nRepair required. Failed checks:\n"
            prompt_text += checks_to_markdown(prior_checks)
        prompt_path = logs_dir / f"attempt-{attempt:02d}.prompt.md"
        stdout_path = logs_dir / f"attempt-{attempt:02d}.stdout.log"
        stderr_path = logs_dir / f"attempt-{attempt:02d}.stderr.log"
        prompt_path.write_text(prompt_text, encoding="utf-8")
        completed = subprocess.run(
            cmd,
            input=prompt_text,
            text=True,
            shell=True,
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),
        )
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        self.step(
            f"call {'repair ' if repair else ''}LLM for {area}",
            status="ok" if completed.returncode == 0 else "failed",
            attempt=attempt,
            returncode=completed.returncode,
        )
        return LlmCallResult(
            area=area,
            attempt=attempt,
            returncode=completed.returncode,
            stdout_path=self.rel(stdout_path),
            stderr_path=self.rel(stderr_path),
            prompt_path=self.rel(prompt_path),
        )

    # 11, 17
    def validate_generated_boundaries(self, current_area: str) -> None:
        ownership = normalize_ownership(self.command["artifact_ownership"])
        allowed_patterns = [p for patterns in ownership.values() for p in patterns]
        if not self.output_root.exists():
            raise RunnerError(f"Output root was not created: {self.rel(self.output_root)}")
        violations = []
        for path in self.output_root.rglob("*"):
            if path.is_dir():
                continue
            rel = self.rel(path)
            if rel.startswith(f"{self.output_root.name}/{META_DIR_NAME}/"):
                continue
            if not any_path_match(rel, allowed_patterns):
                violations.append(rel)
        if violations:
            raise RunnerError(f"Generated boundary violations after {current_area}: {violations}")
        self.step("validate generated boundaries", area=current_area)

    # 12, 18
    def run_area_checks(self, area: str) -> list[CheckResult]:
        if area == "site-front":
            checks = self.check_site_front()
        elif area == "orchestrator":
            checks = self.check_orchestrator()
        else:
            raise RunnerError(f"Unknown implementation area: {area}")
        self.step(
            f"run {area} checks",
            status="ok" if all(c.ok for c in checks) else "failed",
            failed=[c.name for c in checks if not c.ok],
        )
        return checks

    def check_site_front(self) -> list[CheckResult]:
        site = self.output_root / "site-front"
        checks = [
            exists_check("site-front-dir", site),
            exists_check("site-front-package-json", site / "package.json"),
            exists_check("site-front-index-html", site / "index.html"),
            exists_check("site-front-src", site / "src", is_dir=True),
            exists_check("site-front-dockerfile", site / "Dockerfile"),
            contains_any_check("site-front-renders-counter-text", site, ["Счетчик"]),
            contains_any_check("site-front-renders-static-one", site, [">1<", "{{ 1 }}", " 1", "\n1\n"]),
            forbidden_names_check("site-front-no-forbidden-areas", self.output_root, [
                "site-backend", "admin-front", "admin-backend", "db-canonical", "db-read", "etl"
            ]),
        ]
        package_json = site / "package.json"
        if package_json.exists():
            try:
                package_data = json.loads(package_json.read_text(encoding="utf-8"))
                deps = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}
                checks.append(CheckResult("site-front-uses-vue", "vue" in deps, ["package.json must declare vue dependency"]))
                checks.append(CheckResult("site-front-uses-vite", "vite" in deps, ["package.json must declare vite dependency"]))
                checks.append(CheckResult("site-front-has-build-script", "build" in package_data.get("scripts", {}), ["package.json must declare build script"]))
            except Exception as exc:
                checks.append(CheckResult("site-front-package-json-valid", False, [str(exc)]))
        return checks

    def check_orchestrator(self) -> list[CheckResult]:
        compose = self.output_root / "docker-compose.yaml"
        if not compose.exists():
            compose = self.output_root / "docker-compose.yml"
        checks = [
            exists_check("orchestrator-compose-file", compose),
            exists_check("orchestrator-site-front-dir", self.output_root / "site-front", is_dir=True),
            forbidden_names_check("orchestrator-no-forbidden-areas", self.output_root, [
                "site-backend", "admin-front", "admin-backend", "db-canonical", "db-read", "etl"
            ]),
        ]
        if compose.exists():
            text = compose.read_text(encoding="utf-8")
            checks.append(CheckResult("orchestrator-compose-references-site-front", "site-front" in text, ["Compose must reference site-front service or build context"]))
            checks.append(CheckResult("orchestrator-compose-builds-site-front", "build" in text and "site-front" in text, ["Compose must build site-front"]))
        return checks

    # 14, 20
    def write_area_manifest(self, area: str, result: AreaRunResult) -> str:
        manifest_dir = self.meta_dir / "manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        path = manifest_dir / f"{area}.manifest.json"
        payload = dataclass_to_json(result)
        payload["written_at"] = utc_now()
        payload["ownership"] = normalize_ownership(self.command["artifact_ownership"])[area]
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return self.rel(path)

    # 21
    def run_final_acceptance_checks(self) -> list[CheckResult]:
        checks: list[CheckResult] = []
        checks.extend(self.check_site_front())
        checks.extend(self.check_orchestrator())
        checks.append(contains_any_check("final-page-renders-counter-text", self.output_root / "site-front", ["Счетчик"]))
        checks.append(contains_any_check("final-page-renders-number-one", self.output_root / "site-front", [">1<", "{{ 1 }}", "\n1\n", " 1"]))
        checks.append(CheckResult("final-generated-boundaries", True, ["Boundary validation already passed after each area."]))
        if self.execute_acceptance or os.environ.get("PROJECT_EVO_RUN_DOCKER_CHECKS") == "1":
            checks.extend(self.run_optional_docker_checks())
        self.step("run final acceptance checks", status="ok" if all(c.ok for c in checks) else "failed")
        return checks

    def run_optional_docker_checks(self) -> list[CheckResult]:
        compose_cmd = find_compose_command()
        if not compose_cmd:
            return [CheckResult("docker-compose-command-available", False, ["Neither `docker compose` nor `docker-compose` is available."])]
        checks = []
        config = subprocess.run(compose_cmd + ["config"], cwd=self.output_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        checks.append(CheckResult("docker-compose-config", config.returncode == 0, [config.stderr.strip() or config.stdout.strip()]))
        build = subprocess.run(compose_cmd + ["build"], cwd=self.output_root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        checks.append(CheckResult("docker-compose-build", build.returncode == 0, [tail(build.stderr or build.stdout)]))
        return checks

    # 22
    def write_final_report(self, status: str) -> None:
        self.report["finished_at"] = utc_now()
        self.report["status"] = status
        reports_dir = self.meta_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.meta_dir / "final-report.json"
        md_path = self.meta_dir / "final-report.md"
        json_path.write_text(json.dumps(self.report, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(render_final_report_md(self.report), encoding="utf-8")

    def resolve_output_root(self, output_root: str) -> Path:
        p = Path(output_root)
        if p.is_absolute():
            return p
        return self.root / p

    def resolve_project_relative_path(self, path: str) -> Path:
        p = Path(path)
        if p.is_absolute():
            return p
        if path.startswith("project/") or path.startswith("method/") or path.startswith(self.output_root.name + "/"):
            return self.root / p
        return self.root / "project" / p

    def generated_files_for_area(self, area: str) -> list[str]:
        patterns = normalize_ownership(self.command["artifact_ownership"])[area]
        if not self.output_root.exists():
            return []
        files = []
        for path in self.output_root.rglob("*"):
            if path.is_file():
                rel = self.rel(path)
                if rel.startswith(f"{self.output_root.name}/{META_DIR_NAME}/"):
                    continue
                if any_path_match(rel, patterns):
                    files.append(rel)
        return sorted(files)


# Helpers


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def load_yaml_file(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise RunnerError(f"YAML parse error in {path}: {exc}") from exc


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise RunnerError(f"Env file not found: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def read_markdown_yaml_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    payloads: list[dict[str, Any]] = []
    front = FRONT_MATTER_RE.search(text)
    if front:
        data = yaml.safe_load(front.group(1)) or {}
        if isinstance(data, dict):
            payloads.append(data)
    for match in FENCE_RE.finditer(text):
        data = yaml.safe_load(match.group(1)) or {}
        if isinstance(data, dict):
            payloads.append(data)
    merged: dict[str, Any] = {}
    for p in payloads:
        merged.update(p)
    if not merged:
        raise RunnerError(f"No YAML payload found in markdown file: {path}")
    return merged


def as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(v) for v in value]
    raise RunnerError(f"Expected list or string, got {type(value).__name__}: {value!r}")


def normalize_ownership(value: Any) -> dict[str, list[str]]:
    if isinstance(value, dict):
        return {str(k): as_str_list(v) for k, v in value.items()}
    if isinstance(value, list):
        result: dict[str, list[str]] = {}
        for item in value:
            result[str(item["owner"])] = as_str_list(item.get("artifacts", []))
        return result
    raise RunnerError("artifact ownership must be a mapping or list of owner/artifacts records.")


def any_path_match(path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def unique_existing_paths(root: Path, paths: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in paths:
        p = Path(raw)
        abs_path = p if p.is_absolute() else root / p
        if not abs_path.exists():
            continue
        try:
            rel = abs_path.resolve().relative_to(root).as_posix()
        except ValueError:
            rel = abs_path.as_posix()
        if rel not in seen:
            seen.add(rel)
            result.append(rel)
    return result


def build_context_markdown(root: Path, area: str, files: list[str]) -> str:
    parts = [f"# Context bundle for {area}\n"]
    for rel in files:
        path = root / rel
        if path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        parts.append(f"\n## File: `{rel}`\n\n```{language_for_path(path)}\n{text}\n```\n")
    return "\n".join(parts)


def language_for_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix == ".json":
        return "json"
    if suffix == ".md":
        return "markdown"
    if suffix == ".py":
        return "python"
    return "text"


def indent_yaml(value: Any, spaces: int) -> str:
    dumped = yaml.safe_dump(value, allow_unicode=True, sort_keys=False).rstrip()
    return textwrap.indent(dumped, " " * spaces)


def exists_check(name: str, path: Path, is_dir: bool = False) -> CheckResult:
    ok = path.is_dir() if is_dir else path.exists()
    kind = "directory" if is_dir else "file/path"
    return CheckResult(name, ok, [f"Expected {kind}: {path}"])


def contains_any_check(name: str, root: Path, needles: list[str]) -> CheckResult:
    if not root.exists():
        return CheckResult(name, False, [f"Search root does not exist: {root}"])
    for file in iter_text_files(root):
        text = file.read_text(encoding="utf-8", errors="ignore")
        if any(n in text for n in needles):
            return CheckResult(name, True, [f"Found one of {needles} in {file}"])
    return CheckResult(name, False, [f"Did not find any of {needles} under {root}"])


def forbidden_names_check(name: str, root: Path, names: list[str]) -> CheckResult:
    if not root.exists():
        return CheckResult(name, True, ["Output root does not exist yet."])
    violations = [p.as_posix() for p in root.rglob("*") if any(part == p.name for part in names)]
    return CheckResult(name, not violations, violations or ["No forbidden generated implementation areas found."])


def iter_text_files(root: Path) -> Iterable[Path]:
    allowed = {".ts", ".tsx", ".js", ".jsx", ".vue", ".html", ".css", ".json", ".md", ".yaml", ".yml"}
    if root.is_file():
        if root.suffix.lower() in allowed:
            yield root
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in allowed and META_DIR_NAME not in path.parts:
            yield path


def checks_to_markdown(checks: list[CheckResult]) -> str:
    lines = []
    for check in checks:
        if check.ok:
            continue
        lines.append(f"- {check.name}: FAILED")
        for detail in check.details:
            lines.append(f"  - {detail}")
    return "\n".join(lines) + "\n"


def find_compose_command() -> list[str] | None:
    if shutil.which("docker"):
        probe = subprocess.run(["docker", "compose", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if probe.returncode == 0:
            return ["docker", "compose"]
    if shutil.which("docker-compose"):
        return ["docker-compose"]
    return None


def tail(text: str, limit: int = 4000) -> str:
    return text[-limit:]


def dataclass_to_json(obj: Any) -> Any:
    if hasattr(obj, "__dataclass_fields__"):
        return {k: dataclass_to_json(getattr(obj, k)) for k in obj.__dataclass_fields__.keys()}
    if isinstance(obj, list):
        return [dataclass_to_json(v) for v in obj]
    if isinstance(obj, dict):
        return {k: dataclass_to_json(v) for k, v in obj.items()}
    return obj


def render_final_report_md(report: dict[str, Any]) -> str:
    lines = [
        "# project-evo spec-to-code final report",
        "",
        f"Status: `{report.get('status', 'unknown')}`",
        f"Started: `{report.get('started_at')}`",
        f"Finished: `{report.get('finished_at')}`",
        f"Dry run: `{report.get('dry_run')}`",
        "",
        "## Steps",
        "",
    ]
    for step in report.get("steps", []):
        lines.append(f"- `{step.get('status')}` {step.get('name')}")
    if report.get("area_results"):
        lines.extend(["", "## Area results", ""])
        for area in report["area_results"]:
            lines.append(f"### {area.get('area')}")
            lines.append(f"- attempts: `{area.get('attempts')}`")
            lines.append(f"- manifest: `{area.get('manifest_path')}`")
            failed = [c["name"] for c in area.get("checks", []) if not c.get("ok")]
            lines.append(f"- failed checks: `{failed}`")
            lines.append("")
    lines.extend(["", "## Final checks", ""])
    for check in report.get("final_checks", []):
        mark = "OK" if check.get("ok") else "FAILED"
        lines.append(f"- `{mark}` {check.get('name')}")
    if report.get("error"):
        lines.extend(["", "## Error", "", f"```text\n{report['error']}\n```"])
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="project-evo spec-to-code deterministic runner")
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT, help="Path to spec-to-code input YAML")
    parser.add_argument("--root", default=".", help="Repository root containing method/ and project/")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and create bundles without calling the LLM")
    parser.add_argument("--execute-acceptance", action="store_true", help="Run docker compose validation/build checks")
    parser.add_argument("--env-file", help="Optional env file to load before running, e.g. project/method-instance/env/dev.env")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    runner = SpecToCodeRunner(
        root=Path(args.root),
        input_path=Path(args.input),
        dry_run=args.dry_run,
        execute_acceptance=args.execute_acceptance,
        env_file=Path(args.env_file) if args.env_file else None,
    )
    return runner.run()


if __name__ == "__main__":
    raise SystemExit(main())
