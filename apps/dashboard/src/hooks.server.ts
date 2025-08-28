import type { Handle } from '@sveltejs/kit';
import { getUserFromId } from '$lib/server/auth';

export const handle: Handle = async ({ event, resolve }) => {
	// Add user to locals for access in routes
	event.locals.user = await getUserFromId(event);

	const response = await resolve(event);
	return response;
};
