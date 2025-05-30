<script lang="ts">
  import Button from '$lib/components/ui/button/button.svelte';
  import LoginForm from '$lib/components/LoginForm.svelte';
</script>

<div class="flex flex-col">
  <LoginForm><Button class="mb-4 w-full">Log In</Button></LoginForm>
  <a href="/dashboard"><Button variant="outline" class="w-full">Continue As Guest</Button></a>
  <div class="mt-4 text-center text-sm text-gray-500">
    Don't have an account?{' '}
    <a href="/register" class="text-blue-500 hover:underline">Sign Up</a>
  </div>
</div>
