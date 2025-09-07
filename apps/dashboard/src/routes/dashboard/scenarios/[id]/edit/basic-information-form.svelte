<script lang="ts">
  import * as Form from '$lib/components/ui/form';
  import { Input } from '$lib/components/ui/input';
  import { Textarea } from '$lib/components/ui/textarea';
  import type { SuperForm } from 'sveltekit-superforms';
  import type { ScenarioForm } from './schema';
  import * as Select from '$lib/components/ui/select';
  import { STATE_MAPPING } from '$lib/enums';

  const { form }: { form: SuperForm<ScenarioForm> } = $props();

  const { form: formData } = form;
</script>

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
  <Form.Field {form} name="stateOfResidence">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>State of Residence <span class="text-red-500">*</span></Form.Label>
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
    <Form.Description>Choose the state where you reside.</Form.Description>
    <Form.FieldErrors />
  </Form.Field>
</div>
