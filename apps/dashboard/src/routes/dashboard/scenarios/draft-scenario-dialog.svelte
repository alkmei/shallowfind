<script lang="ts">
  import * as Dialog from '$lib/components/ui/dialog';
  import * as Form from '$lib/components/ui/form';
  import * as RadioGroup from '$lib/components/ui/radio-group';
  import * as Select from '$lib/components/ui/select';
  import Button from '$lib/components/ui/button/button.svelte';
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Textarea } from '$lib/components/ui/textarea';

  import { superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
  import { createScenarioSchema, type CreateScenarioSchema } from './schema';
  import { zod4Client } from 'sveltekit-superforms/adapters';
  import { STATE_MAPPING } from '$lib/enums';

  let { data }: { data: { form: SuperValidated<Infer<CreateScenarioSchema>> } } = $props();

  const form = superForm(data.form, { validators: zod4Client(createScenarioSchema) });

  const { form: formData, enhance } = form;
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
        <Form.FieldErrors />
      </Form.Field>
      <Form.Field {form} name="scenarioType" class="mb-4">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>Scenario Type *</Form.Label>
            <RadioGroup.Root {...props} bind:value={$formData.scenarioType}>
              <div class="flex items-center space-x-2">
                <RadioGroup.Item value="individual" id="individual" />
                <Label for="individual">Individual</Label>
              </div>
              <div class="flex items-center space-x-2">
                <RadioGroup.Item value="married_couple" id="married-couple" />
                <Label for="married-couple">Married Couple</Label>
              </div>
            </RadioGroup.Root>
          {/snippet}
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>

      <Form.Field {form} name="stateOfResidence" class="mb-4">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>State of Residence *</Form.Label>
            <Select.Root {...props} type="single" bind:value={$formData.stateOfResidence}>
              <Select.Trigger>{STATE_MAPPING[$formData.stateOfResidence].name}</Select.Trigger>
              <Select.Content>
                {#each Object.entries(STATE_MAPPING) as [key, state]}
                  <Select.Item value={key}>
                    {state.name}
                  </Select.Item>
                {/each}
              </Select.Content>
            </Select.Root>
          {/snippet}
        </Form.Control>
        <Form.FieldErrors />
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
