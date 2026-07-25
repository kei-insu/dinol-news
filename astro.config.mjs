import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://kei-insu.github.io',
  base: '/dinol-news',
  outDir: './dist',
  publicDir: './public',
  build: { format: 'file' }
});
