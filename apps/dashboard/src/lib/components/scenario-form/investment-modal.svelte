<script lang="ts">
  import type { Investment, InvestmentType, TaxStatusEnum } from '$lib/api/shallowfind.schemas';
  import type { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import type { SuperForm } from 'sveltekit-superforms';
  import * as Dialog from '$lib/components/ui/dialog';
  import * as Select from '$lib/components/ui/select';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Plus } from '@lucide/svelte';
  import { get } from 'svelte/store';
  import z from 'zod';

  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;

  const {
    form,
    investmentTypes
  }: {
    form: SuperForm<ScenariosCreateBody>;
    investmentTypes: InvestmentType[];
  } = $props();

  const { form: formData } = form;

  let open = $state(false);
  let selectedInvestmentTypeName = $state<string>(''); // New: string for Select.Root binding
  let investmentValue = $state('');
  let selectedTaxStatus = $state<keyof typeof TaxStatusEnum | undefined>(undefined);
  let investmentId = $state('');

  // Reactive statement to find the InvestmentType object based on selected name
  let selectedInvestmentType = $state(
    investmentTypes.find((type) => type.name === selectedInvestmentTypeName)
  );

  const taxStatusOptions = [
    { value: 'non-retirement', label: 'Non-retirement' },
    { value: 'pre-tax', label: 'Pre-tax Retirement' },
    { value: 'after-tax', label: 'After-tax Retirement' }
  ];

  function handleSubmit() {
    if (!selectedInvestmentType) return;

    const newInvestment: Investment = {
      investmentType: selectedInvestmentType,
      value: investmentValue,
      taxStatus: selectedTaxStatus ?? 'non-retirement',
      investmentId: investmentId
    };

    // Add to the form's investments array
    const currentInvestments = get(formData).investments || [];
    formData.update((data) => ({
      ...data,
      investments: [...currentInvestments, newInvestment]
    }));

    // Reset form - now includes clearing the name string
    selectedInvestmentTypeName = '';
    investmentValue = '';
    selectedTaxStatus = undefined;
    investmentId = '';
    open = false;
  }

  function isFormValid(): boolean {
    return !!(
      // selectedInvestmentType &&
      (
        investmentValue &&
        investmentValue.match(/^-?\d{0,12}(?:\.\d{0,2})?$/) &&
        selectedTaxStatus &&
        investmentId &&
        investmentId.length <= 100
      )
    );
  }
</script>

<Dialog.Root bind:open>
  <Dialog.Trigger>
    <Button class="w-48"><Plus /> New Investment</Button>
  </Dialog.Trigger>
  <Dialog.Content class="max-w-xl">
    <Dialog.Title>Add New Investment</Dialog.Title>
    <Dialog.Description>
      Add a new investment to your scenario. Select an investment type and enter the details.
    </Dialog.Description>

    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <label for="investmentType" class="text-sm font-medium">
          Investment Type <span class="text-red-500">*</span>
        </label>
        <Select.Root type="single" bind:value={selectedInvestmentTypeName}>
          <Select.Trigger>
            {selectedInvestmentTypeName || 'Select an investment type'}
          </Select.Trigger>
          <Select.Content>
            {#each investmentTypes as type (type.name)}
              <Select.Item value={type.name}>
                <div class="flex flex-col">
                  <span class="font-medium">{type.name}</span>
                  <span class="text-muted-foreground truncate text-sm">{type.description}</span>
                </div>
              </Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
        {#if investmentTypes.length === 0}
          <p class="text-muted-foreground text-sm">
            No investment types available. Please add some first.
          </p>
        {/if}
      </div>

      <!-- Rest of the form remains the same -->
      <div class="flex flex-col gap-2">
        <label for="value" class="text-sm font-medium">
          Investment Value <span class="text-red-500">*</span>
        </label>
        <Input
          id="value"
          type="text"
          placeholder="0.00"
          bind:value={investmentValue}
          pattern="^-?\d{(0, 12)}(?:\.\d{(0, 2)})?$"
        />
        <p class="text-muted-foreground text-sm">
          Enter the investment value (up to 12 digits with 2 decimal places)
        </p>
        {#if investmentValue && !investmentValue.match(/^-?\d{0,12}(?:\.\d{0,2})?$/)}
          <p class="text-sm text-red-500">Invalid format. Please enter a valid number.</p>
        {/if}
      </div>

      <div class="flex flex-col gap-2">
        <label for="taxStatus" class="text-sm font-medium">
          Tax Status <span class="text-red-500">*</span>
        </label>
        <Select.Root type="single" bind:value={selectedTaxStatus}>
          <Select.Trigger>
            {selectedTaxStatus ? selectedTaxStatus : 'Select tax status'}
          </Select.Trigger>
          <Select.Content>
            {#each taxStatusOptions as option (option.value)}
              <Select.Item value={option.value}>{option.label}</Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>

      <div class="flex flex-col gap-2">
        <label for="investmentId" class="text-sm font-medium">
          Investment ID <span class="text-red-500">*</span>
        </label>
        <Input
          id="investmentId"
          type="text"
          placeholder="Enter unique investment ID"
          bind:value={investmentId}
          maxlength={100}
        />
        <p class="text-muted-foreground text-sm">
          Enter a unique identifier for this investment (max 100 characters)
        </p>
      </div>

      {#if selectedInvestmentType}
        <div class="bg-muted/50 rounded border p-3">
          <h4 class="mb-2 font-medium">Selected Investment Type Details</h4>
          <div class="space-y-1 text-sm">
            <p><strong>Name:</strong> {selectedInvestmentType.name}</p>
            <p><strong>Description:</strong> {selectedInvestmentType.description}</p>
            <p><strong>Expense Ratio:</strong> {selectedInvestmentType.expenseRatio}%</p>
            <p><strong>Taxable:</strong> {selectedInvestmentType.taxability ? 'Yes' : 'No'}</p>
          </div>
        </div>
      {/if}
    </div>

    <Dialog.Footer>
      <Button variant="outline" onclick={() => (open = false)}>Cancel</Button>
      <Button type="submit" onclick={handleSubmit} disabled={!isFormValid()}>Add Investment</Button>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>
