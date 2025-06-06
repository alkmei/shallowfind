<script lang="ts">
  import { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import { defaults, superForm } from 'sveltekit-superforms';
  import { zod } from 'sveltekit-superforms/adapters';
  import * as Form from '$lib/components/ui/form';
  import { Input } from '$lib/components/ui/input';
  import Checkbox from '$lib/components/ui/checkbox/checkbox.svelte';

  const form = superForm(defaults(zod(scenariosCreateBody)), {
    validators: zod(scenariosCreateBody),
    SPA: true,
    dataType: 'json',
    onUpdate({ form }) {
      if (!form.valid) return;
      // Handle form submission logic here
      console.log('Form submitted:', form.data);
    }
  });

  const { form: formData, enhance } = form;

  let isMarried = $state($formData.maritalStatus === 'couple');

  $effect(() => {
    $formData.maritalStatus = isMarried ? 'couple' : 'individual';
  });
</script>

<form method="POST" use:enhance>
  <Form.Field {form} name="name">
    <Form.Control>
      <Form.Label>Scenario Name <span class="text-red-500">*</span></Form.Label>
      <Input bind:value={$formData.name} />
    </Form.Control>
    <Form.Description>Enter a unique name for your scenario.</Form.Description>
    <Form.FieldErrors />
  </Form.Field>

  <Form.Field {form} name="maritalStatus">
    <Form.Control>
      <Form.Label>Is Married?</Form.Label>
      <Checkbox bind:checked={isMarried} />
    </Form.Control>
  </Form.Field>

  <Form.Button class="mt-4">Create Scenario</Form.Button>
</form>
