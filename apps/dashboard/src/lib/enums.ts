// prettier-ignore
export const STATE_VALUES = [
	'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
	'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
	'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
	'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
	'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
] as const;

export type State = (typeof STATE_VALUES)[number];

export const SCENARIO_TYPE_VALUES = ['individual', 'married_couple'] as const;
export type ScenarioType = (typeof SCENARIO_TYPE_VALUES)[number];

export const SCENARIO_STATUS_VALUES = ['draft', 'active', 'archived'] as const;
export type ScenarioStatus = (typeof SCENARIO_STATUS_VALUES)[number];

export const ACCOUNT_TAX_STATUS_VALUES = [
  'non_retirement',
  'pre_tax_retirement',
  'after_tax_retirement'
] as const;
export type AccountTaxStatus = (typeof ACCOUNT_TAX_STATUS_VALUES)[number];

export const INVESTMENT_TAXABILITY_VALUES = ['taxable', 'tax_exempt'] as const;
export type InvestmentTaxability = (typeof INVESTMENT_TAXABILITY_VALUES)[number];

export const EVENT_SERIES_TYPE_VALUES = ['income', 'expense', 'invest', 'rebalance'] as const;
export type EventSeriesType = (typeof EVENT_SERIES_TYPE_VALUES)[number];

export const STRATEGY_TYPE_VALUES = [
  'spending',
  'expense_withdrawal',
  'rmd',
  'roth_conversion'
] as const;
export type StrategyType = (typeof STRATEGY_TYPE_VALUES)[number];

export const START_TIMING_TYPE_VALUES = [
  'same_year',
  'year_after',
  'event_series',
  'distribution'
] as const;
export type StartTimingType = (typeof START_TIMING_TYPE_VALUES)[number];

export const SHARE_PERMISSION_VALUES = ['ro', 'rw'] as const;
export type SharePermission = (typeof SHARE_PERMISSION_VALUES)[number];
