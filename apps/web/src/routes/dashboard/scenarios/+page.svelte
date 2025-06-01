<script>
  import Button from '$lib/components/ui/button/button.svelte';
</script>

<header class="px-6">
  <div class="flex items-center justify-between">
    <h1 class="text-4xl">My Scenarios</h1>
    <Button class="mt-4" variant="default" href="/dashboard/scenarios/create">
      Create New Scenario
    </Button>
  </div>
  <p class="text-muted-foreground mt-2">Manage and explore your financial scenarios.</p>
</header>
<main></main>
