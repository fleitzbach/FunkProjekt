<!-- WorldMap.svelte -->

<div class="map" bind:this={chartdiv} id="chartdiv"></div>

<style>
	.map {
		width: 100%;
		height: 100%;
	}
</style>


<script lang="ts">
	import { onMount } from 'svelte';
	import * as am5 from '@amcharts/amcharts5?client';
	import * as am5map from '@amcharts/amcharts5/map?client';
	import am5geodata_worldLow from '@amcharts/amcharts5-geodata/worldLow?client';
	import am5themes_Animated from '@amcharts/amcharts5/themes/Animated?client';
	let chartdiv;
	export let pointsPromise: Promise<Array<{ id: string, latitude: number, longitude: number, name: string }>>;
	onMount(async () => {
		/* Chart code */
		// Create root element
		// https://www.amcharts.com/docs/v5/getting-started/#Root_element
		let root = am5.Root.new('chartdiv');
		
		// Set themes
		// https://www.amcharts.com/docs/v5/concepts/themes/
		root.setThemes([am5themes_Animated.new(root)]);
		
		// Create the map chart
		// https://www.amcharts.com/docs/v5/charts/map-chart/
		let chart = root.container.children.push(
			am5map.MapChart.new(root, {
				panX: 'rotateX',
				panY: 'translateY',
				projection: am5map.geoMercator()
			})
			);
			
			chart.set('zoomControl', am5map.ZoomControl.new(root, {}));
			
			// Create main polygon series for countries
			// https://www.amcharts.com/docs/v5/charts/map-chart/map-polygon-series/
			let polygonSeries = chart.series.push(
				am5map.MapPolygonSeries.new(root, {
					geoJSON: am5geodata_worldLow,
				})
				);
				
				polygonSeries.mapPolygons.template.setAll({
					fill: am5.color(0xdadada)
				});
				
				// Create point series for markers
				// https://www.amcharts.com/docs/v5/charts/map-chart/map-point-series/
				let pointSeries = chart.series.push(am5map.ClusteredPointSeries.new(root, {}));
				
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
				tooltipText: '{name}'
			});
			
			return am5.Bullet.new(root, {
				sprite: circle
			});
		});
		
		let points = await pointsPromise
		console.log(points)

		for (var i = 0; i < 1000; i++) {
			let point = points[i];
			addPoint(point.longitude, point.latitude, point.name);
		}
		
		function addPoint(longitude: number, latitude: number, title: string) {
			pointSeries.data.push({
				geometry: { type: 'Point', coordinates: [longitude, latitude] },
				title: title
			});
		}
		
		// Make stuff animate on load
		chart.appear(1000, 100);
		
		function search() {
			
		}
	});

</script>

