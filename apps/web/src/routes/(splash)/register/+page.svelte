<script lang="ts">
  import { createUsersCreate, usersCreate } from '$lib/api/users/users';
  import { usersCreateBody } from '$lib/api/users/users.zod';
  import * as Form from '$lib/components/ui/form';
  import * as Card from '$lib/components/ui/card';
  import { defaults, superForm } from 'sveltekit-superforms';
  import { zod, zodClient } from 'sveltekit-superforms/adapters';
  import { Input } from '$lib/components/ui/input';
  import LoginForm from '$lib/components/login-form.svelte';
  import { X } from '@lucide/svelte';
  import { goto } from '$app/navigation';

  const mutation = createUsersCreate({
    mutation: {
      onSuccess: () => {
        // Redirect to login or dashboard after successful registration
        goto('/');
      },
      onError: (error) => {
        // TODO: Handle error, e.g., show a notification or alert
        console.error('Registration failed:', error);
      }
    }
  });

  const form = superForm(defaults(zod(usersCreateBody)), {
    validators: zodClient(usersCreateBody),
    SPA: true,
    async onUpdate({ form }) {
      if (!form.valid) return;
      $mutation.mutate({ data: form.data });
    }
  });

  const { form: formData, enhance } = form;

  // Client-side validation functions
  function validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  function validatePassword(password: string): boolean {
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/;
    return passwordRegex.test(password);
  }

  // Validation state helpers
  $: emailInvalid = $formData.email && !validateEmail($formData.email);
  $: passwordInvalid = $formData.password && !validatePassword($formData.password);
  $: passwordMismatch =
    $formData.passwordConfirm && $formData.password !== $formData.passwordConfirm;
</script>

<Card.Root class="w-128">
  <Card.Header>
    <Card.Title class="align-center flex items-center justify-between"
      ><span>Register</span>
      <a href="/" class="text-gray-400 hover:text-gray-50">
        <X size="16" class="inline" />
      </a></Card.Title
    >
    <Card.Description>Create a new account</Card.Description>
  </Card.Header>
  <Card.Content>
    <form method="POST" use:enhance class="flex flex-col gap-4">
      <Form.Field {form} name="email">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>
              Email <span class="text-red-500">*</span>
            </Form.Label>
            <Input
              {...props}
              bind:value={$formData.email}
              placeholder="johndoe@example.com"
              type="email"
              required
              aria-invalid={emailInvalid ? 'true' : undefined}
              aria-describedby={emailInvalid ? 'email-error' : undefined}
            />
            {#if emailInvalid}
              <p id="email-error" class="mt-1 text-sm text-red-500">
                Please enter a valid email address
              </p>
            {/if}
          {/snippet}
        </Form.Control>
      </Form.Field>

      <div class="flex">
        <Form.Field {form} name="firstName" class="mr-2 flex-1">
          <Form.Control>
            {#snippet children({ props })}
              <Form.Label>First Name</Form.Label>
              <Input {...props} bind:value={$formData.firstName} placeholder="John" />
            {/snippet}
          </Form.Control>
          <Form.FieldErrors />
        </Form.Field>
        <Form.Field {form} name="lastName" class="ml-2 flex-1">
          <Form.Control>
            {#snippet children({ props })}
              <Form.Label>Last Name</Form.Label>
              <Input {...props} bind:value={$formData.lastName} placeholder="Doe" />
            {/snippet}
          </Form.Control>
          <Form.FieldErrors />
        </Form.Field>
      </div>

      <Form.Field {form} name="password">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>
              Password <span class="text-red-500">*</span>
            </Form.Label>
            <Input
              type="password"
              {...props}
              bind:value={$formData.password}
              required
              aria-invalid={passwordInvalid ? 'true' : undefined}
              aria-describedby={passwordInvalid ? 'password-error' : undefined}
            />
            {#if passwordInvalid}
              <p id="password-error" class="mt-1 text-sm text-red-500">
                Password must be at least 8 characters with uppercase, lowercase, and number
              </p>
            {/if}
          {/snippet}
        </Form.Control>
      </Form.Field>

      <Form.Field {form} name="passwordConfirm">
        <Form.Control>
          {#snippet children({ props })}
            <Form.Label>
              Confirm Password <span class="text-red-500">*</span>
            </Form.Label>
            <Input
              type="password"
              {...props}
              bind:value={$formData.passwordConfirm}
              required
              aria-invalid={passwordMismatch ? 'true' : undefined}
              aria-describedby={passwordMismatch ? 'password-confirm-error' : undefined}
            />
            {#if passwordMismatch}
              <p id="password-confirm-error" class="mt-1 text-sm text-red-500">
                Passwords do not match
              </p>
            {/if}
          {/snippet}
        </Form.Control>
      </Form.Field>

      <Form.Button class="mt-4">Register</Form.Button>
    </form>
    <div class="mt-4 text-center text-sm text-gray-500">
      Have an account? <LoginForm
        ><span class="cursor-pointer text-blue-500 hover:underline">Login</span></LoginForm
      >
    </div>
  </Card.Content>
</Card.Root>

<style>
  /* Style inputs with aria-invalid for visual feedback */
  :global(input[aria-invalid='true']) {
    border-color: rgb(239 68 68); /* red-500 equivalent */
    border-width: 1px;
  }
</style>
