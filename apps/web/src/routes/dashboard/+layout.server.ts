import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals }) => {
  // Check if user is authenticated (this should already be handled by hooks)
  if (!locals.user) {
    throw redirect(302, '/login');
  }

  // Return user data and any other dashboard-specific data
  return {
    user: locals.user
  };
};
