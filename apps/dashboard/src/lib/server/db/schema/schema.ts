import {
  varchar,
  text,
  timestamp,
  integer,
  jsonb,
  decimal,
  boolean,
  type AnyPgColumn,
  uuid,
  pgEnum,
  pgTable
} from 'drizzle-orm/pg-core';
import { user } from './auth-schema';

interface NormalDistribution {
  type: 'normal';
  mean: number;
  stdev: number;
}

interface FixedDistribution {
  type: 'fixed';
  value: number;
}

interface UniformDistribution {
  type: 'uniform';
  min: number;
  max: number;
}

type Distribution = NormalDistribution | FixedDistribution | UniformDistribution;

// prettier-ignore
export const stateEnum = pgEnum('state', [
	'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
	'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
	'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
	'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
	'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]);

export const scenarioTypeEnum = pgEnum('scenario_type', ['individual', 'married_couple']);
export const scenarioStatusEnum = pgEnum('scenario_status', ['draft', 'active', 'archived']);
export const accountTaxStatusEnum = pgEnum('account_tax_status', [
  'non_retirement',
  'pre_tax_retirement',
  'after_tax_retirement'
]);
export const investmentTaxabilityEnum = pgEnum('investment_taxability', ['taxable', 'tax_exempt']);
export const eventSeriesTypeEnum = pgEnum('event_series_type', [
  'income',
  'expense',
  'invest',
  'rebalance'
]);
export const strategyTypeEnum = pgEnum('strategy_type', [
  'spending',
  'expense_withdrawal',
  'rmd',
  'roth_conversion'
]);
export const sharePermissionEnum = pgEnum('share_permission', ['ro', 'rw']);

// For event series timing
export const startTimingTypeEnum = pgEnum('start_timing_type', [
  'same_year',
  'year_after',
  'distribution'
]);

export const scenario = pgTable('scenario', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: text('user_id')
    .notNull()
    .references(() => user.id, { onDelete: 'cascade' }),
  title: varchar('title', { length: 255 }).notNull(),
  description: text('description').notNull(),
  scenarioType: scenarioTypeEnum('scenario_type').notNull(),
  scenarioStatus: scenarioStatusEnum('scenario_status').notNull().default('draft'),

  // Personal information
  userBirthYear: integer('user_birth_year'),
  spouseBirthYear: integer('spouse_birth_year'),
  userLifeExpectancy: jsonb('user_life_expectancy').$type<Distribution>(),
  spouseLifeExpectancy: jsonb('spouse_life_expectancy').$type<Distribution>(),

  // Financial settings
  financialGoal: decimal('financial_goal'),
  stateOfResidence: stateEnum('state_of_residence').notNull(),
  inflationAssumption: jsonb('inflation_assumption').$type<Distribution>(),
  annualRetirementContributionLimit: decimal('annual_retirement_contribution_limit'),

  // Roth optimization
  rothOptimizerEnabled: boolean('roth_optimizer_enabled').notNull().default(false),
  rothOptimizerStartYear: integer('roth_optimizer_start_year'),
  rothOptimizerEndYear: integer('roth_optimizer_end_year'),

  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow()
});

export const investmentType = pgTable('investment_type', {
  id: uuid('id').primaryKey(),
  scenarioId: uuid('scenario_id')
    .references(() => scenario.id)
    .notNull(),

  name: varchar('name', { length: 255 }).notNull(),
  description: text('description').notNull(),
  expectedAnnualReturn: jsonb('expected_annual_return').$type<Distribution>().notNull(),
  expenseRatio: decimal('expense_ratio').notNull(), // Fixed percentage
  expectedAnnualIncome: jsonb('expected_annual_income').$type<Distribution>().notNull(),
  taxability: investmentTaxabilityEnum('taxability').notNull(),
  isCash: boolean('is_cash').notNull().default(false)
});

export const investment = pgTable('investment', {
  id: uuid('id').primaryKey(),
  scenarioId: uuid('scenario_id')
    .references(() => scenario.id)
    .notNull(),
  investmentTypeId: uuid('investment_type_id')
    .references(() => investmentType.id)
    .notNull(),

  name: varchar('name', { length: 255 }).notNull(),
  currentValue: decimal('current_value').notNull().default(0),
  accountTaxStatus: accountTaxStatusEnum('account_tax_status').notNull(),

  orderIndex: integer('order_index').notNull()
});

export const eventSeries = pgTable('event_series', {
  id: uuid('id').primaryKey(),
  scenarioId: uuid('scenario_id')
    .references(() => scenario.id)
    .notNull(),
  name: varchar('name', { length: 255 }).notNull(),
  description: text('description').notNull(),
  type: eventSeriesTypeEnum('type').notNull(),

  // Timing
  startYear: jsonb('start_year').$type<Distribution>(),
  duration: jsonb('duration').$type<Distribution>(),
  referenceEventSeriesId: uuid('reference_event_series_id').references(
    (): AnyPgColumn => eventSeries.id
  ),
  startTimingType: startTimingTypeEnum('start_timing_type'),

  isActive: boolean('is_active').notNull().default(true),
  orderIndex: integer('order_index').notNull(),

  // Income/Expense fields
  initialAmount: decimal('initial_amount'),
  annualChange: jsonb('annual_change').$type<Distribution>(),
  inflationAdjusted: boolean('inflation_adjusted').default(false),
  userPercentage: decimal('user_percentage'), // For married couples
  isSocialSecurity: boolean('is_social_security').default(false), // For income event
  isDiscretionary: boolean('is_discretionary').default(false), // For expense event

  // Invest/Rebalance fields
  assetAllocation: jsonb('asset_allocation').$type<Record<number, number>>(), // Percentage per investment type ID
  isGlidePath: boolean('is_glide_path').default(false),
  initialAllocation: jsonb('initial_allocation').$type<Record<number, number>>(), // For glide path
  finalAllocation: jsonb('final_allocation').$type<Record<number, number>>(), // For glide path
  maximumCash: decimal('maximum_cash'), // For invest events
  targetTaxStatus: accountTaxStatusEnum('target_tax_status') // For rebalance events
});

export const strategy = pgTable('strategy', {
  id: uuid('id').primaryKey(),
  scenarioId: uuid('scenario_id')
    .references(() => scenario.id)
    .notNull(),

  type: strategyTypeEnum('type').notNull(),

  name: varchar('name', { length: 255 }).notNull(),
  description: text('description').notNull(),
  isActive: boolean('is_active').notNull().default(true),

  // Ordering configuration - JSONField containing ordered list of investment IDs
  // or event series IDs depending on strategy type
  ordering: jsonb('ordering').$type<number[]>()
});

export const scenarioSharing = pgTable('scenario_sharing', {
  id: uuid('id').primaryKey(),
  scenarioId: uuid('scenario_id')
    .references(() => scenario.id)
    .notNull(),

  sharedWithUserId: text('shared_with_user_id').notNull(),
  permission: sharePermissionEnum('permission').notNull()
});
