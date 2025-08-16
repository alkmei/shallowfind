import { fail, superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import type { Actions, PageServerLoad } from './$types';
import { postApiScenariosBody } from '$lib/api/scenario-management/scenarios/scenarios.zod';
import { getScenarios } from '$lib/api/scenario-management/scenarios/scenarios';
import { redirect } from '@sveltejs/kit';

export const load: PageServerLoad = async () => {
  const scenarios = await getScenarios().getApiScenarios();

  return {
    form: await superValidate(zod(postApiScenariosBody)),
    scenarios: scenarios.data
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

    const idToken = event.cookies.get('idToken');

    const response = await getScenarios().postApiScenarios(form.data, {
      headers: {
        Authorization: `Bearer ${idToken}`
      }
    });

    if (response.status > 399) {
      return fail(response.status, {
        form
      });
    }

    redirect(303, `/dashboard/scenarios/${response.data.id}/edit`);
  }
};
