<script lang="ts">
	import ArrowUpFromLine from 'lucide-svelte/icons/arrow-up-from-line';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ArrowUpFromLine
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
