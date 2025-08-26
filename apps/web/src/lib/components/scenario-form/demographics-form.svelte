<script lang="ts">
  import { putApiScenariosIdBody } from '$lib/api/scenario-management/scenarios/scenarios.zod';
  import * as Form from '$lib/components/ui/form';
  import type { SuperForm } from 'sveltekit-superforms';
  import z from 'zod';
  import { Checkbox } from '../ui/checkbox';
  import { Input } from '../ui/input';
  import LifeExpectancy from './life-expectancy.svelte';

  type ScenariosCreateBody = z.infer<typeof putApiScenariosIdBody>;

  const {
    form
  }: {
    form: SuperForm<ScenariosCreateBody>;
  } = $props();
  const { form: formData } = form;

  $formData.userBirthYear = $formData.userBirthYear || new Date().getFullYear() - 30;
  let isMarried = $state({
    get value() {
      return $formData.scenarioType === 'MarriedCouple';
    },
    set value(newValue: boolean) {
      $formData.scenarioType = newValue ? 'MarriedCouple' : 'Individual';
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
  <div class="flex w-full flex-row gap-3">
    <Form.Field {form} name="userBirthYear" class="flex-grow">
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
    {#if $formData.scenarioType === 'MarriedCouple'}
      <Form.Field {form} name="spouseBirthYear" class="flex-grow">
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
    {/if}
  </div>
  <LifeExpectancy {form} isMarried={isMarried.value} />
</div>
