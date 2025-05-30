<script lang="ts">
  import * as Form from '$lib/components/ui/form';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Input } from '$lib/components/ui/input';
  import { superForm, defaults } from 'sveltekit-superforms';
  import { zod, zodClient } from 'sveltekit-superforms/adapters';
  import { sessionCreateBody } from './api/session/session.zod';
  import { createSessionCreate, sessionCreate } from './api/session/session';
  import { goto } from '$app/navigation';

  const createSession = createSessionCreate({
    mutation: {
      onSuccess: () => {
        // Redirect to the dashboard or another page after successful login
        goto('/dashboard');
      },
      onError: (error) => {
        // Handle error, e.g., show a notification or alert
        console.error('Login failed:', error);
      }
    }
  });

  const form = superForm(defaults(zod(sessionCreateBody)), {
    validators: zodClient(sessionCreateBody),
    SPA: true,
    onUpdate({ form }) {
      if (!form.valid) return;
      $createSession.mutate({ data: form.data });
    }
  });

  const { form: formData, enhance } = form;

  let { children } = $props();
</script>

<Dialog.Root>
  <Dialog.Trigger>
    {@render children()}
  </Dialog.Trigger>

  <Dialog.Content>
    <Dialog.Header
      ><Dialog.Title>Log In</Dialog.Title>

      <Dialog.Description>Please enter your email and password to log in.</Dialog.Description
      ></Dialog.Header
    >
    <form method="POST" use:enhance>
      <Form.Field {form} name="email">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>Email <span class="text-red-500">*</span></Form.Label>
            <Input {...props} bind:value={$formData.email} />
          {/snippet}
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
      <Form.Field {form} name="password">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>Password <span class="text-red-500">*</span></Form.Label>
            <Input type="password" {...props} bind:value={$formData.password} />
          {/snippet}
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
      <Form.Button class="mt-4">Submit</Form.Button>
    </form>
  </Dialog.Content>
</Dialog.Root>
