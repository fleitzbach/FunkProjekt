<script lang="ts">
	import { cn } from '$lib/utils';
	import { DateField as DateFieldPrimitive } from 'bits-ui';

	type $$Props = DateFieldPrimitive.InputProps;

	let className: $$Props['class'] = undefined;

	export { className as class };
</script>

<DateFieldPrimitive.Root locale='de'>
	<div>
		<DateFieldPrimitive.Label class="text-sm font-semibold">
			<slot />
		</DateFieldPrimitive.Label>
		<DateFieldPrimitive.Input
			let:segments
			class={cn(
				'shadow-sm flex gap-1 h-10 min-w-32 rounded-md border border-input bg-transparent px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
				className
			)}
			{...$$restProps}
			on:click
			on:focusout
		>
			{#each segments as { part, value }}
				<DateFieldPrimitive.Segment {part} class="rounded-md ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
					{value}
				</DateFieldPrimitive.Segment>
			{/each}
		</DateFieldPrimitive.Input>
	</div>
</DateFieldPrimitive.Root>
