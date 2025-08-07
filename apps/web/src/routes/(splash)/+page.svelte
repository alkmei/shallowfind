<script lang="ts">
  import Button from '$lib/components/ui/button/button.svelte';

  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
</script>

<div class="flex flex-col">
  <Button class="mb-4 w-full"><a href={`${backendUrl}/auth/google/login`}>Log In</a></Button>
  <a href="/dashboard"><Button variant="outline" class="w-full">Continue As Guest</Button></a>
</div>
