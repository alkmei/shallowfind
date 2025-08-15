import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';
import axios from 'axios';

export const load: LayoutServerLoad = async ({ locals, cookies }) => {
  // Check if user is authenticated (this should already be handled by hooks)
  if (!locals.user) {
    throw redirect(302, '/');
  }

  axios.defaults.headers.common['Authorization'] = `Bearer ${cookies.get('idToken')}`;

  // Return user data and any other dashboard-specific data
  return {
    user: locals.user
  };
};
