<script lang="ts">
  import SuperDebug from 'sveltekit-superforms';

  const { data } = $props();
  const { scenario } = data;
</script>

<h1>{scenario.title}</h1>
<p>{scenario.description}</p>
<p>{scenario.scenarioType}</p>
<p>{scenario.scenarioStatus}</p>

<SuperDebug data={scenario} />
