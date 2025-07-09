import { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod.js';
import { superValidate } from 'sveltekit-superforms';
import { zod } from 'sveltekit-superforms/adapters';
import { z } from 'zod';

export const load = async ({ params, fetch }) => {
  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;
  const scenarioDefault: ScenariosCreateBody = {
    name: '',
    description: null,
    userBirthYear: 0,
    spouseBirthYear: null,
    userLifeExpectancy: {
      type: 'fixed',
      value: null,
      mean: null,
      stdev: null,
      lower: null,
      upper: null
    },
    spouseLifeExpectancy: {
      type: 'fixed',
      value: null,
      mean: null,
      stdev: null,
      lower: null,
      upper: null
    },
    inflationAssumption: {
      type: 'fixed',
      value: null,
      mean: null,
      stdev: null,
      lower: null,
      upper: null
    },
    afterTaxContributionLimit: '',
    financialGoal: '',
    residenceState: 'AL',
    rothConversionStart: null,
    rothConversionEnd: null,
    investments: [],
    eventSeries: []
  };
  const form = await superValidate(scenarioDefault, zod(scenariosCreateBody));

  return { form };
};
