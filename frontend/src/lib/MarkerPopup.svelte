<script>
	import { createEventDispatcher } from 'svelte';
	import { Button } from '$lib/components/ui/button'
	export let name;
	const dispatch = createEventDispatcher();

	function handleButtonClick() {
		const event = new CustomEvent('viewData', {
            detail: { name },
            bubbles: true // This allows the event to bubble up through the DOM
        });
        dispatchEvent(event);
	}
</script>

<div class="text-primary">
	<h4 class="scroll-m-20 text-xl font-semibold tracking-tight capitalize">{name.toLowerCase()}</h4>
	<br />
	<Button type="button" on:click={handleButtonClick} data-action='viewData'>View Data</Button>
</div>
