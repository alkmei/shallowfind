import { z } from 'zod/v4';

export const createScenarioSchema = z.object({
	name: z.string().min(2).max(255),
	description: z.string().max(1000).optional(),
	scenarioType: z.enum(['individual', 'married_couple'])
});

export type CreateScenarioSchema = typeof createScenarioSchema;
