import { adminAuth } from '$lib/firebase/admin';
import type { RequestEvent } from '@sveltejs/kit';

export async function getUserFromId(event: RequestEvent) {
  const idCookie = event.cookies.get('idToken');

  if (!idCookie) {
    return null;
  }

  try {
    const decodedClaims = await adminAuth.verifyIdToken(idCookie, true);
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
