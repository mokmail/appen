<script lang="ts">
	import ChevronRight from 'lucide-svelte/icons/chevron-right';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<ChevronRight
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
