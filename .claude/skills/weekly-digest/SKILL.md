---
name: weekly-digest
description: Redacta el resumen semanal de cambios del radar para publicar en Discord. Úsalo cuando pidan el resumen, digest o novedades del radar de la semana (o de un rango de fechas).
argument-hint: "[desde, p. ej. '7 days ago' o 2026-11-01]"
disable-model-invocation: true
allowed-tools: Read, Bash(python3 scripts/radar/digest.py *), Bash(git log *)
---

# Resumen semanal del radar para Discord

1. Calcula los cambios con `python3 scripts/radar/digest.py --since "<desde>"`, donde `<desde>` es `$ARGUMENTS` o, si viene vacío, `7 days ago`.
   El script compara `src/data/radar.json` entre la última versión anterior a esa fecha y `HEAD`, y devuelve JSON con `added`, `moved`, `removed` y `updated`.
2. Si no hubo cambios, responde una línea: "Sin cambios en el radar esta semana" y sugiere temas del foro sin votar si los conoces.
3. Si hubo cambios, redacta el mensaje con este formato (Markdown de Discord, **≤ 1800 caracteres**):

```
📡 **Radar de The Agentic Stack — semana del <fecha>**

🆕 **Nuevos**
• **<Nombre>** → <Anillo> (<Cuadrante>): <descripción breve>

↕️ **Movimientos**
• **<Nombre>**: <Anillo anterior> → <Anillo nuevo> — <por qué, de la descripción>

👋 **Salen del radar**
• **<Nombre>**

Vota y comenta en el foro #radar · https://agenticstack.cl/radar
```

Emojis de anillo: 🟢 Adoptar · 🔵 Probar · 🟡 Evaluar · 🔴 Esperar. Omite secciones vacías. 4. Muestra el texto listo para copiar. **No lo publiques**: la publicación automática la hace el workflow `radar-sync` por webhook; publicar a mano es decisión de quien lo pide.
