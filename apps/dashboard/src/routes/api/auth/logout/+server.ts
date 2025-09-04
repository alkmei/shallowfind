import { json, type RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ locals: { supabase } }) => {
  // Clear the session cookie
  const { error } = await supabase.auth.signOut();

  if (error) {
    return json({ error: error.message }, { status: 400 });
  }
  return json({ success: true });
};
