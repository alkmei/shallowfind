import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import type { Actions, PageServerLoad } from './$types';
import { postApiScenariosBody } from '$lib/api/scenario-management/scenarios/scenarios.zod';
import { getScenarios } from '$lib/api/scenario-management/scenarios/scenarios';

export const load: PageServerLoad = async () => {
  return {
    form: await superValidate(zod(postApiScenariosBody))
  };
};

export const actions: Actions = {
  default: async (event) => {
    const form = await superValidate(event, zod(postApiScenariosBody));
    if (!form.valid) {
      return fail(400, {
        form
      });
    }

    const response = await getScenarios().postApiScenarios(form.data, {
      withCredentials: true
    });

    return {
      form
    };
  }
};
