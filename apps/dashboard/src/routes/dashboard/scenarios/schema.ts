import { scenarioTypeEnum, stateEnum } from '$lib/server/db/schema/schema';
import { z } from 'zod/v4';

export const createScenarioSchema = z.object({
  name: z.string().min(2).max(255),
  description: z.string().max(1000).optional(),
  scenarioType: z.enum(scenarioTypeEnum.enumValues),
  stateOfResidence: z.enum(stateEnum.enumValues)
});

export type CreateScenarioSchema = typeof createScenarioSchema;
