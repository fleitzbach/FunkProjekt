<script lang="ts">
	import { derived } from 'svelte/store';
	import { currentStation, dataStore, stationList } from './store';
	import type { Station } from './types';

	import {
		addSortBy,
		addTableFilter,
		addHiddenColumns,
		addSelectedRows
	} from 'svelte-headless-table/plugins';
	import { createTable, Render, Subscribe, createRender } from 'svelte-headless-table';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';

	import * as Table from '$lib/components/ui/table';
	import { Button } from '$lib/components/ui/button';
	import { ArrowUpDown, ChevronDown } from 'lucide-svelte';
	import LoadingOverlay from './LoadingOverlay.svelte';
	
	// Derive tableData from dataStore and formatting.
	const tableData = derived(stationList, ($stationList) => $stationList.data);

	// Initialize the table with configuration for sorting, filtering, hiding columns, and row selection.
	const table = createTable(tableData, {
		sort: addSortBy({ disableMultiSort: true }),
		filter: addTableFilter({
			fn: ({ filterValue, value }) => value.includes(filterValue)
		}),
		hide: addHiddenColumns(),
		select: addSelectedRows()
	});

	// Define the columns for the table, including configuration for filtering and custom cell rendering.
	let columns = table.createColumns([
		table.column({
			accessor: 'id',
			header: 'StationID',
			plugins: {
				filter: {
					exclude: false
				}
			}
		}),
		table.column({
			accessor: 'name',
			header: 'Name',
			plugins: {
				filter: {
					exclude: true
				}
			}
		}),
		table.column({
			accessor: 'first_year',
			header: 'First Year',
			cell: ({ value }) => {
				return value == null ? '–' : value;
			},
			plugins: {
				filter: {
					exclude: true
				}
			}
		}),
		table.column({
			accessor: 'last_year',
			header: 'Last Year',
			cell: ({ value }) => {
				return value == null ? '–' : value;
			},
			plugins: {
				filter: {
					exclude: true
				}
			}
		}),
		table.column({
			accessor: 'latitude',
			header: 'Latitude',
			plugins: {
				filter: {
					exclude: true
				}
			}
		}),
		table.column({
			accessor: 'longitude',
			header: 'Longitude',
			plugins: {
				filter: {
					exclude: true
				}
			}
		}),
		table.column({
			accessor: 'distance',
			header: 'Distance',
			cell: ({ value }) => {
				const formatted = new Intl.NumberFormat('en-US', {
					style: 'unit',
					unit: 'kilometer',
					unitDisplay: 'short'
				}).format(value);
				return value == null ? '–' : formatted;
			},
			plugins: {
				filter: {
					exclude: true
				}
			}
		}),
		table.column({
			accessor: (station) => station,
			header: '',
			cell: ({ value }) => {
				return createRender(Button, {
					variant: 'link',
					size: 'sm',
					class: 'p-0'
				})
					.on('click', () => handleButtonClick(value))
					.slot('view Data');
			},
			plugins: {
				sort: {
					disable: true
				}
			}
		})
	]);

	function handleButtonClick(station: Station) {
		// Function to handle button click in the table, updating the current station and fetching temperature data.
		currentStation.setCurrentStation(station);
		dataStore.fetchTemperatureData(station.id);
	}

	// Use table.createViewModel to extract necessary properties for rendering the table and managing its state.
	const { headerRows, pageRows, tableAttrs, tableBodyAttrs, pluginStates, flatColumns, rows } =
		table.createViewModel(columns);
	const { hiddenColumnIds } = pluginStates.hide;
	const { selectedDataIds } = pluginStates.select;
	const ids = flatColumns.map((col) => col.id);

	// Setup for managing which columns are hidden.
	let hideForId = Object.fromEntries(ids.map((id) => [id, true]));
	$: $hiddenColumnIds = Object.entries(hideForId)
		.filter(([, hide]) => !hide)
		.map(([id]) => id);
	const hidableCols = ['name', 'distance', 'latitude', 'longitude', 'first_year', 'last_year'];
</script>

<div class="pb-4">
	<DropdownMenu.Root>
		<DropdownMenu.Trigger asChild let:builder>
			<Button variant="outline" class="ml-auto" builders={[builder]}>
				Columns <ChevronDown class="ml-2 h-4 w-4" />
			</Button>
		</DropdownMenu.Trigger>
		<DropdownMenu.Content>
			{#each flatColumns as col}
				{#if hidableCols.includes(col.id)}
					<DropdownMenu.CheckboxItem bind:checked={hideForId[col.id]}>
						{col.header}
					</DropdownMenu.CheckboxItem>
				{/if}
			{/each}
		</DropdownMenu.Content>
	</DropdownMenu.Root>
</div>

<LoadingOverlay noData={$tableData.length == 0} backgroundOverlay={false}></LoadingOverlay>
<div class="relative flex h-[calc(100%-3.5rem)] min-h-0 flex-row overflow-clip rounded-md">
	<Table.Root {...$tableAttrs}>
		<Table.Header>
			{#each $headerRows as headerRow (headerRow.id)}
				<Subscribe rowAttrs={headerRow.attrs()}>
					<Table.Row class="bg-background sticky top-0">
						{#each headerRow.cells as cell (cell.id)}
							<Subscribe attrs={cell.attrs()} let:attrs props={cell.props()} let:props>
								<Table.Head {...attrs}>
									{#if cell.id === 'distance'}
										<Button variant="ghost" class="-mx-4" on:click={props.sort.toggle}>
											<Render of={cell.render()} />
											<ArrowUpDown class={'ml-2 h-4 w-4'} />
										</Button>
									{:else}
										<Render of={cell.render()} />
									{/if}
								</Table.Head>
							</Subscribe>
						{/each}
					</Table.Row>
				</Subscribe>
			{/each}
		</Table.Header>
		<Table.Body {...$tableBodyAttrs}>
			{#each $pageRows as row (row.id)}
				<Subscribe rowAttrs={row.attrs()} let:rowAttrs>
					<Table.Row {...rowAttrs} data-state={$selectedDataIds[row.id] && 'selected'}>
						{#each row.cells as cell (cell.id)}
							<Subscribe attrs={cell.attrs()} let:attrs>
								<Table.Cell {...attrs} class="[&:has([role=checkbox])]:pl-3">
									<Render of={cell.render()} />
								</Table.Cell>
							</Subscribe>
						{/each}
					</Table.Row>
				</Subscribe>
			{/each}
		</Table.Body>
	</Table.Root>
</div>
