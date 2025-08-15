<script lang="ts">
  import type { PageData } from './$types';
  import DraftScenarioDialog from './draft-scenario-dialog.svelte';

  let { data }: { data: PageData } = $props();
</script>

<h1 class="text-2xl">My Scenarios</h1>
<DraftScenarioDialog {data} />

<ul>
  {#each data.scenarios as scenario}
    <li>
      <a href={`/dashboard/scenarios/${scenario.id}`}>{scenario.name}</a>
    </li>
  {/each}
</ul>
