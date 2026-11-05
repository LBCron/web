---
paths:
  - "src/content/**"
---

# Reglas de contenido (blog y autores)

- Posts en `src/content/blog/<slug>.md` (o `.mdx` si usa componentes). El slug es el nombre del archivo: kebab-case, sin tildes ni ñ, ≤ 60 caracteres.
- Front-matter obligatorio (ver `src/content.config.ts`):
  - `title` (≤ 80 caracteres), `description` (≤ 160, se usa en SEO y RSS)
  - `pubDate` (`YYYY-MM-DD`), `updatedDate` opcional
  - `authors`: lista de handles de GitHub que existan en `src/content/authors/`
  - `tags`: 1–5 etiquetas en minúsculas, kebab-case, reutiliza las existentes antes de crear nuevas
  - `draft: true` mientras no esté listo (no se publica ni aparece en RSS)
- Autores: `src/content/authors/<handle>.json` con `name`, `github` (= handle) y opcionalmente `bio` y `url`.
- Estilo: español neutro, tuteo, frases cortas. Sin "en este artículo veremos". Explica siglas la primera vez (p. ej. "MCP (Model Context Protocol)").
- Código en bloques con lenguaje (` ```ts `). Imágenes en `src/assets/blog/<slug>/` con `alt` descriptivo.
- Enlaces externos con texto descriptivo, nunca "aquí".
- El contenido queda bajo CC BY-SA 4.0 (`LICENSE-content`): no pegues texto ajeno sin licencia compatible.
