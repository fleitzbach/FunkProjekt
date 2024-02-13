<script lang="ts">
	import Chart from 'chart.js/auto';
	import { onMount } from 'svelte';
	import { dataStore, currentStation, dataSettings } from './store';
	import { Input } from './components/ui/input';
	import { Button } from './components/ui/button';
	import { API_URL } from '../config';
	import * as Select from './components/ui/select';
	import { Label } from './components/ui/label';
	import { DateField } from './components/ui/date-field';
	import { Root } from 'postcss';
	import type { DataSettings } from './types';
	let chartElement;
	let chart;
	
	let dataControls: DataSettings = {
		interval: 'year'
	};

	onMount(() => {
		// Init empty chart
		chart = new Chart(chartElement, {
			type: 'line',
			data: {
				labels: [],
				datasets: [
					{
						label: 'Maximum Temperature (°C)',
						data: [],
						tension: 0.2,
						borderColor: '#ef4444'
					},
					{
						label: 'Minimum Temperature (°C)',
						data: [],
						tension: 0.2,
						borderColor: '#00f'
					}
				]
			},

			options:{
				animation: false,
				plugins: {
					decimation: {
						enabled: true,
						algorithm: 'lttb',
						samples: 2
					}
				}
			}
		});

		// Setup subscription to the store
		const unsubscribe = dataStore.subscribe((data) => {
			updateChart(data);
		});

		// Cleanup on component destroy
		return () => {
			unsubscribe();
			if (chart) chart.destroy();
		};
	});

	function updateChart(data) {
		if (chart) {
			chart.data.labels = data.map((row) => row.date);
			chart.data.datasets[0].data = data.map((row) => row.TMAX);
			chart.data.datasets[1].data = data.map((row) => row.TMIN);
			chart.update();
		}
	}

	function updateData() {
		console.log(dataControls);
		let settings: DataSettings = {interval: dataControls.interval}
		let dateParser = /(\d{1,2}).(\d{1,2}).(\d{4})/
		
		if (dataControls.start) {
			let start = new Date(dataControls.start.replace(dateParser, '$3-$2-$1'));
			settings.start = start.toISOString().split('T')[0];
			dataControls.start = start.toLocaleDateString('de-DE');
		}
		if (dataControls.end) {
			let end = new Date(dataControls.end.replace(dateParser, '$3-$2-$1'));
			settings.end = end.toISOString().split('T')[0];
			dataControls.end = end.toLocaleDateString('de-DE');
		}
		dataSettings.setSettings(settings);
		dataStore.fetchTemperatureData($currentStation.id);
	}

	function intervalChange(option) {
		let o = option as Option<T>;
    	if (o) {
			dataControls.interval = o.value;
		}
	}

	function close() {
		currentStation.clearCurrentStation();
	}
</script>

<div class="w-full flex flex-row ">
	<!-- Data Controls -->
	<div class="p-5 flex flex-col gap-5 items-baseline min-w-[300px] max-w-[300px] w-full">
		<h3 class="scroll-m-20 text-2xl font-semibold tracking-tight">Controls</h3>
		<div class='w-full'>
			<Label for='data-interval' class='font-semibold'>Data interval</Label>
			<Select.Root onSelectedChange={intervalChange}>
				<Select.Trigger>
					<Select.Value placeholder='Interval'>
					</Select.Value>
				</Select.Trigger>
				<Select.Content>
					<Select.Item value='year'>Year</Select.Item>
					<Select.Item value='season'>Season</Select.Item>
					<Select.Item value='month'>Month</Select.Item>
					<Select.Item value='day'>Day</Select.Item>
				</Select.Content>
			</Select.Root>
		</div>
		<div class="flex flex-row items-center gap-5">
			<div>
				<Label for="start" class="font-semibold">Start date</Label>
				<Input type="text" id="start" bind:value={dataControls.start} class="w-full" />
			</div>
			<div>
				<Label for="end" class="font-semibold">End date</Label>
				<Input type="text" id="end" bind:value={dataControls.end} class="w-full" />
			</div>
		</div>
		<Button on:click={updateData}>Update Data</Button>
	</div>
	<!-- Visualisation -->
	<div class="w-full p-5">
		<div class='flex flex-row justify-between'>
			<h3 class="scroll-m-20 text-2xl font-semibold tracking-tight">{$currentStation.name}</h3>
			<Button on:click={close} variant='link'>x</Button>
		</div>
		<canvas bind:this={chartElement} class="h-full max-h-96 w-full"></canvas>
	</div>
</div>
