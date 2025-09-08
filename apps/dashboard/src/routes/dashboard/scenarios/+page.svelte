<script lang="ts">
  import ScenarioCard from '$lib/components/scenario-card.svelte';
  import type { PageData } from './$types';
  import DraftScenarioDialog from './draft-scenario-dialog.svelte';
  import ImportScenarioDialog from './import-scenario-dialog.svelte';

  let { data }: { data: PageData } = $props();
</script>

<h1 class="mb-2 text-2xl">My Scenarios</h1>

{#if data.form}
  <div class="mb-2">
    <DraftScenarioDialog {data} />
    <ImportScenarioDialog />
  </div>
{/if}

<ul class="grid grid-cols-2 gap-4 lg:grid-cols-4">
  {#if data.scenarios}
    {#each data.scenarios as scenario}
      <ScenarioCard {scenario} />
    {/each}
  {/if}
</ul>
