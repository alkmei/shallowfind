import { json, type RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ cookies }) => {
  // Clear the session cookie
  cookies.delete('session', { path: '/' });

  return json({ success: true });
};
