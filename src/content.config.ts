import { defineCollection, reference } from "astro:content";
import { file, glob } from "astro/loaders";
import { z } from "astro/zod";
import { quadrantIds, ringIds } from "./lib/radar";

const slug = /^[a-z0-9]+(-[a-z0-9]+)*$/;
const isoDate = /^\d{4}-\d{2}-\d{2}$/;

const blog = defineCollection({
  loader: glob({ pattern: "**/*.{md,mdx}", base: "./src/content/blog" }),
  schema: ({ image }) =>
    z.object({
      title: z.string().min(1).max(80),
      description: z.string().min(1).max(160),
      pubDate: z.coerce.date(),
      updatedDate: z.coerce.date().optional(),
      authors: z.array(reference("authors")).min(1),
      tags: z.array(z.string().regex(slug, "etiquetas en kebab-case")).min(1).max(5),
      draft: z.boolean().default(false),
      cover: image().optional(),
      coverAlt: z.string().optional(),
    }),
});

const authors = defineCollection({
  loader: glob({ pattern: "*.json", base: "./src/content/authors" }),
  schema: z.object({
    name: z.string().min(1),
    github: z.string().regex(/^[A-Za-z0-9-]+$/),
    bio: z.string().max(200).optional(),
    url: z.url().optional(),
  }),
});

const radar = defineCollection({
  loader: file("src/data/radar.json", {
    parser: (text) => JSON.parse(text).entries,
  }),
  schema: z.object({
    name: z.string().min(1),
    quadrant: z.enum(quadrantIds),
    ring: z.enum(ringIds),
    moved: z.union([z.literal(-1), z.literal(0), z.literal(1), z.literal(2)]),
    description: z.string().min(1).max(280),
    discussion: z.url().nullable(),
    threadId: z.string().nullable(),
    date: z.string().regex(isoDate),
    status: z.enum(["propuesta", "votado"]),
  }),
});

export const collections = { blog, authors, radar };
