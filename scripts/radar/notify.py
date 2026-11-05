#!/usr/bin/env python3
"""Publica en Discord (webhook) un resumen de los cambios de anillo del sync.

Uso: DISCORD_WEBHOOK_URL=... python3 scripts/radar/notify.py --changes cambios.json [--pr-url URL]
Sin cambios de anillo no publica nada. Con --dry-run imprime el mensaje.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import radar  # noqa: E402


def build_message(changes: dict, pr_url: str | None) -> str:
    footer = "Detalle y votación en el foro #radar · https://agenticstack.cl/radar"
    if pr_url:
        footer = f"Propuesta de actualización en revisión: <{pr_url}>\n{footer}"
    return radar.format_discord(changes, heading="Cambios en el radar según el foro", footer=footer)


def post(webhook: str, content: str) -> None:
    body = json.dumps({"content": content, "allowed_mentions": {"parse": []}}).encode()
    req = urllib.request.Request(
        webhook,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "agenticstack-radar/0.1"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        resp.read()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--changes", required=True)
    ap.add_argument("--pr-url")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    changes = json.loads(Path(args.changes).read_text(encoding="utf-8"))
    if not radar.has_ring_changes(changes):
        print("Sin cambios de anillo: no se publica nada.")
        return 0
    message = build_message(changes, args.pr_url)
    if args.dry_run:
        print(message)
        return 0
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook:
        print("DISCORD_WEBHOOK_URL no está definido: se omite la publicación.", file=sys.stderr)
        return 0
    post(webhook, message)
    print("📣 Resumen publicado en Discord.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
