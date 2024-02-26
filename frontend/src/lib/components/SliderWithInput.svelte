<script lang="ts">
	import { Input } from '$lib/components/ui/input';
	import { Slider } from '$lib/components/ui/slider';

	export let value = 0;
	export let max = 100;
	export let min = 0;
	export let unit: string = '';

	let internalSliderValue = [value];

	// Function to handle slider value change
	function handleSliderChange(event) {
		const newValue = event.detail[0];
		if (newValue !== value) {
			value = newValue;
		}
	}

	// Function to handle input change
	function handleInputChange(event) {
		const newValue = parseFloat(event.target.value);
		if (isNaN(newValue)) {
			event.target.value = internalSliderValue[0];
			return;
		}
		value = internalSliderValue[0]; 
		if (!isNaN(newValue) && newValue !== internalSliderValue[0]) {
			internalSliderValue = [newValue];
			value = newValue; // Update the external value
		}
	}

	function handleKeypress(e) {
		if (e.key == 'Enter') {
			handleInputChange(e);
		}
	}
</script>

<div class="flex flex-row items-center justify-start gap-5">
	<Slider value={internalSliderValue} on:change={handleSliderChange} {min} {max} />
	<div class="flex flex-row items-center justify-start gap-1">
		<Input
			value={value.toString()}
			on:blur={handleInputChange}
			on:keypress={handleKeypress}
			class="w-14"
		/>
		{#if unit}
			<div class="text-sm">{unit}</div>
		{/if}
	</div>
</div>
