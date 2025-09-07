<script lang="ts">
  import { superForm } from 'sveltekit-superforms';
  import * as Dialog from '$lib/components/ui/dialog';
  import * as Form from '$lib/components/ui/form';
  import * as Select from '$lib/components/ui/select';
  import { Button, buttonVariants } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Plus } from '@lucide/svelte';
  import type { PageProps } from './$types';
  import { zod4Client } from 'sveltekit-superforms/adapters';
  import { investmentSchema } from './schema';
  import * as RadioGroup from '$lib/components/ui/radio-group';
  import { Label } from '$lib/components/ui/label';

  const { data }: PageProps = $props();

  const investmentForm = superForm(data.investmentForm, {
    validators: zod4Client(investmentSchema)
  });

  const { form: formData, enhance } = investmentForm;

  let open = $state(false);

  const taxStatusOptions = [
    { value: 'non_retirement', label: 'Non-retirement' },
    { value: 'pre_tax_retirement', label: 'Pre-tax Retirement' },
    { value: 'after_tax_retirement', label: 'After-tax Retirement' }
  ];
</script>

<Dialog.Root bind:open>
  <Dialog.Trigger class={'w-48' + buttonVariants({ variant: 'default' })} type="button">
    <Plus /> New Investment
  </Dialog.Trigger>
  <Dialog.Content class="max-w-xl">
    <Dialog.Title>Add New Investment</Dialog.Title>
    <Dialog.Description>
      Add a new investment to your scenario. Select an investment type and enter the details.
    </Dialog.Description>

    <form method="POST" use:enhance action="?/investment" class="flex flex-col gap-4">
      <Form.Field form={investmentForm} name="name">
        <Form.Control>
          <Form.Label>Investment Name *</Form.Label>
          <Input placeholder="e.g., My 401(k)" bind:value={$formData.name} />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>

      <Form.Field form={investmentForm} name="currentValue">
        <Form.Control>
          <Form.Label>Current Value ($)</Form.Label>
          <Input placeholder="e.g., 10000" bind:value={$formData.currentValue} />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>

      <Form.Field form={investmentForm} name="investmentTypeId">
        <Form.Control>
          <Form.Label>Investment Type *</Form.Label>
          <Select.Root bind:value={$formData.investmentTypeId} type="single">
            <Select.Trigger class="w-full" aria-label="Investment Type">
              {$formData.investmentTypeId
                ? data.scenario.investmentTypes.find(
                    (type) => type.id === $formData.investmentTypeId
                  )?.name
                : 'Select an investment type'}
            </Select.Trigger>
            <Select.Content>
              {#each data.scenario.investmentTypes as type (type.id)}
                <Select.Item value={type.id}>
                  {type.name}
                </Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>

      <Form.Field form={investmentForm} name="accountTaxStatus">
        <Form.Control>
          <Form.Label>Tax Status</Form.Label>
          <RadioGroup.Root bind:value={$formData.accountTaxStatus}>
            {#each taxStatusOptions as option (option.value)}
              <div class="flex items-center space-x-2">
                <RadioGroup.Item value={option.value} id={option.value} />
                <Label for={option.value}>
                  {option.label}
                </Label>
              </div>
            {/each}
          </RadioGroup.Root>
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>

      <Dialog.Footer>
        <Dialog.Close>
          <Button type="button" variant="outline">Cancel</Button>
        </Dialog.Close>
        <Form.Button type="submit">Add Investment</Form.Button>
      </Dialog.Footer>
    </form>
  </Dialog.Content>
</Dialog.Root>
