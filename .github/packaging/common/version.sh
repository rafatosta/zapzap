#!/usr/bin/env bash
set -euo pipefail

python - <<'PY_VERSION'
from pathlib import Path
import ast

init_py = Path("zapzap") / "__init__.py"
for node in ast.parse(init_py.read_text(encoding="utf-8")).body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__version__":
                print(ast.literal_eval(node.value))
                raise SystemExit
raise SystemExit("__version__ not found")
PY_VERSION
