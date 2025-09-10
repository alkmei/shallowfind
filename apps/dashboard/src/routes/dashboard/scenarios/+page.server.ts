import { fail, superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { Actions, PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { createScenarioSchema, YAMLScenarioSchema, type YAMLScenarioType } from './schema';
import { db } from '$lib/server/db';
import { eq } from 'drizzle-orm';
import {
  eventSeries,
  investment,
  investmentType,
  scenario,
  strategy
} from '$lib/server/db/schema/schema';
import { parse as parseYaml } from 'yaml';

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
  create: async (event) => {
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
      // Read and parse YAML file
      const yamlContent = await file.text();
      const parsedYaml = parseYaml(yamlContent);

      // Validate against Zod schema
      const validationResult = YAMLScenarioSchema.safeParse(parsedYaml);

      if (!validationResult.success) {
        const errors = validationResult.error.issues.map((issue) => ({
          path: issue.path.join('.'),
          message: issue.message
        }));

        return fail(400, {
          message: 'Invalid YAML format',
          errors,
          details: 'Please check the file format and try again.'
        });
      }

      const scenarioData: YAMLScenarioType = validationResult.data;

      // Start database transaction
      const result = await db.transaction(async (tx) => {
        // 1. Create the scenario record
        const [newScenario] = await tx
          .insert(scenario)
          .values({
            // @ts-expect-error IDE error
            userId: user.id,
            title: scenarioData.name,
            description: scenarioData.name, // Using name as description since YAML doesn't have separate description
            scenarioType: scenarioData.maritalStatus === 'couple' ? 'married_couple' : 'individual',
            scenarioStatus: 'draft',
            userBirthYear: scenarioData.birthYears[0],
            spouseBirthYear: scenarioData.birthYears[1] || null,
            userLifeExpectancy: scenarioData.lifeExpectancy[0],
            spouseLifeExpectancy: scenarioData.lifeExpectancy[1] || null,
            financialGoal: scenarioData.financialGoal.toString(),
            stateOfResidence: scenarioData.residenceState.toUpperCase(), // Cast to match enum
            inflationAssumption: scenarioData.inflationAssumption,
            annualRetirementContributionLimit: scenarioData.afterTaxContributionLimit.toString(),
            rothOptimizerEnabled: scenarioData.RothConversionOpt,
            rothOptimizerStartYear: scenarioData.RothConversionStart || null,
            rothOptimizerEndYear: scenarioData.RothConversionEnd || null
          })
          .returning();

        // 2. Create investment types
        const investmentTypeMap = new Map<string, string>(); // name -> id mapping

        for (const invType of scenarioData.investmentTypes) {
          const [newInvestmentType] = await tx
            .insert(investmentType)
            .values({
              // @ts-expect-error IDE error
              scenarioId: newScenario.id,
              name: invType.name,
              description: invType.description,
              expectedAnnualReturn: invType.returnDistribution,
              returnPercent: invType.returnAmtOrPct === 'percent',
              expenseRatio: invType.expenseRatio.toString(),
              expectedAnnualIncome: invType.incomeDistribution,
              incomePercent: invType.incomeAmtOrPct === 'percent',
              taxability: invType.taxability ? 'taxable' : 'tax_exempt',
              isCash: invType.name === 'cash'
            })
            .returning();

          investmentTypeMap.set(invType.name, newInvestmentType.id);
        }

        // 3. Create investments
        const investmentMap = new Map<string, string>(); // yaml id -> db id mapping

        for (const inv of scenarioData.investments) {
          const investmentTypeId = investmentTypeMap.get(inv.investmentType);
          if (!investmentTypeId) {
            throw new Error(`Investment type ${inv.investmentType} not found`);
          }

          const [newInvestment] = await tx
            .insert(investment)
            .values({
              scenarioId: newScenario.id,
              investmentTypeId,
              name: inv.id, // Using YAML id as name
              currentValue: inv.value.toString(),
              accountTaxStatus:
                inv.taxStatus === 'non-retirement'
                  ? 'non_retirement'
                  : inv.taxStatus === 'pre-tax'
                    ? 'pre_tax_retirement'
                    : 'after_tax_retirement'
            })
            .returning();

          investmentMap.set(inv.id, newInvestment.id);
        }

        // 4. Create event series
        const eventSeriesMap = new Map<string, string>(); // name -> id mapping

        // First pass: create all event series without references
        for (let i = 0; i < scenarioData.eventSeries.length; i++) {
          const es = scenarioData.eventSeries[i];

          const [newEventSeries] = await tx
            .insert(eventSeries)
            .values({
              // @ts-expect-error IDE error
              scenarioId: newScenario.id,
              name: es.name,
              description: es.name, // Using name as description
              type: es.type,
              startYear: typeof es.start === 'object' && 'value' in es.start ? es.start : null,
              duration: es.duration,
              referenceEventSeriesId: null, // Will update in second pass
              startTimingType:
                typeof es.start === 'object' && 'type' in es.start
                  ? es.start.type === 'startWith'
                    ? 'same_year'
                    : es.start.type === 'startAfter'
                      ? 'year_after'
                      : 'distribution'
                  : null,
              isActive: true,
              orderIndex: i,

              // Income/Expense fields
              initialAmount: 'initialAmount' in es ? es.initialAmount?.toString() : null,
              annualChange: 'changeDistribution' in es ? es.changeDistribution : null,
              inflationAdjusted: 'inflationAdjusted' in es ? es.inflationAdjusted : null,
              userPercentage: 'userFraction' in es ? es.userFraction?.toString() : null,
              isSocialSecurity: 'socialSecurity' in es ? es.socialSecurity : false,
              isDiscretionary: 'discretionary' in es ? es.discretionary : false,

              // Invest/Rebalance fields
              assetAllocation:
                'assetAllocation' in es
                  ? // Convert investment IDs to database IDs
                    Object.fromEntries(
                      Object.entries(es.assetAllocation).map(([invId, percentage]) => [
                        investmentMap.get(invId) || invId,
                        percentage
                      ])
                    )
                  : null,
              isGlidePath: 'glidePath' in es ? es.glidePath : false,
              initialAllocation:
                'assetAllocation' in es
                  ? Object.fromEntries(
                      Object.entries(es.assetAllocation).map(([invId, percentage]) => [
                        investmentMap.get(invId) || invId,
                        percentage
                      ])
                    )
                  : null,
              finalAllocation:
                'assetAllocation2' in es && es.assetAllocation2
                  ? Object.fromEntries(
                      Object.entries(es.assetAllocation2).map(([invId, percentage]) => [
                        investmentMap.get(invId) || invId,
                        percentage
                      ])
                    )
                  : null,
              maximumCash: 'maxCash' in es ? es.maxCash?.toString() : null,
              targetTaxStatus: es.type === 'rebalance' ? 'non_retirement' : null // Default for rebalance
            })
            .returning();

          eventSeriesMap.set(es.name, newEventSeries.id);
        }

        // Second pass: update event series references
        for (const es of scenarioData.eventSeries) {
          if (typeof es.start === 'object' && 'eventSeries' in es.start) {
            const referenceId = eventSeriesMap.get(es.start.eventSeries);
            const currentId = eventSeriesMap.get(es.name);

            if (referenceId && currentId) {
              await tx
                .update(eventSeries)
                .set({ referenceEventSeriesId: referenceId })
                .where(eq(eventSeries.id, currentId));
            }
          }
        }

        // 5. Create strategies
        const strategies = [
          {
            type: 'spending' as const,
            name: 'Spending Strategy',
            description: 'Order of discretionary expenses',
            ordering: scenarioData.spendingStrategy
          },
          {
            type: 'expense_withdrawal' as const,
            name: 'Expense Withdrawal Strategy',
            description: 'Order of investments to sell for expenses',
            ordering: scenarioData.expenseWithdrawalStrategy.map(
              (invId) => investmentMap.get(invId) || invId
            )
          },
          {
            type: 'rmd' as const,
            name: 'RMD Strategy',
            description: 'Order of pre-tax investments for RMD',
            ordering: scenarioData.RMDStrategy.map((invId) => investmentMap.get(invId) || invId)
          }
        ];

        // Add Roth conversion strategy if enabled
        if (scenarioData.RothConversionOpt && scenarioData.RothConversionStrategy) {
          strategies.push({
            // @ts-expect-error IDE error
            type: 'roth_conversion' as const,
            name: 'Roth Conversion Strategy',
            description: 'Order of pre-tax investments for Roth conversion',
            ordering: scenarioData.RothConversionStrategy.map(
              (invId) => investmentMap.get(invId) || invId
            )
          });
        }

        for (const strat of strategies) {
          await tx.insert(strategy).values({
            scenarioId: newScenario.id,
            type: strat.type,
            name: strat.name,
            description: strat.description,
            isActive: true,
            ordering: strat.ordering
          });
        }

        return newScenario;
      });

      return {
        success: true,
        scenarioId: result.id,
        message: 'Scenario imported successfully'
      };
    } catch (error) {
      console.error('Error importing scenario:', error);

      if (error instanceof Error) {
        if (error.message.includes('YAML')) {
          return fail(400, {
            message: 'Invalid YAML format',
            details: error.message
          });
        }

        return fail(500, {
          message: 'Failed to import scenario',
          details: error.message
        });
      }

      return fail(500, {
        message: 'An unexpected error occurred while importing the scenario'
      });
    }
  }
};
