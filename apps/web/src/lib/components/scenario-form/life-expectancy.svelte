<script lang="ts">
  import * as Form from '$lib/components/ui/form';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Switch } from '$lib/components/ui/switch';
  import type { SuperForm } from 'sveltekit-superforms';
  import { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import { z } from 'zod';
  import * as Card from '../ui/card';

  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;

  const {
    form,
    isMarried
  }: {
    form: SuperForm<ScenariosCreateBody>;
    isMarried: boolean;
  } = $props();
  const { form: formData } = form;

  let isSelfNormalDistribution = $state({
    get value() {
      return $formData.userLifeExpectancy.type === 'normal';
    },
    set value(newValue: boolean) {
      $formData.userLifeExpectancy.type = newValue ? 'normal' : 'fixed';
      if (newValue) {
        $formData.userLifeExpectancy.value = null;
      } else {
        $formData.userLifeExpectancy.mean = null;
        $formData.userLifeExpectancy.stdev = null;
      }
    }
  });

  let isSpouseNormalDistribution = $state({
    get value() {
      return $formData.spouseLifeExpectancy?.type === 'normal';
    },
    set value(newValue: boolean) {
      if (!$formData.spouseLifeExpectancy) return;
      $formData.spouseLifeExpectancy.type = newValue ? 'normal' : 'fixed';
      if (newValue) {
        $formData.spouseLifeExpectancy.value = null;
      } else {
        $formData.spouseLifeExpectancy.mean = null;
        $formData.spouseLifeExpectancy.stdev = null;
      }
    }
  });
</script>

<Card.Root>
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
        <span class="text-muted-foreground text-sm">
          {isSelfNormalDistribution.value ? 'Normal (mean ± std dev)' : 'Fixed value'}
        </span>
      </div>

      <!-- Life Expectancy Fields -->
      <div class="space-y-3">
        {#if isSelfNormalDistribution.value}
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
        {:else}
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
{#if isMarried}
  <Card.Root>
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
          <span class="text-muted-foreground text-sm">
            {isSpouseNormalDistribution.value ? 'Normal (mean ± std dev)' : 'Fixed value'}
          </span>
        </div>

        <!-- Life Expectancy Fields -->
        <div class="space-y-3">
          {#if isSpouseNormalDistribution.value}
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
          {:else}
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
