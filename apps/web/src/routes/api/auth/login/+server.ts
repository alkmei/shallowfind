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
    // const uid = decodedToken.uid;

    // Create a session cookie (optional - you can also just use the ID token)
    // Session cookies last longer and can be configured
    const expiresIn = 60 * 60 * 24 * 5 * 1000; // 5 days
    const sessionCookie = await adminAuth.createSessionCookie(idToken, { expiresIn });

    // Set the session cookie
    cookies.set('session', sessionCookie, {
      maxAge: expiresIn / 1000, // Convert to seconds
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
