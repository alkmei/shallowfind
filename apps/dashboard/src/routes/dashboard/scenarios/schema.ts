import { SCENARIO_TYPE_VALUES, STATE_VALUES } from '$lib/enums';
import { z } from 'zod/v4';

export const createScenarioSchema = z.object({
  name: z.string().min(2).max(255),
  description: z.string().max(1000).optional(),
  scenarioType: z.enum(SCENARIO_TYPE_VALUES),
  stateOfResidence: z.enum(STATE_VALUES)
});

export type CreateScenarioSchema = typeof createScenarioSchema;
