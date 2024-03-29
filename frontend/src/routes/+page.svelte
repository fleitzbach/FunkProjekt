<script lang="ts">
	import * as L from 'leaflet?client';
	import 'leaflet/dist/leaflet.css';
	import 'leaflet.markercluster?client';
	import 'leaflet.markercluster/dist/MarkerCluster.css';
	import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
	import MarkerPopup from '$lib/MarkerPopup.svelte';
	import { Input } from '$lib/components/ui/input';
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label';
	import { Separator } from '$lib/components/ui/separator';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import SliderWithInput from '$lib/components/SliderWithInput.svelte';
	import { Toaster } from '$lib/components/ui/sonner';
	import { toast } from 'svelte-sonner';
	import { mode, ModeWatcher } from 'mode-watcher';
	import * as Tabs from '$lib/components/ui/tabs';
	import TemperatureChart from '$lib/TemperatureChart.svelte';
	import { stationList, currentStation } from '$lib/store';
	import Switch from '$lib/components/ui/switch/switch.svelte';
	import StationTable from '$lib/StationTable.svelte';
	import type { Station } from '$lib/types';
	import { Info } from 'lucide-svelte';

	let map;
	let circle;
	let maxStations: number = 100;
	let markers;
	let markerIcon;
	const initialView = [[48, 9], 6];

	let darkMap;
	let lightMap;

	let coordinates: string;
	// set latitude and longitude dynamically
	$: latitude = coordinates?.split(/\,\s*/)[0];
	$: longitude = coordinates?.split(/\,\s*/)[1];
	let radius: number = 50;
	let startYear;
	let endYear;
	let searchByCoordinates: boolean = true;
	let searchName = '';

	$: handleThemeChange($mode);
	let selectionMarker;
	let selectionMarkerIcon;

	function handleThemeChange(mode) {
		if (lightMap && darkMap) {
			if (mode === 'dark') {
				darkMap.addTo(map);
				lightMap.remove();
			} else {
				lightMap.addTo(map);
				darkMap.remove();
			}
		}
	}

	function mapAction(container) {
		// initialize map and related components
		map = L.map(container, {
			preferCanvas: true,
			zoomControl: false,
			maxZoom: 12,
			minZoom: 3
		}).setView(...initialView);

		map.on('click', onMapClick);

		darkMap = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
			attribution: `&copy;<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>,
          &copy;<a href="https://carto.com/attributions" target="_blank">CARTO</a>`,
			subdomains: 'abcd'
		});

		lightMap = L.tileLayer(
			'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
			{
				attribution: `&copy;<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>,
          &copy;<a href="https://carto.com/attributions" target="_blank">CARTO</a>`,
				subdomains: 'abcd'
			}
		);

		handleThemeChange($mode);

		L.DomUtil.addClass(map._container, 'cursor-default');
		L.DomUtil.removeClass(map._container, 'leaflet-grab');

		markerIcon = new L.divIcon({
			html: `<svg width="32px" height="32px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M11.291 21.706 12 21l-.709.706zM12 21l.708.706a1 1 0 0 1-1.417 0l-.006-.007-.017-.017-.062-.063a47.708 47.708 0 0 1-1.04-1.106 49.562 49.562 0 0 1-2.456-2.908c-.892-1.15-1.804-2.45-2.497-3.734C4.535 12.612 4 11.248 4 10c0-4.539 3.592-8 8-8 4.408 0 8 3.461 8 8 0 1.248-.535 2.612-1.213 3.87-.693 1.286-1.604 2.585-2.497 3.735a49.583 49.583 0 0 1-3.496 4.014l-.062.063-.017.017-.006.006L12 21zm0-8a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" clip-rule="evenodd"/></svg>`,
			iconSize: [32, 32],
			iconAnchor: [16, 32],
			popupAnchor: [0, -16],
			className: 'drop-shadow fill-primary'
		});

		selectionMarkerIcon = new L.divIcon({
			html: `<svg width="32px" height="32px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M11.291 21.706 12 21l-.709.706zM12 21l.708.706a1 1 0 0 1-1.417 0l-.006-.007-.017-.017-.062-.063a47.708 47.708 0 0 1-1.04-1.106 49.562 49.562 0 0 1-2.456-2.908c-.892-1.15-1.804-2.45-2.497-3.734C4.535 12.612 4 11.248 4 10c0-4.539 3.592-8 8-8 4.408 0 8 3.461 8 8 0 1.248-.535 2.612-1.213 3.87-.693 1.286-1.604 2.585-2.497 3.735a49.583 49.583 0 0 1-3.496 4.014l-.062.063-.017.017-.006.006L12 21zm0-8a3 3 0 1 0 0-6 3 3 0 0 0 0 6z" clip-rule="evenodd"/></svg>`,
			iconSize: [32, 32],
			iconAnchor: [16, 32],
			popupAnchor: [0, -16],
			className: 'drop-shadow fill-red-500 cursor-default'
		});

		circle = L.circle([0, 0], {
			color: '#105082',
			fillColor: '#105082',
			fillOpacity: 0.1,
			radius: 0,
			interactive: false
		});

		markers = L.markerClusterGroup({
			spiderfyOnMaxZoom: false,
			showCoverageOnHover: false,
			zoomToBoundsOnClick: true,
			maxClusterRadius: 40,
			disableClusteringAtZoom: map.getMaxZoom(),
			iconCreateFunction: function (cluster) {
				return L.divIcon({
					html: `
						<div class="flex justify-center items-center w-full h-full">
							<h4 class="scroll-m-20 text-md font-semibold tracking-tight">
							${cluster.getChildCount()}
							</h4>
						</div>
						`,
					iconSize: [32, 32],
					className: 'bg-background text-primary rounded-full shadow'
				});
			}
		});

		map.addLayer(markers);

		// listen for map resize
		const mapResizeObserver = new ResizeObserver((entries) => {
			for (let entry of entries) {
				if (map) map.invalidateSize();
			}
		});

		mapResizeObserver.observe(document.querySelector('#map-container'));

		// subscribe to station list
		const unsubscribe = stationList.subscribe((data) => {
			if (!latitude || !longitude) {
				return;
			}
			if (!map) {
				return;
			}

			updateMarkers(data);
		});

		// cleanup when component is destroyed
		return {
			destroy: () => {
				unsubscribe();
				markers.remove();
				circle.remove();
				map.remove();
				mapResizeObserver.disconnect();
				map = null;
			}
		};
	}

	function onMapClick(e) {
		let lat = e.latlng.lat.toFixed(5);
		let lng = e.latlng.lng.toFixed(5);
		if (selectionMarker) {
			map.removeLayer(selectionMarker);
		}
		if (searchByCoordinates) {
			coordinates = `${lat}, ${lng}`;
			selectionMarker = L.marker([lat, lng], { icon: selectionMarkerIcon, interactive: false });
			selectionMarker.addTo(map);
		}
	}

	// hide selection marker when searching by name
	$: if (!searchByCoordinates) {
		if (selectionMarker) {
			selectionMarker.setOpacity(0);
		}
	} else if (searchByCoordinates) {
		if (selectionMarker) {
			selectionMarker.setOpacity(1);
		}
	}

	async function search(e) {
		const lat = parseFloat(latitude);
		const lng = parseFloat(longitude);

		let start = parseInt(startYear);
		let end = parseInt(endYear);

		if (isNaN(start)) {
			startYear = '';
		} else {
			startYear = start;
		}

		if (isNaN(end)) {
			endYear = '';
		} else {
			endYear = end;
		}

		if (searchByCoordinates) {
			if (isNaN(lat) || isNaN(lng)) {
				toast.warning('Please enter valid coordinates.');
				return;
			}

			if (selectionMarker) {
				map.removeLayer(selectionMarker);
			}

			// Add Marker to Search Coordinates
			coordinates = `${lat}, ${lng}`;
			selectionMarker = L.marker([lat, lng], { icon: selectionMarkerIcon, interactive: false });
			selectionMarker.addTo(map);

			stationList.fetchStationsByCoords(
				lat,
				lng,
				radius,
				startYear || undefined,
				endYear || undefined,
				maxStations || undefined
			);
		} else {
			if (!searchName) {
				toast.warning('Please enter a station name.');
				return;
			}

			circle.remove();
			stationList.fetchStationsByName(searchName);
		}
	}

	function updateMarkers(stations) {
		stations = stations.data;
		markers.clearLayers();
		stations.forEach((station: Station) => {
			const marker = L.marker([station.latitude, station.longitude], { icon: markerIcon });
			const popupContent = document.createElement('div');
			new MarkerPopup({
				target: popupContent,
				props: { station: station }
			});
			marker.bindPopup(popupContent);
			markers.addLayer(marker);
		});
		if (searchByCoordinates) {
			updateCircle(latitude, longitude, radius);
			map.fitBounds(circle.getBounds());
		}
		if (searchByCoordinates === false) {
			if (stations.length === 0) {
				return;
			}
			map.fitBounds(markers.getBounds());
		}
	}

	function updateCircle(lat, lng, radius) {
		circle.setRadius(radius * 1000);
		circle.setLatLng([lat, lng]);
		circle.addTo(map);
	}
</script>

<main>
	<Tabs.Root value="map" class="flex h-full w-full flex-col">
		<div class="relative m-0 flex h-full min-h-0 w-full min-w-0 flex-grow flex-row">
			<!-- Search settings -->
			<div class="flex h-full min-h-0 w-full max-w-[320px] flex-col items-baseline overflow-auto">
				<h3
					class="bg-accent dark:text-primary text-primary-foreground sticky top-0 z-10 flex w-full flex-row items-center justify-between p-5 text-2xl font-semibold tracking-tight"
				>
					Search for stations
					<img src="/favicon.png" alt="logo" class="aspect-square h-8 rounded-full" />
				</h3>
				<div class="flex w-full flex-col gap-5 p-5">
					<div>
						<Label for="search-by-coordinates" class="font-semibold">Search by</Label>
						<div class="flex items-center gap-2 py-2">
							Name
							<Switch bind:checked={searchByCoordinates}></Switch>
							Coordinates
						</div>
					</div>
					{#if searchByCoordinates}
						<div class="flex flex-col gap-5">
							<div class="w-full">
								<Label for="coordinates" class="font-semibold">Coordinates</Label>
								<Tooltip.Root>
									<Tooltip.Trigger class="inline-block">
										<Info size={12} />
									</Tooltip.Trigger>
									<Tooltip.Content
										>Click anywhere on the <br /> map to set coordinates.</Tooltip.Content
									>
								</Tooltip.Root>
								<Input
									type="text"
									bind:value={coordinates}
									placeholder="Latitude, Longitude"
									id="coordinates"
									class=""
								/>
							</div>
							<div class="w-full">
								<Label for="radius" class="font-semibold">Radius</Label>
								<SliderWithInput bind:value={radius} min={10} max={100} unit={'km'}
								></SliderWithInput>
							</div>
							<div class="flex flex-row items-center gap-5">
								<div>
									<Label for="start" class="font-semibold">Start year</Label>
									<Input
										type="text"
										id="start"
										bind:value={startYear}
										class="w-full"
										placeholder="jjjj"
									/>
								</div>
								<div>
									<Label for="end" class="font-semibold">End year</Label>
									<Input
										type="text"
										id="end"
										bind:value={endYear}
										class="w-full"
										placeholder="jjjj"
									/>
								</div>
							</div>
						</div>
						<div class="w-full">
							<Label for="radius" class="font-semibold">Max Stations</Label>
							<SliderWithInput bind:value={maxStations} min={1} max={500}></SliderWithInput>
						</div>
					{:else}
						<div class="w-full overflow-clip">
							<Label for="station-name" class="font-semibold">Station Name</Label>
							<Input type="text" id="station-name" class="w-full" bind:value={searchName} />
						</div>
					{/if}

					<Button type="button" disabled={$stationList.loading} class="w-24" on:click={search}>
						{#if $stationList.loading}
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
							Search
						{/if}
					</Button>
				</div>
			</div>
			<Separator orientation="vertical"></Separator>

			<!-- Map View -->
			<Tabs.Content value="map" id="map-container" class="relative m-0 h-full w-full ">
				<div id="map" class="h-full w-full outline-none" use:mapAction></div>
				<!-- Zoom Controls -->
				<div class="absolute left-0 top-0 z-[1000] flex flex-col gap-2 p-5">
					<Button variant="outline" class="bg-background w-10 p-0 shadow" on:click={map.zoomIn(1)}
						><svg
							width="16"
							height="16"
							class="fill-primary"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
							><path
								d="M11.883 3.007 12 3a1 1 0 0 1 .993.883L13 4v7h7a1 1 0 0 1 .993.883L21 12a1 1 0 0 1-.883.993L20 13h-7v7a1 1 0 0 1-.883.993L12 21a1 1 0 0 1-.993-.883L11 20v-7H4a1 1 0 0 1-.993-.883L3 12a1 1 0 0 1 .883-.993L4 11h7V4a1 1 0 0 1 .883-.993L12 3l-.117.007Z"
							/></svg
						></Button
					>
					<Button variant="outline" class="bg-background w-10 p-0 shadow" on:click={map.zoomOut(1)}
						><svg
							width="16"
							height="16"
							class="fill-primary"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
							><path d="M3.997 13H20a1 1 0 1 0 0-2H3.997a1 1 0 1 0 0 2Z" /></svg
						></Button
					>
				</div>
			</Tabs.Content>
			<!-- List View -->
			<Tabs.Content value="list" class="relative m-0 box-border h-full w-full min-w-0 p-5">
				<StationTable></StationTable>
			</Tabs.Content>
			<div class="absolute right-0 top-0 z-[1000] p-5">
				<Tabs.List>
					<Tabs.Trigger value="map">Map</Tabs.Trigger>
					<Tabs.Trigger value="list">List</Tabs.Trigger>
				</Tabs.List>
			</div>
		</div>
		<!-- show the temperature chart if a station is selected -->
		{#if $currentStation.id != ''}
			<Separator orientation="horizontal"></Separator>
			<TemperatureChart></TemperatureChart>
		{/if}
	</Tabs.Root>

	<Toaster richColors={true} />
</main>
<ModeWatcher />

<style>
	#map {
		background: hsl(var(--primary-foreground));
	}
	main {
		height: 100vh;
	}
</style>
