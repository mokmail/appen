<script lang="ts">
	import LayoutGrid from 'lucide-svelte/icons/layout-grid';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<LayoutGrid
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
