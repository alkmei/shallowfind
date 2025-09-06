import { z } from 'zod/v4';
import {
  ACCOUNT_TAX_STATUS_VALUES,
  INVESTMENT_TAXABILITY_VALUES,
  SCENARIO_TYPE_VALUES,
  SHARE_PERMISSION_VALUES,
  START_TIMING_TYPE_VALUES,
  STATE_VALUES,
  STRATEGY_TYPE_VALUES
} from '$lib/enums';

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
    min: z.number().min(0),
    max: z.number().min(0)
  })
]);

const nonNegativeDecimalRegex = /^\d+(\.\d{1,4})?$/;

// Main scenario form schema (single page)
export const scenarioFormSchema = z
  .object({
    // Basic Information
    title: z.string().min(2).max(255),
    description: z.string().max(1000),
    stateOfResidence: z.enum(STATE_VALUES),

    // Demographics
    scenarioType: z.enum(SCENARIO_TYPE_VALUES),
    userBirthYear: z.number().int().min(1900).max(new Date().getFullYear()),
    spouseBirthYear: z.number().int().min(1900).max(new Date().getFullYear()).optional(),
    userLifeExpectancy: distributionSchema,
    spouseLifeExpectancy: distributionSchema.optional(),

    // Financial Settings
    financialGoal: z.string().regex(nonNegativeDecimalRegex),
    inflationAssumption: distributionSchema,
    annualRetirementContributionLimit: z.string().regex(nonNegativeDecimalRegex),

    // Roth Optimizer Settings
    rothOptimizerEnabled: z.boolean().default(false),
    rothOptimizerStartYear: z.number().int().min(1900).optional(),
    rothOptimizerEndYear: z.number().int().min(1900).optional(),

    // Sharing Settings
    shares: z
      .array(
        z.object({
          sharedWithUserId: z.string().min(1),
          permission: z.enum(SHARE_PERMISSION_VALUES)
        })
      )
      .default([])
  })
  .refine(
    (data) => {
      // For married couples, spouse birth year and life expectancy are required
      if (data.scenarioType === 'married_couple') {
        return data.spouseBirthYear !== undefined && data.spouseLifeExpectancy !== undefined;
      }
      return true;
    },
    {
      message: 'Spouse information is required for married couple scenarios',
      path: ['spouseBirthYear']
    }
  )
  .refine(
    (data) => {
      // If Roth optimizer is enabled, start and end years are required
      if (data.rothOptimizerEnabled) {
        return data.rothOptimizerStartYear !== undefined && data.rothOptimizerEndYear !== undefined;
      }
      return true;
    },
    {
      message: 'Start and end years are required when Roth optimizer is enabled',
      path: ['rothOptimizerStartYear']
    }
  )
  .refine(
    (data) => {
      // End year must be after or equal to start year
      if (data.rothOptimizerStartYear && data.rothOptimizerEndYear) {
        return data.rothOptimizerEndYear >= data.rothOptimizerStartYear;
      }
      return true;
    },
    {
      message: 'End year must be after or equal to start year',
      path: ['rothOptimizerEndYear']
    }
  )
  .refine(
    (data) => {
      // Ensure no duplicate user shares
      const userIds = data.shares.map((share) => share.sharedWithUserId);
      return userIds.length === new Set(userIds).size;
    },
    {
      message: 'Cannot share with the same user multiple times',
      path: ['shares']
    }
  );

// Separate schemas for the complex models that will be handled independently

// Investment Types (separate form/API)
export const investmentTypeSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().max(1000).default(''),
  expectedAnnualReturn: distributionSchema,
  expectedAnnualIncome: distributionSchema,
  expenseRatio: z.number().min(0).max(1), // Percentage as decimal
  taxability: z.enum(INVESTMENT_TAXABILITY_VALUES),
  isCash: z.boolean().default(false)
});

export const investmentTypesSchema = z
  .object({
    scenarioId: z.string().uuid(),
    investmentTypes: z
      .array(investmentTypeSchema)
      .min(1, 'At least one investment type is required')
  })
  .refine(
    (data) => {
      // Ensure there's exactly one cash investment type
      const cashTypes = data.investmentTypes.filter((type) => type.isCash);
      return cashTypes.length === 1;
    },
    {
      message: 'Exactly one investment type must be marked as cash',
      path: ['investmentTypes']
    }
  )
  .refine(
    (data) => {
      // Tax-exempt investments should not be marked as cash
      const taxExemptCash = data.investmentTypes.some(
        (type) => type.isCash && type.taxability === 'tax_exempt'
      );
      return !taxExemptCash;
    },
    {
      message: 'Cash investment type cannot be tax-exempt',
      path: ['investmentTypes']
    }
  );

// Investments (separate form/API)
export const investmentSchema = z.object({
  name: z.string().min(1).max(255),
  investmentTypeId: z.uuid(),
  currentValue: z.number().min(0),
  accountTaxStatus: z.enum(ACCOUNT_TAX_STATUS_VALUES),
  orderIndex: z.number().int().min(0).default(0)
});

export const investmentsSchema = z.object({
  scenarioId: z.uuid(),
  investments: z.array(investmentSchema).min(1, 'At least one investment is required')
});

// Event Series (separate form/API)
const baseEventSeriesSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().max(1000).default(''),
  isActive: z.boolean().default(true),
  orderIndex: z.number().int().min(0).default(0),

  // Timing fields
  startYear: distributionSchema.optional(),
  duration: distributionSchema,
  startTimingType: z.enum(START_TIMING_TYPE_VALUES).default('distribution'),
  referenceEventSeriesId: z.uuid().optional()
});

const incomeEventSeriesSchema = baseEventSeriesSchema.extend({
  type: z.literal('income'),
  initialAmount: z.number().min(0),
  annualChange: distributionSchema.default({ type: 'fixed', value: 0 }),
  inflationAdjusted: z.boolean().default(false),
  userPercentage: z.number().min(0).max(100).optional(),
  isSocialSecurity: z.boolean().default(false)
});

const expenseEventSeriesSchema = baseEventSeriesSchema.extend({
  type: z.literal('expense'),
  initialAmount: z.number().min(0),
  annualChange: distributionSchema.default({ type: 'fixed', value: 0 }),
  inflationAdjusted: z.boolean().default(false),
  userPercentage: z.number().min(0).max(100).optional(),
  isDiscretionary: z.boolean().default(false)
});

const investEventSeriesSchema = baseEventSeriesSchema.extend({
  type: z.literal('invest'),
  assetAllocation: z.record(z.string(), z.number().min(0).max(100)),
  isGlidePath: z.boolean().default(false),
  initialAllocation: z.record(z.string(), z.number().min(0).max(100)).optional(),
  finalAllocation: z.record(z.string(), z.number().min(0).max(100)).optional(),
  maximumCash: z.number().min(0)
});

const rebalanceEventSeriesSchema = baseEventSeriesSchema.extend({
  type: z.literal('rebalance'),
  assetAllocation: z.record(z.string(), z.number().min(0).max(100)),
  isGlidePath: z.boolean().default(false),
  initialAllocation: z.record(z.string(), z.number().min(0).max(100)).optional(),
  finalAllocation: z.record(z.string(), z.number().min(0).max(100)).optional(),
  targetTaxStatus: z.enum(ACCOUNT_TAX_STATUS_VALUES)
});

const eventSeriesSchema = z.discriminatedUnion('type', [
  incomeEventSeriesSchema,
  expenseEventSeriesSchema,
  investEventSeriesSchema,
  rebalanceEventSeriesSchema
]);

export const eventSeriesCreateSchema = z.object({
  scenarioId: z.uuid(),
  eventSeries: eventSeriesSchema
});

export const eventSeriesUpdateSchema = z.object({
  eventSeriesId: z.uuid(),
  eventSeries: eventSeriesSchema
});

// Strategies (separate form/API)
export const strategySchema = z.object({
  type: z.enum(STRATEGY_TYPE_VALUES),
  name: z.string().min(1).max(255),
  description: z.string().max(1000).default(''),
  isActive: z.boolean().default(true),
  ordering: z.array(z.string().uuid()).min(1, 'Strategy must include at least one item')
});

export const strategyCreateSchema = z.object({
  scenarioId: z.uuid(),
  strategy: strategySchema
});

export const strategyUpdateSchema = z.object({
  strategyId: z.uuid(),
  strategy: strategySchema.partial()
});

// Type inference helpers
export type ScenarioForm = z.infer<typeof scenarioFormSchema>;
export type Distribution = z.infer<typeof distributionSchema>;
export type InvestmentType = z.infer<typeof investmentTypeSchema>;
export type InvestmentTypes = z.infer<typeof investmentTypesSchema>;
export type Investment = z.infer<typeof investmentSchema>;
export type Investments = z.infer<typeof investmentsSchema>;
export type EventSeries = z.infer<typeof eventSeriesSchema>;
export type EventSeriesCreate = z.infer<typeof eventSeriesCreateSchema>;
export type EventSeriesUpdate = z.infer<typeof eventSeriesUpdateSchema>;
export type Strategy = z.infer<typeof strategySchema>;
export type StrategyCreate = z.infer<typeof strategyCreateSchema>;
export type StrategyUpdate = z.infer<typeof strategyUpdateSchema>;

// Export the main schema for the single-page scenario form
export default scenarioFormSchema;
