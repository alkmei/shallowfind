import type { PageServerLoad } from './$types';
import { db } from '$lib/server/db';
import { scenario as scenarioSchema } from '$lib/server/db/schema/schema';
import { eq } from 'drizzle-orm';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import scenarioFormSchema, { type ScenarioForm } from './schema';

export const load: PageServerLoad = async ({ params }) => {
  const id = params.id;

  const scenarios = await db.select().from(scenarioSchema).where(eq(scenarioSchema.id, id));

  const scenario = scenarios[0];

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
    spouseBirthYear: scenario.spouseBirthYear || (isMarried ? new Date().getFullYear() - 25 : undefined),
    userLifeExpectancy: scenario.userLifeExpectancy || { type: 'fixed', value: 85 },
    spouseLifeExpectancy: scenario.spouseLifeExpectancy || (isMarried ? { type: 'fixed', value: 85 } : undefined),
    financialGoal: scenario.financialGoal || "0",
    inflationAssumption: scenario.inflationAssumption || { type: 'fixed', value: 0.03 },
    annualRetirementContributionLimit: scenario.annualRetirementContributionLimit || "0",
    rothOptimizerEnabled: scenario.rothOptimizerEnabled || false,
    rothOptimizerStartYear: scenario.rothOptimizerStartYear || undefined,
    rothOptimizerEndYear: scenario.rothOptimizerEndYear || undefined,
  }

  return {
    form: await superValidate(scenarioData, zod4(scenarioFormSchema)),
    scenario
  };
};
