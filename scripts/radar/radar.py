"""Modelo de datos del radar: constantes, carga, validación, diferencias y mensajes.

Sin dependencias externas (solo biblioteca estándar) para que corra igual en local,
en hooks y en GitHub Actions.
"""

from __future__ import annotations

import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any

QUADRANTS: dict[str, str] = {
    "tecnicas": "Técnicas y patrones",
    "frameworks": "Frameworks y SDKs de agentes",
    "herramientas": "Herramientas y protocolos",
    "modelos": "Modelos y plataformas",
}

# Orden de adentro hacia afuera: un índice mayor es más conservador.
RINGS: dict[str, str] = {
    "adoptar": "Adoptar",
    "probar": "Probar",
    "evaluar": "Evaluar",
    "esperar": "Esperar",
}
RING_ORDER = list(RINGS)

RING_EMOJI: dict[str, str] = {
    "adoptar": "🟢",
    "probar": "🔵",
    "evaluar": "🟡",
    "esperar": "🔴",
}
EMOJI_RING = {v: k for k, v in RING_EMOJI.items()}

STATUSES = ("propuesta", "votado")
MOVED_VALUES = (-1, 0, 1, 2)
MAX_DESCRIPTION = 280
REQUIRED = (
    "id",
    "name",
    "quadrant",
    "ring",
    "moved",
    "description",
    "discussion",
    "threadId",
    "date",
    "status",
)

_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def slugify(text: str) -> str:
    """'Model Context Protocol (MCP)' -> 'model-context-protocol-mcp'."""
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", norm.lower()).strip("-")


def normalize(text: str) -> str:
    """Minúsculas sin tildes ni signos, para comparar nombres de tags."""
    return slugify(text).replace("-", " ")


def load(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dumps(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def save(path: str | Path, data: dict[str, Any]) -> None:
    Path(path).write_text(dumps(data), encoding="utf-8")


def today() -> str:
    return date.today().isoformat()


def validate(data: Any) -> list[str]:
    """Devuelve la lista de errores (vacía si el radar es válido)."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["la raíz debe ser un objeto con 'updated' y 'entries'"]
    if not _DATE_RE.match(str(data.get("updated", ""))):
        errors.append("'updated' debe ser una fecha YYYY-MM-DD")
    entries = data.get("entries")
    if not isinstance(entries, list):
        return [*errors, "'entries' debe ser una lista"]

    seen_ids: set[str] = set()
    seen_threads: set[str] = set()
    for i, e in enumerate(entries):
        where = f"entries[{i}] ({e.get('id', '?') if isinstance(e, dict) else '?'})"
        if not isinstance(e, dict):
            errors.append(f"{where}: debe ser un objeto")
            continue
        missing = [k for k in REQUIRED if k not in e]
        if missing:
            errors.append(f"{where}: faltan campos {', '.join(missing)}")
            continue
        extra = sorted(set(e) - set(REQUIRED))
        if extra:
            errors.append(f"{where}: campos desconocidos {', '.join(extra)}")
        if not isinstance(e["id"], str) or not _SLUG_RE.match(e["id"]):
            errors.append(f"{where}: 'id' debe ser kebab-case")
        elif e["id"] in seen_ids:
            errors.append(f"{where}: 'id' duplicado")
        seen_ids.add(str(e["id"]))
        if not isinstance(e["name"], str) or not e["name"].strip():
            errors.append(f"{where}: 'name' vacío")
        if e["quadrant"] not in QUADRANTS:
            errors.append(f"{where}: 'quadrant' debe ser uno de {', '.join(QUADRANTS)}")
        if e["ring"] not in RINGS:
            errors.append(f"{where}: 'ring' debe ser uno de {', '.join(RINGS)}")
        if e["moved"] not in MOVED_VALUES or isinstance(e["moved"], bool):
            errors.append(f"{where}: 'moved' debe ser -1, 0, 1 o 2")
        desc = e["description"]
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{where}: 'description' vacía")
        elif len(desc) > MAX_DESCRIPTION:
            errors.append(
                f"{where}: 'description' supera {MAX_DESCRIPTION} caracteres ({len(desc)})"
            )
        disc = e["discussion"]
        if disc is not None and not (isinstance(disc, str) and disc.startswith("https://")):
            errors.append(f"{where}: 'discussion' debe ser una URL https o null")
        tid = e["threadId"]
        if tid is not None:
            if not (isinstance(tid, str) and tid.isdigit()):
                errors.append(f"{where}: 'threadId' debe ser un id numérico en texto o null")
            elif tid in seen_threads:
                errors.append(f"{where}: 'threadId' duplicado")
            else:
                seen_threads.add(tid)
        if not isinstance(e["date"], str) or not _DATE_RE.match(e["date"]):
            errors.append(f"{where}: 'date' debe ser YYYY-MM-DD")
        if e["status"] not in STATUSES:
            errors.append(f"{where}: 'status' debe ser 'propuesta' o 'votado'")
        if e["status"] == "votado" and tid is None:
            errors.append(f"{where}: un blip 'votado' necesita 'threadId' (votación en el foro)")
    return errors


def diff(old: dict[str, Any], new: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Compara dos versiones del radar por 'id'."""
    before = {e["id"]: e for e in old.get("entries", [])}
    after = {e["id"]: e for e in new.get("entries", [])}
    added = [after[i] for i in after if i not in before]
    removed = [before[i] for i in before if i not in after]
    moved, updated = [], []
    for i in after.keys() & before.keys():
        a, b = before[i], after[i]
        if a["ring"] != b["ring"]:
            moved.append({**b, "from": a["ring"]})
        elif {k: v for k, v in a.items() if k != "moved"} != {
            k: v for k, v in b.items() if k != "moved"
        }:
            updated.append(b)
    key = lambda e: e["name"].lower()  # noqa: E731
    return {
        "added": sorted(added, key=key),
        "moved": sorted(moved, key=key),
        "removed": sorted(removed, key=key),
        "updated": sorted(updated, key=key),
    }


def has_ring_changes(changes: dict[str, list]) -> bool:
    return bool(changes["added"] or changes["moved"] or changes["removed"])


def _ring(r: str) -> str:
    return f"{RING_EMOJI[r]} {RINGS[r]}"


def format_discord(
    changes: dict[str, list],
    *,
    heading: str,
    footer: str = "Vota y comenta en el foro #radar · https://agenticstack.cl/radar",
    limit: int = 1800,
) -> str:
    """Mensaje en Markdown de Discord con los cambios de anillo (≤ limit caracteres)."""
    lines = [f"📡 **{heading}**", ""]
    if changes["added"]:
        lines.append("🆕 **Nuevos**")
        lines += [
            f"• **{e['name']}** → {_ring(e['ring'])} ({QUADRANTS[e['quadrant']]})"
            for e in changes["added"]
        ]
        lines.append("")
    if changes["moved"]:
        lines.append("↕️ **Movimientos**")
        lines += [
            f"• **{e['name']}**: {_ring(e['from'])} → {_ring(e['ring'])}" for e in changes["moved"]
        ]
        lines.append("")
    if changes["removed"]:
        lines.append("👋 **Salen del radar**")
        lines += [f"• **{e['name']}**" for e in changes["removed"]]
        lines.append("")
    if not has_ring_changes(changes):
        lines += ["Sin cambios de anillo.", ""]
    lines.append(footer)
    text = "\n".join(lines)
    if len(text) > limit:
        cut = text[: limit - len(footer) - 6].rsplit("\n", 1)[0]
        text = f"{cut}\n…\n\n{footer}"
    return text
