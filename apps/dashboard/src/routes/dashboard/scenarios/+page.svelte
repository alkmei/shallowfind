<script lang="ts">
  import ScenarioCard from '$lib/components/scenario-card.svelte';
  import type { PageData } from './$types';
  import DraftScenarioDialog from './draft-scenario-dialog.svelte';

  let { data }: { data: PageData } = $props();
</script>

<h1 class="text-2xl">My Scenarios</h1>
<DraftScenarioDialog {data} />

<ul class="grid grid-cols-2 gap-4 lg:grid-cols-4">
  {#each data.scenarios as scenario}
    <ScenarioCard {scenario} />
  {/each}
</ul>
