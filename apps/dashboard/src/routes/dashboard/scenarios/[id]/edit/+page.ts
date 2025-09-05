import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params }) => {
  redirect(302, `/dashboard/scenarios/${params.id}/edit/basic-information`);
};
