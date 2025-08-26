<script lang="ts">
  import type { InvestmentType, Distribution } from '$lib/api/shallowfind.schemas';
  import { AmountOrPercentEnum } from '$lib/api/shallowfind.schemas';
  import * as Dialog from '$lib/components/ui/dialog';
  import * as Tabs from '$lib/components/ui/tabs';
  import { Button } from '$lib/components/ui/button';
  import { Label } from '$lib/components/ui/label';
  import { Input } from '$lib/components/ui/input';
  import { Textarea } from '$lib/components/ui/textarea';
  import { Plus } from '@lucide/svelte';
  import { Switch } from '$lib/components/ui/switch';
  import { Checkbox } from '$lib/components/ui/checkbox';

  const { investmentTypes }: { investmentTypes: InvestmentType[] } = $props();

  let open = $state(false);
  let formData = $state({
    name: '',
    description: '',
    returnAmtOrPct: AmountOrPercentEnum.percent as AmountOrPercentEnum,
    returnDistribution: {
      type: 'fixed',
      value: null,
      mean: null,
      stdev: null,
      lower: null,
      upper: null
    } as Distribution,
    expenseRatio: 0,
    incomeAmtOrPct: AmountOrPercentEnum.percent as AmountOrPercentEnum,
    incomeDistribution: {
      type: 'fixed',
      value: null,
      mean: null,
      stdev: null,
      lower: null,
      upper: null
    } as Distribution,
    taxability: false
  });

  // Create separate boolean variables for switches
  let returnIsAmount = $state(false);
  let incomeIsAmount = $state(false);

  // Update enum values when boolean changes
  $effect(() => {
    formData.returnAmtOrPct = returnIsAmount
      ? AmountOrPercentEnum.amount
      : AmountOrPercentEnum.percent;
  });

  $effect(() => {
    formData.incomeAmtOrPct = incomeIsAmount
      ? AmountOrPercentEnum.amount
      : AmountOrPercentEnum.percent;
  });

  function handleSubmit() {
    const newInvestmentType: InvestmentType = {
      name: formData.name,
      description: formData.description,
      returnAmtOrPct: formData.returnAmtOrPct,
      returnDistribution: formData.returnDistribution,
      expenseRatio: formData.expenseRatio,
      incomeAmtOrPct: formData.incomeAmtOrPct,
      incomeDistribution: formData.incomeDistribution,
      taxability: formData.taxability
    };

    investmentTypes.push(newInvestmentType);

    // Reset form
    formData = {
      name: '',
      description: '',
      returnAmtOrPct: AmountOrPercentEnum.percent,
      returnDistribution: {
        type: 'fixed',
        value: null,
        mean: null,
        stdev: null,
        lower: null,
        upper: null
      },
      expenseRatio: 0,
      incomeAmtOrPct: AmountOrPercentEnum.percent,
      incomeDistribution: {
        type: 'fixed',
        value: null,
        mean: null,
        stdev: null,
        lower: null,
        upper: null
      },
      taxability: false
    };

    // Reset switch states
    returnIsAmount = false;
    incomeIsAmount = false;

    open = false;
  }
</script>

<Dialog.Root bind:open>
  <Dialog.Trigger>
    <Button class="w-48"><Plus /> New Investment Type</Button>
  </Dialog.Trigger>
  <Dialog.Content class="max-w-2xl">
    <Dialog.Title>Add New Investment Type</Dialog.Title>
    <Dialog.Description>
      Add a new investment type to categorize your investments. Names should be unique.
    </Dialog.Description>

    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <Label for="name">Name</Label>
        <Input id="name" bind:value={formData.name} maxlength={100} />
      </div>

      <div class="flex flex-col gap-2">
        <Label for="description">Description</Label>
        <Textarea id="description" bind:value={formData.description} />
      </div>

      <div class="flex flex-col gap-2">
        <Label for="expenseRatio">Expense Ratio</Label>
        <Input
          id="expenseRatio"
          type="number"
          step="0.01"
          min="0"
          bind:value={formData.expenseRatio}
        />
      </div>

      <div class="flex items-center gap-2">
        <Label for="returnAmtOrPct">Return Amount or Percentage</Label>
        <Switch id="returnAmtOrPct" bind:checked={returnIsAmount} />
        <span class="text-muted-foreground text-sm">
          {returnIsAmount ? 'Amount' : 'Percentage'}
        </span>
      </div>

      <div class="flex flex-col gap-2">
        <Label>Return Distribution</Label>
        <Tabs.Root bind:value={formData.returnDistribution.type}>
          <Tabs.List class="w-full">
            <Tabs.Trigger value="fixed">Fixed</Tabs.Trigger>
            <Tabs.Trigger value="normal">Normal</Tabs.Trigger>
            <Tabs.Trigger value="uniform">Uniform</Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content value="fixed">
            <div class="flex flex-col gap-2">
              <Label>Fixed Return Value ({returnIsAmount ? '$' : '%'})</Label>
              <Input type="number" step="0.01" bind:value={formData.returnDistribution.value} />
            </div>
          </Tabs.Content>
          <Tabs.Content value="normal" class="flex flex-row gap-3">
            <div class="flex flex-grow flex-col gap-2">
              <Label>Mean Return ({returnIsAmount ? '$' : '%'})</Label>
              <Input type="number" step="0.01" bind:value={formData.returnDistribution.mean} />
            </div>
            <div class="flex flex-grow flex-col gap-2">
              <Label>Standard Deviation ({returnIsAmount ? '$' : '%'})</Label>
              <Input
                type="number"
                step="0.01"
                min="0"
                bind:value={formData.returnDistribution.stdev}
              />
            </div>
          </Tabs.Content>
          <Tabs.Content value="uniform" class="flex flex-row gap-3">
            <div class="flex flex-grow flex-col gap-2">
              <Label>Lower Bound ({returnIsAmount ? '$' : '%'})</Label>
              <Input type="number" step="0.01" bind:value={formData.returnDistribution.lower} />
            </div>
            <div class="flex flex-grow flex-col gap-2">
              <Label>Upper Bound ({returnIsAmount ? '$' : '%'})</Label>
              <Input type="number" step="0.01" bind:value={formData.returnDistribution.upper} />
            </div>
          </Tabs.Content>
        </Tabs.Root>
      </div>

      <div class="flex items-center gap-2">
        <Label for="incomeAmtOrPct">Income Amount or Percentage</Label>
        <Switch id="incomeAmtOrPct" bind:checked={incomeIsAmount} />
        <span class="text-muted-foreground text-sm">
          {incomeIsAmount ? 'Amount' : 'Percentage'}
        </span>
      </div>

      <div class="flex flex-col gap-2">
        <Label>Income Distribution</Label>
        <Tabs.Root bind:value={formData.incomeDistribution.type}>
          <Tabs.List class="w-full">
            <Tabs.Trigger value="fixed">Fixed</Tabs.Trigger>
            <Tabs.Trigger value="normal">Normal</Tabs.Trigger>
            <Tabs.Trigger value="uniform">Uniform</Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content value="fixed">
            <div class="flex flex-col gap-2">
              <Label>Fixed Income Value ({incomeIsAmount ? '$' : '%'})</Label>
              <Input type="number" step="0.01" bind:value={formData.incomeDistribution.value} />
            </div>
          </Tabs.Content>
          <Tabs.Content value="normal" class="flex flex-row gap-3">
            <div class="flex flex-grow flex-col gap-2">
              <Label>Mean Income ({incomeIsAmount ? '$' : '%'})</Label>
              <Input type="number" step="0.01" bind:value={formData.incomeDistribution.mean} />
            </div>
            <div class="flex flex-grow flex-col gap-2">
              <Label>Standard Deviation ({incomeIsAmount ? '$' : '%'})</Label>
              <Input
                type="number"
                step="0.01"
                min="0"
                bind:value={formData.incomeDistribution.stdev}
              />
            </div>
          </Tabs.Content>
          <Tabs.Content value="uniform" class="flex flex-row gap-3">
            <div class="flex flex-grow flex-col gap-2">
              <Label>Lower Bound ({incomeIsAmount ? '$' : '%'})</Label>
              <Input type="number" step="0.01" bind:value={formData.incomeDistribution.lower} />
            </div>
            <div class="flex flex-grow flex-col gap-2">
              <Label>Upper Bound ({incomeIsAmount ? '$' : '%'})</Label>
              <Input type="number" step="0.01" bind:value={formData.incomeDistribution.upper} />
            </div>
          </Tabs.Content>
        </Tabs.Root>
      </div>

      <div class="flex items-center gap-2">
        <Checkbox id="taxability" bind:checked={formData.taxability} />
        <Label for="taxability">Taxable</Label>
      </div>
    </div>

    <Dialog.Footer>
      <Button variant="outline" onclick={() => (open = false)}>Cancel</Button>
      <Button type="submit" onclick={handleSubmit}>Save Investment Type</Button>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>
