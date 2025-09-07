<script lang="ts">
  import type { EventSeries } from '$lib/server/db/schema/schema';
  import type { PageProps } from './$types';
  import EventSeriesModal from './event-series-modal.svelte';

  let { params, data, form }: PageProps = $props();

  let eventSeries = $state(data.scenario.eventSeries || []);

  const addEventSeries = (es: EventSeries) => {
    // Placeholder for adding event series logic
    console.log('New Event Series added:', es);
  };
</script>

<div class="flex flex-col gap-3">
  <div class="flex items-center justify-between">
    <h2 class="text-xl font-bold">Event Series</h2>
    <EventSeriesModal {params} {data} {form} onSubmit={addEventSeries} />
  </div>
  <div class="space-y-4 p-1"></div>
</div>
