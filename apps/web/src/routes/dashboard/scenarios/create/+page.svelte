<script lang="ts">
  import BasicInformation from '$lib/components/scenario-form/basic-information-form.svelte';
  import { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import { z } from 'zod';
  import { zod } from 'sveltekit-superforms/adapters';
  import { defaults, superForm, type SuperForm } from 'sveltekit-superforms';
  import { createScenariosCreate } from '$lib/api/scenarios/scenarios';
  import { goto } from '$app/navigation';
  import Button from '$lib/components/ui/button/button.svelte';
  import { Progress } from '$lib/components/ui/progress';
  import DemographicsForm from '$lib/components/scenario-form/demographics-form.svelte';

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
  <div class="mb-6">
    <h1 class="mb-4 text-2xl font-bold">Create Scenario</h1>
    <Progress max={formState.totalSteps - 1} value={formState.currentStep} />
  </div>

  {#if formState.currentStep === 0}
    <BasicInformation {form} />
  {:else if formState.currentStep === 1}
    <DemographicsForm {form} />
  {/if}
  <div class="mt-4">
    {#if formState.currentStep > 0}
      <Button variant="outline" onclick={() => (formState.currentStep -= 1)}>Previous</Button>
    {/if}
    {#if formState.currentStep < formState.totalSteps - 1}
      <Button type="button" onclick={() => (formState.currentStep += 1)}>Next</Button>
    {:else}
      <Button type="submit">Submit</Button>
    {/if}
  </div>
</form>

<!-- Use $formData to access the reactive form data -->
<pre
  class="bg-muted max-h-96 overflow-x-auto overflow-y-auto rounded-md p-4 font-mono text-xs break-words whitespace-pre-wrap">
  <code>{JSON.stringify($formData, null, 2)}</code>
</pre>
