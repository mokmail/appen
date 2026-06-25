<script lang="ts">
	import ArrowRightToLine from 'lucide-svelte/icons/arrow-right-to-line';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ArrowRightToLine
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
