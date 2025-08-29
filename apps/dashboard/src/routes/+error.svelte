<script lang="ts">
  import { page } from '$app/stores';
  import Button from '$lib/components/ui/button/button.svelte';
</script>

<main class="flex h-screen flex-col items-center justify-center">
  <h1 class="m-8 text-3xl font-bold">Error</h1>
  <p class="m-8">Sorry, an unexpected error has occurred.</p>
  <p class="m-8">{$page.status} - {$page.error?.message}</p>
  <a href="/"><Button>Go Back Home</Button></a>
</main>
