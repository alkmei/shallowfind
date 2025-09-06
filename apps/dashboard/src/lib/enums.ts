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

export const STATE_MAPPING = {
  AL: { name: 'Alabama' },
  AK: { name: 'Alaska' },
  AZ: { name: 'Arizona' },
  AR: { name: 'Arkansas' },
  CA: { name: 'California' },
  CO: { name: 'Colorado' },
  CT: { name: 'Connecticut' },
  DE: { name: 'Delaware' },
  FL: { name: 'Florida' },
  GA: { name: 'Georgia' },
  HI: { name: 'Hawaii' },
  ID: { name: 'Idaho' },
  IL: { name: 'Illinois' },
  IN: { name: 'Indiana' },
  IA: { name: 'Iowa' },
  KS: { name: 'Kansas' },
  KY: { name: 'Kentucky' },
  LA: { name: 'Louisiana' },
  ME: { name: 'Maine' },
  MD: { name: 'Maryland' },
  MA: { name: 'Massachusetts' },
  MI: { name: 'Michigan' },
  MN: { name: 'Minnesota' },
  MS: { name: 'Mississippi' },
  MO: { name: 'Missouri' },
  MT: { name: 'Montana' },
  NE: { name: 'Nebraska' },
  NV: { name: 'Nevada' },
  NH: { name: 'New Hampshire' },
  NJ: { name: 'New Jersey' },
  NM: { name: 'New Mexico' },
  NY: { name: 'New York' },
  NC: { name: 'North Carolina' },
  ND: { name: 'North Dakota' },
  OH: { name: 'Ohio' },
  OK: { name: 'Oklahoma' },
  OR: { name: 'Oregon' },
  PA: { name: 'Pennsylvania' },
  RI: { name: 'Rhode Island' },
  SC: { name: 'South Carolina' },
  SD: { name: 'South Dakota' },
  TN: { name: 'Tennessee' },
  TX: { name: 'Texas' },
  UT: { name: 'Utah' },
  VT: { name: 'Vermont' },
  VA: { name: 'Virginia' },
  WA: { name: 'Washington' },
  WV: { name: 'West Virginia' },
  WI: { name: 'Wisconsin' },
  WY: { name: 'Wyoming' }
};
