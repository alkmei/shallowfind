<script lang="ts">
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();

  let page = $state(0);
</script>

<h1>Edit Scenario</h1>
