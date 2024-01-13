<script>
	import { createEventDispatcher } from 'svelte';
	export let name;
	const dispatch = createEventDispatcher();

	function handleButtonClick() {
		dispatch('viewData', { name });
	}
</script>

<div>
	{name}
	<br />
	<button type="button" on:click={handleButtonClick}>View Data</button>
</div>
