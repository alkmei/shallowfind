import { SCENARIO_TYPE_VALUES, STATE_VALUES } from '$lib/enums';
import { z } from 'zod/v4';

export const createScenarioSchema = z.object({
  name: z.string().min(2).max(255),
  description: z.string().max(1000).optional(),
  scenarioType: z.enum(SCENARIO_TYPE_VALUES),
  stateOfResidence: z.enum(STATE_VALUES)
});

export type CreateScenarioSchema = typeof createScenarioSchema;

// Below is for YAML file

// Distribution schemas
const YAMLFixedDistribution = z.object({
  type: z.literal('fixed'),
  value: z.number()
});

const YAMLNormalDistribution = z.object({
  type: z.literal('normal'),
  mean: z.number(),
  stdev: z.number().positive()
});

const YAMLUniformDistribution = z.object({
  type: z.literal('uniform'),
  lower: z.number(),
  upper: z.number()
});

const YAMLDistribution = z.union([
  YAMLFixedDistribution,
  YAMLNormalDistribution,
  YAMLUniformDistribution
]);

// Event series start references
const YAMLStartWithEventSeries = z.object({
  type: z.literal('startWith'),
  eventSeries: z.string()
});

const YAMLStartAfterEventSeries = z.object({
  type: z.literal('startAfter'),
  eventSeries: z.string()
});

const YAMLEventSeriesStart = z.union([
  YAMLDistribution,
  YAMLStartWithEventSeries,
  YAMLStartAfterEventSeries
]);

// Investment Type schema
const YAMLInvestmentType = z.object({
  name: z.string().min(1),
  description: z.string(),
  returnAmtOrPct: z.enum(['amount', 'percent']),
  returnDistribution: YAMLDistribution,
  expenseRatio: z.number().min(0).max(1), // Should be between 0 and 100% (as decimal)
  incomeAmtOrPct: z.enum(['amount', 'percent']),
  incomeDistribution: YAMLDistribution,
  taxability: z.boolean()
});

// Investment schema
const YAMLInvestment = z.object({
  investmentType: z.string().min(1),
  value: z.number().nonnegative(),
  taxStatus: z.enum(['non-retirement', 'pre-tax', 'after-tax']),
  id: z.string().min(1)
});

// Base event series fields
const YAMLBaseEventSeries = z.object({
  name: z.string().min(1),
  start: YAMLEventSeriesStart,
  duration: YAMLDistribution,
  type: z.enum(['income', 'expense', 'invest', 'rebalance'])
});

// Income/Expense event series fields
const YAMLIncomeExpenseFields = z.object({
  initialAmount: z.number().nonnegative(),
  changeAmtOrPct: z.enum(['amount', 'percent']),
  changeDistribution: YAMLDistribution,
  inflationAdjusted: z.boolean(),
  userFraction: z.number().min(0).max(1)
});

// Income-specific fields
const YAMLIncomeFields = z.object({
  socialSecurity: z.boolean()
});

// Expense-specific fields
const YAMLExpenseFields = z.object({
  discretionary: z.boolean()
});

// Asset allocation schema (investment id to percentage mapping)
const YAMLAssetAllocation = z.record(z.string(), z.number().min(0).max(1));

// Invest event fields
const YAMLInvestFields = z.object({
  assetAllocation: YAMLAssetAllocation,
  glidePath: z.boolean(),
  assetAllocation2: YAMLAssetAllocation.optional(),
  maxCash: z.number().nonnegative()
});

// Rebalance event fields
const YAMLRebalanceFields = z.object({
  assetAllocation: YAMLAssetAllocation
});

// Event series schemas by type
const YAMLIncomeEventSeries = YAMLBaseEventSeries.extend(YAMLIncomeExpenseFields.shape)
  .extend(YAMLIncomeFields.shape)
  .extend({ type: z.literal('income') });

const YAMLExpenseEventSeries = YAMLBaseEventSeries.extend(YAMLIncomeExpenseFields.shape)
  .extend(YAMLExpenseFields.shape)
  .extend({ type: z.literal('expense') });

const YAMLInvestEventSeries = YAMLBaseEventSeries.extend(YAMLInvestFields.shape).extend({
  type: z.literal('invest')
});

const YAMLRebalanceEventSeries = YAMLBaseEventSeries.extend(YAMLRebalanceFields.shape).extend({
  type: z.literal('rebalance')
});

// Union of all event series types
const YAMLEventSeries = z.union([
  YAMLIncomeEventSeries,
  YAMLExpenseEventSeries,
  YAMLInvestEventSeries,
  YAMLRebalanceEventSeries
]);

// Main scenario schema
export const YAMLScenarioSchema = z.object({
  name: z.string().min(1),
  maritalStatus: z.enum(['couple', 'individual']),
  birthYears: z.array(z.number().int().min(1900).max(2100)).min(1).max(2),
  lifeExpectancy: z.array(YAMLDistribution).min(1).max(2),
  investmentTypes: z.array(YAMLInvestmentType).min(1),
  investments: z.array(YAMLInvestment).min(1),
  eventSeries: z.array(YAMLEventSeries),
  inflationAssumption: YAMLDistribution,
  afterTaxContributionLimit: z.number().nonnegative(),
  spendingStrategy: z.array(z.string()),
  expenseWithdrawalStrategy: z.array(z.string()).min(1),
  RMDStrategy: z.array(z.string()),
  RothConversionOpt: z.boolean(),
  RothConversionStart: z.number().int().optional(),
  RothConversionEnd: z.number().int().optional(),
  RothConversionStrategy: z.array(z.string()).optional(),
  financialGoal: z.number().nonnegative(),
  residenceState: z
    .string()
    .length(2)
    .regex(/^[A-Z]{2}$/)
});

// Export individual schemas for partial validation if needed
export {
  YAMLDistribution,
  YAMLInvestmentType,
  YAMLInvestment,
  YAMLEventSeries,
  YAMLIncomeEventSeries,
  YAMLExpenseEventSeries,
  YAMLInvestEventSeries,
  YAMLRebalanceEventSeries
};

// Type inference
export type YAMLScenarioType = z.infer<typeof YAMLScenarioSchema>;
export type YAMLDistributionType = z.infer<typeof YAMLDistribution>;
export type YAMLInvestmentTypeType = z.infer<typeof YAMLInvestmentType>;
export type YAMLInvestmentType = z.infer<typeof YAMLInvestment>;
export type YAMLEventSeriesType = z.infer<typeof YAMLEventSeries>;
