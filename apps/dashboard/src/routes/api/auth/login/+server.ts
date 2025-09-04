import { redirect, type RequestHandler } from '@sveltejs/kit';

export const POST: RequestHandler = async ({ request, locals: { supabase } }) => {
  const { email, password } = await request.json();
  const { error } = await supabase.auth.signInWithPassword({ email, password });

  if (error) {
    console.error(error);
    redirect(303, '/?error=Invalid%20credentials');
  } else {
    redirect(303, '/dashboard');
  }
};
