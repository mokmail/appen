<script lang="ts">
	import ArrowUpLeft from 'lucide-svelte/icons/arrow-up-left';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ArrowUpLeft
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
