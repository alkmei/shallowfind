<script lang="ts">
  import * as Form from '$lib/components/ui/form';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Button } from './components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { superForm, defaults } from 'sveltekit-superforms';
  import { zod, zodClient } from 'sveltekit-superforms/adapters';
  import { sessionCreateBody } from './api/session/session.zod';
  import { sessionCreate } from './api/session/session';
  import { goto } from '$app/navigation';

  const form = superForm(defaults(zod(sessionCreateBody)), {
    validators: zodClient(sessionCreateBody),
    SPA: true,
    async onUpdate({ form }) {
      if (!form.valid) return;

      const res = await sessionCreate(form.data);
      if (res.status === 200) {
        goto('/dashboard');
      } else {
        // TODO: Show error message to user
        console.error('Login failed', res.data);
      }
    }
  });

  const { form: formData, enhance } = form;

  let className = '';
  export { className as class };
</script>

<Dialog.Root>
  <Dialog.Trigger>
    <Button class={className}>Log In</Button>
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
            <Form.Label>Email</Form.Label>
            <Input {...props} bind:value={$formData.email} />
            <Form.Label>Password</Form.Label>
            <Input type="password" {...props} bind:value={$formData.password} />
          {/snippet}
        </Form.Control>
        <Form.FieldErrors />
      </Form.Field>
      <Form.Button class="mt-4">Submit</Form.Button>
    </form>
  </Dialog.Content>
</Dialog.Root>
