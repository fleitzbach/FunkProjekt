<script lang="ts">
	import Chart from 'chart.js/auto';
	import { onMount } from 'svelte';
	import { dataStore, currentStationStore } from './store';
	import { Input } from './components/ui/input';
	import Button from './components/ui/button/button.svelte';
	import { API_URL } from '../config';

	let chartElement;
	let chart;
  let interval

	onMount(() => {
    // Init empty chart
		chart = new Chart(chartElement, {
			type: 'line',
			data: {
				labels: [],
				datasets: [
					{
						label: 'Maximum Temperature',
						data: [],
						tension: 0.2,
            borderColor: "#f00"
					},
					{
						label: 'Minimum Temperature',
						data: [],
						tension: 0.2,
            borderColor: '#00f'
					}
				]
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
		console.log(data)
		if (chart) {
			chart.data.labels = data.map((row) => row.date);
			chart.data.datasets[0].data = data.map((row) => row.TMAX)
			chart.data.datasets[1].data = data.map((row) => row.TMIN)
			chart.update();
		}
	}

  function updateData() {
    console.log($currentStationStore)
    let start = $currentStationStore.first_year + "-01-01";
    let end = $currentStationStore.last_year + "-12-31";
    let id = $currentStationStore.id
		let dataUrl = `${API_URL}/data/${id}/${'year'}?start=${start}&end=${end}`;
    dataStore.fetchData(dataUrl);
  }
</script>

<div class="w-full h-full box-content flex flex-row">
  <!-- Data Controls -->
  <div class="p-5 flex flex-col gap-5 items-baseline max-w-[300px] w-full">
    <h3 class="scroll-m-20 text-2xl font-semibold tracking-tight">Controls</h3>
    <Input bind:value={interval}></Input>
    <Button on:click={updateData}>Update Data</Button>
  </div>
  <!-- Visualisation -->
  <div class="w-full h-full p-5">
    <h3 class="scroll-m-20 text-2xl font-semibold tracking-tight">{$currentStationStore.name}</h3>
    <canvas bind:this={chartElement} class='h-full w-full'></canvas>
  </div>
</div>
