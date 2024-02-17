<script lang="ts">
	export let loading = false;
	export let loadingMessage = 'data loading...';

	export let noData = false;
	export let noDataMessage = 'no data available';
</script>

{#if loading}
    <div class="absolute inset-0 flex justify-center items-center bg-primary-foreground/70">
        {loadingMessage}
    </div>
{:else if noData}
    <div class="absolute inset-0 flex justify-center items-center bg-primary-foreground/70">
        {noDataMessage}
    </div>
{/if}
