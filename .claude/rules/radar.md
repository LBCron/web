---
paths:
  - "src/data/radar.json"
  - "scripts/radar/**"
---

# Reglas del radar

`src/data/radar.json` tiene la forma `{ "updated": "YYYY-MM-DD", "entries": [Blip, ...] }`.

Blip:

| campo | valores |
| --- | --- |
| `id` | slug único kebab-case (`model-context-protocol`) |
| `name` | nombre visible |
| `quadrant` | `tecnicas` · `frameworks` · `herramientas` · `modelos` |
| `ring` | `adoptar` · `probar` · `evaluar` · `esperar` |
| `moved` | `0` sin cambio · `1` subió (hacia Adoptar) · `-1` bajó · `2` nuevo |
| `description` | 1–3 frases en español, ≤ 280 caracteres, por qué está en ese anillo |
| `discussion` | URL del hilo del foro de Discord o `null` |
| `threadId` | id del hilo de Discord (string) o `null`; es la clave que usa el sync |
| `date` | `YYYY-MM-DD` del último cambio de anillo |
| `status` | `propuesta` (sin votación todavía) · `votado` (anillo decidido en el foro) |

- Cuadrantes: Técnicas y patrones · Frameworks y SDKs de agentes · Herramientas y protocolos · Modelos y plataformas.
- Anillos: Adoptar (lo usamos en producción y lo recomendamos) · Probar (vale la pena en proyectos reales con cuidado) · Evaluar (explorar, prototipos) · Esperar (no empezar nada nuevo con esto).
- Un cambio de anillo hecho a mano exige justificación en el PR y `status: "propuesta"` hasta que el foro vote. Los blips con `status: "votado"` solo los mueve el sync (o una votación documentada).
- Al mover: actualiza `ring`, `moved` y `date`. Al revisar el radar completo, los `moved` antiguos vuelven a `0`.
- Valida siempre con `npm run radar:validate`.
- Emojis de voto en el foro: 🟢 Adoptar · 🔵 Probar · 🟡 Evaluar · 🔴 Esperar.
