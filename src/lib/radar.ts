export const QUADRANTS = [
  { id: "tecnicas", name: "Técnicas y patrones" },
  { id: "frameworks", name: "Frameworks y SDKs de agentes" },
  { id: "herramientas", name: "Herramientas y protocolos" },
  { id: "modelos", name: "Modelos y plataformas" },
] as const;

export const RINGS = [
  {
    id: "adoptar",
    name: "Adoptar",
    emoji: "🟢",
    color: "#15803d",
    summary: "Lo usamos en proyectos reales y lo recomendamos como opción por defecto.",
  },
  {
    id: "probar",
    name: "Probar",
    emoji: "🔵",
    color: "#1d4ed8",
    summary: "Vale la pena usarlo en un proyecto real con un riesgo acotado.",
  },
  {
    id: "evaluar",
    name: "Evaluar",
    emoji: "🟡",
    color: "#b45309",
    summary: "Interesante: hay que explorarlo con prototipos para entender su impacto.",
  },
  {
    id: "esperar",
    name: "Esperar",
    emoji: "🔴",
    color: "#b91c1c",
    summary: "No empezar nada nuevo con esto por ahora; seguir observando.",
  },
] as const;

export type QuadrantId = (typeof QUADRANTS)[number]["id"];
export type RingId = (typeof RINGS)[number]["id"];

export const quadrantIds = QUADRANTS.map((q) => q.id) as [QuadrantId, ...QuadrantId[]];
export const ringIds = RINGS.map((r) => r.id) as [RingId, ...RingId[]];

export const quadrantName = (id: QuadrantId) => QUADRANTS.find((q) => q.id === id)!.name;
export const ring = (id: RingId) => RINGS.find((r) => r.id === id)!;

export const MOVED_LABEL: Record<number, string> = {
  2: "Nuevo",
  1: "Subió",
  0: "Sin cambios",
  [-1]: "Bajó",
};
