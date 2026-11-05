import type { CollectionEntry } from "astro:content";
import { QUADRANTS, RINGS, type QuadrantId } from "./radar";

/**
 * radar.js numera los cuadrantes así: 0 abajo-derecha, 1 abajo-izquierda,
 * 2 arriba-izquierda, 3 arriba-derecha. Elegimos una disposición tipo ThoughtWorks.
 */
export const RADAR_POSITION: Record<QuadrantId, 0 | 1 | 2 | 3> = {
  tecnicas: 2,
  herramientas: 3,
  modelos: 1,
  frameworks: 0,
};

export const radarQuadrants = [0, 1, 2, 3].map((pos) => QUADRANTS.find((q) => RADAR_POSITION[q.id] === pos)!);

const ringIndex = (id: string) => RINGS.findIndex((r) => r.id === id);

/**
 * Replica la numeración de radar.js (cuadrantes en orden 2,3,1,0; anillos de adentro
 * hacia afuera; nombre alfabético) para que la tabla y el gráfico muestren el mismo número.
 */
export function numberBlips(blips: CollectionEntry<"radar">[]) {
  const numbers = new Map<string, number>();
  let n = 1;
  for (const pos of [2, 3, 1, 0]) {
    for (let r = 0; r < RINGS.length; r++) {
      blips
        .filter((b) => RADAR_POSITION[b.data.quadrant] === pos && ringIndex(b.data.ring) === r)
        .sort((a, b) => a.data.name.localeCompare(b.data.name))
        .forEach((b) => numbers.set(b.id, n++));
    }
  }
  return numbers;
}

export function toRadarEntries(blips: CollectionEntry<"radar">[]) {
  return blips.map((b) => ({
    label: b.data.name,
    quadrant: RADAR_POSITION[b.data.quadrant],
    ring: ringIndex(b.data.ring),
    moved: b.data.moved,
    link: `#blip-${b.id}`,
    active: true,
  }));
}
