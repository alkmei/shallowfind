import type { PageServerLoad } from './$types';
import { db } from '$lib/server/db';
import { scenario as scenarioSchema } from '$lib/server/db/schema/schema';
import { eq } from 'drizzle-orm';
import { error } from '@sveltejs/kit';
import { superValidate } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';
import scenarioFormSchema from './schema';

export const load: PageServerLoad = async ({ params }) => {
  const id = params.id;

  const scenarios = await db.select().from(scenarioSchema).where(eq(scenarioSchema.id, id));

  const scenario = scenarios[0];

  if (!scenario) {
    throw error(404, { message: 'Scenario not found' });
  }

  return {
    form: await superValidate(scenario, zod4(scenarioFormSchema)),
    scenario
  };
};
