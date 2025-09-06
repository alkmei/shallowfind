<script lang="ts">
  import * as Dialog from '$lib/components/ui/dialog';
  import * as Tabs from '$lib/components/ui/tabs';
  import * as Form from '$lib/components/ui/form';
  import { Button } from '$lib/components/ui/button';
  import { Label } from '$lib/components/ui/label';
  import { Input } from '$lib/components/ui/input';
  import { Textarea } from '$lib/components/ui/textarea';
  import { Plus } from '@lucide/svelte';
  import { Switch } from '$lib/components/ui/switch';
  import { Checkbox } from '$lib/components/ui/checkbox';
  import { investmentTypeSchema } from './schema';
  import { superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
  import { zod4Client } from 'sveltekit-superforms/adapters';
  import type { PageProps } from './$types';

  const { data }: PageProps = $props();

  let open = $state(false);

  let returnIsAmount = $state(false);
  let incomeIsAmount = $state(false);

  let { investmentTypeForm } = data;

  const form = superForm(investmentTypeForm, {
    validators: zod4Client(investmentTypeSchema),
    dataType: 'json'
  });
  let { form: formData, enhance } = form;

  let isTaxable = $state({
    get value() {
      return $formData.taxability === 'taxable';
    },
    set value(newValue: boolean) {
      $formData.taxability = newValue ? 'taxable' : 'tax_exempt';
    }
  });
</script>

<Dialog.Root bind:open>
  <Dialog.Trigger>
    <Button class="w-48"><Plus /> New Investment Type</Button>
  </Dialog.Trigger>
  <Dialog.Content class="max-w-2xl">
    <form method="POST" use:enhance>
      <Dialog.Title>Add New Investment Type</Dialog.Title>
      <Dialog.Description>
        Add a new investment type to categorize your investments. Names should be unique.
      </Dialog.Description>
      <div class="flex flex-col gap-4">
        <Form.Field {form} name="name" class="flex flex-col gap-2">
          <Form.Control>
            <Form.Label>Name</Form.Label>
            <Input bind:value={$formData.name} maxlength={100} />
          </Form.Control>
        </Form.Field>
        <Form.Field {form} name="description" class="flex flex-col gap-2">
          <Form.Control>
            <Form.Label>Description</Form.Label>
            <Textarea bind:value={$formData.description} />
          </Form.Control>
        </Form.Field>
        <Form.Field {form} name="expenseRatio" class="flex flex-col gap-2">
          <Form.Control>
            <Form.Label>Expense Ratio</Form.Label>
            <Input type="number" step="0.01" min="0" bind:value={$formData.expenseRatio} />
          </Form.Control>
        </Form.Field>
        <Form.Field {form} name="returnPercent" class="flex items-center gap-2">
          <Form.Label>Return Amount or Percentage</Form.Label>
          <Switch bind:checked={$formData.returnPercent} />
          <span class="text-sm text-muted-foreground">
            {$formData.returnPercent ? 'Percentage' : 'Amount'}
          </span>
        </Form.Field>
        <div class="flex flex-col gap-2">
          <Label>Return Distribution</Label>
          <Tabs.Root bind:value={$formData.expectedAnnualReturn.type}>
            <Tabs.List class="w-full">
              <Tabs.Trigger value="fixed">Fixed</Tabs.Trigger>
              <Tabs.Trigger value="normal">Normal</Tabs.Trigger>
              <Tabs.Trigger value="uniform">Uniform</Tabs.Trigger>
            </Tabs.List>
            <Tabs.Content value="fixed">
              {#if $formData.expectedAnnualReturn.type === 'fixed'}
                <Form.Field {form} name="expectedAnnualReturn.value" class="flex flex-col gap-2">
                  <Form.Label>
                    Fixed Return Value ({$formData.returnPercent ? '%' : '$'})
                  </Form.Label>
                  <Input
                    type="number"
                    step="0.01"
                    bind:value={$formData.expectedAnnualReturn.value}
                  />
                </Form.Field>
              {/if}
            </Tabs.Content>
            <Tabs.Content value="normal" class="flex flex-row gap-3">
              {#if $formData.expectedAnnualReturn.type === 'normal'}
                <Form.Field
                  {form}
                  name="expectedAnnualReturn.mean"
                  class="flex flex-grow flex-col gap-2"
                >
                  <Form.Label>Mean Return ({returnIsAmount ? '$' : '%'})</Form.Label>
                  <Input
                    type="number"
                    step="0.01"
                    bind:value={$formData.expectedAnnualReturn.mean}
                  />
                </Form.Field>
                <Form.Field
                  {form}
                  name="expectedAnnualReturn.stdev"
                  class="flex flex-grow flex-col gap-2"
                >
                  <Form.Label>Standard Deviation ({returnIsAmount ? '$' : '%'})</Form.Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    bind:value={$formData.expectedAnnualReturn.stdev}
                  />
                </Form.Field>
              {/if}
            </Tabs.Content>
            <Tabs.Content value="uniform" class="flex flex-row gap-3">
              {#if $formData.expectedAnnualIncome.type === 'uniform'}
                <Form.Field
                  {form}
                  name="expectedAnnualIncome.min"
                  class="flex flex-grow flex-col gap-2"
                >
                  <Label>Lower Bound ({returnIsAmount ? '$' : '%'})</Label>
                  <Input
                    type="number"
                    step="0.01"
                    bind:value={$formData.expectedAnnualIncome.min}
                  />
                </Form.Field>
                <Form.Field
                  {form}
                  name="expectedAnnualIncome.max"
                  class="flex flex-grow flex-col gap-2"
                >
                  <Label>Upper Bound ({returnIsAmount ? '$' : '%'})</Label>
                  <Input
                    type="number"
                    step="0.01"
                    bind:value={$formData.expectedAnnualIncome.max}
                  />
                </Form.Field>
              {/if}
            </Tabs.Content>
          </Tabs.Root>
        </div>
        <Form.Field {form} name="incomePercent" class="flex items-center gap-2">
          <Form.Label>Income Amount or Percentage</Form.Label>
          <Switch bind:checked={$formData.incomePercent} />
          <span class="text-sm text-muted-foreground">
            {$formData.incomePercent ? 'Percentage' : 'Amount'}
          </span>
        </Form.Field>
        <div class="flex flex-col gap-2">
          <Label>Income Distribution</Label>
          <Tabs.Root bind:value={$formData.expectedAnnualIncome.type}>
            <Tabs.List class="w-full">
              <Tabs.Trigger value="fixed">Fixed</Tabs.Trigger>
              <Tabs.Trigger value="normal">Normal</Tabs.Trigger>
              <Tabs.Trigger value="uniform">Uniform</Tabs.Trigger>
            </Tabs.List>
            <Tabs.Content value="fixed">
              {#if $formData.expectedAnnualIncome.type === 'fixed'}
                <Form.Field {form} name="expectedAnnualIncome.value" class="flex flex-col gap-2">
                  <Form.Label>Fixed Income Value ({incomeIsAmount ? '$' : '%'})</Form.Label>
                  <Input
                    type="number"
                    step="0.01"
                    bind:value={$formData.expectedAnnualIncome.value}
                  />
                </Form.Field>
              {/if}
            </Tabs.Content>
            <Tabs.Content value="normal" class="flex flex-row gap-3">
              {#if $formData.expectedAnnualIncome.type === 'normal'}
                <Form.Field
                  {form}
                  name="expectedAnnualIncome.mean"
                  class="flex flex-grow flex-col gap-2"
                >
                  <Form.Label>Mean Income ({incomeIsAmount ? '$' : '%'})</Form.Label>
                  <Input
                    type="number"
                    step="0.01"
                    bind:value={$formData.expectedAnnualIncome.mean}
                  />
                </Form.Field>
                <Form.Field
                  {form}
                  name="expectedAnnualIncome.stdev"
                  class="flex flex-grow flex-col gap-2"
                >
                  <Form.Label>Standard Deviation ({incomeIsAmount ? '$' : '%'})</Form.Label>
                  <Input
                    type="number"
                    step="0.01"
                    min="0"
                    bind:value={$formData.expectedAnnualIncome.stdev}
                  />
                </Form.Field>
              {/if}
            </Tabs.Content>
            <Tabs.Content value="uniform" class="flex flex-row gap-3">
              {#if $formData.expectedAnnualIncome.type === 'uniform'}
                <Form.Field
                  {form}
                  name="expectedAnnualIncome.min"
                  class="flex flex-grow flex-col gap-2"
                >
                  <Form.Label>Lower Bound ({incomeIsAmount ? '$' : '%'})</Form.Label>
                  <Input
                    type="number"
                    step="0.01"
                    bind:value={$formData.expectedAnnualIncome.min}
                  />
                </Form.Field>
                <Form.Field
                  {form}
                  name="expectedAnnualIncome.max"
                  class="flex flex-grow flex-col gap-2"
                >
                  <Form.Label>Upper Bound ({incomeIsAmount ? '$' : '%'})</Form.Label>
                  <Input
                    type="number"
                    step="0.01"
                    bind:value={$formData.expectedAnnualIncome.max}
                  />
                </Form.Field>
              {/if}
            </Tabs.Content>
          </Tabs.Root>
        </div>
        <Form.Field {form} name="taxability" class="flex items-center gap-2">
          <Form.Label>Taxable</Form.Label>
          <Checkbox bind:checked={isTaxable.value} />
        </Form.Field>
      </div>
      <Dialog.Footer>
        <Button variant="outline" onclick={() => (open = false)}>Cancel</Button>
        <Form.Button type="submit">Save Investment Type</Form.Button>
      </Dialog.Footer>
    </form>
  </Dialog.Content>
</Dialog.Root>
