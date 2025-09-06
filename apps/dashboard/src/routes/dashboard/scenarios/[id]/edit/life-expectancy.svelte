<script lang="ts">
  import * as Form from '$lib/components/ui/form';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Switch } from '$lib/components/ui/switch';
  import type { SuperForm } from 'sveltekit-superforms';
  import * as Card from '$lib/components/ui/card';
  import type { ScenarioForm } from './schema';

  const {
    form
  }: {
    form: SuperForm<ScenarioForm>;
  } = $props();
  const { form: formData } = form;

  let isSelfNormalDistribution = $state({
    get value() {
      return $formData.userLifeExpectancy.type === 'normal';
    },
    set value(newValue: boolean) {
      $formData.userLifeExpectancy.type = newValue ? 'normal' : 'fixed';
    }
  });

  let isSpouseNormalDistribution = $state({
    get value() {
      return $formData.spouseLifeExpectancy?.type === 'normal';
    },
    set value(newValue: boolean) {
      if (!$formData.spouseLifeExpectancy) return;
      $formData.spouseLifeExpectancy.type = newValue ? 'normal' : 'fixed';
    }
  });

  formData.update(
    (form) => {
      if (!form.userLifeExpectancy) {
        form.userLifeExpectancy = { type: 'fixed', value: 78 };
      }
      if (form.scenarioType === 'married_couple' && !form.spouseLifeExpectancy) {
        form.spouseLifeExpectancy = { type: 'fixed', value: 78 };
      }
      return form;
    },
    { taint: false }
  );
</script>

<Card.Root class="w-full">
  <Card.Header>
    <Card.Title>Life Expectancy</Card.Title>
    <Card.Description>
      Set the life expectancy for the user. This can be a fixed value or a normal distribution.
    </Card.Description>
  </Card.Header>
  <Card.Content>
    <div class="space-y-4">
      <!-- Distribution Type Switch -->
      <div class="flex items-center space-x-2">
        <Label for="distribution-switch">Use Normal Distribution</Label>
        <Switch id="distribution-switch" bind:checked={isSelfNormalDistribution.value} />
        <span class="text-sm text-muted-foreground">
          {isSelfNormalDistribution.value ? 'Normal (mean ± std dev)' : 'Fixed value'}
        </span>
      </div>

      <!-- Life Expectancy Fields -->
      <div class="space-y-3">
        {#if $formData.userLifeExpectancy.type === 'normal'}
          <!-- Normal Distribution Fields -->
          <div class="grid grid-cols-2 gap-3">
            <Form.Field {form} name="userLifeExpectancy.mean">
              <Form.Control>
                <Form.Label>Mean Age</Form.Label>
                <Input
                  type="number"
                  bind:value={$formData.userLifeExpectancy.mean}
                  min="1"
                  max="120"
                  placeholder="e.g., 78"
                />
              </Form.Control>
              <Form.FieldErrors />
              <Form.Description>
                Normal distribution allows for uncertainty in life expectancy. Most values will fall
                within 2 standard deviations of the mean.
              </Form.Description>
            </Form.Field>

            <Form.Field {form} name="userLifeExpectancy.stdev">
              <Form.Control>
                <Form.Label>Standard Deviation</Form.Label>
                <Input
                  type="number"
                  bind:value={$formData.userLifeExpectancy.stdev}
                  min="0.1"
                  max="20"
                  step="0.1"
                  placeholder="e.g., 5"
                />
              </Form.Control>
              <Form.FieldErrors />
            </Form.Field>
          </div>
        {:else if $formData.userLifeExpectancy.type === 'fixed'}
          <!-- Fixed Distribution Field -->
          <Form.Field {form} name="userLifeExpectancy.value">
            <Form.Control>
              <Form.Label>Life Expectancy (Years)</Form.Label>
              <Input
                type="number"
                bind:value={$formData.userLifeExpectancy.value}
                min="1"
                max="120"
                placeholder="e.g., 78"
              />
            </Form.Control>
            <Form.Description>Enter a fixed life expectancy value in years.</Form.Description>
            <Form.FieldErrors />
          </Form.Field>
        {/if}
      </div>
    </div>
  </Card.Content>
</Card.Root>

{#if $formData.scenarioType === 'married_couple'}
  <Card.Root class="w-full">
    <Card.Header>
      <Card.Title>Spouse Life Expectancy</Card.Title>
      <Card.Description>
        Set the life expectancy for the spouse. This can be a fixed value or a normal distribution.
      </Card.Description>
    </Card.Header>
    <Card.Content>
      <div class="space-y-4">
        <!-- Distribution Type Switch -->
        <div class="flex items-center space-x-2">
          <Label for="distribution-switch">Use Normal Distribution</Label>
          <Switch id="distribution-switch" bind:checked={isSpouseNormalDistribution.value} />
          <span class="text-sm text-muted-foreground">
            {isSpouseNormalDistribution.value ? 'Normal (mean ± std dev)' : 'Fixed value'}
          </span>
        </div>

        <!-- Life Expectancy Fields -->
        <div class="space-y-3">
          {#if $formData.spouseLifeExpectancy?.type === 'normal'}
            <!-- Normal Distribution Fields -->
            <div class="grid grid-cols-2 gap-3">
              <Form.Field {form} name="spouseLifeExpectancy.mean">
                <Form.Control>
                  <Form.Label>Mean Age</Form.Label>
                  <Input
                    type="number"
                    bind:value={$formData.spouseLifeExpectancy!.mean}
                    min="1"
                    max="120"
                    placeholder="e.g., 78"
                  />
                </Form.Control>
                <Form.FieldErrors />
                <Form.Description>
                  Normal distribution allows for uncertainty in life expectancy. Most values will
                  fall within 2 standard deviations of the mean.
                </Form.Description>
              </Form.Field>

              <Form.Field {form} name="spouseLifeExpectancy.stdev">
                <Form.Control>
                  <Form.Label>Standard Deviation</Form.Label>
                  <Input
                    type="number"
                    bind:value={$formData.spouseLifeExpectancy!.stdev}
                    min="0.1"
                    max="20"
                    step="0.1"
                    placeholder="e.g., 5"
                  />
                </Form.Control>
                <Form.FieldErrors />
              </Form.Field>
            </div>
          {:else if $formData.spouseLifeExpectancy?.type === 'fixed'}
            <!-- Fixed Distribution Field -->
            <Form.Field {form} name="spouseLifeExpectancy.value">
              <Form.Control>
                <Form.Label>Life Expectancy (Years)</Form.Label>
                <Input
                  type="number"
                  bind:value={$formData.spouseLifeExpectancy!.value}
                  min="1"
                  max="120"
                  placeholder="e.g., 78"
                />
              </Form.Control>
              <Form.Description>Enter a fixed life expectancy value in years.</Form.Description>
              <Form.FieldErrors />
            </Form.Field>
          {/if}
        </div>
      </div>
    </Card.Content>
  </Card.Root>
{/if}
