#!/usr/bin/env bash
# Run agent-foundry from this checkout (no pipx reinstall needed).
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}"
exec python - "$@" <<'PY'
import sys
from agent_foundry.cli import main

if __name__ == "__main__":
    sys.argv = ["agent-foundry", *sys.argv[1:]]
    raise SystemExit(main())
PY
