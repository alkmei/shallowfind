<script lang="ts">
  import type { Investment, InvestmentType } from '$lib/server/db/schema/schema';
  import InvestmentTypeModal from './investment-type-modal.svelte';
  import type { PageProps } from './$types';
  import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
  import InvestmentTypeDisplayCard from './investment-type-display-card.svelte';
  import InvestmentModal from './investment-modal.svelte';
  import InvestmentDisplayCard from './investment-info-card.svelte';

  let { params, data, form }: PageProps = $props();

  let investmentTypes: InvestmentType[] = $state(data.scenario.investmentTypes || []);
  let investments = $state(data.scenario.investments || []);

  const addInvestmentType = (it: InvestmentType) => {
    investmentTypes = [...investmentTypes, it];
  };

  const addInvestment = (inv: Investment) => {
    investments = [...investments, inv];
  };
</script>

<div class="mb-4 flex flex-col gap-2">
  <div class="flex justify-between">
    <h2 class="grow text-xl font-bold">Investment Types</h2>
    <InvestmentTypeModal {params} {data} {form} onSubmit={addInvestmentType} />
  </div>
  {#if investmentTypes.length > 0}
    <ScrollArea class="max-h-256 w-full rounded border">
      <ul class="flex max-h-256 flex-col gap-4 p-4">
        {#each investmentTypes as type (type.id)}
          <InvestmentTypeDisplayCard investmentType={type} />
        {/each}
      </ul>
    </ScrollArea>
  {:else}
    <div class="rounded border p-8 text-center">
      <p class="text-gray-400">No investment types available. Please add some.</p>
    </div>
  {/if}
</div>

<div class="flex flex-col gap-3">
  <div class="flex justify-between">
    <h2 class="grow text-xl font-bold">Investments</h2>
    <InvestmentModal {params} {data} {form} onSubmit={addInvestment} />
  </div>
  {#if investments.length > 0}
    <ScrollArea class="max-h-256 w-full rounded border">
      <ul class="flex flex-col gap-4 p-4">
        {#each investments as investment (investment.id)}
          <li class="rounded border p-4">
            <h3 class="text-lg font-semibold">{investment.name}</h3>
            <p class="text-sm">
              Type:
              {investmentTypes.find((type) => type.id === investment.investmentTypeId)?.name}
            </p>
            <p class="text-sm">Current Value: ${investment.currentValue}</p>
            <p class="text-sm">
              Tax Status: {investment.accountTaxStatus.replaceAll('_', ' ')}
            </p>
          </li>
        {/each}
      </ul>
    </ScrollArea>
  {:else}
    <div class="rounded border p-8 text-center">
      <p class="text-gray-400">No investments available. Please add some.</p>
    </div>
  {/if}
</div>
