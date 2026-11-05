#!/usr/bin/env bash
# Hook PostToolUse (Edit|Write): si se editó src/data/radar.json, lo valida.
# Sale con código 2 para que Claude vea el error y lo corrija.
set -uo pipefail

file=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null)
case "$file" in
  */src/data/radar.json|src/data/radar.json) ;;
  *) exit 0 ;;
esac
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0
if ! out=$(python3 scripts/radar/validate.py src/data/radar.json 2>&1); then
  echo "radar.json no pasa la validación:" >&2
  echo "$out" >&2
  exit 2
fi
exit 0
