<script lang="ts">
	export let loading = false;
	export let loadingMessage = 'data loading...';

	export let noData = false;
	export let noDataMessage = 'no data available';

	export let backgroundOverlay = true;
</script>

{#if loading}
	<div
		class="absolute inset-0 flex items-center justify-center {backgroundOverlay
			? 'bg-primary-foreground/70'
			: ''}"
	>
		{loadingMessage}
	</div>
{:else if noData}
	<div
		class="absolute inset-0 flex items-center justify-center {backgroundOverlay
			? 'bg-primary-foreground/70'
			: ''}"
	>
		{noDataMessage}
	</div>
{/if}
