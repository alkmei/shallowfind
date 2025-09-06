import type { Actions, PageServerLoad } from './$types';
import { db } from '$lib/server/db';
import {
  scenario as scenarioSchema,
  type InvestmentType,
  investmentType
} from '$lib/server/db/schema/schema';
import { eq } from 'drizzle-orm';
import { error, fail } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import scenarioFormSchema, { investmentTypeSchema, type ScenarioForm } from './schema';

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

  // FIXME: Figure out why refreshes reset the form even with superValidate
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
    scenario
  };
};

export const actions = {
  investmentType: async ({ request, locals }) => {
    const user = locals.user;

    if (!user) {
      return fail(401, { message: 'Unauthorized' });
    }

    const result = await superValidate(request, zod4(investmentTypeSchema));

    if (!result.valid) {
      return fail(400, { form: result });
    }

    // Process the valid form data
    const newInvestmentType = result.data;

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
    await db.insert(investmentType).values(dbInvestmentType);

    return {
      success: true,
      investmentType: newInvestmentType
    };
  }
} satisfies Actions;
