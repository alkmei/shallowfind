<script lang="ts">
  import { usersCreate } from '$lib/api/users/users';
  import { usersCreateBody } from '$lib/api/users/users.zod';
  import * as Card from '$lib/components/ui/card';
  import { defaults, superForm } from 'sveltekit-superforms';
  import { zod, zodClient } from 'sveltekit-superforms/adapters';

  const form = superForm(defaults(zod(usersCreateBody)), {
    validators: zodClient(usersCreateBody),
    SPA: true,
    async onUpdate({ form }) {
      if (!form.valid) return;

      const res = await usersCreate(form.data);
      if (res.status === 200) {
        // Handle successful registration, e.g., redirect to login page
        console.log('User created successfully', res.data);
      } else {
});
</script>

<Card.Root class="w-128">
  <Card.Header>
    <Card.Title>Register</Card.Title>
    <Card.Description>Create a new account</Card.Description>
  </Card.Header>
  <Card.Content>
    <form></form>
  </Card.Content>
</Card.Root>
