#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path


def read_spec(project_dir: Path) -> str:
    spec_path = project_dir / "spec" / "index.md"

    if not project_dir.exists():
        raise FileNotFoundError(f"project directory does not exist: {project_dir}")

    if not spec_path.exists():
        raise FileNotFoundError(f"spec file does not exist: {spec_path}")

    return spec_path.read_text(encoding="utf-8")


def extract_counter_title(spec_text: str) -> str:
    match = re.search(r"(?im)^\s*title\s*:\s*(.+?)\s*$", spec_text)
    if match:
        return match.group(1).strip()
    return "Счетчик"


def extract_counter_value(spec_text: str) -> str:
    match = re.search(r"(?im)^\s*value\s*:\s*(\d+)\s*$", spec_text)
    if match:
        return match.group(1).strip()
    return "1"


def generate_index_html(title: str, value: str) -> str:
    safe_title = html.escape(title)
    safe_value = html.escape(value)

    return f"""<!doctype html>
<html lang=\"ru\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{safe_title}</title>
  <style>
    :root {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif;
      color: #111827;
      background: #f9fafb;
    }}
    body {{
      min-height: 100vh;
      margin: 0;
      display: grid;
      place-items: center;
    }}
    main {{
      padding: 40px;
      border-radius: 24px;
      background: white;
      box-shadow: 0 20px 50px rgba(15, 23, 42, 0.10);
      text-align: center;
      min-width: 260px;
    }}
    h1 {{
      margin: 0 0 16px;
      font-size: 32px;
      line-height: 1.1;
    }}
    .value {{
      font-size: 72px;
      line-height: 1;
      font-weight: 700;
    }}
  </style>
</head>
<body>
  <main>
    <h1>{safe_title}</h1>
    <div class=\"value\">{safe_value}</div>
  </main>
</body>
</html>
"""


def write_generated(project_dir: Path, html_text: str) -> Path:
    generated_dir = project_dir / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)

    output_path = generated_dir / "index.html"
    output_path.write_text(html_text, encoding="utf-8")

    return output_path


def run(project_dir: Path) -> Path:
    spec_text = read_spec(project_dir)
    title = extract_counter_title(spec_text)
    value = extract_counter_value(spec_text)
    html_text = generate_index_html(title, value)

    return write_generated(project_dir, html_text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate site-0 code from a single spec document.")
    parser.add_argument("--project-dir", required=True, help="Path to project workspace, e.g. project--site-0")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    try:
        output_path = run(project_dir)
    except Exception as exc:
        print(f"spec-to-code FAILED: {exc}", file=sys.stderr)
        return 1

    print(f"spec-to-code OK: generated {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
