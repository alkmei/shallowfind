import * as admin from 'firebase-admin';
import * as serviceAccount from './shallowfind.json';

admin.initializeApp({
  credential: admin.credential.cert({
    projectId: serviceAccount.project_id,
    privateKey: serviceAccount.private_key,
    clientEmail: serviceAccount.client_email,
  }),
});

export { admin };
