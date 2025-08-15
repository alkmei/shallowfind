import { json, type RequestHandler } from '@sveltejs/kit';
import { adminAuth } from '$lib/firebase/admin';

export const POST: RequestHandler = async ({ request, cookies }) => {
  try {
    const { idToken } = await request.json();

    if (!idToken) {
      return json({ error: 'ID token is required' }, { status: 400 });
    }

    // Verify the ID token
    const decodedToken = await adminAuth.verifyIdToken(idToken);

    // Store the ID token directly as a cookie
    cookies.set('idToken', idToken, {
      maxAge: 60 * 60, // 1 hour (ID tokens typically expire in 1 hour)
      httpOnly: true,
      secure: true,
      sameSite: 'lax',
      path: '/'
    });

    return json({
      success: true,
      user: {
        uid: decodedToken.uid,
        email: decodedToken.email,
        name: decodedToken.name
      }
    });
  } catch (error) {
    console.error('Auth error:', error);
    return json({ error: 'Authentication failed' }, { status: 401 });
  }
};
