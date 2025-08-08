<script lang="ts">
  import { Label } from '$lib/components/ui/label';
  import { Input } from '$lib/components/ui/input';
  import { Button } from '$lib/components/ui/button';
  import { User } from '@lucide/svelte';
  import {
    signInWithEmailAndPassword,
    signInAnonymously,
    GoogleAuthProvider,
    signInWithPopup
  } from 'firebase/auth';
  import { auth } from '$lib/firebase/client';
  import { goto } from '$app/navigation';

  const googleAuthProvider = new GoogleAuthProvider();
  const id = $props.id();

  let email = $state('');
  let password = $state('');
  let loading = $state(false);
  let error = $state('');

  async function setSessionCookie(idToken: string) {
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ idToken })
      });

      if (!response.ok) {
        throw new Error('Failed to set session cookie');
      }

      return await response.json();
    } catch (err) {
      console.error('Session cookie error:', err);
      throw err;
    }
  }

  async function handleEmailLogin(event: Event) {
    event.preventDefault();
    loading = true;
    error = '';

    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const idToken = await userCredential.user.getIdToken();
      await setSessionCookie(idToken);
      await goto('/dashboard');
    } catch (err: any) {
      error = err.message;
      console.error('Email login error:', err);
    } finally {
      loading = false;
    }
  }

  async function handleGoogleLogin() {
    loading = true;
    error = '';

    try {
      const result = await signInWithPopup(auth, googleAuthProvider);
      const idToken = await result.user.getIdToken();
      await setSessionCookie(idToken);
      await goto('/dashboard');
    } catch (err: any) {
      error = err.message;
      console.error('Google login error:', err);
    } finally {
      loading = false;
    }
  }

  async function handleAnonymousLogin() {
    loading = true;
    error = '';

    try {
      const userCredential = await signInAnonymously(auth);
      const idToken = await userCredential.user.getIdToken();
      await setSessionCookie(idToken);
      await goto('/dashboard');
    } catch (err: any) {
      error = err.message;
      console.error('Anonymous login error:', err);
    } finally {
      loading = false;
    }
  }
</script>

<form class="flex flex-col gap-6" onsubmit={handleEmailLogin}>
  <div class="flex flex-col items-center gap-2 text-center">
    <h1 class="text-2xl font-bold">Login to your account</h1>
    <p class="text-sm text-balance text-muted-foreground">
      Enter your email below to login to your account
    </p>
  </div>

  {#if error}
    <div class="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-600">
      {error}
    </div>
  {/if}

  <div class="grid gap-6">
    <div class="grid gap-3">
      <Label for="email-{id}">Email</Label>
      <Input
        id="email-{id}"
        type="email"
        placeholder="m@example.com"
        required
        bind:value={email}
        disabled={loading}
      />
    </div>
    <div class="grid gap-3">
      <div class="flex items-center">
        <Label for="password-{id}">Password</Label>
        <a href="##" class="ml-auto text-sm underline-offset-4 hover:underline">
          Forgot your password?
        </a>
      </div>
      <Input id="password-{id}" type="password" required bind:value={password} disabled={loading} />
    </div>
    <Button type="submit" class="w-full" disabled={loading}>
      {loading ? 'Signing in...' : 'Login'}
    </Button>
    <div
      class="relative text-center text-sm after:absolute after:inset-0 after:top-1/2 after:z-0 after:flex after:items-center after:border-t after:border-border"
    >
      <span class="relative z-10 bg-background px-2 text-muted-foreground"> Or continue with </span>
    </div>
    <Button
      variant="outline"
      class="w-full"
      type="button"
      onclick={handleGoogleLogin}
      disabled={loading}
    >
      <svg
        version="1.1"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 48 48"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        style="display: block;"
        class="mr-2 h-4 w-4"
      >
        <path
          fill="#EA4335"
          d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"
        ></path>
        <path
          fill="#4285F4"
          d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"
        ></path>
        <path
          fill="#FBBC05"
          d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"
        ></path>
        <path
          fill="#34A853"
          d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"
        ></path>
        <path fill="none" d="M0 0h48v48H0z"></path>
      </svg>
      {loading ? 'Signing in...' : 'Login with Google'}
    </Button>
    <Button
      variant="outline"
      class="w-full"
      type="button"
      onclick={handleAnonymousLogin}
      disabled={loading}
    >
      <User class="mr-2 h-4 w-4" />
      {loading ? 'Signing in...' : 'Continue as Guest'}
    </Button>
  </div>
  <div class="text-center text-sm">
    Don't have an account?
    <a href="/register" class="underline underline-offset-4"> Sign up </a>
  </div>
</form>
