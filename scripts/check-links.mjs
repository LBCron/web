#!/usr/bin/env node
// Revisa enlaces internos (href/src que empiezan con "/") en los HTML generados.
// Uso: node scripts/check-links.mjs dist
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const root = process.argv[2] ?? "dist";
if (!existsSync(root)) {
  console.error(`No existe ${root}/. Ejecuta primero: npm run build`);
  process.exit(1);
}

const htmlFiles = [];
(function walk(dir) {
  for (const name of readdirSync(dir)) {
    const p = join(dir, name);
    if (statSync(p).isDirectory()) walk(p);
    else if (name.endsWith(".html")) htmlFiles.push(p);
  }
})(root);

const ATTR = /\b(?:href|src)=["'](\/[^"'#?]*)(?:[?#][^"']*)?["']/g;
const resolves = (url) => {
  const clean = decodeURIComponent(url).replace(/\/$/, "");
  const base = join(root, clean);
  return (
    clean === "" ||
    (existsSync(base) && statSync(base).isFile()) ||
    existsSync(join(base, "index.html")) ||
    existsSync(`${base}.html`)
  );
};

const broken = [];
let checked = 0;
for (const file of htmlFiles) {
  const html = readFileSync(file, "utf8");
  for (const [, url] of html.matchAll(ATTR)) {
    if (url.startsWith("//")) continue; // protocolo relativo: externo
    checked++;
    if (!resolves(url)) broken.push(`${relative(root, file)} → ${url}`);
  }
}

if (broken.length) {
  console.error(`❌ ${broken.length} enlaces internos rotos (de ${checked} revisados):`);
  for (const b of [...new Set(broken)]) console.error(`  ${b}`);
  process.exit(1);
}
console.log(`✅ ${checked} enlaces internos revisados en ${htmlFiles.length} páginas, sin errores.`);
