<script lang="ts">
  import type { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import * as Form from '$lib/components/ui/form';
  import type { SuperForm } from 'sveltekit-superforms';
  import z from 'zod';
  import * as Tabs from '$lib/components/ui/tabs';

  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;

  const {
    form
  }: {
    form: SuperForm<ScenariosCreateBody>;
  } = $props();
  const { form: formData } = form;
</script>

<div class="flex flex-col gap-3">
  <h2 class="text-xl font-bold">Financial Settings</h2>
  <h3>Inflation Assumption</h3>

  <Tabs.Root bind:value={$formData.inflationAssumption.type}>
    <Tabs.List>
      <Tabs.Trigger value="fixed">Fixed</Tabs.Trigger>
      <Tabs.Trigger value="normal">Normal</Tabs.Trigger>
      <Tabs.Trigger value="uniform">Uniform</Tabs.Trigger>
    </Tabs.List>
  </Tabs.Root>
</div>
