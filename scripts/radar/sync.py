#!/usr/bin/env python3
"""Sincroniza el radar con el foro de Discord.

Modelo del foro:
  - un hilo = un blip
  - la etiqueta (tag) del hilo = cuadrante
  - reacciones en el primer mensaje = votos de anillo
    (🟢 Adoptar, 🔵 Probar, 🟡 Evaluar, 🔴 Esperar)

Por cada hilo con quórum se calcula el anillo por mayoría (empate → el anillo más
conservador, es decir, el más externo) y se compara con src/data/radar.json.
El script solo escribe el archivo; el workflow radar-sync.yml abre el PR.

Uso:
  # contra el fixture local (sin red)
  python3 scripts/radar/sync.py --fixture scripts/radar/fixtures/forum.json --dry-run

  # contra Discord (requiere DISCORD_TOKEN y FORUM_CHANNEL_ID)
  python3 scripts/radar/sync.py --changes-out cambios.json --pr-body-out pr.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Protocol

sys.path.insert(0, str(Path(__file__).resolve().parent))

import radar  # noqa: E402

DEFAULT_QUORUM = 5
DEFAULT_MOVED_RESET_DAYS = 90
API = "https://discord.com/api/v10"
USER_AGENT = "DiscordBot (https://github.com/agentic-stack-cl/web, 0.1)"

# Nombres de tags del foro (normalizados, sin tildes) → cuadrante.
# Se acepta el nombre completo o la primera palabra.
TAG_ALIASES: dict[str, str] = {
    "tecnicas y patrones": "tecnicas",
    "tecnicas": "tecnicas",
    "frameworks y sdks": "frameworks",
    "frameworks y sdks de agentes": "frameworks",
    "frameworks": "frameworks",
    "herramientas y protocolos": "herramientas",
    "herramientas": "herramientas",
    "modelos y plataformas": "modelos",
    "modelos": "modelos",
}


# ---------------------------------------------------------------------------
# Fuentes de datos
# ---------------------------------------------------------------------------


class ForumSource(Protocol):
    def channel(self) -> dict[str, Any]: ...
    def threads(self) -> list[dict[str, Any]]: ...
    def starter_message(self, thread_id: str) -> dict[str, Any] | None: ...


class FixtureSource:
    """Lee un JSON con la misma forma que las respuestas de la API de Discord."""

    def __init__(self, path: str | Path):
        self.data = json.loads(Path(path).read_text(encoding="utf-8"))

    def channel(self) -> dict[str, Any]:
        return self.data["channel"]

    def threads(self) -> list[dict[str, Any]]:
        forum_id = self.data["channel"]["id"]
        active = [
            t for t in self.data["active_threads"]["threads"] if t.get("parent_id") == forum_id
        ]
        return active + self.data["archived_threads"]["threads"]

    def starter_message(self, thread_id: str) -> dict[str, Any] | None:
        return self.data["messages"].get(thread_id)


class DiscordSource:
    """Cliente mínimo de la API REST de Discord (token de bot, solo lectura)."""

    def __init__(self, token: str, forum_id: str):
        self.token = token
        self.forum_id = forum_id
        self._channel: dict[str, Any] | None = None

    def _get(self, path: str) -> Any:
        req = urllib.request.Request(
            f"{API}{path}",
            headers={"Authorization": f"Bot {self.token}", "User-Agent": USER_AGENT},
        )
        for _ in range(5):
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.load(resp)
            except urllib.error.HTTPError as exc:
                if exc.code == 429:
                    retry = float(json.load(exc).get("retry_after", 1))
                    time.sleep(retry + 0.1)
                    continue
                if exc.code == 404:
                    return None
                raise
        raise RuntimeError(f"Discord: demasiados reintentos en {path}")

    def channel(self) -> dict[str, Any]:
        if self._channel is None:
            self._channel = self._get(f"/channels/{self.forum_id}")
        return self._channel

    def threads(self) -> list[dict[str, Any]]:
        guild_id = self.channel()["guild_id"]
        active = self._get(f"/guilds/{guild_id}/threads/active")["threads"]
        threads = [t for t in active if t.get("parent_id") == self.forum_id]
        before = None
        while True:
            q = "?limit=100" + (f"&before={before}" if before else "")
            page = self._get(f"/channels/{self.forum_id}/threads/archived/public{q}")
            threads += page["threads"]
            if not page.get("has_more") or not page["threads"]:
                break
            before = page["threads"][-1]["thread_metadata"]["archive_timestamp"]
        return threads

    def starter_message(self, thread_id: str) -> dict[str, Any] | None:
        # En los foros, el primer mensaje tiene el mismo id que el hilo.
        return self._get(f"/channels/{thread_id}/messages/{thread_id}")


# ---------------------------------------------------------------------------
# Lógica de votación
# ---------------------------------------------------------------------------


@dataclass
class Thread:
    id: str
    name: str
    quadrant: str | None
    votes: dict[str, int]
    content: str
    url: str

    @property
    def total(self) -> int:
        return sum(self.votes.values())


def count_votes(message: dict[str, Any] | None) -> dict[str, int]:
    """Cuenta reacciones de anillo en el primer mensaje del hilo."""
    votes = dict.fromkeys(radar.RINGS, 0)
    for reaction in (message or {}).get("reactions", []):
        ring = radar.EMOJI_RING.get(reaction.get("emoji", {}).get("name", ""))
        if ring:
            votes[ring] += int(reaction.get("count", 0))
    return votes


def winning_ring(votes: dict[str, int], quorum: int) -> str | None:
    """Anillo con más votos si se alcanza el quórum; en empate gana el más externo."""
    if sum(votes.values()) < quorum:
        return None
    best = max(votes.values())
    tied = [r for r in radar.RING_ORDER if votes[r] == best]
    return tied[-1]


def quadrant_for(thread: dict[str, Any], tags: dict[str, str]) -> str | None:
    for tag_id in thread.get("applied_tags", []):
        name = radar.normalize(tags.get(tag_id, ""))
        if name in TAG_ALIASES:
            return TAG_ALIASES[name]
        first = name.split(" ")[0] if name else ""
        if first in TAG_ALIASES:
            return TAG_ALIASES[first]
    return None


def read_forum(source: ForumSource) -> list[Thread]:
    channel = source.channel()
    tags = {t["id"]: t["name"] for t in channel.get("available_tags", [])}
    guild = channel.get("guild_id", "0")
    out = []
    for t in source.threads():
        msg = source.starter_message(t["id"])
        out.append(
            Thread(
                id=t["id"],
                name=t["name"].strip(),
                quadrant=quadrant_for(t, tags),
                votes=count_votes(msg),
                content=(msg or {}).get("content", ""),
                url=f"https://discord.com/channels/{guild}/{t['id']}",
            )
        )
    return out


# ---------------------------------------------------------------------------
# Aplicar cambios
# ---------------------------------------------------------------------------


@dataclass
class Result:
    data: dict[str, Any]
    changes: dict[str, list[dict[str, Any]]]
    skipped: list[str] = field(default_factory=list)


def first_paragraph(text: str, limit: int = radar.MAX_DESCRIPTION) -> str:
    para = next((p.strip() for p in text.split("\n\n") if p.strip()), "")
    para = " ".join(para.split())
    if len(para) <= limit:
        return para or "Propuesto en el foro de Discord."
    return para[: limit - 1].rsplit(" ", 1)[0] + "…"


def find_entry(entries: list[dict[str, Any]], thread: Thread) -> dict[str, Any] | None:
    for e in entries:
        if e["threadId"] == thread.id:
            return e
    # Adopta blips sembrados a mano (sin hilo) con el mismo nombre.
    slug = radar.slugify(thread.name)
    for e in entries:
        if e["threadId"] is None and slug in (e["id"], radar.slugify(e["name"])):
            return e
    return None


def apply(
    current: dict[str, Any],
    threads: list[Thread],
    *,
    quorum: int = DEFAULT_QUORUM,
    today: str | None = None,
    moved_reset_days: int = DEFAULT_MOVED_RESET_DAYS,
) -> Result:
    today = today or radar.today()
    data = json.loads(json.dumps(current))  # copia profunda
    entries: list[dict[str, Any]] = data["entries"]
    skipped: list[str] = []

    for t in threads:
        if t.quadrant is None:
            skipped.append(f"{t.name}: el hilo no tiene una etiqueta de cuadrante")
            continue
        ring = winning_ring(t.votes, quorum)
        if ring is None:
            skipped.append(f"{t.name}: {t.total} votos, bajo el quórum de {quorum}")
            continue
        entry = find_entry(entries, t)
        if entry is None:
            ids = {e["id"] for e in entries}
            new_id = radar.slugify(t.name) or f"hilo-{t.id}"
            if new_id in ids:
                new_id = f"{new_id}-{t.id[-4:]}"
            entries.append(
                {
                    "id": new_id,
                    "name": t.name,
                    "quadrant": t.quadrant,
                    "ring": ring,
                    "moved": 2,
                    "description": first_paragraph(t.content),
                    "discussion": t.url,
                    "threadId": t.id,
                    "date": today,
                    "status": "votado",
                }
            )
            continue
        entry.update(
            {"threadId": t.id, "discussion": t.url, "status": "votado", "quadrant": t.quadrant}
        )
        if entry["ring"] != ring:
            closer = radar.RING_ORDER.index(ring) < radar.RING_ORDER.index(entry["ring"])
            entry.update({"ring": ring, "moved": 1 if closer else -1, "date": today})

    # Los indicadores de movimiento se apagan tras un tiempo.
    limit = (date.fromisoformat(today) - timedelta(days=moved_reset_days)).isoformat()
    for e in entries:
        if e["moved"] != 0 and e["date"] < limit:
            e["moved"] = 0

    changes = radar.diff(current, data)
    if any(changes.values()):
        data["updated"] = today
    return Result(data=data, changes=changes, skipped=skipped)


def pr_body(result: Result, quorum: int) -> str:
    c = result.changes
    lines = [
        "Sincronización automática del radar con el foro de Discord.",
        "",
        f"Quórum: {quorum} votos. Empates → anillo más conservador.",
        "",
    ]

    def row(e: dict[str, Any], change: str) -> str:
        link = f"[hilo]({e['discussion']})" if e.get("discussion") else "—"
        return f"| {e['name']} | {radar.QUADRANTS[e['quadrant']]} | {change} | {link} |"

    if any(c.values()):
        lines += ["| Blip | Cuadrante | Cambio | Discusión |", "| --- | --- | --- | --- |"]
        lines += [row(e, f"🆕 {radar.RINGS[e['ring']]}") for e in c["added"]]
        lines += [
            row(e, f"{radar.RINGS[e['from']]} → {radar.RINGS[e['ring']]}") for e in c["moved"]
        ]
        lines += [row(e, "actualizado (hilo, estado o metadatos)") for e in c["updated"]]
        lines += [row(e, "👋 fuera") for e in c["removed"]]
    if result.skipped:
        lines += ["", "<details><summary>Hilos sin cambios aplicados</summary>", ""]
        lines += [f"- {s}" for s in result.skipped]
        lines += ["", "</details>"]
    lines += [
        "",
        "Revisa con el subagente `radar-curator` antes de aprobar.",
        "",
        "🤖 Generado por `.github/workflows/radar-sync.yml`",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--radar", default="src/data/radar.json", help="ruta de radar.json")
    ap.add_argument("--fixture", help="JSON local con la forma de la API de Discord (sin red)")
    ap.add_argument(
        "--quorum", type=int, default=int(os.environ.get("RADAR_QUORUM", DEFAULT_QUORUM))
    )
    ap.add_argument("--today", help="fecha a usar (YYYY-MM-DD), útil en tests")
    ap.add_argument("--dry-run", action="store_true", help="no escribe radar.json")
    ap.add_argument("--changes-out", help="escribe los cambios en JSON aquí")
    ap.add_argument("--pr-body-out", help="escribe el cuerpo del PR en Markdown aquí")
    args = ap.parse_args(argv)

    if args.fixture:
        source: ForumSource = FixtureSource(args.fixture)
    else:
        token, forum = os.environ.get("DISCORD_TOKEN"), os.environ.get("FORUM_CHANNEL_ID")
        if not token or not forum:
            print("Faltan DISCORD_TOKEN y/o FORUM_CHANNEL_ID (o usa --fixture).", file=sys.stderr)
            return 2
        source = DiscordSource(token, forum)

    current = radar.load(args.radar)
    result = apply(current, read_forum(source), quorum=args.quorum, today=args.today)

    errors = radar.validate(result.data)
    if errors:
        print("❌ El resultado no es un radar válido:", *errors, sep="\n  - ", file=sys.stderr)
        return 1

    c = result.changes
    print(
        f"Nuevos: {len(c['added'])} · Movidos: {len(c['moved'])} · "
        f"Actualizados: {len(c['updated'])} · Omitidos: {len(result.skipped)}"
    )
    for s in result.skipped:
        print(f"  · {s}")

    if args.changes_out:
        Path(args.changes_out).write_text(
            json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    if args.pr_body_out:
        Path(args.pr_body_out).write_text(pr_body(result, args.quorum), encoding="utf-8")
    if not args.dry_run and any(c.values()):
        radar.save(args.radar, result.data)
        print(f"✏️  {args.radar} actualizado")
    return 0


if __name__ == "__main__":
    sys.exit(main())
