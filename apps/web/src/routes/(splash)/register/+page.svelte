<script lang="ts">
  import { usersCreate } from '$lib/api/users/users';
  import * as Card from '$lib/components/ui/card';
  import { defaults, superForm } from 'sveltekit-superforms';
  import { zod } from 'sveltekit-superforms/adapters';

  const form = superForm(defaults(zod(usersCreate())));
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
