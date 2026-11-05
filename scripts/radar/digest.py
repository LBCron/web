#!/usr/bin/env python3
"""Cambios del radar desde una fecha, según el historial de git.

Uso:
  python3 scripts/radar/digest.py --since "7 days ago"            # JSON
  python3 scripts/radar/digest.py --since 2026-11-01 --format discord
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import radar  # noqa: E402

RADAR_PATH = "src/data/radar.json"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def radar_at(since: str, path: str = RADAR_PATH) -> dict:
    """Versión de radar.json vigente justo antes de `since` (vacía si no existía)."""
    rev = git("log", "-1", f"--before={since}", "--format=%H", "--", path).strip()
    if not rev:
        return {"updated": "", "entries": []}
    return json.loads(git("show", f"{rev}:{path}"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--since", default="7 days ago")
    ap.add_argument("--format", choices=["json", "discord"], default="json")
    ap.add_argument("--radar", default=RADAR_PATH)
    args = ap.parse_args(argv)

    changes = radar.diff(radar_at(args.since, args.radar), radar.load(args.radar))
    if args.format == "json":
        print(json.dumps(changes, ensure_ascii=False, indent=2))
    else:
        print(radar.format_discord(changes, heading="Radar de The Agentic Stack — resumen semanal"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
