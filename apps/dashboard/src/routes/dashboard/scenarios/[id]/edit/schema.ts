import { z } from 'zod/v4';
import { scenarioTypeEnum, stateEnum } from '$lib/server/db/schema/schema';

const distributionSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('fixed'),
    value: z.number().min(0)
  }),
  z.object({
    type: z.literal('normal'),
    mean: z.number().min(0),
    stdev: z.number().min(0)
  }),
  z.object({
    type: z.literal('uniform'),
    lower: z.number().min(0),
    upper: z.number().min(0)
  })
]);

// Everything is optional
const updateScenarioSchema = z.object({
  title: z.string().min(2).max(255).optional(),
  description: z.string().max(1000).optional(),
  scenarioType: z.enum(scenarioTypeEnum.enumValues).optional(),
  userBirthYear: z.number().int().min(1900).max(new Date().getFullYear()).optional(),
  spouseBirthYear: z.number().int().min(1900).max(new Date().getFullYear()).optional(),
  userLifeExpectancy: distributionSchema.optional(),
  spouseLifeExpectancy: distributionSchema.optional(),
  financialGoal: z.number().min(0).optional(),
  stateOfResidence: z.enum(stateEnum.enumValues).optional(),
  inflationAssumption: distributionSchema.optional(),
  annualRetirementContributionLimit: z.number().min(0).optional(),
  rothOptimizerEnabled: z.boolean().optional(),
  rothOptimizerStartYear: z.number().int().min(new Date().getFullYear()).optional(),
  rothOptimizerEndYear: z.number().int().min(new Date().getFullYear()).optional()
});
