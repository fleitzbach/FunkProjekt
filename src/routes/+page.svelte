<!-- index.svelte -->
<script>
  import WorldMap from '$lib/WorldMap.svelte';
  import WorldMapLeaflet from '$lib/WorldMapLeaflet.svelte';
  export let data;
  let pointsPromise = data.pointsPromise
  
</script>

<main>
  <WorldMapLeaflet {pointsPromise} />
</main>

<style>
  
  main {
    height: 100vh;
  }
</style>
