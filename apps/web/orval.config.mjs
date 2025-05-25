export default {
  shallowfind: {
    input: '../server/schema.yml',
    output: {
      mode: 'tags-split',
      target: './src/lib/api/',
      client: 'svelte-query'
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
};
