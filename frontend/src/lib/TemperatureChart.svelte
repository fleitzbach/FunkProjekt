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
	import { each } from 'chart.js/helpers';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import { X } from 'lucide-svelte';
	import { LucideArrowUpRightSquare } from 'lucide-svelte';
	import { toast } from 'svelte-sonner';
	import LoadingOverlay from '$lib/LoadingOverlay.svelte';
	import 'chartjs-adapter-luxon';
	import * as Sheet from '$lib/components/ui/sheet';
	import Datatable from './DataTable.svelte';

	let chartElement;
	let chart;


	let dataControls: DataSettings = {
		interval: $dataSettings.interval
	};

	let intervals = [
		{ value: 'year', label: 'Year', disabled: false },
		{ value: 'season', label: 'Season', disabled: false },
		{ value: 'month', label: 'Month', disabled: false },
		{ value: 'day', label: 'Day', disabled: false }
	];

	$: selectedInterval = intervals.find((interval) => interval.value === dataControls.interval);

	onMount(() => {
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
			options: {
				responsive: true,
				maintainAspectRatio: false,
				interaction: {
					mode: 'index',
					intersect: false
				},
				plugins: {
					decimation: {
						enabled: true,
						algorithm: 'lttb',
						samples: 0.5
					}
				},
				scales: {
					x: {
						type: 'time'
					}
				},
				onClick: function (event, chartElements) {
					if (chartElements.length > 0) {
						const elementIndex = chartElements[0].index;
						const dataPoint = this.data.labels[elementIndex];
						if (dataControls.interval == 'year') {
							dataControls.start = `01.01.${dataPoint}`;
							dataControls.end = `30.12.${dataPoint}`;
							dataControls.interval = 'month';
							updateData();
						} else if (dataControls.interval == 'month') {
							let datapoint_split = dataPoint.split('-');
							let datapoint_year = datapoint_split[0];
							let datapoint_month = datapoint_split[1];
							let isLeapYear =
								(datapoint_year % 4 === 0 && datapoint_year % 100 !== 0) ||
								datapoint_year % 400 === 0;
							let datapoint_endDay;
							if (
								datapoint_month === '01' ||
								datapoint_month === '03' ||
								datapoint_month === '05' ||
								datapoint_month === '07' ||
								datapoint_month === '08' ||
								datapoint_month === '10' ||
								datapoint_month === '12'
							) {
								datapoint_endDay = 31;
							} else if (
								datapoint_month === '04' ||
								datapoint_month === '06' ||
								datapoint_month === '09' ||
								datapoint_month === '11'
							) {
								datapoint_endDay = 30;
							} else if (datapoint_month === '02') {
								datapoint_endDay = isLeapYear ? 29 : 28;
							} else {
								// Handle invalid month
								console.error('Invalid month:', datapoint_month);
								return;
							}
							dataControls.start = `01.${datapoint_month}.${datapoint_year}`;
							dataControls.end = `${datapoint_endDay}.${datapoint_month}.${datapoint_year}`;
							dataControls.interval = 'day';
							updateData();
						} else {
						}
					}
				}
			}
		});


		// Setup subscription to the store
		const unsubscribe = dataStore.subscribe((data) => {
			if (!data.loading) {
				updateChart(data.data);
			}
		});

		// Cleanup on component destroy
		return () => {
			unsubscribe();
			if (chart) chart.destroy();
		};
	});

	const generateSeasons = (startYear: number, endYear: number): string[] => {
		const seasons = ['winter', 'spring', 'summer', 'autumn'];
		const allSeasons: string[] = [];

		for (let year = startYear; year <= endYear; year++) {
			seasons.forEach((season, index) => {
			allSeasons.push(${year}${index + 1}${season});
			});
		}

		return allSeasons;
		};

	const fillMissingData = (data) => {
		const firstYear = parseInt(data[0].season.substring(0, 4));
		const lastYear = parseInt(data[data.length - 1].season.substring(0, 4));

		const allSeasons = generateSeasons(firstYear, lastYear);

		return allSeasons.map((season) => {
			const existingData = data.find((d) => d.season === season);
			return existingData ? existingData : { season };
		});
	};

	function updateChart(data) {
		console.log(data)
		if (chart && data) {
			if (dataControls.interval == "season") {
				data = fillMissingData(data);
				let labels = data.map(d => {
					let seasonCode = d.season.substring(5, d.season.length);
					let year = d.season.substring(0, 4);
					let season;
					switch(seasonCode) {
					case 'spring': season = 'Spring'; break;
					case 'summer': season = 'Sommer'; break;
					case 'autumn': season = 'Herbst'; break;
					case 'winter': season = 'Winter'; break;
					default: season = 'Unbekannt';
				}
				return `${season} ${year}`;
				});

				chart.data.labels = labels;
				chart.data.datasets[0].data = data.map((row) => row.TMAX);
				chart.data.datasets[1].data = data.map((row) => row.TMIN);
				chart.options.scales.x = {};
				chart.update();
				
			} else {
				chart.data.labels = data.map((row) => row.date);
				chart.data.datasets[0].data = data.map((row) => row.TMAX);
				chart.data.datasets[1].data = data.map((row) => row.TMIN);
				chart.options.scales.x = {type:"time"};
				chart.update();
			}
		}
	}

	function updateData() {
		let settings: DataSettings = { interval: dataControls.interval };
		let dateParser = /(\d{1,2}).(\d{1,2}).(\d{4})/;
		dataSettings.setSettings(settings);
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
		dataStore.fetchTemperatureData($currentStation.id);
	}

	function intervalChange(option) {
		let o = option as Option<T>;
		if (o) {
			dataControls.interval = o.value;
		}
	}

	function clearSettings() {
		dataControls = { interval: 'year' };
		dataSettings.clearSettings();
		toast('cleared settings');
	}

	function close() {
		currentStation.clearCurrentStation();
	}
</script>

<div class="w-full flex flex-row bg-primary-foreground">
	<!-- Data Controls -->
	<div class="p-5 flex flex-col gap-5 items-baseline min-w-[300px] max-w-[300px] w-full">
		<div class="flex flex-row justify-between w-full">
			<h3 class="scroll-m-20 text-2xl font-semibold tracking-tight">Controls</h3>
			<Button on:click={clearSettings} variant="link" class="p-0 font-normal">clear</Button>
		</div>
		<div class="w-full">
			<Label for="data-interval" class="font-semibold">Data interval</Label>
			<Select.Root bind:selected={selectedInterval} onSelectedChange={intervalChange}>
				<Select.Trigger>
					<Select.Value></Select.Value>
				</Select.Trigger>
				<Select.Content>
					{#each intervals as interval}
						<Select.Item value={interval.value} disabled={interval.disabled}
							>{interval.label}</Select.Item
						>
					{/each}
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
	<div class="w-full min-w-0 p-5">
		<div class="flex flex-row justify-between">
			<h3 class="scroll-m-20 text-2xl font-semibold tracking-tight">{$currentStation.name}</h3>
			<div class="flex items-center gap-x-5">
				<Sheet.Root>
					<Tooltip.Root>
						<Tooltip.Trigger>
							<Sheet.Trigger>
								<Button variant="ghost" class="aspect-square p-0">
									<LucideArrowUpRightSquare></LucideArrowUpRightSquare>
								</Button>
							</Sheet.Trigger>
						</Tooltip.Trigger>
						<Tooltip.Content class="z-[9999]">Show data as list</Tooltip.Content>
					</Tooltip.Root>
					<Sheet.Content class="z-[1000]">
						<Sheet.Header>
							<Sheet.Title>List Data</Sheet.Title>
						</Sheet.Header>
						<Datatable></Datatable>
					</Sheet.Content>
				</Sheet.Root>
				<Button on:click={close} variant="ghost" class="aspect-square p-0"><X></X></Button>
			</div>
		</div>
		<div class="relative h-full max-h-96 w-full">
			<LoadingOverlay loading={$dataStore.loading} noData={$dataStore.data.length == 0}
			></LoadingOverlay>

			<canvas bind:this={chartElement}></canvas>
		</div>
	</div>
</div>
