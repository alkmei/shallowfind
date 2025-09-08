import type { Actions, PageServerLoad } from './$types';
import { db } from '$lib/server/db';
import {
  scenario as scenarioSchema,
  type InvestmentType,
  investmentType,
  type Investment,
  investment,
  type EventSeries,
  eventSeries
} from '$lib/server/db/schema/schema';
import { eq } from 'drizzle-orm';
import { error, fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import scenarioFormSchema, {
  eventSeriesCreateSchema,
  investmentSchema,
  investmentTypeSchema,
  type ScenarioForm
} from './schema';

export const load: PageServerLoad = async ({ params }) => {
  const id = params.id;

  const scenario = await db.query.scenario.findFirst({
    where: eq(scenarioSchema.id, id),
    with: {
      investmentTypes: true,
      investments: true,
      eventSeries: true,
      strategies: true,
      sharedWith: true
    }
  });

  if (!scenario) {
    throw error(404, { message: 'Scenario not found' });
  }

  const isMarried = scenario.scenarioType === 'married_couple';

  const scenarioData: ScenarioForm = {
    title: scenario.title,
    description: scenario.description,
    stateOfResidence: scenario.stateOfResidence,
    scenarioType: scenario.scenarioType,
    userBirthYear: scenario.userBirthYear || new Date().getFullYear() - 25,
    spouseBirthYear:
      scenario.spouseBirthYear || (isMarried ? new Date().getFullYear() - 25 : undefined),
    userLifeExpectancy: scenario.userLifeExpectancy || { type: 'fixed', value: 85 },
    spouseLifeExpectancy:
      scenario.spouseLifeExpectancy || (isMarried ? { type: 'fixed', value: 85 } : undefined),
    financialGoal: scenario.financialGoal || '0',
    inflationAssumption: scenario.inflationAssumption || { type: 'fixed', value: 0.03 },
    annualRetirementContributionLimit: scenario.annualRetirementContributionLimit || '0',
    rothOptimizerEnabled: scenario.rothOptimizerEnabled || false,
    rothOptimizerStartYear: scenario.rothOptimizerStartYear || undefined,
    rothOptimizerEndYear: scenario.rothOptimizerEndYear || undefined,
    shares: []
  };

  return {
    form: await superValidate(scenarioData, zod4(scenarioFormSchema)),
    investmentTypeForm: await superValidate(
      { scenarioId: scenario.id },
      zod4(investmentTypeSchema)
    ),
    investmentForm: await superValidate({ scenarioId: scenario.id }, zod4(investmentSchema)),
    eventSeriesForm: await superValidate(
      {
        scenarioId: scenario.id,
        eventSeries: {
          name: '',
          description: '',
          type: 'income' as const,
          startYear: { type: 'fixed', value: 2025 },
          duration: {
            type: 'fixed',
            value: 10
          },
          startTimingType: 'distribution' as const,
          referenceEventSeriesId: undefined,
          initialAmount: 0
        }
      },
      zod4(eventSeriesCreateSchema)
    ),
    scenario
  };
};

export const actions = {
  investmentType: async ({ request, locals }) => {
    const user = locals.user;

    if (!user) {
      return fail(401, { message: 'Unauthorized' });
    }

    const form = await superValidate(request, zod4(investmentTypeSchema));

    if (!form.valid) {
      return fail(400, { form });
    }

    // Process the valid form data
    const newInvestmentType = form.data;

    const scenario = await db.query.scenario.findFirst({
      where: eq(scenarioSchema.id, newInvestmentType.scenarioId)
    });

    if (!scenario) {
      return fail(404, { message: 'Scenario not found' });
    }

    if (scenario.userId !== user.id) {
      return fail(403, { message: 'Forbidden' });
    }

    const dbInvestmentType: Omit<InvestmentType, 'id'> = {
      scenarioId: newInvestmentType.scenarioId,
      name: newInvestmentType.name,
      description: newInvestmentType.description,
      expenseRatio: newInvestmentType.expenseRatio,
      returnPercent: newInvestmentType.returnPercent,
      expectedAnnualReturn: newInvestmentType.expectedAnnualReturn,
      incomePercent: newInvestmentType.incomePercent,
      expectedAnnualIncome: newInvestmentType.expectedAnnualIncome,
      taxability: newInvestmentType.taxability,
      isCash: newInvestmentType.isCash
    };

    // Save the new investment type to the database
    const result = await db.insert(investmentType).values(dbInvestmentType).returning();

    return { form, uuid: result[0].id, message: 'Investment type created successfully' };
  },

  investment: async ({ request, locals }) => {
    const user = locals.user;

    if (!user) {
      return fail(401, { message: 'Unauthorized' });
    }

    const form = await superValidate(request, zod4(investmentSchema));

    if (!form.valid) {
      return fail(400, { form });
    }

    // Process the valid form data
    const newInvestment = form.data;

    const scenario = await db.query.scenario.findFirst({
      where: eq(scenarioSchema.id, newInvestment.scenarioId)
    });

    if (!scenario) {
      return fail(404, { message: 'Scenario not found' });
    }

    if (scenario.userId !== user.id) {
      return fail(403, { message: 'Forbidden' });
    }

    const it = await db.query.investmentType.findFirst({
      where: eq(investmentType.id, newInvestment.investmentTypeId)
    });

    if (!it || it.scenarioId !== scenario.id) {
      return fail(400, { message: 'Invalid investment type' });
    }

    const dbInvestment: Omit<Investment, 'id'> = {
      scenarioId: newInvestment.scenarioId,
      name: newInvestment.name,
      currentValue: newInvestment.currentValue,
      accountTaxStatus: newInvestment.accountTaxStatus,
      investmentTypeId: newInvestment.investmentTypeId
    };

    // Save the new investment to the database
    const result = await db.insert(investment).values(dbInvestment).returning();

    return { form, uuid: result[0].id, message: 'Investment created successfully' };
  },

  eventSeries: async ({ request, locals }) => {
    const user = locals.user;
    if (!user) {
      return fail(401, { message: 'Unauthorized' });
    }

    const form = await superValidate(request, zod4(eventSeriesCreateSchema));
    if (!form.valid) {
      return fail(400, { form });
    }

    const { data } = form;

    // Verify scenario exists and user owns it
    const scenario = await db.query.scenario.findFirst({
      where: eq(scenarioSchema.id, data.scenarioId)
    });

    if (!scenario) {
      return fail(404, { message: 'Scenario not found' });
    }

    if (scenario.userId !== user.id) {
      return fail(403, { message: 'Forbidden' });
    }

    // Validate reference event series if provided
    if (data.eventSeries.referenceEventSeriesId) {
      const refEventSeries = await db.query.eventSeries.findFirst({
        where: eq(eventSeries.id, data.eventSeries.referenceEventSeriesId)
      });

      if (!refEventSeries || refEventSeries.scenarioId !== scenario.id) {
        return fail(400, { message: 'Invalid reference event series' });
      }
    }

    // Build the database record
    const dbEventSeries: Omit<EventSeries, 'id'> = {
      scenarioId: data.scenarioId,
      name: data.eventSeries.name,
      description: data.eventSeries.description,
      type: data.eventSeries.type,
      startYear: data.eventSeries.startYear || null, // Start year should not be null when using distribution
      duration: data.eventSeries.duration,
      referenceEventSeriesId: data.eventSeries.referenceEventSeriesId || null,
      startTimingType: data.eventSeries.startTimingType,
      isActive: data.eventSeries.isActive,
      orderIndex: data.eventSeries.orderIndex,

      // Income/Expense specific fields
      initialAmount: null,
      annualChange: null,
      inflationAdjusted: null,
      userPercentage: null,
      isSocialSecurity: null,
      isDiscretionary: null,

      // Invest/Rebalance specific fields
      assetAllocation: null,
      isGlidePath: null,
      initialAllocation: null,
      finalAllocation: null,
      maximumCash: null,
      targetTaxStatus: null
    };

    // Set type-specific fields based on discriminated union
    switch (data.eventSeries.type) {
      case 'income':
        dbEventSeries.initialAmount = data.eventSeries.initialAmount.toString();
        dbEventSeries.annualChange = data.eventSeries.annualChange;
        dbEventSeries.inflationAdjusted = data.eventSeries.inflationAdjusted;
        dbEventSeries.userPercentage = data.eventSeries.userPercentage?.toString() || null;
        dbEventSeries.isSocialSecurity = data.eventSeries.isSocialSecurity;
        break;

      case 'expense':
        dbEventSeries.initialAmount = data.eventSeries.initialAmount.toString();
        dbEventSeries.annualChange = data.eventSeries.annualChange;
        dbEventSeries.inflationAdjusted = data.eventSeries.inflationAdjusted;
        dbEventSeries.userPercentage = data.eventSeries.userPercentage?.toString() || null;
        dbEventSeries.isDiscretionary = data.eventSeries.isDiscretionary;
        break;

      case 'invest': {
        // Validate that asset allocation percentages sum to 100
        const investTotal = Object.values(data.eventSeries.assetAllocation).reduce(
          (sum, pct) => sum + pct,
          0
        );
        if (Math.abs(investTotal - 100) > 0.01) {
          return fail(400, { message: 'Asset allocation percentages must sum to 100%' });
        }

        dbEventSeries.assetAllocation = data.eventSeries.assetAllocation;
        dbEventSeries.isGlidePath = data.eventSeries.isGlidePath;
        dbEventSeries.initialAllocation = data.eventSeries.initialAllocation || null;
        dbEventSeries.finalAllocation = data.eventSeries.finalAllocation || null;
        dbEventSeries.maximumCash = data.eventSeries.maximumCash.toString();

        // Validate glide path allocations if using glide path
        if (data.eventSeries.isGlidePath) {
          if (!data.eventSeries.initialAllocation || !data.eventSeries.finalAllocation) {
            return fail(400, { message: 'Initial and final allocations required for glide path' });
          }

          const initialTotal = Object.values(data.eventSeries.initialAllocation).reduce(
            (sum, pct) => sum + pct,
            0
          );
          const finalTotal = Object.values(data.eventSeries.finalAllocation).reduce(
            (sum, pct) => sum + pct,
            0
          );

          if (Math.abs(initialTotal - 100) > 0.01 || Math.abs(finalTotal - 100) > 0.01) {
            return fail(400, { message: 'Glide path allocations must each sum to 100%' });
          }
        }
        break;
      }

      case 'rebalance': {
        // Validate that asset allocation percentages sum to 100
        const rebalanceTotal = Object.values(data.eventSeries.assetAllocation).reduce(
          (sum, pct) => sum + pct,
          0
        );
        if (Math.abs(rebalanceTotal - 100) > 0.01) {
          return fail(400, { message: 'Asset allocation percentages must sum to 100%' });
        }

        dbEventSeries.assetAllocation = data.eventSeries.assetAllocation;
        dbEventSeries.isGlidePath = data.eventSeries.isGlidePath;
        dbEventSeries.initialAllocation = data.eventSeries.initialAllocation || null;
        dbEventSeries.finalAllocation = data.eventSeries.finalAllocation || null;
        dbEventSeries.targetTaxStatus = data.eventSeries.targetTaxStatus;

        // Validate glide path allocations if using glide path
        if (data.eventSeries.isGlidePath) {
          if (!data.eventSeries.initialAllocation || !data.eventSeries.finalAllocation) {
            return fail(400, { message: 'Initial and final allocations required for glide path' });
          }

          const initialTotal = Object.values(data.eventSeries.initialAllocation).reduce(
            (sum, pct) => sum + pct,
            0
          );
          const finalTotal = Object.values(data.eventSeries.finalAllocation).reduce(
            (sum, pct) => sum + pct,
            0
          );

          if (Math.abs(initialTotal - 100) > 0.01 || Math.abs(finalTotal - 100) > 0.01) {
            return fail(400, { message: 'Glide path allocations must each sum to 100%' });
          }
        }
        break;
      }
    }

    try {
      // Save the new event series to the database
      const result = await db.insert(eventSeries).values(dbEventSeries).returning();

      return {
        form,
        uuid: result[0].id,
        message: 'Event series created successfully'
      };
    } catch (error) {
      console.error('Failed to create event series:', error);
      return fail(500, { message: 'Failed to create event series' });
    }
  }
} satisfies Actions;
