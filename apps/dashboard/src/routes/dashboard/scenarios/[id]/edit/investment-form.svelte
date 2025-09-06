<script lang="ts">
  import type { Infer, SuperForm, SuperValidated } from 'sveltekit-superforms';
  import type { InvestmentType, ScenarioForm, InvestmentTypes } from './schema';
  import * as Card from '$lib/components/ui/card';
  import type {
    Scenario,
    InvestmentType as InvestmentTypeModel
  } from '$lib/server/db/schema/schema';
  import InvestmentTypeModal from './investment-type-modal.svelte';
  import type { PageProps } from './$types';

  let { params, data, form }: PageProps = $props();

  let scenarioInvestmentTypes: InvestmentTypes = $state({
    scenarioId: data.scenario.id,
    investmentTypes: data.scenario.investmentTypes || []
  });
</script>

<div class="mb-4 flex flex-col gap-8">
  <div class="flex justify-between">
    <h2 class="grow text-xl font-bold">Investment Types</h2>
    <InvestmentTypeModal {params} {data} {form} />
  </div>
  {#if scenarioInvestmentTypes.investmentTypes.length > 0}
    <ul class="flex flex-col gap-2 rounded border p-2">
      {#each scenarioInvestmentTypes.investmentTypes as type (type.name)}
        <Card.Root>
          <Card.Header>
            <Card.Title>{type.name}</Card.Title>
            <Card.Description>{type.description}</Card.Description>
          </Card.Header>
          <Card.Content>
            <p>Return: {type.expectedAnnualReturn.mean} {type.returnPercent ? '%' : '$'}</p>
            <p>Expense Ratio: {type.expenseRatio}%</p>
            <p>Income: {type.expectedAnnualIncome.mean} {type.incomePercent ? '%' : '$'}</p>
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
    <!-- <InvestmentModal {form} {investmentTypes} /> -->
  </div>
</div>
