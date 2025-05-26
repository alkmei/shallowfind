<script lang="ts">
  import * as Form from '$lib/components/ui/form';
  import * as Dialog from '$lib/components/ui/dialog';
  import { Button } from './components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { superForm, defaults } from 'sveltekit-superforms';
  import { zod, zodClient } from 'sveltekit-superforms/adapters';
  import { tokenCreateBody } from '$lib/api/token/token.zod';
    import { tokenCreate } from './api/token/token';

  const form = superForm(defaults(zod(tokenCreateBody)), {
    validators: zodClient(tokenCreateBody),
    SPA: true,
    onUpdate({form}) {
      if (!form.valid) return
    },
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
