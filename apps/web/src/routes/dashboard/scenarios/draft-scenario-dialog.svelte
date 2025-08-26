<script lang="ts">
  import * as Dialog from '$lib/components/ui/dialog';
  import * as Form from '$lib/components/ui/form';
  import * as RadioGroup from '$lib/components/ui/radio-group';
  import Button from '$lib/components/ui/button/button.svelte';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';

  import { postApiScenariosBody } from '$lib/api/scenario-management/scenarios/scenarios.zod';
  import { superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
  import { zodClient } from 'sveltekit-superforms/adapters';

  let { data }: { data: { form: SuperValidated<Infer<typeof postApiScenariosBody>> } } = $props();

  const form = superForm(data.form, {
    validators: zodClient(postApiScenariosBody)
  });

  const { form: formData, errors, enhance } = form;
</script>

<Dialog.Root>
  <Dialog.Trigger>
    <Button>New Scenario</Button>
  </Dialog.Trigger>
  <Dialog.Content>
    <Dialog.Header>
      <Dialog.Title>Create a New Scenario</Dialog.Title>
      <Dialog.Description>
        Start building your scenario by providing the necessary details.
      </Dialog.Description>
    </Dialog.Header>

    <form method="POST" use:enhance>
      <Form.Field {form} name="name" class="mb-4">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>Name *</Form.Label>
            <Input {...props} bind:value={$formData.name} />
          {/snippet}
        </Form.Control>
      </Form.Field>
      <Form.Field {form} name="description" class="mb-4">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>Description</Form.Label>
            <Textarea {...props} bind:value={$formData.description} />
          {/snippet}
        </Form.Control>
      </Form.Field>
      <Form.Field {form} name="scenarioType" class="mb-4">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>Scenario Type *</Form.Label>
            <RadioGroup.Root {...props} bind:value={$formData.scenarioType}>
              <div class="flex items-center space-x-2">
                <RadioGroup.Item value="Individual" id="individual" />
                <Label for="individual">Individual</Label>
              </div>
              <div class="flex items-center space-x-2">
                <RadioGroup.Item value="MarriedCouple" id="married-couple" />
                <Label for="married-couple">Married Couple</Label>
              </div>
            </RadioGroup.Root>
          {/snippet}
        </Form.Control>
      </Form.Field>

      <Dialog.Footer>
        <Dialog.Close>
          <Button variant="secondary">Cancel</Button>
        </Dialog.Close>
        <Form.Button>Create Scenario</Form.Button>
      </Dialog.Footer>
    </form>
  </Dialog.Content>
</Dialog.Root>
