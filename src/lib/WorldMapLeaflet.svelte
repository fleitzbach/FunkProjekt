<script lang="ts">
	import { onMount } from 'svelte';
	import * as L from 'leaflet?client';
	import 'leaflet/dist/leaflet.css';
	import 'leaflet.markercluster?client';
	import 'leaflet.markercluster/dist/MarkerCluster.css';
	import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
	import { calculateDistance } from './calculateDistance';
	import MarkerPopup from '$lib/MarkerPopup.svelte';
	import { Input } from '$lib/components/ui/input';
	import { Slider } from '$lib/components/ui/slider';
	import { Button } from '$lib/components/ui/button';
	import { Label } from '$lib/components/ui/label';
	import { Separator } from '$lib/components/ui/separator';
	import * as HoverCard from '$lib/components/ui/hover-card';
	import * as Tooltip from '$lib/components/ui/tooltip';
	import SliderWithInput from '$lib/components/SliderWithInput.svelte';
	import { Toaster } from '$lib/components/ui/sonner';
	import { toast } from 'svelte-sonner';
	import { setMode, mode, ModeWatcher } from 'mode-watcher';
	import * as Popover from '$lib/components/ui/popover';
	let map;
	let circle;
	let coordinates;
	$: latitude = coordinates?.split(/\,\s*/)[0];
	$: longitude = coordinates?.split(/\,\s*/)[1];
	let radius = 50;

	export let pointsPromise;
	let points;
	let markers;
	const initialView = [[48, 9], 6];
	let markerIcon;
	let darkMap;
	let lightMap;
	$: handleThemeChange($mode);
	let dataLoading = true;

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

	function createMap(container) {
		let m = L.map(container, {
			preferCanvas: true,
			zoomControl: false,
			maxZoom: 12,
			minZoom: 3
		}).setView(...initialView);

		return m;
	}

	function mapAction(container) {
		console.log('test');
		map = createMap(container);

		return {
			destroy: () => {
				map.remove();
				map = null;
			}
		};
	}

	function onMapClick(e) {
		let lat = e.latlng.lat.toFixed(5);
		let lng = e.latlng.lng.toFixed(5);
		coordinates = `${lat}, ${lng}`;
	}

	function dataLoaded() {
		dataLoading = false;
		toast('data loaded');
	}

	onMount(() => {
		pointsPromise.then((res) => {
			points = res;
			dataLoaded();
		});

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

		markerIcon = new L.Icon({
			iconUrl: './icons/pin.svg',
			iconSize: [32, 32],
			iconAnchor: [16, 32],
			popupAnchor: [0, -16],
			className: 'drop-shadow fill-primary'
		});

		circle = L.circle([0, 0], {
			color: '#ef4444',
			fillColor: '#ef4444',
			fillOpacity: 0.1,
			radius: 0,
			interactive: false
		});
	});

	function viewData() {
		console.log('test');
	}

	function search(e) {
		let lat = parseFloat(latitude);
		let lng = parseFloat(longitude);
		console.log(lat, lng, radius);

		if (!isNaN(lat) && !isNaN(lng)) {
			circle.setRadius(radius * 1000);
			circle.setLatLng([lat, lng]);
			circle.addTo(map);

			let closestPoint: {};
			let closestDistance = Infinity;
			let nearbyPoints = points.filter((point) => {
				const distance = calculateDistance(lat, lng, point.latitude, point.longitude);
				return distance <= radius;
			});

			nearbyPoints = nearbyPoints.map((point) => {
				return {
					latlng: [point.latitude, point.longitude],
					name: point.name
				};
			});
			markers.clearLayers();
			nearbyPoints.forEach((point) => {
				let marker = L.marker(point.latlng, { icon: markerIcon });
				const popupContent = document.createElement('div');
				new MarkerPopup({
					target: popupContent,
					props: {
						name: point.name
					}
				});

				marker.bindPopup(popupContent);

				markers.addLayer(marker);
			});

			map.fitBounds(circle.getBounds());
		}
	}
</script>

<div class="flex flex-row h-full">
	<div class="p-5 flex flex-col gap-5 items-baseline max-w-[300px] w-full">
		<h3 class="scroll-m-20 text-2xl font-semibold tracking-tight">Search for stations</h3>
		<div class="w-full">
			<Label for="station" class="font-semibold">Station</Label>

			<Input type="text" placeholder="Station name or ID" id="station" />
		</div>
		<div class="w-full">
			<Label for="coordinates" class="font-semibold">Coordinates</Label>
			<Tooltip.Root>
				<Tooltip.Trigger class="inline-block">
					<img width="12" height="12" src="./icons/info-outlined.svg" alt="info" />
				</Tooltip.Trigger>
				<Tooltip.Content>Click anywhere on the map to set coordinates.</Tooltip.Content>
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
			<SliderWithInput bind:value={radius} min={10} max={100} unit={'km'}></SliderWithInput>
		</div>
		<Button type="button" disabled={dataLoading} on:click={search}>Search</Button>
	</div>
	<div class="relative w-full h-full">
		<div id="map" class="h-full w-full outline-none" use:mapAction></div>
		<div class="absolute top-0 left-0 p-5 z-[1000] flex flex-col gap-2">
			<Button variant="ghost" class="shadow w-10 p-0 bg-background" on:click={map.zoomIn(1)}
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
			<Button variant="ghost" class="shadow w-10 p-0 bg-background" on:click={map.zoomOut(1)}
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
	</div>
</div>

<Toaster />

<ModeWatcher />

<style>
	#map {
		background: hsl(var(--background));
	}
</style>
