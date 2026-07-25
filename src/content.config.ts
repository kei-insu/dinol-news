import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const langPair = z.object({
  kr: z.string().nullable(),
  en: z.string().nullable(),
});

const news = defineCollection({
  loader: glob({ pattern: '*.json', base: './content/news' }),
  schema: z.object({
    contentId: z.string(),
    date: z.string(),
    section: z.enum(['ai', 'design']),
    order: z.number(),
    source: z.object({
      name: z.string().nullable(),
      publishedAt: z.string().nullable(),
    }),
    url: z.string(),
    isEn: z.boolean(),
    featured: z.boolean(),
    category: langPair,
    title: langPair,
    summary: langPair,
    points: z.object({
      kr: z.array(z.string()),
      en: z.array(z.string()),
    }),
    positions: z.array(z.string()),
    designer: langPair,
    impactScore: z.number().nullable(),
    recommend: langPair,
    comment: langPair,
    thumbLabel: z.string().nullable(),
    thumbGradient: z.string().nullable(),
    _todo: z.array(z.string()),
  }),
});

export const collections = { news };
