<script lang="ts">
  import type { ScenarioResponse } from '$lib/api/scenario-management/scenarioManagerAPI.schemas';
  import { ClipboardPen, Edit } from '@lucide/svelte';
  import * as Card from './ui/card';
  import * as Tooltip from './ui/tooltip';

  let { scenario }: { scenario: ScenarioResponse } = $props();
</script>

<Card.Root class="transition-all hover:border-accent-foreground">
  <Card.Header>
    <Card.Title class="flex items-center justify-between">
      <a class="hover:underline" href={`/dashboard/scenarios/${scenario.id}`}>{scenario.name}</a>
      {#if scenario.status === 'Draft'}
        <Tooltip.Root>
          <Tooltip.Trigger>
            <ClipboardPen class="opacity-40" strokeWidth={1} />
          </Tooltip.Trigger>
          <Tooltip.Content class="w-fit">Draft Scenario</Tooltip.Content>
        </Tooltip.Root>
      {/if}
    </Card.Title>
    <Card.Description>{scenario.description}</Card.Description>
  </Card.Header>
  <Card.Content>
    {#if scenario.createdAt}
      <p>Created at: {new Date(scenario.createdAt).toLocaleString()}</p>
    {/if}
    {#if scenario.updatedAt}
      <p>Updated at: {new Date(scenario.updatedAt).toLocaleString()}</p>
    {/if}
  </Card.Content>
  <Card.Footer>
    <Tooltip.Root>
      <Tooltip.Trigger>
        <a href="/dashboard/scenarios/{scenario.id}/edit">
          <Edit class="opacity-40 hover:opacity-100" />
        </a>
      </Tooltip.Trigger>
      <Tooltip.Content class="w-fit">Edit Scenario</Tooltip.Content>
    </Tooltip.Root>
  </Card.Footer>
</Card.Root>
