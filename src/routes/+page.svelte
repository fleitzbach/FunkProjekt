<!-- index.svelte -->
<script>
  import WorldMap from '$lib/WorldMap.svelte';
  export let data;
  let pointsPromise = data.pointsPromise
</script>

<main>
  <WorldMap {pointsPromise} />
</main>

<style>
  
  main {
    height: 100vh;
  }
</style>
