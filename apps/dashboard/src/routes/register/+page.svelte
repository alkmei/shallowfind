<script lang="ts">
  import * as Card from '$lib/components/ui/card/index.js';
  import * as Form from '$lib/components/ui/form/index.js';
  import { Input } from '$lib/components/ui/input/index.js';
  import { superForm, type Infer, type SuperValidated } from 'sveltekit-superforms';
  import { registerSchema, type RegisterSchema } from './schema';
  import { zod4Client } from 'sveltekit-superforms/adapters';
  import { authClient } from '$lib/client';
  const id = $props.id();

  let { data }: { data: { form: SuperValidated<Infer<RegisterSchema>> } } = $props();

  let submitting = $state(false);

  const form = superForm(data.form, {
    validators: zod4Client(registerSchema),
    SPA: true,
    onUpdate({ form }) {
      authClient.signUp.email(
        {
          email: form.data.email,
          password: form.data.password,
          name: form.data.name
        },
        {
          onRequest: () => {
            submitting = true;
            form.errors = {};
          },
          onSuccess: () => {
            submitting = false;
            // Redirect to dashboard or show success message
            window.location.href = '/dashboard';
          },
          onError: (ctx) => {
            console.error('Registration error:', ctx.error);
            submitting = false;
          }
        }
      );
    }
  });

  const { form: formData, enhance } = form;
</script>

<div
  class="flex h-screen w-full items-center justify-center bg-[url(https://images.unsplash.com/photo-1623118176012-9b0c6fa0712d?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)] bg-cover bg-center"
>
  <Card.Root class="mx-auto w-full max-w-sm">
    <Card.Header>
      <Card.Title class="text-2xl">Register</Card.Title>
      <Card.Description>Enter your information below to create a new account</Card.Description>
    </Card.Header>
    <Card.Content>
      <form method="POST" use:enhance class="grid gap-1">
        <Form.Field {form} name="name" class="grid gap-2">
          <Form.Control>
            <Form.Label for="name-{id}">Name</Form.Label>
            <Input id="name-{id}" type="text" placeholder="Your name" bind:value={$formData.name} />
          </Form.Control>
          <Form.FieldErrors />
        </Form.Field>
        <Form.Field {form} name="email" class="grid gap-2">
          <Form.Control>
            <Form.Label for="email-{id}">Email *</Form.Label>
            <Input
              id="email-{id}"
              type="email"
              placeholder="m@example.com"
              required
              bind:value={$formData.email}
            />
          </Form.Control>
          <Form.FieldErrors />
        </Form.Field>
        <Form.Field {form} name="password" class="grid gap-2">
          <Form.Control>
            <Form.Label for="password-{id}">Password *</Form.Label>
            <Input id="password-{id}" type="password" required bind:value={$formData.password} />
          </Form.Control>
          <Form.FieldErrors />
        </Form.Field>
        <Form.Button type="submit" class="w-full">Register</Form.Button>
      </form>
      <div class="mt-4 text-center text-sm">
        Want to login?
        <a href="##" class="underline"> Sign in </a>
      </div>
    </Card.Content>
  </Card.Root>
</div>
