import { zod4 } from 'sveltekit-superforms/adapters';
import { superValidate } from 'sveltekit-superforms';
import { registerSchema } from './schema';
import type { PageLoad } from './$types';

export const load: PageLoad = async () => {
  return {
    form: await superValidate(zod4(registerSchema))
  };
};
