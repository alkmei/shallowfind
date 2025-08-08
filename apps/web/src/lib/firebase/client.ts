import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: 'AIzaSyArNUPcwUwbPjk6Jxn5YQEZo1m8ilEBY30',
  authDomain: 'shallowfind-df121.firebaseapp.com',
  projectId: 'shallowfind-df121',
  storageBucket: 'shallowfind-df121.firebasestorage.app',
  messagingSenderId: '454327889819',
  appId: '1:454327889819:web:0b96349a1d64af5b903b3e'
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
