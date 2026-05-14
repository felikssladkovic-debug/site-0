#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TOOL = ROOT / "meta" / "tools" / "check-document-metadata-header.py"
DOC = """---
id: method.same
type: rule
status: active
scope: reusable-method
---

# Doc
"""

def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        method = Path(tmp) / "method"
        method.mkdir()
        (method / "a.md").write_text(DOC, encoding="utf-8")
        (method / "b.md").write_text(DOC, encoding="utf-8")
        result = subprocess.run(["python3", str(TOOL), "--method-dir", str(method)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert result.returncode != 0
        assert "duplicate id" in result.stderr
    print("OK test-3-ids-are-uniq")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
