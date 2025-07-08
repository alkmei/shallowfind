<script lang="ts">
  import type { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import * as Form from '$lib/components/ui/form';
  import { Input } from '$lib/components/ui/input';
  import type { SuperForm } from 'sveltekit-superforms';
  import z from 'zod';
  import Checkbox from '../ui/checkbox/checkbox.svelte';
  import Textarea from '../ui/textarea/textarea.svelte';

  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;

  const {
    form
  }: {
    form: SuperForm<ScenariosCreateBody>;
  } = $props();
  const { form: formData } = form;

  $formData.userBirthYear = $formData.userBirthYear || new Date().getFullYear() - 30;
  let isMarried = $state({
    get value() {
      return $formData.maritalStatus === 'couple';
    },
    set value(newValue: boolean) {
      $formData.maritalStatus = newValue ? 'couple' : 'individual';
    }
  });
</script>

<div class="flex flex-col gap-3">
  <h2 class="text-xl font-bold">Basic Information</h2>
  <Form.Field {form} name="name">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Scenario Name <span class="text-red-500">*</span></Form.Label>
        <Input {...props} bind:value={$formData.name} />
      {/snippet}
    </Form.Control>
    <Form.Description>Enter a unique name for your scenario.</Form.Description>
    <Form.FieldErrors />
  </Form.Field>
  <Form.Field {form} name="description">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Description</Form.Label>
        <Textarea {...props} bind:value={$formData.description} />
      {/snippet}
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>
  <Form.Field {form} name="maritalStatus" class="flex items-center gap-2">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Marital Status</Form.Label>
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
    {#if $formData.maritalStatus === 'couple'}
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
</div>
