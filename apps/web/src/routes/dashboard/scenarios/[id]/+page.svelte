<script lang="ts">
  const { data } = $props();
  const { scenario } = data;
</script>

<h1>{scenario.name}</h1>
<p>{scenario.description}</p>
<p>{scenario.scenarioType}</p>
<p>{scenario.status}</p>
