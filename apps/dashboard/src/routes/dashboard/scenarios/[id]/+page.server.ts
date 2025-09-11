import { db } from '$lib/server/db';
import { eq } from 'drizzle-orm';
import { scenario as scenarioSchema } from '$lib/server/db/schema/schema';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
  const id = params.id;

  const scenario = await db.query.scenario.findFirst({
    where: eq(scenarioSchema.id, id),
    with: {
      investmentTypes: true,
      investments: true,
      eventSeries: true,
      strategies: true,
      sharedWith: true
    }
  });

  if (!scenario) {
    throw new Error('Scenario not found');
  }

  return {
    scenario
  };
};
