<script lang="ts">
	import SlidersHorizontal from 'lucide-svelte/icons/sliders-horizontal';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<SlidersHorizontal
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
