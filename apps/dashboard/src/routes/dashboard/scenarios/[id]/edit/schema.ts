import { z } from 'zod/v4';
import {
  investmentTaxabilityEnum,
  startTimingTypeEnum,
  stateEnum,
  accountTaxStatusEnum,
  strategyTypeEnum,
  sharePermissionEnum
} from '$lib/server/db/schema/schema';

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

// Step 1: Basic Information
export const basicInformationSchema = z.object({
  title: z.string().min(2).max(255),
  description: z.string().max(1000),
  stateOfResidence: z.enum(stateEnum.enumValues)
});

// Step 2: Demographics
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

// Step 3: Financial Settings
export const financialSettingsSchema = z
  .object({
    financialGoal: z.number().min(0),
    inflationAssumption: distributionSchema,
    annualRetirementContributionLimit: z.number().min(0),
    rothOptimizerEnabled: z.boolean().default(false),
    rothOptimizerStartYear: z.number().int().min(1900).optional(),
    rothOptimizerEndYear: z.number().int().min(1900).optional()
  })
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
      // End year must be after start year
      if (data.rothOptimizerStartYear && data.rothOptimizerEndYear) {
        return data.rothOptimizerEndYear >= data.rothOptimizerStartYear;
      }
      return true;
    },
    {
      message: 'End year must be after or equal to start year',
      path: ['rothOptimizerEndYear']
    }
  );

// Step 4: Investment Types
export const investmentTypeSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().max(1000).default(''),
  expectedAnnualReturn: distributionSchema,
  expectedAnnualIncome: distributionSchema,
  expenseRatio: z.number().min(0).max(1), // Percentage as decimal
  taxability: z.enum(investmentTaxabilityEnum.enumValues),
  isCash: z.boolean().default(false)
});

export const investmentTypesSchema = z
  .object({
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

// Step 5: Investments
export const investmentSchema = z.object({
  name: z.string().min(1).max(255),
  investmentTypeId: z.uuid(),
  currentValue: z.number().min(0),
  accountTaxStatus: z.enum(accountTaxStatusEnum.enumValues)
});

export const investmentsSchema = z
  .object({
    investments: z.array(investmentSchema).min(1, 'At least one investment is required')
  })
  .refine(
    (data) => {
      // Ensure there's at least one cash investment in non-retirement account
      const cashInvestments = data.investments.filter(
        (inv) =>
          inv.accountTaxStatus === 'non_retirement' && inv.name.toLowerCase().includes('cash')
      );
      return cashInvestments.length >= 1;
    },
    {
      message: 'At least one cash investment in a non-retirement account is required',
      path: ['investments']
    }
  );

// Step 6: Event Series
const baseEventSeriesSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().max(1000).default(''),
  isActive: z.boolean().default(true),

  // Timing fields
  startYear: distributionSchema.optional(),
  duration: distributionSchema,
  startTimingType: z.enum(startTimingTypeEnum.enumValues).default('distribution'),
  referenceEventSeriesId: z.string().uuid().optional()
});

const incomeEventSeriesSchema = baseEventSeriesSchema.extend({
  type: z.literal('income'),
  initialAmount: z.number().min(0),
  annualChange: distributionSchema.default({ type: 'fixed', value: 0 }),
  inflationAdjusted: z.boolean().default(false),
  userPercentage: z.number().min(0).max(100).optional(), // For married couples
  isSocialSecurity: z.boolean().default(false)
});

const expenseEventSeriesSchema = baseEventSeriesSchema.extend({
  type: z.literal('expense'),
  initialAmount: z.number().min(0),
  annualChange: distributionSchema.default({ type: 'fixed', value: 0 }),
  inflationAdjusted: z.boolean().default(false),
  userPercentage: z.number().min(0).max(100).optional(), // For married couples
  isDiscretionary: z.boolean().default(false)
});

const investEventSeriesSchema = baseEventSeriesSchema.extend({
  type: z.literal('invest'),
  assetAllocation: z.record(z.string(), z.number().min(0).max(100)), // Investment ID -> percentage
  isGlidePath: z.boolean().default(false),
  initialAllocation: z.record(z.string(), z.number().min(0).max(100)).optional(),
  finalAllocation: z.record(z.string(), z.number().min(0).max(100)).optional(),
  maximumCash: z.number().min(0)
});

const rebalanceEventSeriesSchema = baseEventSeriesSchema.extend({
  type: z.literal('rebalance'),
  assetAllocation: z.record(z.string(), z.number().min(0).max(100)), // Investment ID -> percentage
  isGlidePath: z.boolean().default(false),
  initialAllocation: z.record(z.string(), z.number().min(0).max(100)).optional(),
  finalAllocation: z.record(z.string(), z.number().min(0).max(100)).optional(),
  targetTaxStatus: z.enum(accountTaxStatusEnum.enumValues)
});

const eventSeriesSchema = z.discriminatedUnion('type', [
  incomeEventSeriesSchema,
  expenseEventSeriesSchema,
  investEventSeriesSchema,
  rebalanceEventSeriesSchema
]);

export const eventSeriesListSchema = z
  .object({
    eventSeries: z.array(eventSeriesSchema).default([])
  })
  .refine(
    (data) => {
      // Validate asset allocation percentages sum to 100 for invest/rebalance events
      for (const event of data.eventSeries) {
        if (event.type === 'invest' || event.type === 'rebalance') {
          const totalPercentage = Object.values(event.assetAllocation).reduce(
            (sum, pct) => sum + pct,
            0
          );
          if (Math.abs(totalPercentage - 100) > 0.01) {
            return false;
          }

          // For glide path, validate initial and final allocations
          if (event.isGlidePath) {
            if (!event.initialAllocation || !event.finalAllocation) return false;

            const initialTotal = Object.values(event.initialAllocation).reduce(
              (sum, pct) => sum + pct,
              0
            );
            const finalTotal = Object.values(event.finalAllocation).reduce(
              (sum, pct) => sum + pct,
              0
            );

            if (Math.abs(initialTotal - 100) > 0.01 || Math.abs(finalTotal - 100) > 0.01) {
              return false;
            }
          }
        }
      }
      return true;
    },
    {
      message: 'Asset allocation percentages must sum to 100%',
      path: ['eventSeries']
    }
  )
  .refine(
    (data) => {
      // No overlapping invest event series
      const investEvents = data.eventSeries.filter((e) => e.type === 'invest');
      // FIXME: This would require more complex temporal overlap checking in practice
      return true;
    },
    {
      message: 'Invest event series cannot overlap temporally',
      path: ['eventSeries']
    }
  )
  .refine(
    (data) => {
      // Validate reference event series IDs exist
      const eventIds = new Set(data.eventSeries.map((_, index) => index.toString()));
      for (const event of data.eventSeries) {
        if (event.referenceEventSeriesId && !eventIds.has(event.referenceEventSeriesId)) {
          return false;
        }
      }
      return true;
    },
    {
      message: 'Referenced event series must exist',
      path: ['eventSeries']
    }
  );

// Step 7: Strategies
export const strategySchema = z.object({
  type: z.enum(strategyTypeEnum.enumValues),
  name: z.string().min(1).max(255),
  description: z.string().max(1000).default(''),
  isActive: z.boolean().default(true),
  ordering: z.array(z.string().uuid()).min(1, 'Strategy must include at least one item')
});

export const strategiesSchema = z
  .object({
    spendingStrategy: strategySchema.optional(),
    expenseWithdrawalStrategy: strategySchema,
    rmdStrategy: strategySchema,
    rothConversionStrategy: strategySchema.optional()
  })
  .refine(
    (data) => {
      // Validate strategy types match their intended use
      if (data.spendingStrategy && data.spendingStrategy.type !== 'spending') return false;
      if (data.expenseWithdrawalStrategy.type !== 'expense_withdrawal') return false;
      if (data.rmdStrategy.type !== 'rmd') return false;
      if (data.rothConversionStrategy && data.rothConversionStrategy.type !== 'roth_conversion')
        return false;

      return true;
    },
    {
      message: 'Strategy types must match their intended use',
      path: ['strategies']
    }
  );

// Step 8: Sharing Settings
export const sharingSchema = z
  .object({
    shares: z
      .array(
        z.object({
          sharedWithUserId: z.string().min(1),
          permission: z.enum(sharePermissionEnum.enumValues)
        })
      )
      .default([])
  })
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

// Complete scenario schema (for final validation or full scenario creation)
export const completeScenarioSchema = z.object({
  basicInformation: basicInformationSchema,
  demographics: demographicsSchema,
  financialSettings: financialSettingsSchema,
  investmentTypes: investmentTypesSchema,
  investments: investmentsSchema,
  eventSeries: eventSeriesListSchema,
  strategies: strategiesSchema,
  sharing: sharingSchema
});

// Export individual step schemas for form validation
export const stepSchemas = {
  1: basicInformationSchema,
  2: demographicsSchema,
  3: financialSettingsSchema,
  4: investmentTypesSchema,
  5: investmentsSchema,
  6: eventSeriesListSchema,
  7: strategiesSchema,
  8: sharingSchema
} as const;

// Type inference helpers
export type BasicInformation = z.infer<typeof basicInformationSchema>;
export type Demographics = z.infer<typeof demographicsSchema>;
export type FinancialSettings = z.infer<typeof financialSettingsSchema>;
export type InvestmentTypes = z.infer<typeof investmentTypesSchema>;
export type Investments = z.infer<typeof investmentsSchema>;
export type EventSeriesList = z.infer<typeof eventSeriesListSchema>;
export type Strategies = z.infer<typeof strategiesSchema>;
export type Sharing = z.infer<typeof sharingSchema>;
export type CompleteScenario = z.infer<typeof completeScenarioSchema>;
export type Distribution = z.infer<typeof distributionSchema>;
export type InvestmentType = z.infer<typeof investmentTypeSchema>;
export type Investment = z.infer<typeof investmentSchema>;
export type EventSeries = z.infer<typeof eventSeriesSchema>;
export type Strategy = z.infer<typeof strategySchema>;
