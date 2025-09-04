import type { PageServerLoad } from './$types';
import { db } from '$lib/server/db';
import { scenario as scenarioSchema } from '$lib/server/db/schema/schema';
import { eq } from 'drizzle-orm';

export const load: PageServerLoad = async ({ params }) => {
  const id = params.id;

  const scenario = await db.select().from(scenarioSchema).where(eq(scenarioSchema.id, id));

  if (!scenario) {
    throw new Error('Scenario not found');
  }

  return {
    scenario
  };
};
