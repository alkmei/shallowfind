<script lang="ts">
  import * as Form from '$lib/components/ui/form';
  import type { SuperForm } from 'sveltekit-superforms';
  import { Checkbox } from '$lib/components/ui/checkbox';
  import { Input } from '$lib/components/ui/input';
  import LifeExpectancy from './life-expectancy.svelte';
  import type { ScenarioForm } from './schema';

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
    {#if $formData.scenarioType === 'married_couple'}
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

    <LifeExpectancy {form} />
  </div>
</div>
