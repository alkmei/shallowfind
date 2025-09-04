import { z } from 'zod/v4';
import {
  eventSeriesTypeEnum,
  investmentTaxabilityEnum,
  scenarioTypeEnum,
  startTimingTypeEnum,
  stateEnum
} from '$lib/server/db/schema/schema';
import { ref } from 'process';

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

// FIXME: Need to pass decimals as strings to avoid precision loss

export const basicInformationSchema = z.object({
  title: z.string().min(2).max(255),
  description: z.string().max(1000),
  stateOfResidence: z.enum(stateEnum.enumValues)
});

export const demographicsSchema = z.discriminatedUnion('scenarioType', [
  z.object({
    scenarioType: z.literal('individual'),
    userBirthYear: z.number().int().min(1900).max(new Date().getFullYear()),
    userLifeExpectancy: distributionSchema,
    spouseBirthYear: z.undefined(),
    spouseLifeExpectancy: z.undefined()
  }),
  z.object({
    scenarioType: z.literal('married_couple'),
    userBirthYear: z.number().int().min(1900).max(new Date().getFullYear()),
    spouseBirthYear: z.number().int().min(1900).max(new Date().getFullYear()),
    userLifeExpectancy: distributionSchema,
    spouseLifeExpectancy: distributionSchema
  })
]);

export const financialSettingsSchema = z.object({
  financialGoal: z.number().min(0),
  inflationAssumption: z.number().min(0),
  annualRetirementContributionLimit: z.number().min(0),
  roth: z
    .discriminatedUnion('enabled', [
      z.object({
        enabled: z.literal(false)
      }),
      z.object({
        enabled: z.literal(true),
        startYear: z.number().int().min(1900).max(new Date().getFullYear()).optional(),
        endYear: z.number().int().min(1900).max(new Date().getFullYear()).optional()
      })
    ])
    .optional()
});

export const investmentTypeSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().max(1000).optional(),
  expectedAnnualReturn: distributionSchema,
  expectedAnnualIncome: distributionSchema,
  expenseRatio: z.number(),
  taxability: z.enum(investmentTaxabilityEnum.enumValues),
  isCash: z.boolean()
});

export const investmentSchema = z.object({
  name: z.string().min(1).max(255),
  currentValue: z.number().min(0)
});

export const eventSeries = z.object({
  name: z.string().min(1).max(255),
  description: z.string().max(1000).optional(),
  type: z.enum(eventSeriesTypeEnum.enumValues),

  startYear: distributionSchema,
  duration: distributionSchema,
  startTimingType: z.enum(startTimingTypeEnum.enumValues),
  referenceEventSeriesId: z.string().uuid().optional()
});
