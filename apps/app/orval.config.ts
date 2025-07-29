import { defineConfig } from 'orval';

export default defineConfig({
  shallowfind: {
    input: '../server/schema.yml',
    output: {
      mode: 'tags-split',
      target: './src/lib/api/',
      client: 'svelte-query',
      override: {
        query: {
          options: {
            useQuery: true,
            staleTime: 1000 * 60 * 5 // 5 minutes
          }
        }
      }
    }
  },
  shallowfindZod: {
    input: '../server/schema.yml',
    output: {
      mode: 'tags-split',
      target: './src/lib/api/',
      client: 'zod',
      fileExtension: '.zod.ts'
    }
  }
});
