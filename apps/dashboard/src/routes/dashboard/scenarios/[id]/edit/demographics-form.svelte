<script lang="ts">
  import * as Form from '$lib/components/ui/form';
  import type { SuperForm } from 'sveltekit-superforms';
  import { Checkbox } from '$lib/components/ui/checkbox';
  import { Input } from '$lib/components/ui/input';
  import type { ScenarioForm } from './schema';
  import * as Card from '$lib/components/ui/card';
  import { Label } from '$lib/components/ui/label';
  import { Switch } from '$lib/components/ui/switch';

  const {
    form
  }: {
    form: SuperForm<ScenarioForm>;
  } = $props();
  const { form: formData } = form;

  $formData.userBirthYear = $formData.userBirthYear || new Date().getFullYear() - 30;
  formData.update((form) => {
    if (form.scenarioType === 'individual') {
      form.spouseBirthYear = undefined;
      form.spouseLifeExpectancy = undefined;
    } else {
      if (!form.spouseBirthYear) form.spouseBirthYear = new Date().getFullYear() - 30;
    }

    return form;
  });

  let isMarried = $state({
    get value() {
      return $formData.scenarioType === 'married_couple';
    },
    set value(newValue: boolean) {
      $formData.scenarioType = newValue ? 'married_couple' : 'individual';
    }
  });

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
</script>

<div class="flex flex-col gap-3">
  <h2 class="text-xl font-bold">Demographic Information</h2>
  <Form.Field {form} name="scenarioType" class="flex items-center gap-2">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>is Married?</Form.Label>
        <Checkbox {...props} bind:checked={isMarried.value} />
      {/snippet}
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>

  <div class="grid grid-cols-2 gap-3">
    <div
      class="{$formData.scenarioType === 'married_couple' ? 'col-span-1' : 'col-span-2'} space-y-4"
    >
      <Form.Field {form} name="userBirthYear" class="col-span-1">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>User Birth Year <span class="text-red-500">*</span></Form.Label>
            <Input
              type="number"
              min="1900"
              max={new Date().getFullYear()}
              {...props}
              bind:value={$formData.userBirthYear}
            />
          {/snippet}
        </Form.Control>
        <Form.Description>Enter your birth year.</Form.Description>
        <Form.FieldErrors />
      </Form.Field>
      <Card.Root class="w-full">
        <Card.Header>
          <Card.Title>Life Expectancy</Card.Title>
          <Card.Description>
            Set the life expectancy for the user. This can be a fixed value or a normal
            distribution.
          </Card.Description>
        </Card.Header>
        <Card.Content>
          <div class="space-y-4">
            <!-- Distribution Type Switch -->
            <div class="flex items-center space-x-2">
              <Label for="distribution-switch">Distribution Type</Label>
              <Switch id="distribution-switch" bind:checked={isSelfNormalDistribution.value} />
              <span class="text-muted-foreground text-sm">
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
                      Normal distribution allows for uncertainty in life expectancy. Most values
                      will fall within 2 standard deviations of the mean.
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
    </div>

    {#if $formData.scenarioType === 'married_couple'}
      <div class="">
        <Form.Field {form} name="spouseBirthYear">
          <Form.Control>
            {#snippet children({ props })}
              <Form.Label>Spouse Birth Year <span class="text-red-500">*</span></Form.Label>
              <Input
                type="number"
                min="1900"
                max={new Date().getFullYear()}
                defaultValue={new Date().getFullYear() - 30}
                {...props}
                bind:value={$formData.spouseBirthYear}
              />
            {/snippet}
          </Form.Control>
          <Form.Description>Enter the birth year of your spouse.</Form.Description>
          <Form.FieldErrors />
        </Form.Field>
        <Card.Root class="w-full">
          <Card.Header>
            <Card.Title>Spouse Life Expectancy</Card.Title>
            <Card.Description>
              Set the life expectancy for the spouse. This can be a fixed value or a normal
              distribution.
            </Card.Description>
          </Card.Header>
          <Card.Content>
            <div class="space-y-4">
              <!-- Distribution Type Switch -->
              <div class="flex items-center space-x-2">
                <Label for="distribution-switch">Distribution Type</Label>
                <Switch id="distribution-switch" bind:checked={isSpouseNormalDistribution.value} />
                <span class="text-muted-foreground text-sm">
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
                        Normal distribution allows for uncertainty in life expectancy. Most values
                        will fall within 2 standard deviations of the mean.
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
                    <Form.Description
                      >Enter a fixed life expectancy value in years.</Form.Description
                    >
                    <Form.FieldErrors />
                  </Form.Field>
                {/if}
              </div>
            </div>
          </Card.Content>
        </Card.Root>
      </div>
    {/if}
  </div>
</div>
