#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


REQUIRED_FIELDS = ("id", "type", "status", "scope")
ALLOWED_FIELDS = set(REQUIRED_FIELDS)

KNOWN_TYPES = {
    "rule",
    "command-schema",
    "ontology-schema",
    "view-meta",
    "validation-contract",
    "example",
}

KNOWN_STATUSES = {
    "draft",
    "active",
    "deprecated",
    "archived",
}

KNOWN_SCOPES = {
    "reusable-method",
    "generated-artifact",
}

HEADER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


@dataclass
class ValidationError:
    path: Path
    message: str


def iter_method_markdown_files(method_dir: Path) -> Iterable[Path]:
    for path in sorted(method_dir.rglob("*.md")):
        rel_parts = path.relative_to(method_dir).parts
        if rel_parts and rel_parts[0] == "tests":
            continue
        yield path


def parse_simple_yaml_header(text: str) -> Tuple[Dict[str, str], str | None]:
    match = HEADER_RE.match(text)
    if not match:
        return {}, "missing YAML front matter header"

    raw = match.group(1)
    data: Dict[str, str] = {}

    for line_no, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip()

        if not stripped:
            continue

        if ":" not in stripped:
            return data, f"invalid metadata line {line_no}: {line!r}"

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            return data, f"empty metadata key on line {line_no}"

        if not value:
            return data, f"empty metadata value for key {key!r}"

        if key in data:
            return data, f"duplicate metadata key: {key!r}"

        data[key] = value

    return data, None


def validate_file(path: Path) -> List[ValidationError]:
    text = path.read_text(encoding="utf-8")
    header, parse_error = parse_simple_yaml_header(text)

    errors: List[ValidationError] = []

    if parse_error:
        return [ValidationError(path, parse_error)]

    keys = set(header.keys())

    missing = [field for field in REQUIRED_FIELDS if field not in header]
    for field in missing:
        errors.append(ValidationError(path, f"missing required field: {field}"))

    extra = sorted(keys - ALLOWED_FIELDS)
    for field in extra:
        errors.append(ValidationError(path, f"unexpected metadata field: {field}"))

    if "type" in header and header["type"] not in KNOWN_TYPES:
        errors.append(ValidationError(path, f"unknown type: {header['type']}"))

    if "status" in header and header["status"] not in KNOWN_STATUSES:
        errors.append(ValidationError(path, f"unknown status: {header['status']}"))

    if "scope" in header and header["scope"] not in KNOWN_SCOPES:
        errors.append(ValidationError(path, f"unknown scope: {header['scope']}"))

    return errors


def validate_method_dir(method_dir: Path) -> List[ValidationError]:
    if not method_dir.exists():
        return [ValidationError(method_dir, "method directory does not exist")]

    if not method_dir.is_dir():
        return [ValidationError(method_dir, "method path is not a directory")]

    errors: List[ValidationError] = []
    ids: Dict[str, Path] = {}

    for path in iter_method_markdown_files(method_dir):
        file_errors = validate_file(path)
        errors.extend(file_errors)

        if not file_errors:
            text = path.read_text(encoding="utf-8")
            header, _ = parse_simple_yaml_header(text)
            doc_id = header.get("id")
            if doc_id:
                if doc_id in ids:
                    errors.append(ValidationError(path, f"duplicate id {doc_id!r}; already used by {ids[doc_id]}"))
                else:
                    ids[doc_id] = path

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate metadata headers in /method Markdown documents.")
    parser.add_argument("--method-dir", required=True, help="Path to the /method directory")
    args = parser.parse_args()

    method_dir = Path(args.method_dir).resolve()
    errors = validate_method_dir(method_dir)

    if errors:
        print("Document metadata header check FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error.path}: {error.message}", file=sys.stderr)
        return 1

    checked = list(iter_method_markdown_files(method_dir))
    print(f"Document metadata header check OK: {len(checked)} method Markdown file(s) checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
