import { getScenarios } from '$lib/api/scenario-management/scenarios/scenarios';
import { superValidate } from 'sveltekit-superforms';
import type { PageServerLoad } from './$types';
import { putApiScenariosIdBody } from '$lib/api/scenario-management/scenarios/scenarios.zod';
import { zod } from 'sveltekit-superforms/adapters';

export const load: PageServerLoad = async ({ params }) => {
  const id = params.id;

  const scenario = await getScenarios().getApiScenariosId(id);

  if (!scenario) {
    throw new Error('Scenario not found');
  }

  return {
    form: await superValidate(scenario.data, zod(putApiScenariosIdBody))
  };
};
