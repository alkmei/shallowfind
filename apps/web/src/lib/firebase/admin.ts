import { initializeApp, cert, getApps } from 'firebase-admin/app';
import { getAuth } from 'firebase-admin/auth';
import serviceAccount from './pk.json';

if (!getApps().length) {
  initializeApp({
    credential: cert({
      projectId: serviceAccount.project_id,
      privateKey: serviceAccount.private_key,
      clientEmail: serviceAccount.client_email
    })
  });
}

export const adminAuth = getAuth();
