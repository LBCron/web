# The Agentic Stack — web

[![CI](https://github.com/agentic-stack-cl/web/actions/workflows/ci.yml/badge.svg)](https://github.com/agentic-stack-cl/web/actions/workflows/ci.yml)
[![Deploy](https://github.com/agentic-stack-cl/web/actions/workflows/deploy.yml/badge.svg)](https://github.com/agentic-stack-cl/web/actions/workflows/deploy.yml)

Sitio público de **The Agentic Stack**, la comunidad chilena que explora el desarrollo de software agéntico: radar tecnológico, blog y páginas de comunidad.

🌐 https://agenticstack.cl · 📋 [Tablero "Web pública"](https://github.com/orgs/agentic-stack-cl/projects/1) · 🤝 [Cómo contribuir](CONTRIBUTING.md)

## Qué hay aquí

|                              |                                                                                                                                                                                                                       |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Radar** (`/radar`)         | Técnicas, frameworks, herramientas y modelos en anillos Adoptar · Probar · Evaluar · Esperar, votados en el foro de Discord y sincronizados por un job diario. Datos en [`src/data/radar.json`](src/data/radar.json). |
| **Blog** (`/blog`)           | Posts de la comunidad en Markdown, con etiquetas, RSS y comentarios vía giscus (GitHub Discussions).                                                                                                                  |
| **Comunidad** (`/comunidad`) | Reglas, cómo unirse y cómo contribuir.                                                                                                                                                                                |

## Desarrollo

```bash
npm install
npm run dev     # http://localhost:4321
npm run check && npm run build
```

Stack: [Astro](https://astro.build) 7, Tailwind CSS 4, [radar.js de Zalando](https://github.com/zalando/tech-radar), Python 3.11 (pipeline del radar), GitHub Pages.

## Un repo agéntico

Este repo trae configuración de [Claude Code](https://code.claude.com/docs) lista para usar y como ejemplo para la comunidad: `CLAUDE.md`, reglas por ruta, subagentes (`content-editor`, `radar-curator`, `web-reviewer`, `release-checker`), skills (`/new-post`, `/radar-blip`, `/weekly-digest`), hooks y plugins recomendados. Lee [docs/AGENTIC.md](docs/AGENTIC.md).

## Documentación

- [docs/AGENTIC.md](docs/AGENTIC.md) — trabajar con Claude Code en este repo
- [docs/RADAR-SYNC.md](docs/RADAR-SYNC.md) — pipeline radar ↔ Discord
- [docs/DEPLOY.md](docs/DEPLOY.md) — despliegue y configuración del repo
- [docs/DNS.md](docs/DNS.md) — registros DNS en NIC Chile

## Licencias

- Código: [MIT](LICENSE)
- Contenido (`src/content/`, `src/data/`): [CC BY-SA 4.0](LICENSE-content)
- Identidad visual (`public/brand/`): © The Agentic Stack
