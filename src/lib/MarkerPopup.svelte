<script>
	import { createEventDispatcher } from 'svelte';
	export let name;
	const dispatch = createEventDispatcher();
    import { Button } from '$lib/components/ui/button'

	function handleButtonClick() {
		dispatch('viewData', { name });
	}
</script>

<div>
	<h4 class="scroll-m-20 text-xl font-semibold tracking-tight capitalize">{name.toLowerCase()}</h4>
	<br />
	<Button type="button" on:click={handleButtonClick}>View Data</Button>
</div>
