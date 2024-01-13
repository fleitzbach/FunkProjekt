<script lang="ts">
	import { onMount } from 'svelte';
	import * as L from 'leaflet?client';
	import 'leaflet/dist/leaflet.css';
	import 'leaflet.markercluster?client';
	import 'leaflet.markercluster/dist/MarkerCluster.css';
	import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
	import { calculateDistance } from './calculateDistance';
    import MarkerPopup from '$lib/MarkerPopup.svelte'
	let map;
	let circle;
	let latitude;
	let longitude;
	let radius;
	export let pointsPromise;
	let points;
	let markers;
	const initialView = [[48, 9], 5];

	function createMap(container) {
		let m = L.map(container, { preferCanvas: true }).setView(...initialView);
		L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
			attribution: `&copy;<a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>,
	        &copy;<a href="https://carto.com/attributions" target="_blank">CARTO</a>`,
			subdomains: 'abcd',
			maxZoom: 14
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
		circle.setLatLng(e.latlng);
	}

	function dataLoaded() {
		console.log('data loaded');
	}

	function renderPopupComponent(name) {
		const { html } = PopupComponent.render({ name });
		return html;
	}

	onMount(() => {
		pointsPromise.then((res) => {
			points = res;
			dataLoaded();
		});

		circle = L.circle([48, 9], {
			color: 'red',
			fillColor: '#f03',
			fillOpacity: 0.2,
			radius: 50000
		}).addTo(map);

		//circle.bindOverla(circlePopup);

		//map.on('click', onMapClick);

		markers = L.markerClusterGroup({
			spiderfyOnMaxZoom: false,
			showCoverageOnHover: false,
			zoomToBoundsOnClick: true,
			maxClusterRadius: 30
		});
		map.addLayer(markers);
	});

	function viewData() {
		console.log('test');
	}

	function search(e) {
		let lat = parseFloat(latitude.value);
		let long = parseFloat(longitude.value);
		let maxDistance = radius.value;
		console.log(lat, long, maxDistance);

		if (lat != null && long != null) {
			circle.setRadius(maxDistance * 1000);
			circle.setLatLng([lat, long]);

			let closestPoint: {};
			let closestDistance = Infinity;
			let nearbyPoints = points.filter((point) => {
				const distance = calculateDistance(lat, long, point.latitude, point.longitude);
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
				let marker = L.marker(point.latlng);
				marker.bindPopup(
					`<div>${point.name}</div><br><button type='button' on:click={viewData()}>view Data</button>`
				);
				markers.addLayer(marker);
			});

			map.fitBounds(circle.getBounds());
		}
	}
</script>

<div id="map" class="h-2/3 w-full" use:mapAction></div>
<input type="text" bind:this={latitude} on:change={search} value="48" />
<input type="text" bind:this={longitude} on:change={search} value="9" />
<input type="range" bind:this={radius} on:change={search} id="radius" min="1" max="1000" />
<button type="button" on:click={search}>search</button>
