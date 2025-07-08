<script lang="ts">
  import type { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import * as Form from '$lib/components/ui/form';
  import { Input } from '$lib/components/ui/input';
  import type { SuperForm } from 'sveltekit-superforms';
  import z from 'zod';
  import Checkbox from '../ui/checkbox/checkbox.svelte';
  import { Field } from 'formsnap';

  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;

  const {
    form
  }: {
    form: SuperForm<ScenariosCreateBody>;
  } = $props();
  const { form: formData } = form;

  let isMarried = $state($formData.maritalStatus === 'couple');

  $effect(() => {
    $formData.maritalStatus = isMarried ? 'couple' : 'individual';
  });
</script>

<div>
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
        <Form.Label>Marital Status</Form.Label>
        <Checkbox {...props} bind:checked={isMarried} />
      {/snippet}
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>
  <Form.Field {form} name="maritalStatus">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Marital Status</Form.Label>
        <Checkbox {...props} bind:checked={isMarried} />
      {/snippet}
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>
</div>
