<script lang="ts">
  import BasicInformation from '$lib/components/scenario-form/basic-information.svelte';
  import * as Form from '$lib/components/ui/form';
  import { get } from 'svelte/store';
  import { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import { z } from 'zod';
  import { zod } from 'sveltekit-superforms/adapters';
  import { defaults, superForm, type SuperForm } from 'sveltekit-superforms';
  import { createScenariosCreate } from '$lib/api/scenarios/scenarios';
  import { goto } from '$app/navigation';

  type ScenarioFormData = z.infer<typeof scenariosCreateBody>;

  const mutation = createScenariosCreate({
    mutation: {
      onSuccess: () => {
        goto('/dashboard/scenarios');
      },
      onError: (error) => {
        console.error('Error creating scenario:', error);
      }
    }
  });

  // Destructure the form stores from superForm
  const form = superForm(defaults(zod(scenariosCreateBody)), {
    validators: zod(scenariosCreateBody),
    SPA: true,
    dataType: 'json',
    onUpdate({ form }) {
      if (!form.valid) return;
      $mutation.mutate({ data: form.data });
    }
  });

  const { form: formData, enhance } = form;

  interface FormState {
    currentStep: number;
    totalSteps: number;
    isValid: Record<number, boolean>;
    touched: Record<number, boolean>;
  }

  const formState = $state<FormState>({
    currentStep: 0,
    totalSteps: 7,
    isValid: {},
    touched: {}
  });
</script>

<form method="POST" use:enhance>
  {#if formState.currentStep === 0}
    <!-- Pass the form data store and other form utilities -->
    <BasicInformation {form} />
  {/if}
  <Form.Button class="mt-4">Create Scenario</Form.Button>
</form>

<!-- Use $formData to access the reactive form data -->
<pre
  class="bg-muted max-h-96 overflow-x-auto overflow-y-auto rounded-md p-4 font-mono text-xs break-words whitespace-pre-wrap">
  <code>{JSON.stringify($formData, null, 2)}</code>
</pre>
