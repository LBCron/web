import { existsSync } from "node:fs";
import { join } from "node:path";

/** Devuelve la ruta pública de un archivo de marca solo si existe en public/brand/. */
function asset(file: string): string | null {
  return existsSync(join(process.cwd(), "public", "brand", file)) ? `/brand/${file}` : null;
}

export const BRAND = {
  logoHorizontal: asset("logotipo-horizontal.svg"),
  logoHorizontalWhite: asset("logotipo-horizontal-blanco.svg"),
  logo: asset("logo-color.svg"),
  logoWhite: asset("logo-blanco.svg"),
  og: asset("logo-512.png"),
  favicon32: asset("favicon-32.png"),
  faviconSvg: asset("favicon.svg"),
};
