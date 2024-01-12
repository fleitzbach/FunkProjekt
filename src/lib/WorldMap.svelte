<script lang="ts">
	import { onMount } from 'svelte';
	import * as am5 from '@amcharts/amcharts5?client';
	import * as am5map from '@amcharts/amcharts5/map?client';
	import am5geodata_worldHigh from '@amcharts/amcharts5-geodata/worldHigh?client';
	import am5themes_Animated from '@amcharts/amcharts5/themes/Animated?client';
	import { calculateDistance } from './calculateDistance';
	let chartdiv;
	let longitude;
	let latitude;
	let points;
	let radius;
	let pointSeries;
	let chart;
	let geoCircle;
	export let pointsPromise: Promise<
		Array<{ id: string; latitude: number; longitude: number; name: string }>
	>;

	async function dataLoaded() {}

	onMount(() => {
		pointsPromise.then((res) => {
			points = res;
			dataLoaded();
		});
		/* Chart code */
		// Create root element
		// https://www.amcharts.com/docs/v5/getting-started/#Root_element
		let root = am5.Root.new('chartdiv');

		// Set themes
		// https://www.amcharts.com/docs/v5/concepts/themes/
		root.setThemes([am5themes_Animated.new(root)]);

		// Create the map chart
		// https://www.amcharts.com/docs/v5/charts/map-chart/
		chart = root.container.children.push(
			am5map.MapChart.new(root, {
				panX: 'rotateX',
				panY: 'rotateY',
				projection: am5map.geoOrthographic(),
				maxZoomLevel: 500,
				minZoomLevel: 1,
				maxPanOut: 0.5
			})
		);

		chart.set('zoomControl', am5map.ZoomControl.new(root, {}));

		// Create main polygon series for countries
		// https://www.amcharts.com/docs/v5/charts/map-chart/map-polygon-series/
		let polygonSeries = chart.series.push(
			am5map.MapPolygonSeries.new(root, {
				geoJSON: am5geodata_worldHigh
			})
		);
		let graticuleSeries = chart.series.unshift(am5map.GraticuleSeries.new(root, {}));

		graticuleSeries.mapLines.template.setAll({
			stroke: am5.color(0x000000),
			strokeOpacity: 0.1
		});

		geoCircle = chart.series.push(am5map.MapPolygonSeries.new(root, {}));

		polygonSeries.mapPolygons.template.setAll({
			fill: am5.color(0xdadada)
		});

		// Create point series for markers
		// https://www.amcharts.com/docs/v5/charts/map-chart/map-point-series/
		pointSeries = chart.series.push(
			am5map.ClusteredPointSeries.new(root, {
				minDistance: 5,
				scatterDistance: 1,
				scatterRadius: 1,
				stopClusterZoom: 0.9
			})
		);

		// Set clustered bullet
		// https://www.amcharts.com/docs/v5/charts/map-chart/clustered-point-series/#Group_bullet
		pointSeries.set('clusteredBullet', function (root) {
			let container = am5.Container.new(root, {
				cursorOverStyle: 'pointer'
			});

			let circle1 = container.children.push(
				am5.Circle.new(root, {
					radius: 8,
					tooltipY: 0,
					fill: am5.color(0xff8c00)
				})
			);

			let circle2 = container.children.push(
				am5.Circle.new(root, {
					radius: 12,
					fillOpacity: 0.3,
					tooltipY: 0,
					fill: am5.color(0xff8c00)
				})
			);

			let circle3 = container.children.push(
				am5.Circle.new(root, {
					radius: 16,
					fillOpacity: 0.3,
					tooltipY: 0,
					fill: am5.color(0xff8c00)
				})
			);

			let label = container.children.push(
				am5.Label.new(root, {
					centerX: am5.p50,
					centerY: am5.p50,
					fill: am5.color(0xffffff),
					populateText: true,
					fontSize: '8',
					text: '{value}'
				})
			);

			container.events.on('click', function (e) {
				pointSeries.zoomToCluster(e.target.dataItem);
			});

			return am5.Bullet.new(root, {
				sprite: container
			});
		});

		// Create regular bullets
		pointSeries.bullets.push(function () {
			let circle = am5.Circle.new(root, {
				radius: 6,
				tooltipY: 0,
				fill: am5.color(0xff8c00),
				tooltipText: '{name}\n\n{id}\n{latitude}, {longitude}\n{distance}'
			});

			return am5.Bullet.new(root, {
				sprite: circle
			});
		});

		// Make stuff animate on load
		chart.appear(1000, 100);
	});

	function search(e) {
		let lat = parseFloat(latitude.value);
		let long = parseFloat(longitude.value);
		let maxDistance = radius.value;
		console.log(lat, long, maxDistance);

		if (lat != null && long != null) {
			// chart.zoomToGeoPoint({ longitude: long, latitude: lat }, 6);

			let geoCirclePolygon = am5map.getGeoCircle(
				{ latitude: lat, longitude: long },
				maxDistance / 110
			);

			geoCircle.data.setAll([{ geometry: geoCirclePolygon }]);
			geoCircle.mapPolygons.template.setAll({
				stroke: am5.color(0xffffff),
				strokeWidth: 2,
				fillOpacity: 0.5
			});

			let closestPoint: {};
			let closestDistance = Infinity;
			let nearbyPoints = points.filter((point) => {
				const distance = calculateDistance(lat, long, point.latitude, point.longitude);
				return distance <= maxDistance;
			});

			nearbyPoints = nearbyPoints.map((point) => {
				return {
					geometry: { type: 'Point', coordinates: [ point.longitude, point.latitude,] },
					id: point.id,
					name: point.name,
					distance: calculateDistance(lat, long, point.latitude, point.longitude)
				};
			});

			// console.log(nearbyPoints);
			pointSeries.data.setAll(nearbyPoints);
		}
	}
</script>

<!-- WorldMap.svelte -->

<div class="map" bind:this={chartdiv} id="chartdiv"></div>
<input type="text" bind:this={latitude} value="48" />
<input type="text" bind:this={longitude} value="9" />
<input type="range" bind:this={radius} id="radius" min="1" max="1000" />
<button type="button" on:click={search}>search</button>

<style>
	.map {
		width: 100%;
		height: 50%;
	}
</style>
