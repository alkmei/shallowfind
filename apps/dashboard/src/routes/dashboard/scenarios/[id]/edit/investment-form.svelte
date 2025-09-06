<script lang="ts">
  import type { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import type { SuperForm } from 'sveltekit-superforms';
  import z from 'zod';
  import type { InvestmentType } from '$lib/api/shallowfind.schemas';
  import InvestmentTypeModal from './investment-type-modal.svelte';
  import * as Card from '$lib/components/ui/card';
  import InvestmentModal from './investment-modal.svelte';

  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;

  let { form }: { form: SuperForm<ScenariosCreateBody> } = $props();

  let investmentTypes: InvestmentType[] = $state([]);
</script>

<div class="mb-4 flex flex-col gap-8">
  <div class="flex justify-between">
    <h2 class="grow text-xl font-bold">Investment Types</h2>
    <InvestmentTypeModal {investmentTypes} />
  </div>
  {#if investmentTypes.length > 0}
    <ul class="flex flex-col gap-2 rounded border p-2">
      {#each investmentTypes as type (type.name)}
        <Card.Root>
          <Card.Header>
            <Card.Title>{type.name}</Card.Title>
            <Card.Description>{type.description}</Card.Description>
          </Card.Header>
          <Card.Content>
            <p>Return: {type.returnDistribution.mean} {type.returnAmtOrPct}</p>
            <p>Expense Ratio: {type.expenseRatio}%</p>
            <p>Income: {type.incomeDistribution.mean} {type.incomeAmtOrPct}</p>
            <p>Taxable: {type.taxability ? 'Yes' : 'No'}</p>
          </Card.Content>
        </Card.Root>
      {/each}
    </ul>
  {:else}
    <div class="rounded border p-8 text-center">
      <p class="text-gray-400">No investment types available. Please add some.</p>
    </div>
  {/if}
</div>

<div class="flex flex-col gap-3">
  <div class="flex justify-between">
    <h2 class="grow text-xl font-bold">Investments</h2>
    <InvestmentModal {form} {investmentTypes} />
  </div>
</div>
