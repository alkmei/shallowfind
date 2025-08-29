import { fail, superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { Actions, PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { createScenarioSchema } from './schema';
import { db } from '$lib/server/db';
import { scenario } from '$lib/server/db/schema';

export const load: PageServerLoad = async (event) => {
	const user = event.locals.user;
	if (!user) {
		return fail(401, { message: 'Unauthorized' });
	}
	const scenarios = await db.query.scenario.findMany({ with: { userId: user.uid } });
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

		db.insert(scenario).values({
			userId: user.uid,
			title: form.data.name,
			description: form.data.description || '',
			scenarioType: form.data.scenarioType
		});

		redirect(303, `/dashboard/scenarios/${response.data.id}/edit`);
	}
};
