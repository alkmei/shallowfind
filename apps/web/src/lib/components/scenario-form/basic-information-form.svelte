<script lang="ts">
  import type { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import * as Form from '$lib/components/ui/form';
  import { Input } from '$lib/components/ui/input';
  import type { SuperForm } from 'sveltekit-superforms';
  import z from 'zod';
  import Textarea from '../ui/textarea/textarea.svelte';

  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;

  const {
    form
  }: {
    form: SuperForm<ScenariosCreateBody>;
  } = $props();
  const { form: formData } = form;
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
</div>
