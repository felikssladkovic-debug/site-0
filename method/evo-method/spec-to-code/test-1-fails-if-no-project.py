#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "method" / "tools" / "spec-to-code.py"

def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        missing_project = Path(tmp) / "project--missing"
        result = subprocess.run(["python3", str(TOOL), "--project-dir", str(missing_project)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode != 0
        assert "project directory does not exist" in result.stderr
    print("OK test-1-fails-if-no-project")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
