import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, url }) => {
  // If user is already authenticated, redirect to dashboard
  if (locals.user) {
    // Check if there's a redirect URL in the query params
    const redirectTo = url.searchParams.get('redirect') || '/dashboard';
    throw redirect(302, redirectTo);
  }

  // Return any data needed for the login page
  return {
    // You can return any initial data here
  };
};
