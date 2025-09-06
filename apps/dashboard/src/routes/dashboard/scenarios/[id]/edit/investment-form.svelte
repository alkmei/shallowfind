<script lang="ts">
  import type { InvestmentType } from '$lib/server/db/schema/schema';
  import InvestmentTypeModal from './investment-type-modal.svelte';
  import type { PageProps } from './$types';
  import ScrollArea from '$lib/components/ui/scroll-area/scroll-area.svelte';
  import InvestmentTypeDisplayCard from './investment-type-display-card.svelte';

  let { params, data, form }: PageProps = $props();

  let investmentTypes: InvestmentType[] = $state(data.scenario.investmentTypes || []);

  const addInvestmentType = (it: InvestmentType) => {
    investmentTypes = [...investmentTypes, it];
  };
</script>

<div class="mb-4 flex flex-col gap-2">
  <div class="flex justify-between">
    <h2 class="grow text-xl font-bold">Investment Types</h2>
    <InvestmentTypeModal {params} {data} {form} onSubmit={addInvestmentType} />
  </div>
  {#if investmentTypes.length > 0}
    <ScrollArea class="h-128 w-full rounded border">
      <ul class="flex flex-col gap-4 p-4">
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
    <!-- <InvestmentModal {form} {investmentTypes} /> -->
  </div>
</div>
