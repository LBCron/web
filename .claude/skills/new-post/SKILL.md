---
name: new-post
description: Crea un post nuevo del blog con front-matter correcto, rama y archivo en src/content/blog/. Úsalo cuando alguien quiera escribir, proponer o empezar un post o artículo para el blog.
argument-hint: "<título del post>"
allowed-tools: Read, Write, Glob, Grep, Bash(git switch *), Bash(git checkout *), Bash(npm run check *)
---

# Crear un post nuevo

Título recibido: `$ARGUMENTS` (si está vacío, pregúntalo).

1. **Autor**: obtén el handle de GitHub con `gh api user --jq .login` (o pregúntalo). Si no existe `src/content/authors/<handle>.json`, créalo con `{"name": "...", "github": "<handle>"}` preguntando el nombre visible.
2. **Slug**: kebab-case del título, sin tildes ni ñ (`á→a`, `ñ→n`), sin artículos iniciales, ≤ 60 caracteres. Verifica que no exista `src/content/blog/<slug>.md`.
3. **Rama**: `git switch -c post/<slug>` (si ya estás en una rama `post/*`, quédate en ella).
4. **Etiquetas**: lista las existentes con `grep -rh "^tags:" -A5 src/content/blog/ | sort -u` y propone 1–5, reutilizando.
5. **Archivo**: copia [template.md](template.md) a `src/content/blog/<slug>.md` y rellena:
   - `title`: el título (≤ 80 caracteres)
   - `description`: una frase que resuma el post (≤ 160), redáctala tú y pídele confirmación
   - `pubDate`: la fecha de hoy
   - `authors`, `tags`
   - `draft: true`
6. Si el usuario dio contenido o un esquema, redacta el cuerpo siguiendo `.claude/rules/content.md`; si no, deja la estructura del template.
7. Ejecuta `npm run check` y corrige errores de front-matter.
8. Sugiere el siguiente paso: escribir, luego invocar al subagente `content-editor`, cambiar a `draft: false` y abrir el PR con la plantilla "Post nuevo" (`Closes #N` si hay issue).

No hagas commit ni push sin que te lo pidan.
