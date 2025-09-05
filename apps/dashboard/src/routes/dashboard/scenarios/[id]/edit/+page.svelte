<script lang="ts">
  import { superForm } from 'sveltekit-superforms';
  import type { PageProps } from './$types';
  import { zod4Client } from 'sveltekit-superforms/adapters';
  import scenarioFormSchema from './schema';
  import * as Form from '$lib/components/ui/form';
  import { Input } from '$lib/components/ui/input';
  import { Textarea } from '$lib/components/ui/textarea';
  let { data }: PageProps = $props();

  const form = superForm(data.form, {
    validators: zod4Client(scenarioFormSchema),
    dataType: 'json'
  });

  const { form: formData, enhance } = form;
</script>

<h1>Edit Scenario</h1>

<form method="POST">
  <div class="flex flex-col gap-3">
    <h2 class="text-xl font-bold">Basic Information</h2>
    <Form.Field {form} name="title">
      <Form.Control>
        {#snippet children({ props })}
          <Form.Label>Scenario Title <span class="text-red-500">*</span></Form.Label>
          <Input {...props} bind:value={$formData.title} />
        {/snippet}
      </Form.Control>
      <Form.Description>Enter a unique title for your scenario.</Form.Description>
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
</form>
