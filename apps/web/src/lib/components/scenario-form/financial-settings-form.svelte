<script lang="ts">
  import type { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import * as Form from '$lib/components/ui/form';
  import type { SuperForm } from 'sveltekit-superforms';
  import z from 'zod';
  import * as Tabs from '$lib/components/ui/tabs';
  import { Input } from '../ui/input';
  import { Switch } from '../ui/switch';
  import { Label } from '../ui/label';

  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;

  const {
    form
  }: {
    form: SuperForm<ScenariosCreateBody>;
  } = $props();
  const { form: formData } = form;
</script>

<div class="flex flex-col gap-3">
  <h2 class="text-xl font-bold">Inflation Assumption</h2>

  <Tabs.Root bind:value={$formData.inflationAssumption.type}>
    <Tabs.List class="w-full">
      <Tabs.Trigger value="fixed">Fixed</Tabs.Trigger>
      <Tabs.Trigger value="normal">Normal</Tabs.Trigger>
      <Tabs.Trigger value="uniform">Uniform</Tabs.Trigger>
    </Tabs.List>
    <Tabs.Content value="fixed">
      <Form.Field {form} name="inflationAssumption.value">
        <Form.Control>
          <Form.Label>Fixed Inflation Rate (%)</Form.Label>
          <Input
            type="number"
            step="0.01"
            min="-5"
            max="20"
            bind:value={$formData.inflationAssumption.value}
          />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
    </Tabs.Content>
    <Tabs.Content value="normal" class="flex flex-row gap-3">
      <Form.Field {form} name="inflationAssumption.mean" class="flex-grow">
        <Form.Control>
          <Form.Label>Mean Inflation Rate (%)</Form.Label>
          <Input type="number" step="0.01" bind:value={$formData.inflationAssumption.mean} />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
      <Form.Field {form} name="inflationAssumption.stdev" class="flex-grow">
        <Form.Control>
          <Form.Label>Standard Deviation (%)</Form.Label>
          <Input
            type="number"
            step="0.01"
            min="0"
            bind:value={$formData.inflationAssumption.stdev}
          />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
    </Tabs.Content>
    <Tabs.Content value="uniform" class="flex flex-row gap-3">
      <Form.Field {form} name="inflationAssumption.lower" class="flex-grow">
        <Form.Control>
          <Form.Label>Lower Bound (%)</Form.Label>
          <Input type="number" step="0.01" bind:value={$formData.inflationAssumption.lower} />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
      <Form.Field {form} name="inflationAssumption.upper" class="flex-grow">
        <Form.Control>
          <Form.Label>Upper Bound (%)</Form.Label>
          <Input type="number" step="0.01" bind:value={$formData.inflationAssumption.upper} />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
    </Tabs.Content>
  </Tabs.Root>

  <h2 class="text-xl font-bold">Financial Settings</h2>
  <Form.Field {form} name="afterTaxContributionLimit">
    <Form.Control>
      <Form.Label>After Tax Contribution Limit ($ USD)</Form.Label>
      <Input
        type="string"
        placeholder="Enter after tax contribution limit here"
        bind:value={$formData.afterTaxContributionLimit}
      />
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>
  <Form.Field {form} name="financialGoal">
    <Form.Control>
      <Form.Label>Financial Goal ($ USD)</Form.Label>
      <Input
        type="string"
        placeholder="Enter financial goal here"
        bind:value={$formData.financialGoal}
      />
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>

  <h2 class="text-xl font-bold">Roth Conversion Optimizer</h2>

  <Label>Roth Conversion Optimizer</Label>
  <Form.Field {form} name="rothConversionOpt">
    <Form.Control>
      <Form.Label>Enable Roth Conversion Optimization</Form.Label>
      <Switch bind:checked={$formData.rothConversionOpt} />
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>
  {#if $formData.rothConversionOpt}
    <div class="flex flex-row gap-3">
      <Form.Field {form} name="rothConversionStart" class="flex-grow">
        <Form.Control>
          <Form.Label>Conversion Start Year</Form.Label>
          <Input
            type="number"
            placeholder="Start Year"
            min={new Date().getFullYear()}
            max={new Date().getFullYear() + 100}
            bind:value={$formData.rothConversionStart}
          />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
      <Form.Field {form} name="rothConversionEnd" class="flex-grow">
        <Form.Control>
          <Form.Label>Conversion End Year</Form.Label>
          <Input
            type="number"
            placeholder="End Year"
            min={$formData.rothConversionStart
              ? Number($formData.rothConversionStart) + 1
              : new Date().getFullYear() + 1}
            max={new Date().getFullYear() + 100}
            bind:value={$formData.rothConversionEnd}
          />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
    </div>
  {/if}
</div>
