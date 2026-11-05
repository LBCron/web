---
name: radar-blip
description: Agrega un ítem (blip) al radar tecnológico o lo mueve de anillo/cuadrante, con justificación. Úsalo cuando alguien proponga una tecnología, técnica, herramienta o modelo para el radar, o quiera cambiar su anillo (Adoptar, Probar, Evaluar, Esperar).
argument-hint: "<nombre> [anillo] [cuadrante]"
allowed-tools: Read, Edit, Grep, Bash(npm run radar:validate *), Bash(git switch *), Bash(git diff *)
---

# Agregar o mover un blip del radar

Entrada: `$ARGUMENTS`. Reglas y esquema completos en `.claude/rules/radar.md`.

## 1. Entender la propuesta

- Busca si ya existe: `grep -n -i "<nombre>" src/data/radar.json`. Si existe, es un **movimiento**; si no, es un **blip nuevo**.
- Si falta el cuadrante, el anillo o la justificación, pregúntalo. La justificación es obligatoria: ¿quién lo usa en la comunidad, en qué contexto y con qué resultado?
- Pide (opcional) el enlace al hilo del foro de Discord.

## 2. Editar `src/data/radar.json`

**Blip nuevo**: agrega al final de `entries`:

```json
{
  "id": "<slug-kebab>",
  "name": "<Nombre>",
  "quadrant": "tecnicas | frameworks | herramientas | modelos",
  "ring": "adoptar | probar | evaluar | esperar",
  "moved": 2,
  "description": "<por qué está en este anillo, ≤ 280 caracteres>",
  "discussion": null,
  "threadId": null,
  "date": "<hoy YYYY-MM-DD>",
  "status": "propuesta"
}
```

**Movimiento**: cambia `ring`; `moved` = `1` si se acerca a Adoptar, `-1` si se aleja; `date` = hoy; actualiza `description` con el nuevo porqué; `status` = `propuesta` salvo que haya votación documentada.

Actualiza `updated` en la raíz a hoy.

## 3. Validar y cerrar

1. `npm run radar:validate`.
2. Delega en el subagente `radar-curator` la revisión del cambio.
3. Si no estás en una rama `radar/*`, sugiere `git switch -c radar/<slug>`.
4. Redacta para el PR (plantilla "Blip nuevo"): qué cambia, justificación, enlace al hilo. Recuerda que la votación definitiva ocurre en el foro de Discord (`/radar/como-funciona`).
