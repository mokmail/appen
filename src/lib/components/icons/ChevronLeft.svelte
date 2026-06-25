<script lang="ts">
	import ChevronLeft from 'lucide-svelte/icons/chevron-left';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ChevronLeft
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
