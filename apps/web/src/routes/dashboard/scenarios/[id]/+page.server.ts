import { getScenarios } from '$lib/api/scenario-management/scenarios/scenarios';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
  const id = params.id;

  const scenario = await getScenarios().getApiScenariosId(id);

  if (!scenario) {
    throw new Error('Scenario not found');
  }

  return {
    scenario: scenario.data
  };
};
