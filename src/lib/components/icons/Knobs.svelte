<script lang="ts">
	import SlidersVertical from 'lucide-svelte/icons/sliders-vertical';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<SlidersVertical
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
