#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List


FILE_BLOCK_RE = re.compile(
    r"```project-evo-file\s*\n(?P<header>.*?)\n---\n(?P<content>.*?)\n```",
    re.DOTALL,
)


@dataclass(frozen=True)
class FileOperation:
    action: str
    path: str
    content: str


class SpecToCodeError(Exception):
    pass


def read_text_file(path: Path, label: str) -> str:
    if not path.exists():
        raise SpecToCodeError(f"{label} does not exist: {path}")

    if not path.is_file():
        raise SpecToCodeError(f"{label} is not a file: {path}")

    return path.read_text(encoding="utf-8")


def build_prompt(spec_text: str) -> str:
    return f"""You are a code generator used by project-evo-method.

You receive exactly one project spec document.
Generate runnable code that satisfies the spec.

You do not have filesystem access.
You must return only project-evo file operation blocks.

Allowed block format:

```project-evo-file
action: create
path: relative/path/from/generated/root
---
file content
```

Rules:
- Return only file operation blocks.
- Do not write explanations outside file operation blocks.
- Use only action: create.
- Paths must be relative to the generated root.
- Do not use absolute paths.
- Do not use ".." in paths.
- Generate all files needed to run or inspect the result.
- The runner will write your files into the project generated directory.

Project spec:

<<<PROJECT_SPEC
{spec_text}
PROJECT_SPEC
"""


def call_llm(prompt: str, llm_command: str | None) -> str:
    if not llm_command:
        raise SpecToCodeError(
            "PROJECT_EVO_LLM_COMMAND is not set. "
            "Set it to a command that reads prompt from stdin and writes file-operation blocks to stdout."
        )

    try:
        result = subprocess.run(
            llm_command,
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            check=False,
        )
    except OSError as exc:
        raise SpecToCodeError(f"failed to execute PROJECT_EVO_LLM_COMMAND: {exc}") from exc

    if result.returncode != 0:
        stderr = result.stderr.strip()
        detail = f": {stderr}" if stderr else ""
        raise SpecToCodeError(f"LLM command failed with exit code {result.returncode}{detail}")

    response = result.stdout

    if not response.strip():
        raise SpecToCodeError("LLM command returned empty stdout")

    return response


def parse_header(header_text: str) -> dict[str, str]:
    data: dict[str, str] = {}

    for line_no, line in enumerate(header_text.splitlines(), start=1):
        stripped = line.strip()

        if not stripped:
            continue

        if ":" not in stripped:
            raise SpecToCodeError(f"invalid file block header line {line_no}: {line!r}")

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            raise SpecToCodeError(f"empty file block header key on line {line_no}")

        if not value:
            raise SpecToCodeError(f"empty file block header value for key {key!r}")

        if key in data:
            raise SpecToCodeError(f"duplicate file block header key: {key!r}")

        data[key] = value

    return data


def parse_file_operations(response_text: str) -> List[FileOperation]:
    operations: List[FileOperation] = []

    for match in FILE_BLOCK_RE.finditer(response_text):
        header = parse_header(match.group("header"))
        content = match.group("content")

        allowed_keys = {"action", "path"}
        extra_keys = sorted(set(header.keys()) - allowed_keys)
        if extra_keys:
            raise SpecToCodeError(f"unexpected file block header field(s): {', '.join(extra_keys)}")

        action = header.get("action")
        path = header.get("path")

        if not action:
            raise SpecToCodeError("file block is missing required header field: action")

        if not path:
            raise SpecToCodeError("file block is missing required header field: path")

        if action != "create":
            raise SpecToCodeError(f"unsupported file operation action: {action!r}; v0 supports only 'create'")

        validate_relative_output_path(path)

        operations.append(FileOperation(action=action, path=path, content=content))

    if not operations:
        raise SpecToCodeError("LLM response contains no valid project-evo-file blocks")

    return operations


def validate_relative_output_path(raw_path: str) -> None:
    candidate = Path(raw_path)

    if candidate.is_absolute():
        raise SpecToCodeError(f"output path must be relative, got absolute path: {raw_path}")

    if raw_path.strip() != raw_path:
        raise SpecToCodeError(f"output path must not have leading/trailing whitespace: {raw_path!r}")

    if not raw_path:
        raise SpecToCodeError("output path must not be empty")

    if any(part == ".." for part in candidate.parts):
        raise SpecToCodeError(f"output path must not contain '..': {raw_path}")

    if any(part == "" for part in candidate.parts):
        raise SpecToCodeError(f"invalid output path: {raw_path}")

    if candidate.name in {"", ".", ".."}:
        raise SpecToCodeError(f"invalid output path: {raw_path}")


def ensure_inside_directory(base_dir: Path, target_path: Path) -> None:
    base_resolved = base_dir.resolve()
    target_resolved = target_path.resolve()

    try:
        target_resolved.relative_to(base_resolved)
    except ValueError as exc:
        raise SpecToCodeError(f"output path escapes generated directory: {target_path}") from exc


def clear_generated_dir(generated_dir: Path) -> None:
    generated_dir.mkdir(parents=True, exist_ok=True)

    for child in generated_dir.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def apply_file_operations(generated_dir: Path, operations: List[FileOperation]) -> List[Path]:
    clear_generated_dir(generated_dir)

    written: List[Path] = []

    for operation in operations:
        if operation.action != "create":
            raise SpecToCodeError(f"unsupported action during apply: {operation.action}")

        output_path = generated_dir / operation.path
        ensure_inside_directory(generated_dir, output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(operation.content, encoding="utf-8")

        written.append(output_path)

    return written


def run(project_dir: Path, llm_command: str | None) -> List[Path]:
    if not project_dir.exists():
        raise SpecToCodeError(f"project directory does not exist: {project_dir}")

    if not project_dir.is_dir():
        raise SpecToCodeError(f"project path is not a directory: {project_dir}")

    spec_path = project_dir / "spec" / "index.md"
    generated_dir = project_dir / "generated"

    spec_text = read_text_file(spec_path, "project spec")
    prompt = build_prompt(spec_text)
    llm_response = call_llm(prompt, llm_command)
    operations = parse_file_operations(llm_response)
    written_files = apply_file_operations(generated_dir, operations)

    return written_files


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run project-evo spec-to-code action. "
            "The tool reads one project spec, calls a text-only LLM command, "
            "parses project-evo-file blocks, and writes files into generated/."
        )
    )
    parser.add_argument(
        "--project-dir",
        required=True,
        help="Path to project workspace, e.g. project--site-0",
    )
    parser.add_argument(
        "--llm-command",
        default=None,
        help=(
            "Optional LLM command override. "
            "If omitted, PROJECT_EVO_LLM_COMMAND environment variable is used. "
            "The command must read prompt from stdin and write file-operation blocks to stdout."
        ),
    )

    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    llm_command = args.llm_command or os.environ.get("PROJECT_EVO_LLM_COMMAND")

    try:
        written_files = run(project_dir, llm_command)
    except SpecToCodeError as exc:
        print(f"spec-to-code FAILED: {exc}", file=sys.stderr)
        return 1

    print("spec-to-code OK")
    for path in written_files:
        print(f"- {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
