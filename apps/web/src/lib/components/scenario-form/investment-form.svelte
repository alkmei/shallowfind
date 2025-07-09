<script lang="ts">
  import type { scenariosCreateBody } from '$lib/api/scenarios/scenarios.zod';
  import type { SuperForm } from 'sveltekit-superforms';
  import z from 'zod';
  type ScenariosCreateBody = z.infer<typeof scenariosCreateBody>;

  let { form }: { form: SuperForm<ScenariosCreateBody> } = $props();
</script>

<div class="flex flex-col gap-3">
  <h2 class="text-xl font-bold">Investment Types</h2>
</div>
