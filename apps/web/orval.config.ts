import { defineConfig } from 'orval';

export default defineConfig({
  scenario: {
    input: '../../services/scenario-manager/swagger.json',
    output: {
      mode: 'tags-split',
      target: './src/lib/api/scenario-management',
      baseUrl: 'http://localhost:5050',
      client: 'axios',
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
  scenarioZod: {
    input: '../../services/scenario-manager/swagger.json',
    output: {
      mode: 'tags-split',
      target: './src/lib/api/scenario-management',
      client: 'zod',
      fileExtension: '.zod.ts'
    }
  }
});
