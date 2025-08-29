import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
	apiKey: 'AIzaSyAJCfumUB75Y8Y2nQFVTmeIxF_vBYyOjSg',
	authDomain: 'shallowfind-85be1.firebaseapp.com',
	projectId: 'shallowfind-85be1',
	storageBucket: 'shallowfind-85be1.firebasestorage.app',
	messagingSenderId: '499063613682',
	appId: '1:499063613682:web:61fc5a64e192a96a52486b'
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
