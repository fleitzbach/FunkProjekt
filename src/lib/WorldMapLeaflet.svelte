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
	let map;
	let circle;
	let latitude;
	let longitude;
	let radius = [30];
	export let pointsPromise;
	let points;
	let markers;
	const initialView = [[48, 9], 6];
	let markerIcon;

	function createMap(container) {
		let m = L.map(container, { preferCanvas: true, zoomControl: false, maxZoom: 13 }).setView(
			...initialView
		);
		L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
			attribution: `&copy;<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>,
	        &copy;<a href="https://carto.com/attributions" target="_blank">CARTO</a>`,
			subdomains: 'abcd'
		}).addTo(m);

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
		latitude = e.latlng.lat;
		longitude = e.latlng.lng;
	}

	function dataLoaded() {
		console.log('data loaded');
	}

	onMount(() => {
		pointsPromise.then((res) => {
			points = res;
			dataLoaded();
		});

		circle = L.circle([48, 9], {
			color: 'red',
			fillColor: '#f03',
			fillOpacity: 0.1,
			radius: 50000,
			interactive: false
		}).addTo(map);

		map.on('click', onMapClick);

		L.DomUtil.addClass(map._container, 'cursor-default');
		L.DomUtil.removeClass(map._container, 'leaflet-grab');

		markers = L.markerClusterGroup({
			spiderfyOnMaxZoom: false,
			showCoverageOnHover: false,
			zoomToBoundsOnClick: true,
			maxClusterRadius: 30,
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
					className: 'bg-black text-white rounded-full'
				});
			}
		});
		map.addLayer(markers);

		markerIcon = new L.Icon({
			iconUrl: './icons/pin.svg',
			iconSize: [32, 32],
			iconAnchor: [16, 32],
			popupAnchor: [0, -16]
		});
	});

	function viewData() {
		console.log('test');
	}

	function search(e) {
		let lat = parseFloat(latitude);
		let lng = parseFloat(longitude);
		let maxDistance = radius[0];
		// console.log(lat, lng, maxDistance);

		if (!isNaN(lat) && !isNaN(lng)) {
			circle.setRadius(maxDistance * 1000);
			circle.setLatLng([lat, lng]);

			let closestPoint: {};
			let closestDistance = Infinity;
			let nearbyPoints = points.filter((point) => {
				const distance = calculateDistance(lat, lng, point.latitude, point.longitude);
				return distance <= maxDistance;
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
				marker.on('click', () => {
					const popupContent = document.createElement('div');
					new MarkerPopup({
						target: popupContent,
						props: {
							name: point.name
						}
					});

					marker.bindPopup(popupContent);
				});

				markers.addLayer(marker);
			});

			map.fitBounds(circle.getBounds());
		}
	}
</script>

<div class="flex flex-row h-full">
	<div class="p-5 flex flex-col gap-5 items-baseline grow max-w-[300px] w-full">
		<h3 class="scroll-m-20 text-2xl font-semibold tracking-tight">Search for Stations</h3>
		<div class="w-full">
			<Label for="coordinates" class="font-semibold">Coordinates</Label>
			<HoverCard.Root>
				<HoverCard.Trigger class="inline-block">
					<img width="12" height="12" src="./icons/info-outlined.svg" alt="info" />
				</HoverCard.Trigger>
				<HoverCard.Content>Click anywhere on the map to set coordinates.</HoverCard.Content>
			</HoverCard.Root>
			<div class="rounded-md border border-input" id="coordinates">
				<Input
					type="text"
					bind:value={latitude}
					placeholder="Latitude"
					class="rounded-none border-none"
				/>
				<Separator class="h-[.5px]"></Separator>
				<Input
					type="text"
					bind:value={longitude}
					placeholder="Longitude"
					class="rounded-none border-none"
				/>
			</div>
		</div>
		<div class="w-full">
			<Label for="radius" class="font-semibold">Radius</Label>
			<Slider bind:value={radius} id="radius" class="py-2" />
		</div>
		<Button type="button" on:click={search}>Search</Button>
	</div>
	<div class="relative w-full h-full">
		<div id="map" class="h-full w-full outline-none" use:mapAction></div>
		<div class="absolute top-0 left-0 p-5 z-[1000] flex flex-col gap-2">
			<Button variant="outline" class="shadow w-10 p-0" on:click={map.zoomIn(1)}
				><img width="16" height="16" src="./icons/plus.svg" alt="zoom in" /></Button
			>
			<Button variant="outline" class="shadow w-10 p-0" on:click={map.zoomOut(1)}
				><img width="16" height="16" src="./icons/minus.svg" alt="zoom out" /></Button
			>
		</div>
	</div>
</div>

<style>
</style>
