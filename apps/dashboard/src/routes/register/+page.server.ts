import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  // Check if user is authenticated (this should already be handled by hooks)
  if (locals.user) {
    throw redirect(302, '/dashboard');
  }
};
