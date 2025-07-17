<script lang="ts">
  import type { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import type { SuperForm } from 'sveltekit-superforms';
  import z from 'zod';
  import Button from '../ui/button/button.svelte';
  import type { InvestmentType } from '$lib/api/shallowfind.schemas';
  import { Plus } from '@lucide/svelte';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Label } from '../ui/label';
  import { Input } from '../ui/input';
  import { Textarea } from '../ui/textarea';
  import InvestmentTypeModal from './investment-type-modal.svelte';

  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;

  let { form }: { form: SuperForm<ScenariosCreateBody> } = $props();

  let investmentTypes: InvestmentType[] = $state([]);
</script>

<div class="flex flex-col gap-3">
  <div class="flex justify-between">
    <h2 class="grow text-xl font-bold">Investment Types</h2>
    <InvestmentTypeModal {investmentTypes} />
  </div>
  {#if investmentTypes.length > 0}
    <ul class="rounded border p-2">
      {#each investmentTypes as type (type.name)}
        <li>{type.name} - {type.description}</li>
      {/each}
    </ul>
  {:else}
    <div class="rounded border p-8 text-center">
      <p class="text-gray-400">No investment types available. Please add some.</p>
    </div>
  {/if}
</div>
