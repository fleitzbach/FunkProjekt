<script lang="ts">
	import Chart from 'chart.js/auto';
	import { onMount } from 'svelte';
	import { dataStore, currentStation, dataSettings } from './store';
	import { Input } from './components/ui/input';
	import { Button } from './components/ui/button';
	import * as Select from './components/ui/select';
	import { Label } from './components/ui/label';
	import type { DataSettings } from './types';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import { X } from 'lucide-svelte';
	import { LucideArrowUpRightSquare } from 'lucide-svelte';
	import { Undo2 } from 'lucide-svelte';
	import { toast } from 'svelte-sonner';
	import LoadingOverlay from '$lib/LoadingOverlay.svelte';
	import 'chartjs-adapter-luxon';
	import * as Sheet from '$lib/components/ui/sheet';
	import Datatable from './DataTable.svelte';
	import Datatableseason from './DataTableSeason.svelte';
	import { DateTime } from 'luxon';

	let chartElement;
	let chart;

	let undoUpdate = false;

	let dataControls: DataSettings = {
		interval: $dataSettings.interval
	};

	// Stores history for undo functionality
	let history: DataSettings[] = [];

	// Define dropdown options
	let intervals = [
		{ value: 'year', label: 'Year', disabled: false },
		{ value: 'season', label: 'Season', disabled: false },
		{ value: 'month', label: 'Month', disabled: false },
		{ value: 'day', label: 'Day', disabled: false }
	];

	// Computed property to find the selected interval from the predefined intervals
	$: selectedInterval = intervals.find((interval) => interval.value === dataControls.interval);

	// Defines scale configurations for different intervals on the chart
	const xScale = {
		year: {
			type: 'time',
			time: {
				unit: 'year'
			}
		},
		month: {
			type: 'time',
			time: {
				unit: 'month'
			}
		},
		day: {
			type: 'time',
			time: {
				unit: 'day'
			}
		},
		season: {}
	};

	// Function to revert the last data filter applied
	function undoFiltering() {
		if (history.length == 0) {
			return;
		}
		dataControls = history.pop();
		history = [...history];

		undoUpdate = true;
		updateData();
	}

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
					x: xScale[dataControls.interval]
				},
				onClick: function (event, chartElements) {
					if (chartElements.length === 0) {
						return;
					}
					const elementIndex = chartElements[0].index;
					const dataPoint = this.data.labels[elementIndex];
					if (dataControls.interval == 'year') {
						dataControls.start = `01.01.${dataPoint}`;
						dataControls.end = `31.12.${dataPoint}`;
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
							return;
						}
						dataControls.start = `01.${datapoint_month}.${datapoint_year}`;
						dataControls.end = `${datapoint_endDay}.${datapoint_month}.${datapoint_year}`;
						dataControls.interval = 'day';
						updateData();
					} else if (dataControls.interval == 'season') {
						let datapoint_split = dataPoint.split(' ');
						let datapoint_year = datapoint_split[1];

						if (datapoint_split[0] == 'Winter') {
							dataControls.start = `21.12.${datapoint_year - 1}`;
							dataControls.end = `20.03.${datapoint_year}`;
						} else if (datapoint_split[0] == 'Spring') {
							dataControls.start = `21.03.${datapoint_year}`;
							dataControls.end = `20.06.${datapoint_year}`;
						} else if (datapoint_split[0] == 'Summer') {
							dataControls.start = `21.06.${datapoint_year}`;
							dataControls.end = `22.09.${datapoint_year}`;
						} else if (datapoint_split[0] == 'Autumn') {
							dataControls.start = `23.09.${datapoint_year}`;
							dataControls.end = `20.12.${datapoint_year}`;
						}
						dataControls.interval = 'day';
						updateData();
					}
				}
			}
		});

		// Setup subscription to the store
		const unsubscribe = dataStore.subscribe((data) => {
			if (data.loading) {
				return;
			}
			updateChart(data.data);
		});

		// Cleanup on component destroy
		return () => {
			unsubscribe();
			if (chart) chart.destroy();
		};
	});

	// Generates labels for seasons given a start and end year
	const generateSeasons = (startYear: number, endYear: number): string[] => {
		const seasons = ['winter', 'spring', 'summer', 'autumn'];
		const allSeasons: string[] = [];

		for (let year = startYear; year <= endYear; year++) {
			seasons.forEach((season, index) => {
				allSeasons.push(`${year}${index + 1}${season}`);
			});
		}

		return allSeasons;
	};

	// Fills missing data for seasons
	const fillMissingData = (data) => {
		const firstYear = parseInt(data[0].season.substring(0, 4));
		const lastYear = parseInt(data[data.length - 1].season.substring(0, 4));

		const allSeasons = generateSeasons(firstYear, lastYear);

		return allSeasons.map((season) => {
			const existingData = data.find((d) => d.season === season);
			return existingData ? existingData : { season };
		});
	};

	// Updates the chart with new data
	function updateChart(data) {
		if (chart && data) {
			chart.options.scales.x = xScale[dataControls.interval];
			if (dataControls.interval == 'season') {
				data = fillMissingData(data);
				let labels = data.map((d) => {
					let seasonCode = d.season.substring(5, d.season.length);
					let year = d.season.substring(0, 4);
					let season;
					const seasonMap = {
						spring: 'Spring',
						summer: 'Summer',
						autumn: 'Autumn',
						winter: 'Winter'
					};

					season = seasonMap[seasonCode];
					return `${season} ${year}`;
				});

				chart.data.labels = labels;
				chart.data.datasets[0].data = data.map((row) => row.TMAX);
				chart.data.datasets[1].data = data.map((row) => row.TMIN);
				chart.update();
			} else {
				chart.data.labels = data.map((row) => row.date);
				chart.data.datasets[0].data = data.map((row) => row.TMAX);
				chart.data.datasets[1].data = data.map((row) => row.TMIN);
				chart.update();
			}
		}
	}

	// Parses a date string into a DateTime object
	function parseDate(input) {
		// regex for date in the format dd.mm.yyyy, mm.yyyy or yyyy
		const regex = /^(?:(\d{1,2})\.(\d{1,2})\.(\d{4})|(\d{1,2})\.(\d{4})|(\d{4}))$/;
		const matches = input.match(regex);

		if (!matches) {
			toast.warning('Please enter valid date.');
			return null;
		}

		let date;

		if (matches[1] && matches[2] && matches[3]) {
			// dd.mm.yyyy Format
			date = DateTime.local(
				parseInt(matches[3], 10),
				parseInt(matches[2], 10),
				parseInt(matches[1], 10)
			);
		} else if (matches[4] && matches[5]) {
			// mm.yyyy Format
			date = DateTime.local(parseInt(matches[5], 10), parseInt(matches[4], 10), 1);
		} else if (matches[6]) {
			// yyyy Format
			date = DateTime.local(parseInt(matches[6], 10), 1, 1);
		}

		if (!date || !date.isValid) {
			toast.warning('Please enter valid date.');
			return null;
		}

		return date;
	}

	// Updates data according to current settings and fetches new data if necessary
	function updateData() {
		let start;
		let end;
		if (!undoUpdate) {
			history.push({
				start:
					$dataSettings.start == null
						? ''
						: new Date($dataSettings.start).toLocaleDateString('de-DE'),
				end:
					$dataSettings.end == null ? '' : new Date($dataSettings.end).toLocaleDateString('de-DE'),
				interval: $dataSettings.interval
			});
			history = [...history];
		} else {
			undoUpdate = false;
		}
		let settings: DataSettings = { interval: dataControls.interval };
		dataSettings.setSettings(settings);
		if (dataControls.start) {
			start = parseDate(dataControls.start);
			if (!start.isValid) {
				return;
			} else {
				settings.start = start.toISODate();
				dataControls.start = start.toLocaleString(DateTime.DATE_SHORT, { locale: 'de' });
			}
		}
		if (dataControls.end) {
			end = parseDate(dataControls.end);
			if (!end.isValid) {
				return;
			} else {
				settings.end = end.toISODate();
				dataControls.end = end.toLocaleString(DateTime.DATE_SHORT, { locale: 'de' });
			}
		}

		if (start && end && start > end) {
			toast.warning('End date is before start date.');
			return;
		}

		dataStore.fetchTemperatureData($currentStation.id);
	}

	// needed to internally keep track of the selected interval
	function intervalChange(option) {
		let o = option as Option<T>;
		if (o) {
			dataControls.interval = o.value;
		}
	}

	// Clears input fields
	function clearSettings() {
		dataControls = { interval: 'year' };
		dataSettings.clearSettings();
		toast('cleared settings');
	}

	// Closes the chart section
	function close() {
		currentStation.clearCurrentStation();
	}
</script>

<div class="bg-primary-foreground flex w-full flex-row">
	<!-- Data Controls -->
	<div class="flex w-full min-w-[300px] max-w-[300px] flex-col items-baseline gap-5 p-5">
		<div class="flex w-full flex-row justify-between">
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
				<Input
					type="text"
					id="start"
					bind:value={dataControls.start}
					class="w-full"
					placeholder="tt.mm.jjjj"
				/>
			</div>
			<div>
				<Label for="end" class="font-semibold">End date</Label>
				<Input
					type="text"
					id="end"
					bind:value={dataControls.end}
					class="w-full"
					placeholder="tt.mm.jjjj"
				/>
			</div>
		</div>
		<Button on:click={updateData} disabled={$dataStore.loading} class="w-28">
			{#if $dataStore.loading}
				<svg
					width="24"
					height="24"
					class="fill-primary-foreground"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
					><path
						d="M12,1A11,11,0,1,0,23,12,11,11,0,0,0,12,1Zm0,19a8,8,0,1,1,8-8A8,8,0,0,1,12,20Z"
						opacity=".25"
					/><path
						d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z"
						><animateTransform
							attributeName="transform"
							type="rotate"
							dur="0.75s"
							values="0 12 12;360 12 12"
							repeatCount="indefinite"
						/></path
					></svg
				>
			{:else}
				Update Data
			{/if}</Button
		>
	</div>
	<!-- Visualisation -->
	<div class="w-full min-w-0 p-5">
		<div class="flex flex-row justify-between">
			<h3 class="scroll-m-20 text-2xl font-semibold tracking-tight">{$currentStation.name}</h3>
			<div class="flex items-center gap-x-5">
				<Tooltip.Root>
					<Tooltip.Trigger>
						<Button
							variant="ghost"
							class="aspect-square p-0"
							disabled={history.length === 0}
							on:click={undoFiltering}
						>
							<Undo2></Undo2>
						</Button>
					</Tooltip.Trigger>
					<Tooltip.Content class="z-[9999]">Click to undo!</Tooltip.Content>
				</Tooltip.Root>
				<Sheet.Root>
					<Tooltip.Root>
						<Sheet.Trigger>
							<Tooltip.Trigger>
								<Button variant="ghost" class="aspect-square p-0">
									<LucideArrowUpRightSquare></LucideArrowUpRightSquare>
								</Button>
							</Tooltip.Trigger>
						</Sheet.Trigger>
						<Tooltip.Content class="z-[9999]">Show data as list</Tooltip.Content>
					</Tooltip.Root>
					<Sheet.Content class="z-[1000]">
						<Sheet.Header>
							<Sheet.Title>List Data</Sheet.Title>
						</Sheet.Header>
						<LoadingOverlay noData={$dataStore.data.length === 0} backgroundOverlay={false}
						></LoadingOverlay>

						{#if $dataSettings.interval === 'season'}
							<Datatableseason></Datatableseason>
						{:else}
							<Datatable></Datatable>
						{/if}
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
