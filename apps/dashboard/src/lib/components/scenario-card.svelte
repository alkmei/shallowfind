<script lang="ts">
  import { ClipboardPen, Edit } from '@lucide/svelte';
  import * as Card from './ui/card';
  import * as Tooltip from './ui/tooltip';
  import type { Scenario } from '$lib/server/db/schema/schema';

  let { scenario }: { scenario: Scenario } = $props();
</script>

<Card.Root class="hover:border-accent-foreground transition-all">
  <Card.Header>
    <Card.Title class="flex items-center justify-between">
      <a class="hover:underline" href={`/dashboard/scenarios/${scenario.id}`}>{scenario.title}</a>
      {#if scenario.scenarioStatus === 'draft'}
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
