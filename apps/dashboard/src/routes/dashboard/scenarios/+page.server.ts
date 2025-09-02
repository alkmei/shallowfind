import { fail, superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import type { Actions, PageServerLoad } from './$types';
import { redirect } from '@sveltejs/kit';
import { createScenarioSchema } from './schema';
import { db } from '$lib/server/db';
import { eq } from 'drizzle-orm';
import { scenario } from '$lib/server/db/schema';

export const load: PageServerLoad = async (event) => {
  const user = event.locals.user;
  if (!user) {
    return fail(401, { message: 'Unauthorized' });
  }
  const scenarios = await db.select().from(scenario).where(eq(scenario.userId, user.uid));
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

    const newScenario = await db
      .insert(scenario)
      .values({
        userId: user.uid,
        title: form.data.name,
        description: form.data.description || '',
        scenarioType: form.data.scenarioType,
        stateOfResidence: form.data.stateOfResidence
      })
      .returning({ insertedId: scenario.id });

    redirect(303, `/dashboard/scenarios/${newScenario.at(0)?.insertedId}/edit`);
  }
};
