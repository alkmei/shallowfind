import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import type { PageServerLoad } from './$types';
import { postApiScenariosBody } from '$lib/api/scenario-management/scenarios/scenarios.zod';

export const load: PageServerLoad = async () => {
  return {
    form: await superValidate(zod(postApiScenariosBody))
  };
};
