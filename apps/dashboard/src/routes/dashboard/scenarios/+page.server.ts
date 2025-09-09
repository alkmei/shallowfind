import { fail, superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { Actions, PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { createScenarioSchema } from './schema';
import { db } from '$lib/server/db';
import { eq } from 'drizzle-orm';
import {
  eventSeries,
  investment,
  investmentType,
  scenario,
  strategy,
  type Distribution,
  type EventSeries,
  type Investment,
  type InvestmentType,
  type Strategy
} from '$lib/server/db/schema/schema';
import * as YAML from 'yaml';

export const load: PageServerLoad = async (event) => {
  const user = event.locals.user;
  if (!user) {
    return fail(401, { message: 'Unauthorized' });
  }
  const scenarios = await db.select().from(scenario).where(eq(scenario.userId, user.id));
  return {
    form: await superValidate(zod4(createScenarioSchema)),
    scenarios: scenarios
  };
};

export const actions: Actions = {
  default: async (event) => {
    const form = await superValidate(event, zod4(createScenarioSchema));
    const user = event.locals.user;
    if (!user) {
      return fail(401, { message: 'Unauthorized' });
    }
    if (!form.valid) {
      return fail(400, {
        form
      });
    }

    const newScenario = await db
      .insert(scenario)
      .values({
        userId: user.id,
        title: form.data.name,
        description: form.data.description || '',
        scenarioType: form.data.scenarioType,
        stateOfResidence: form.data.stateOfResidence
      })
      .returning({ insertedId: scenario.id });

    redirect(303, `/dashboard/scenarios/${newScenario.at(0)?.insertedId}/edit`);
  },

  file: async (event) => {
    const user = event.locals.user;
    if (!user) {
      return fail(401, { message: 'Unauthorized' });
    }

    const formData = await event.request.formData();
    const file = formData.get('scenarioFile') as File | null;

    if (!file) {
      return fail(400, { message: 'No file uploaded' });
    }

    if (
      file.type !== 'application/x-yaml' &&
      !file.name.endsWith('.yaml') &&
      !file.name.endsWith('.yml')
    ) {
      return fail(400, { message: 'Invalid file type. Please upload a YAML file.' });
    }

    try {
      const text = await file.text();
      const yamlData = YAML.parse(text);

      // Start database transaction
      const result = await db.transaction(async (tx) => {
        // Create main scenario
        const scenarioData = {
          userId: user.id,
          title: yamlData.name,
          description: yamlData.description || '',
          scenarioType:
            yamlData.maritalStatus === 'couple'
              ? ('married_couple' as const)
              : ('individual' as const),
          stateOfResidence: yamlData.residenceState,
          userBirthYear: yamlData.birthYears[0],
          spouseBirthYear: yamlData.birthYears[1] || null,
          userLifeExpectancy: convertDistribution(yamlData.lifeExpectancy[0]),
          spouseLifeExpectancy: yamlData.lifeExpectancy[1]
            ? convertDistribution(yamlData.lifeExpectancy[1])
            : null,
          financialGoal: yamlData.financialGoal.toString(),
          inflationAssumption: convertDistribution(yamlData.inflationAssumption),
          annualRetirementContributionLimit: yamlData.afterTaxContributionLimit.toString(),
          rothOptimizerEnabled: yamlData.RothConversionOpt,
          rothOptimizerStartYear: yamlData.RothConversionStart,
          rothOptimizerEndYear: yamlData.RothConversionEnd
        };

        const [newScenario] = await tx.insert(scenario).values(scenarioData).returning();
        const scenarioId = newScenario.id;

        // Create investment types
        const investmentTypeMap = new Map<string, string>();
        for (const investmentTypeData of yamlData.investmentTypes) {
          const investmentTypeRecord: Omit<InvestmentType, 'id'> = {
            scenarioId,
            taxability:
              investmentTypeData.taxability === true
                ? 'taxable'
                : ('tax_exempt' as 'taxable' | 'tax_exempt'),
            name: investmentTypeData.name,
            description: investmentTypeData.description,
            expectedAnnualReturn: convertDistribution(investmentTypeData.returnDistribution),
            returnPercent: investmentTypeData.returnAmtOrPct === 'percent',
            expenseRatio: investmentTypeData.expenseRatio.toString(),
            expectedAnnualIncome: convertDistribution(investmentTypeData.incomeDistribution),
            incomePercent: investmentTypeData.incomeAmtOrPct === 'percent',
            isCash: investmentTypeData.name === 'cash'
          };

          const [insertedInvestmentType] = await tx
            .insert(investmentType)
            .values(investmentTypeRecord)
            .returning();

          investmentTypeMap.set(investmentTypeData.name, insertedInvestmentType.id);
        }

        // Create investments
        const investmentMap = new Map<string, string>();
        for (const investmentData of yamlData.investments) {
          const investmentTypeId = investmentTypeMap.get(investmentData.investmentType);
          if (!investmentTypeId) {
            throw new Error(`Investment type not found: ${investmentData.investmentType}`);
          }

          const taxStatus = convertTaxStatus(investmentData.taxStatus);
          const investmentRecord: Omit<Investment, 'id'> = {
            scenarioId,
            investmentTypeId,
            name: investmentData.id,
            currentValue: investmentData.value.toString(),
            accountTaxStatus: taxStatus
          };

          const [insertedInvestment] = await tx
            .insert(investment)
            .values(investmentRecord)
            .returning();

          investmentMap.set(investmentData.id, insertedInvestment.id);
        }

        // Create event series
        const eventSeriesMap = new Map<string, string>();
        for (const eventData of yamlData.eventSeries) {
          const eventRecord: Omit<EventSeries, 'id'> = {
            scenarioId,
            name: eventData.name,
            description: eventData.description || '',
            type: eventData.type,
            startYear: convertStartDistribution(eventData.start),
            duration: convertDistribution(eventData.duration),
            startTimingType: getStartTimingType(eventData.start) ?? 'distribution', // FIXME: CCheck this
            referenceEventSeriesId: getReferencedEventId(eventData.start, eventSeriesMap),
            isActive: true,
            orderIndex: 0,
            // Type-specific fields
            ...(eventData.type === 'income' || eventData.type === 'expense'
              ? {
                  initialAmount: eventData.initialAmount?.toString() || '0',
                  annualChange: convertChangeDistribution(eventData),
                  inflationAdjusted: eventData.inflationAdjusted || false,
                  userPercentage: eventData.userFraction
                    ? (eventData.userFraction * 100).toString()
                    : null,
                  isSocialSecurity: eventData.socialSecurity || false,
                  isDiscretionary: eventData.discretionary || false
                }
              : {}),
            ...(eventData.type === 'invest'
              ? {
                  assetAllocation: convertAssetAllocation(eventData.assetAllocation, investmentMap),
                  isGlidePath: eventData.glidePath || false,
                  initialAllocation: eventData.glidePath
                    ? convertAssetAllocation(eventData.assetAllocation, investmentMap)
                    : null,
                  finalAllocation: eventData.glidePath
                    ? convertAssetAllocation(eventData.assetAllocation2, investmentMap)
                    : null,
                  maximumCash: eventData.maxCash?.toString() || '0'
                }
              : {}),
            ...(eventData.type === 'rebalance'
              ? {
                  assetAllocation: convertAssetAllocation(eventData.assetAllocation, investmentMap),
                  isGlidePath: eventData.glidePath || false,
                  initialAllocation: eventData.glidePath
                    ? convertAssetAllocation(eventData.assetAllocation, investmentMap)
                    : null,
                  finalAllocation: eventData.glidePath
                    ? convertAssetAllocation(eventData.assetAllocation2, investmentMap)
                    : null,
                  targetTaxStatus: 'non_retirement' // Default, could be inferred from asset allocation
                }
              : {})
          };

          const [insertedEventSeries] = await tx
            .insert(eventSeries)
            .values(eventRecord)
            .returning();

          eventSeriesMap.set(eventData.name, insertedEventSeries.id);
        }

        // Create strategies
        if (yamlData.spendingStrategy) {
          const spendingStrategyRecord: Omit<Strategy, 'id'> = {
            scenarioId,
            type: 'spending',
            name: 'Spending Strategy',
            description: 'Imported spending strategy',
            isActive: true,
            ordering: yamlData.spendingStrategy
              .map(
                (name: string) => [...eventSeriesMap.entries()].find(([key]) => key === name)?.[1]
              )
              .filter(Boolean)
          };
          await tx.insert(strategy).values(spendingStrategyRecord);
        }

        if (yamlData.expenseWithdrawalStrategy) {
          const withdrawalStrategyRecord: Omit<Strategy, 'id'> = {
            scenarioId,
            type: 'expense_withdrawal',
            name: 'Expense Withdrawal Strategy',
            description: 'Imported expense withdrawal strategy',
            isActive: true,
            ordering: yamlData.expenseWithdrawalStrategy
              .map((id: string) => investmentMap.get(id))
              .filter(Boolean)
          };
          await tx.insert(strategy).values(withdrawalStrategyRecord);
        }

        if (yamlData.RMDStrategy) {
          const rmdStrategyRecord: Omit<Strategy, 'id'> = {
            scenarioId,
            type: 'rmd',
            name: 'RMD Strategy',
            description: 'Imported RMD strategy',
            isActive: true,
            ordering: yamlData.RMDStrategy.map((id: string) => investmentMap.get(id)).filter(
              Boolean
            )
          };
          await tx.insert(strategy).values(rmdStrategyRecord);
        }

        if (yamlData.RothConversionStrategy) {
          const rothStrategyRecord: Omit<Strategy, 'id'> = {
            scenarioId,
            type: 'roth_conversion',
            name: 'Roth Conversion Strategy',
            description: 'Imported Roth conversion strategy',
            isActive: true,
            ordering: yamlData.RothConversionStrategy.map((id: string) =>
              investmentMap.get(id)
            ).filter(Boolean)
          };
          await tx.insert(strategy).values(rothStrategyRecord);
        }

        return newScenario.id;
      });

      redirect(303, `/dashboard/scenarios/${result}/edit`);
    } catch (error) {
      console.error('Error importing scenario:', error);
      return fail(400, {
        message: `Failed to import scenario: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    }
  }
};

// Helper functions
function convertDistribution(dist: any): Distribution {
  if (dist.type === 'fixed') {
    return { type: 'fixed', value: dist.value };
  } else if (dist.type === 'normal') {
    return { type: 'normal', mean: dist.mean, stdev: dist.stdev };
  } else if (dist.type === 'uniform') {
    return { type: 'uniform', min: dist.lower, max: dist.upper };
  }
  throw new Error(`Unknown distribution type: ${dist.type}`);
}

function convertStartDistribution(start: any): Distribution | null {
  if (start.type === 'startWith' || start.type === 'startAfter') {
    return null; // These use reference event series instead
  }
  return convertDistribution(start);
}

function getStartTimingType(start: any): 'distribution' | 'same_year' | 'year_after' {
  if (start.type === 'startWith') return 'same_year';
  if (start.type === 'startAfter') return 'year_after';
  return 'distribution';
}

function getReferencedEventId(start: any, eventMap: Map<string, string>): string | null {
  if (start.type === 'startWith' || start.type === 'startAfter') {
    return eventMap.get(start.eventSeries) || null;
  }
  return null;
}

function convertChangeDistribution(eventData: any): Distribution {
  if (eventData.changeAmtOrPct === 'percent') {
    // Convert percentage change to decimal
    const dist = eventData.changeDistribution;
    if (dist.type === 'fixed') {
      return { type: 'fixed', value: dist.value };
    } else if (dist.type === 'normal') {
      return { type: 'normal', mean: dist.mean, stdev: dist.stdev };
    } else if (dist.type === 'uniform') {
      return { type: 'uniform', min: dist.lower, max: dist.upper };
    }
  }
  return convertDistribution(eventData.changeDistribution);
}

function convertTaxStatus(
  status: string
): 'non_retirement' | 'pre_tax_retirement' | 'after_tax_retirement' {
  switch (status) {
    case 'non-retirement':
      return 'non_retirement';
    case 'pre-tax':
      return 'pre_tax_retirement';
    case 'after-tax':
      return 'after_tax_retirement';
    default:
      return 'non_retirement';
  }
}

function convertAssetAllocation(
  allocation: Record<string, number>,
  investmentMap: Map<string, string>
): Record<string, number> {
  const result: Record<string, number> = {};
  for (const [investmentId, percentage] of Object.entries(allocation)) {
    const dbInvestmentId = investmentMap.get(investmentId);
    if (dbInvestmentId) {
      result[dbInvestmentId] = percentage * 100; // Convert to percentage
    }
  }
  return result;
}
