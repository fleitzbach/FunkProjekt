<script lang="ts">
	import { onMount } from 'svelte';
	import { createTable, Render, Subscribe } from 'svelte-headless-table';
	import { addSortBy, addTableFilter, addSelectedRows } from 'svelte-headless-table/plugins';
	import { derived } from 'svelte/store';
	import * as Table from '$lib/components/ui/table';
	import { Button } from '$lib/components/ui/button';
	import { ArrowUpDown } from 'lucide-svelte';
	import { dataStore } from './store';

	const tableData = derived(dataStore, ($dataStore) => $dataStore.data);

	const table = createTable(tableData, {
		sort: addSortBy({ disableMultiSort: true }),
		filter: addTableFilter({
			fn: ({ filterValue, value }) => value.includes(filterValue)
		}),
		select: addSelectedRows()
	});
	const columns = table.createColumns([
		table.column({
			accessor: 'season',
			header: 'Season',
			cell: ({ value }) => {
				const year = value.substring(0, 4);
				const seasonCode = value.substring(5);
				let seasonName = '';
				switch (seasonCode) {
					case 'winter':
						seasonName = 'Winter';
						break;
					case 'spring':
						seasonName = 'Spring';
						break;
					case 'summer':
						seasonName = 'Summer';
						break;
					case 'autumn':
						seasonName = 'Autumn';
						break;
					default:
						seasonName = 'Unknown Season';
				}
				return `${seasonName} ${year}`;
			}
		}),
		table.column({
			accessor: 'TMIN',
			header: 'T-Min',
			cell: ({ value }) => {
				return value == null ? '–' : value;
			}
		}),
		table.column({
			accessor: 'TMAX',
			header: 'T-Max',
			cell: ({ value }) => {
				return value == null ? '–' : value;
			}
		})
	]);

	const { headerRows, pageRows, tableAttrs, tableBodyAttrs, pluginStates} =
		table.createViewModel(columns);
	const { selectedDataIds } = pluginStates.select;

	onMount(() => {});
</script>

<div
	class="flex h-full max-h-[calc(100%-1.5rem)] min-h-0 min-w-0 flex-row overflow-clip rounded-md"
>
	<Table.Root {...$tableAttrs}>
		<Table.Header>
			{#each $headerRows as headerRow}
				<Subscribe rowAttrs={headerRow.attrs()}>
					<Table.Row class="bg-background sticky top-0">
						{#each headerRow.cells as cell (cell.id)}
							<Subscribe attrs={cell.attrs()} let:attrs props={cell.props()} let:props>
								<Table.Head {...attrs}>
									{#if cell.id === 'TMIN'}
										<Button variant="ghost" on:click={props.sort.toggle}>
											<Render of={cell.render()} />
											<ArrowUpDown class={'ml-2 h-4 w-4'} />
										</Button>
									{:else if cell.id === 'TMAX'}
										<Button variant="ghost" on:click={props.sort.toggle}>
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
									{#if cell.id === 'TMIN'}
										<div class="px-4">
											<Render of={cell.render()} />
										</div>
									{:else if cell.id === 'TMAX'}
										<div class="px-4">
											<Render of={cell.render()} />
										</div>
									{:else}
										<Render of={cell.render()} />
									{/if}
								</Table.Cell>
							</Subscribe>
						{/each}
					</Table.Row>
				</Subscribe>
			{/each}
		</Table.Body>
	</Table.Root>
</div>
