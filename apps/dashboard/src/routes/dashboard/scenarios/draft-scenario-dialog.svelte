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
  import { type CreateScenarioSchema } from './schema';

  let { data }: { data: { form: SuperValidated<Infer<CreateScenarioSchema>> } } = $props();

  const states = {
    AL: { name: 'Alabama', code: 'AL' },
    AK: { name: 'Alaska', code: 'AK' },
    AZ: { name: 'Arizona', code: 'AZ' },
    AR: { name: 'Arkansas', code: 'AR' },
    CA: { name: 'California', code: 'CA' },
    CO: { name: 'Colorado', code: 'CO' },
    CT: { name: 'Connecticut', code: 'CT' },
    DE: { name: 'Delaware', code: 'DE' },
    FL: { name: 'Florida', code: 'FL' },
    GA: { name: 'Georgia', code: 'GA' },
    HI: { name: 'Hawaii', code: 'HI' },
    ID: { name: 'Idaho', code: 'ID' },
    IL: { name: 'Illinois', code: 'IL' },
    IN: { name: 'Indiana', code: 'IN' },
    IA: { name: 'Iowa', code: 'IA' },
    KS: { name: 'Kansas', code: 'KS' },
    KY: { name: 'Kentucky', code: 'KY' },
    LA: { name: 'Louisiana', code: 'LA' },
    ME: { name: 'Maine', code: 'ME' },
    MD: { name: 'Maryland', code: 'MD' },
    MA: { name: 'Massachusetts', code: 'MA' },
    MI: { name: 'Michigan', code: 'MI' },
    MN: { name: 'Minnesota', code: 'MN' },
    MS: { name: 'Mississippi', code: 'MS' },
    MO: { name: 'Missouri', code: 'MO' },
    MT: { name: 'Montana', code: 'MT' },
    NE: { name: 'Nebraska', code: 'NE' },
    NV: { name: 'Nevada', code: 'NV' },
    NH: { name: 'New Hampshire', code: 'NH' },
    NJ: { name: 'New Jersey', code: 'NJ' },
    NM: { name: 'New Mexico', code: 'NM' },
    NY: { name: 'New York', code: 'NY' },
    NC: { name: 'North Carolina', code: 'NC' },
    ND: { name: 'North Dakota', code: 'ND' },
    OH: { name: 'Ohio', code: 'OH' },
    OK: { name: 'Oklahoma', code: 'OK' },
    OR: { name: 'Oregon', code: 'OR' },
    PA: { name: 'Pennsylvania', code: 'PA' },
    RI: { name: 'Rhode Island', code: 'RI' },
    SC: { name: 'South Carolina', code: 'SC' },
    SD: { name: 'South Dakota', code: 'SD' },
    TN: { name: 'Tennessee', code: 'TN' },
    TX: { name: 'Texas', code: 'TX' },
    UT: { name: 'Utah', code: 'UT' },
    VT: { name: 'Vermont', code: 'VT' },
    VA: { name: 'Virginia', code: 'VA' },
    WA: { name: 'Washington', code: 'WA' },
    WV: { name: 'West Virginia', code: 'WV' },
    WI: { name: 'Wisconsin', code: 'WI' },
    WY: { name: 'Wyoming', code: 'WY' }
  };

  const form = superForm(data.form);

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
              <Select.Trigger>{states[$formData.stateOfResidence].name}</Select.Trigger>
              <Select.Content>
                {#each Object.values(states) as state}
                  <Select.Item value={state.code}>
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
