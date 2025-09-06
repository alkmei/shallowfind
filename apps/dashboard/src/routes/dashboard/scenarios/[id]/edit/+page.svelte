<script lang="ts">
  import { superForm } from 'sveltekit-superforms';
  import type { PageProps } from './$types';
  import { zod4Client } from 'sveltekit-superforms/adapters';
  import scenarioFormSchema from './schema';
  import BasicInformationForm from './basic-information-form.svelte';
  import DemographicsForm from './demographics-form.svelte';
  let { data }: PageProps = $props();

  const form = superForm(data.form, {
    validators: zod4Client(scenarioFormSchema),
    dataType: 'json'
  });

  const { enhance } = form;
</script>

<h1>Edit Scenario</h1>

<form method="POST" use:enhance>
  <BasicInformationForm {form} />
  <DemographicsForm {form} />
</form>
