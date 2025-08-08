import { adminAuth } from '$lib/firebase/admin';
import type { RequestEvent } from '@sveltejs/kit';

export async function getUserFromSession(event: RequestEvent) {
  const sessionCookie = event.cookies.get('session');

  if (!sessionCookie) {
    return null;
  }

  try {
    const decodedClaims = await adminAuth.verifySessionCookie(sessionCookie, true);
    return {
      uid: decodedClaims.uid,
      email: decodedClaims.email,
      name: decodedClaims.name
      // Add other fields as needed
    };
  } catch (error) {
    console.error('Session verification failed:', error);
    return null;
  }
}
