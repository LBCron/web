#!/usr/bin/env python3
"""Valida src/data/radar.json. Uso: python3 scripts/radar/validate.py [ruta]"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from radar import load, validate  # noqa: E402


def main(argv: list[str]) -> int:
    path = argv[1] if len(argv) > 1 else "src/data/radar.json"
    try:
        data = load(path)
    except FileNotFoundError:
        print(f"❌ No existe {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"❌ {path} no es JSON válido: {exc}", file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        print(f"❌ {path}: {len(errors)} errores", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"✅ {path}: {len(data['entries'])} blips válidos")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
