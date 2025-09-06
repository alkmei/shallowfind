import { db } from '$lib/server/db';
import { eq } from 'drizzle-orm';
import { scenario as scenarioSchema } from '$lib/server/db/schema/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
  const id = params.id;

  const scenarios = await db.select().from(scenarioSchema).where(eq(scenarioSchema.id, id));
  const scenario = scenarios[0];

  if (!scenario) {
    throw new Error('Scenario not found');
  }

  return {
    scenario
  };
};
