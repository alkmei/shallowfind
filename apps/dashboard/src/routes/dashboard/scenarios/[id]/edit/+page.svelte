<script lang="ts">
  import { superForm } from 'sveltekit-superforms';
  import type { PageProps } from './$types';
  import { zod4Client } from 'sveltekit-superforms/adapters';
  import scenarioFormSchema from './schema';
  import BasicInformationForm from './basic-information-form.svelte';
  import DemographicsForm from './demographics-form.svelte';
  import SuperDebug from 'sveltekit-superforms';
  import FinancialSettingsForm from './financial-settings-form.svelte';
  let { data }: PageProps = $props();
  import { Separator } from '$lib/components/ui/separator';

  const form = superForm(data.form, {
    validators: zod4Client(scenarioFormSchema),
    dataType: 'json'
  });

  const { form: formData, enhance } = form;
</script>

<h1 class="mb-2 text-3xl font-bold">
  Editing <span class="font-black">{data.scenario.title}</span>
</h1>

<form method="POST" use:enhance class="flex flex-col gap-4">
  <BasicInformationForm {form} />
  <Separator />
  <DemographicsForm {form} />
  <Separator />
  <FinancialSettingsForm {form} />
  <SuperDebug data={$formData} />
</form>
