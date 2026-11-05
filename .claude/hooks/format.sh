#!/usr/bin/env bash
# Hook PostToolUse (Edit|Write): formatea el archivo que Claude acaba de escribir.
# Nunca bloquea: si falta la herramienta, no hace nada.
set -uo pipefail

file=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null)
if [ -z "$file" ] || [ ! -f "$file" ]; then exit 0; fi
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

case "$file" in
  *.py)
    if command -v uvx >/dev/null 2>&1; then
      uvx ruff format -q "$file"; uvx ruff check --fix -q "$file"
    fi ;;
  *.astro|*.ts|*.tsx|*.js|*.mjs|*.json|*.md|*.mdx|*.css|*.yml|*.yaml)
    if [ -x node_modules/.bin/prettier ]; then
      node_modules/.bin/prettier --write --log-level warn --ignore-unknown "$file"
    fi ;;
esac
exit 0
