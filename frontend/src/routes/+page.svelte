<!-- index.svelte -->
<script>
  import WorldMap from '$lib/WorldMap.svelte';
  import WorldMapLeaflet from '$lib/WorldMapLeaflet.svelte';
  
</script>

<main>
  <WorldMapLeaflet />
</main>

<style>
  
  main {
    height: 100vh;
  }
</style>
