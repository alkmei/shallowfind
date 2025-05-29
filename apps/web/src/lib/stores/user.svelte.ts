import { sessionDestroy } from '$lib/api/session/session';
import type { AdminUser } from '$lib/api/shallowfind.schemas';
import { usersMeRetrieve } from '$lib/api/users/users';

type User = Omit<AdminUser, 'password' | 'password_confirm'>;

export function createUser() {
  let user = $state<User | null>(null);
  let loading = $state(false);
  let error: string | null = null;

  async function fetchUser() {
    loading = true;
    error = null;

    try {
      const res = await usersMeRetrieve();

      if (res.status === 200) {
        user = res.data;
        error = null;
      } else {
        throw new Error(`Error fetching user: ${res.status} ${res.statusText}`);
      }
    } catch (err) {
      user = null;
      error = err instanceof Error ? err.message : 'An unknown error occurred';
      console.error('Error fetching user:', err);
    } finally {
      loading = false;
    }
  }

  async function logout() {
    loading = true;
    try {
      await sessionDestroy();
      error = null;
      user = null;
    } catch (err) {
      console.error('Error during logout:', err);
    } finally {
      loading = false;
    }
  }

  function clearError() {
    error = null;
  }

  return {
    get user() {
      return user;
    },
    get loading() {
      return loading;
    },
    get error() {
      return error;
    },
    get fullName() {
      if (!user) return '';
      if (!user.first_name && !user.last_name) return user.email.split('@')[0];
      if (!user.first_name) return user.last_name;
      if (!user.last_name) return user.first_name;
      return `${user.first_name} ${user.last_name}`.trim();
    },

    fetchUser,
    logout,
    clearError
  };
}
