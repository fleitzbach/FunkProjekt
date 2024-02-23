<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import type { Station } from '$lib/types';
	import { currentStation, dataStore } from './store';
	export let station: Station;

	function handleButtonClick() {
		currentStation.setCurrentStation(station);
		dataStore.fetchTemperatureData(station.id);
	}
</script>

<div class="text-primary">
	<h4 class="scroll-m-20 text-xl font-semibold capitalize tracking-tight">
		{station.name.toLowerCase()}
	</h4>
	<br />
	<Button type="button" on:click={handleButtonClick} data-action="viewData">View Data</Button>
</div>
