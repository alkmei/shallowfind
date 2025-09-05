<script lang="ts">
  import { superForm } from 'sveltekit-superforms';
  import type { PageProps } from './$types';
  import { zod4Client } from 'sveltekit-superforms/adapters';
  import scenarioFormSchema from './schema';

  let { data }: PageProps = $props();

  const form = superForm(data.form, {
    validators: zod4Client(scenarioFormSchema)
  });

  const { form: formData, enhance } = form;
</script>

<h1>Edit Scenario</h1>

<form method="POST"></form>
