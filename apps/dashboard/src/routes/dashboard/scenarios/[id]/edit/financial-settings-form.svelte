<script lang="ts">
  import * as Form from '$lib/components/ui/form';
  import * as Card from '$lib/components/ui/card';
  import type { SuperForm } from 'sveltekit-superforms';
  import * as Tabs from '$lib/components/ui/tabs';
  import { Input } from '$lib/components/ui/input';
  import { Switch } from '$lib/components/ui/switch';
  import { Label } from '$lib/components/ui/label';
  import type { ScenarioForm } from './schema';

  const {
    form
  }: {
    form: SuperForm<ScenarioForm>;
  } = $props();
  const { form: formData } = form;
</script>

<div class="flex flex-col gap-3">
  <h2 class="text-xl font-bold">Financial Settings</h2>

  <Card.Root>
    <Card.Header>
      <Card.Title>Inflation Assumption Type</Card.Title>
      <Card.Description>
        Select the type of inflation assumption to use in the simulation.
      </Card.Description>
    </Card.Header>
    <Card.Content>
      <Tabs.Root bind:value={$formData.inflationAssumption.type}>
        <Tabs.List class="w-full">
          <Tabs.Trigger value="fixed">Fixed</Tabs.Trigger>
          <Tabs.Trigger value="normal">Normal</Tabs.Trigger>
          <Tabs.Trigger value="uniform">Uniform</Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="fixed">
          {#if $formData.inflationAssumption.type === 'fixed'}
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
          {/if}
        </Tabs.Content>
        <Tabs.Content value="normal" class="flex flex-row gap-3">
          {#if $formData.inflationAssumption.type === 'normal'}
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
          {/if}
        </Tabs.Content>
        <Tabs.Content value="uniform" class="flex flex-row gap-3">
          {#if $formData.inflationAssumption.type === 'uniform'}
            <Form.Field {form} name="inflationAssumption.min" class="flex-grow">
              <Form.Control>
                <Form.Label>Lower Bound (%)</Form.Label>
                <Input type="number" step="0.01" bind:value={$formData.inflationAssumption.min} />
              </Form.Control>
              <Form.FieldErrors />
            </Form.Field>
            <Form.Field {form} name="inflationAssumption.max" class="flex-grow">
              <Form.Control>
                <Form.Label>Upper Bound (%)</Form.Label>
                <Input type="number" step="0.01" bind:value={$formData.inflationAssumption.max} />
              </Form.Control>
              <Form.FieldErrors />
            </Form.Field>
          {/if}
        </Tabs.Content>
      </Tabs.Root>
    </Card.Content>
  </Card.Root>

  <Form.Field {form} name="annualRetirementContributionLimit">
    <Form.Control>
      <Form.Label>Annual Retirement Contribution Limit ($ USD)</Form.Label>
      <Input
        type="string"
        placeholder="Enter annual retirement contribution limit here"
        bind:value={$formData.annualRetirementContributionLimit}
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

  <Card.Root>
    <Card.Header>
      <Card.Title>Roth Conversion Optimizer</Card.Title>
      <Card.Description>
        Toggle to enable or disable the Roth Conversion Optimizer feature.
      </Card.Description>
    </Card.Header>
    <Card.Content>
      <Form.Field {form} name="rothOptimizerEnabled">
        <Form.Control>
          <Form.Label>Enable Roth Conversion Optimization</Form.Label>
          <Switch bind:checked={$formData.rothOptimizerEnabled} />
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
      {#if $formData.rothOptimizerEnabled}
        <div class="flex flex-row gap-3">
          <Form.Field {form} name="rothOptimizerStartYear" class="flex-grow">
            <Form.Control>
              <Form.Label>Conversion Start Year</Form.Label>
              <Input
                type="number"
                placeholder="Start Year"
                min={new Date().getFullYear()}
                max={new Date().getFullYear() + 100}
                bind:value={$formData.rothOptimizerStartYear}
              />
            </Form.Control>
            <Form.FieldErrors />
          </Form.Field>
          <Form.Field {form} name="rothOptimizerEndYear" class="flex-grow">
            <Form.Control>
              <Form.Label>Conversion End Year</Form.Label>
              <Input
                type="number"
                placeholder="End Year"
                min={$formData.rothOptimizerStartYear
                  ? Number($formData.rothOptimizerStartYear) + 1
                  : new Date().getFullYear() + 1}
                max={new Date().getFullYear() + 100}
                bind:value={$formData.rothOptimizerEndYear}
              />
            </Form.Control>
            <Form.FieldErrors />
          </Form.Field>
        </div>
      {/if}
    </Card.Content>
  </Card.Root>
</div>
